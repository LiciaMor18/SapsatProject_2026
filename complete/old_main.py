import time
import urtc
import bmp280
import sdcard
import os
import imu
from machine import I2C, Pin, SPI

# CONSTANTS
BMP_i2c = 0
BMP_sda = Pin(4)
BMP_scl = Pin(5)

RTC_i2c = 0
RTC_sda = Pin(4)
RTC_scl = Pin(5)

SD_spi = 1
SD_sck = Pin(14)
SD_mosi = Pin(15)
SD_miso = Pin(12)
SD_cs = Pin(13)

MPU_i2c = 0
MPU_sda = Pin(4)
MPU_scl = Pin(5)
MPU_freq = 400000

# Sensors initialization
bmp, p_0, T_0, h_0 = bmp280.initialize_BMP(BMP_i2c, BMP_scl, BMP_sda)
# rtc = urtc.initialize_RTC(RTC_i2c, RTC_scl, RTC_sda)
# sd = sdcard.initialize_SD(SD_spi, SD_sck, SD_mosi, SD_miso, SD_cs)
# mpu = imu.initialize_MPU(MPU_i2c, MPU_scl, MPU_sda, MPU_freq)

# Servomotors
aerobrake_servo = machine.PWM(machine.Pin(2))
aerobrake_servo.freq(50)  # Set PWM frequency to 50Hz, common for servo motors
parachute_servo = machine.PWM(machine.Pin(3))
parachute_servo.freq(50)  # Set PWM frequency to 50Hz, common for servo motors

while True:
    # RTC acquiring date and time
    # print('Entrato nel ciclo')
    # current_datetime = rtc.datetime()	# [comment when not using RTC]
    time.sleep_ms(10)
    
    # BMP acquiring temperature and pressure [comment when not using the sensor]
    T_t = bmp.temperature		# [comment when not using BMP]
    p_t = bmp.pressure			# [comment when not using BMP]
    h_t = bmp280.altitude(T_0, p_t, p_0)
    
    # MPU acquiring accelerations
    # acc_x, acc_y, acc_z = imu.update_gyro(mpu) # [comment when not using MPU]
    
   
    # Format the date and time to print on cmd
    # print(f"Date:{current_datetime.year:04d}-{current_datetime.month:02d}-{current_datetime.day:02d} ")		# [comment when not using RTC]
    # print(f"Time:{current_datetime.hour:02d}:{current_datetime.minute:02d}:{current_datetime.second:02d} ") # [comment when not using RTC]
    print(f"Temperature: {T_t}, Pressure: {p_t}, Altitude: {h_t}") # [comment when not using BMP]
    # print(f"Update: R:{acc_x:.1f} P:{acc_y:.1f} Y:{acc_z:.1f}") # [comment when not using MPU]
    
    #Writing data to CSV file
    # file = open('/sd/text.csv', 'a')
    # file.write(f"{current_datetime.year:04d}-{current_datetime.month:02d}-{current_datetime.day:02d}, {current_datetime.hour:02d}:{current_datetime.minute:02d}:{current_datetime.second:02d}, {T_t}, {p_t}, R:{acc_x:.1f} P:{acc_y:.1f} Y:{acc_z:.1f} \n")
    # file.write(f"0-0-0, 0:0:0, {T_t}, {p_t}, R:{acc_x:.1f} P:{acc_y:.1f} Y:{acc_z:.1f} \n")
    # file.close()
    
    
    time.sleep(1)