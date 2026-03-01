# imu.py MicroPython driver for the InvenSense inertial measurement units
# This is the base class
# Adapted from Sebastian Plamauer's MPU9150 driver:
# https://github.com/micropython-IMU/micropython-mpu9150.git
# Authors Peter Hinch, Sebastian Plamauer
# V0.2 17th May 2017 Platform independent: utime and machine replace pyb

'''
mpu9250 is a micropython module for the InvenSense MPU9250 sensor.
It measures acceleration, turn rate and the magnetic field in three axis.
mpu9150 driver modified for the MPU9250 by Peter Hinch

The MIT License (MIT)
Copyright (c) 2014 Sebastian Plamauer, oeplse@gmail.com, Peter Hinch
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

# User access is now by properties e.g.
# myimu = MPU9250('X')
# magx = myimu.mag.x
# accelxyz = myimu.accel.xyz
# Error handling: on code used for initialisation, abort with message
# At runtime try to continue returning last good data value. We don't want aircraft
# crashing. However if the I2C has crashed we're probably stuffed.

from utime import sleep_ms
from machine import I2C
from vector3d import Vector3d
import time


class MPUException(OSError):
    '''
    Exception for MPU devices
    '''
    pass


def bytes_toint(msb, lsb):
    '''
    Convert two bytes to signed integer (big endian)
    for little endian reverse msb, lsb arguments
    Can be used in an interrupt handler
    '''
    if not msb & 0x80:
        return msb << 8 | lsb  # +ve
    return - (((msb ^ 255) << 8) | (lsb ^ 255) + 1)


class MPU6050(object):
    '''
    Module for InvenSense IMUs. Base class implements MPU6050 6DOF sensor, with
    features common to MPU9150 and MPU9250 9DOF sensors.
    '''

    _I2Cerror = "I2C failure when communicating with IMU"
    _mpu_addr = (104, 105)  # addresses of MPU9150/MPU6050. There can be two devices
    _chip_id = 112

    def __init__(self, side_str, device_addr=None, transposition=(0, 1, 2), scaling=(1, 1, 1)):

        self._accel = Vector3d(transposition, scaling, self._accel_callback)
        self._gyro = Vector3d(transposition, scaling, self._gyro_callback)
        self.buf1 = bytearray(1)                # Pre-allocated buffers for reads: allows reads to
        self.buf2 = bytearray(2)                # be done in interrupt handlers
        self.buf3 = bytearray(3)
        self.buf6 = bytearray(6)

        sleep_ms(200)                           # Ensure PSU and device have settled
        if isinstance(side_str, str):           # Non-pyb targets may use other than X or Y
            self._mpu_i2c = I2C(side_str)
        elif hasattr(side_str, 'readfrom'):     # Soft or hard I2C instance. See issue #3097
            self._mpu_i2c = side_str
        else:
            raise ValueError("Invalid I2C instance")

        if device_addr is None:
            devices = set(self._mpu_i2c.scan())
            mpus = devices.intersection(set(self._mpu_addr))
            number_of_mpus = len(mpus)
            if number_of_mpus == 0:
                raise MPUException("No MPU's detected")
            elif number_of_mpus == 1:
                self.mpu_addr = mpus.pop()
            else:
                raise ValueError("Two MPU's detected: must specify a device address")
        else:
            if device_addr not in (0, 1):
                raise ValueError('Device address must be 0 or 1')
            self.mpu_addr = self._mpu_addr[device_addr]

        self.chip_id                     # Test communication by reading chip_id: throws exception on error
        # Can communicate with chip. Set it up.
        self.wake()                             # wake it up
        self.passthrough = True                 # Enable mag access from main I2C bus
        self.accel_range = 0                    # default to highest sensitivity
        self.gyro_range = 0                     # Likewise for gyro

    # read from device
    def _read(self, buf, memaddr, addr):        # addr = I2C device address, memaddr = memory location within the I2C device
        '''
        Read bytes to pre-allocated buffer Caller traps OSError.
        '''
        self._mpu_i2c.readfrom_mem_into(addr, memaddr, buf)

    # write to device
    def _write(self, data, memaddr, addr):
        '''
        Perform a memory write. Caller should trap OSError.
        '''
        self.buf1[0] = data
        self._mpu_i2c.writeto_mem(addr, memaddr, self.buf1)

    # wake
    def wake(self):
        '''
        Wakes the device.
        '''
        try:
            self._write(0x01, 0x6B, self.mpu_addr)  # Use best clock source
        except OSError:
            raise MPUException(self._I2Cerror)
        return 'awake'

    # mode
    def sleep(self):
        '''
        Sets the device to sleep mode.
        '''
        try:
            self._write(0x40, 0x6B, self.mpu_addr)
        except OSError:
            raise MPUException(self._I2Cerror)
        return 'asleep'

    # chip_id
    @property
    def chip_id(self):
        '''
        Returns Chip ID
        '''
        try:
            self._read(self.buf1, 0x75, self.mpu_addr)
        except OSError:
            raise MPUException(self._I2Cerror)
        chip_id = int(self.buf1[0])
        if chip_id != self._chip_id:
            raise ValueError('Bad chip ID retrieved: MPU communication failure')
        return chip_id

    @property
    def sensors(self):
        '''
        returns sensor objects accel, gyro
        '''
        return self._accel, self._gyro

    # get temperature
    @property
    def temperature(self):
        '''
        Returns the temperature in degree C.
        '''
        try:
            self._read(self.buf2, 0x41, self.mpu_addr)
        except OSError:
            raise MPUException(self._I2Cerror)
        return bytes_toint(self.buf2[0], self.buf2[1])/340 + 35  # I think

    # passthrough
    @property
    def passthrough(self):
        '''
        Returns passthrough mode True or False
        '''
        try:
            self._read(self.buf1, 0x37, self.mpu_addr)
            return self.buf1[0] & 0x02 > 0
        except OSError:
            raise MPUException(self._I2Cerror)

    @passthrough.setter
    def passthrough(self, mode):
        '''
        Sets passthrough mode True or False
        '''
        if type(mode) is bool:
            val = 2 if mode else 0
            try:
                self._write(val, 0x37, self.mpu_addr)  # I think this is right.
                self._write(0x00, 0x6A, self.mpu_addr)
            except OSError:
                raise MPUException(self._I2Cerror)
        else:
            raise ValueError('pass either True or False')

    # sample rate. Not sure why you'd ever want to reduce this from the default.
    @property
    def sample_rate(self):
        '''
        Get sample rate as per Register Map document section 4.4
        SAMPLE_RATE= Internal_Sample_Rate / (1 + rate)
        default rate is zero i.e. sample at internal rate.
        '''
        try:
            self._read(self.buf1, 0x19, self.mpu_addr)
            return self.buf1[0]
        except OSError:
            raise MPUException(self._I2Cerror)

    @sample_rate.setter
    def sample_rate(self, rate):
        '''
        Set sample rate as per Register Map document section 4.4
        '''
        if rate < 0 or rate > 255:
            raise ValueError("Rate must be in range 0-255")
        try:
            self._write(rate, 0x19, self.mpu_addr)
        except OSError:
            raise MPUException(self._I2Cerror)

    # Low pass filters. Using the filter_range property of the MPU9250 is
    # harmless but gyro_filter_range is preferred and offers an extra setting.
    @property
    def filter_range(self):
        '''
        Returns the gyro and temperature sensor low pass filter cutoff frequency
        Pass:               0   1   2   3   4   5   6
        Cutoff (Hz):        250 184 92  41  20  10  5
        Sample rate (KHz):  8   1   1   1   1   1   1
        '''
        try:
            self._read(self.buf1, 0x1A, self.mpu_addr)
            res = self.buf1[0] & 7
        except OSError:
            raise MPUException(self._I2Cerror)
        return res

    @filter_range.setter
    def filter_range(self, filt):
        '''
        Sets the gyro and temperature sensor low pass filter cutoff frequency
        Pass:               0   1   2   3   4   5   6
        Cutoff (Hz):        250 184 92  41  20  10  5
        Sample rate (KHz):  8   1   1   1   1   1   1
        '''
        # set range
        if filt in range(7):
            try:
                self._write(filt, 0x1A, self.mpu_addr)
            except OSError:
                raise MPUException(self._I2Cerror)
        else:
            raise ValueError('Filter coefficient must be between 0 and 6')

    # accelerometer range
    @property
    def accel_range(self):
        '''
        Accelerometer range
        Value:              0   1   2   3
        for range +/-:      2   4   8   16  g
        '''
        try:
            self._read(self.buf1, 0x1C, self.mpu_addr)
            ari = self.buf1[0]//8
        except OSError:
            raise MPUException(self._I2Cerror)
        return ari

    @accel_range.setter
    def accel_range(self, accel_range):
        '''
        Set accelerometer range
        Pass:               0   1   2   3
        for range +/-:      2   4   8   16  g
        '''
        ar_bytes = (0x00, 0x08, 0x10, 0x18)
        if accel_range in range(len(ar_bytes)):
            try:
                self._write(ar_bytes[accel_range], 0x1C, self.mpu_addr)
            except OSError:
                raise MPUException(self._I2Cerror)
        else:
            raise ValueError('accel_range can only be 0, 1, 2 or 3')

    # gyroscope range
    @property
    def gyro_range(self):
        '''
        Gyroscope range
        Value:              0   1   2    3
        for range +/-:      250 500 1000 2000  degrees/second
        '''
        # set range
        try:
            self._read(self.buf1, 0x1B, self.mpu_addr)
            gri = self.buf1[0]//8
        except OSError:
            raise MPUException(self._I2Cerror)
        return gri

    @gyro_range.setter
    def gyro_range(self, gyro_range):
        '''
        Set gyroscope range
        Pass:               0   1   2    3
        for range +/-:      250 500 1000 2000  degrees/second
        '''
        gr_bytes = (0x00, 0x08, 0x10, 0x18)
        if gyro_range in range(len(gr_bytes)):
            try:
                self._write(gr_bytes[gyro_range], 0x1B, self.mpu_addr)  # Sets fchoice = b11 which enables filter
            except OSError:
                raise MPUException(self._I2Cerror)
        else:
            raise ValueError('gyro_range can only be 0, 1, 2 or 3')

    # Accelerometer
    @property
    def accel(self):
        '''
        Acceleremoter object
        '''
        return self._accel

    def _accel_callback(self):
        '''
        Update accelerometer Vector3d object
        '''
        try:
            self._read(self.buf6, 0x3B, self.mpu_addr)
        except OSError:
            raise MPUException(self._I2Cerror)
        self._accel._ivector[0] = bytes_toint(self.buf6[0], self.buf6[1])
        self._accel._ivector[1] = bytes_toint(self.buf6[2], self.buf6[3])
        self._accel._ivector[2] = bytes_toint(self.buf6[4], self.buf6[5])
        scale = (16384, 8192, 4096, 2048)
        self._accel._vector[0] = self._accel._ivector[0]/scale[self.accel_range]
        self._accel._vector[1] = self._accel._ivector[1]/scale[self.accel_range]
        self._accel._vector[2] = self._accel._ivector[2]/scale[self.accel_range]

    def get_accel_irq(self):
        '''
        For use in interrupt handlers. Sets self._accel._ivector[] to signed
        unscaled integer accelerometer values
        '''
        self._read(self.buf6, 0x3B, self.mpu_addr)
        self._accel._ivector[0] = bytes_toint(self.buf6[0], self.buf6[1])
        self._accel._ivector[1] = bytes_toint(self.buf6[2], self.buf6[3])
        self._accel._ivector[2] = bytes_toint(self.buf6[4], self.buf6[5])

    # Gyro
    @property
    def gyro(self):
        '''
        Gyroscope object
        '''
        return self._gyro

    def _gyro_callback(self):
        '''
        Update gyroscope Vector3d object
        '''
        try:
            self._read(self.buf6, 0x43, self.mpu_addr)
        except OSError:
            raise MPUException(self._I2Cerror)
        self._gyro._ivector[0] = bytes_toint(self.buf6[0], self.buf6[1])
        self._gyro._ivector[1] = bytes_toint(self.buf6[2], self.buf6[3])
        self._gyro._ivector[2] = bytes_toint(self.buf6[4], self.buf6[5])
        scale = (131, 65.5, 32.8, 16.4)
        self._gyro._vector[0] = self._gyro._ivector[0]/scale[self.gyro_range]
        self._gyro._vector[1] = self._gyro._ivector[1]/scale[self.gyro_range]
        self._gyro._vector[2] = self._gyro._ivector[2]/scale[self.gyro_range]

    def get_gyro_irq(self):
        '''
        For use in interrupt handlers. Sets self._gyro._ivector[] to signed
        unscaled integer gyro values. Error trapping disallowed.
        '''
        self._read(self.buf6, 0x43, self.mpu_addr)
        self._gyro._ivector[0] = bytes_toint(self.buf6[0], self.buf6[1])
        self._gyro._ivector[1] = bytes_toint(self.buf6[2], self.buf6[3])
        self._gyro._ivector[2] = bytes_toint(self.buf6[4], self.buf6[5])

# My addiction
def initialize_MPU(i2c_ch, scl, sda, freq):
    i2c = I2C(i2c_ch, scl = scl, sda = sda, freq = freq)
    mpu = MPU6050(i2c)
    
    advanced_calibrate(i2c, mpu, 1000)
    
MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B
CONFIG = 0x1A

# Variabili di Stato Globali 
bx = by = bz = 0.0
filtered_x = filtered_y = 0.0
pure_gyro_x = pure_gyro_y = pure_gyro_z = 0.0

# Variabili per i dati istantanei (per i getter)
last_ax = last_ay = last_az = 0.0
last_gx = last_gy = last_gz = 0.0

alpha = 0.96 
last_time = time.ticks_ms()

   

def advanced_calibrate(i2c, mpu, samples=1000):
    global bx, by, bz
    
    i2c.writeto_mem(MPU_ADDR, PWR_MGMT_1, b'\x01')
    i2c.writeto_mem(MPU_ADDR, CONFIG, b'\x03')
    
    print(f"Calibrazione... Tenere fermo il sensore ({samples} campioni)")
    sum_gx = sum_gy = sum_gz = 0
    for i in range(samples):
        sum_gx += mpu.gyro.x
        sum_gy += mpu.gyro.y
        sum_gz += mpu.gyro.z
        if i % (samples // 10) == 0:
            percentuale = (i / samples) * 100
            print(f"Calibrazione: {int(percentuale)}%")
        time.sleep_ms(2) 
    
    bx, by, bz = sum_gx / samples, sum_gy / samples, sum_gz / samples
    print("Calibrazione completata con successo!\n")

def update_gyro():
    """Aggiorna la logica degli angoli e le variabili globali senza ritornare nulla"""
    global last_time, filtered_x, filtered_y, pure_gyro_x, pure_gyro_y, pure_gyro_z
    global last_ax, last_ay, last_az, last_gx, last_gy, last_gz

    # Delta Time
    current_time = time.ticks_ms()
    dt = time.ticks_diff(current_time, last_time) / 1000.0
    last_time = current_time
    if dt <= 0: dt = 0.001

    # 1. Lettura Accelerazione
    last_ax, last_ay, last_az = mpu.accel.x, mpu.accel.y, mpu.accel.z

    # 2. Lettura Velocità Angolare (rimozione bias)
    last_gx = mpu.gyro.x - bx
    last_gy = mpu.gyro.y - by
    last_gz = mpu.gyro.z - bz

    # 3. Posizione Angolare (Integrale puro)
    pure_gyro_x += last_gx * dt
    pure_gyro_y += last_gy * dt
    pure_gyro_z += last_gz * dt

    # 4. Filtro Complementare
    accel_angle_x = math.atan2(last_ay, last_az) * 57.2957
    accel_angle_y = math.atan2(-last_ax, math.sqrt(last_ay**2 + last_az**2)) * 57.2957
    
    filtered_x = alpha * (filtered_x + last_gx * dt) + (1 - alpha) * accel_angle_x
    filtered_y = alpha * (filtered_y + last_gy * dt) + (1 - alpha) * accel_angle_y

    print(f"Update: P:{filtered_x:.1f} R:{filtered_y:.1f} Y:{pure_gyro_z:.1f}")
    
    return filtered_x, filtered_y, pure_gyro_z

# Getter Functions

def get_current_yaw():
    return pure_gyro_z

def get_gyro_z_speed():
    return last_gz

def get_pitch():
    return filtered_x

def get_roll():
    return filtered_y

def get_accel_z():
    return last_az