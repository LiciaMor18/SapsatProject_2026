from state_machine import StateMachine

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

buzzer = PWM(Pin(15)) # Azzecca il pin corretto

# Sensors initialization
# bmp, p_0, T_0, h_0 = bmp280.initialize_BMP(BMP_i2c, BMP_scl, BMP_sda)
# rtc = urtc.initialize_RTC(RTC_i2c, RTC_scl, RTC_sda)
# sd = sdcard.initialize_SD(SD_spi, SD_sck, SD_mosi, SD_miso, SD_cs)
# mpu = imu.initialize_MPU(MPU_i2c, MPU_scl, MPU_sda, MPU_freq)


# Servomotors
aerobrake_servo = machine.PWM(machine.Pin(2))
aerobrake_servo.freq(50)  # Set PWM frequency to 50Hz, common for servo motors
parachute_servo = machine.PWM(machine.Pin(3))
parachute_servo.freq(50)  # Set PWM frequency to 50Hz, common for servo motors

if __name__ == '__main__':
    
    sm = StateMachine(buzzer, bmp, rtc, mpu, sd, aerobrake_servo, parachute_servo, p_0, 'start')
    print(sm)
    sm.run()






