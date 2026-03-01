import time
import urtc
import bmp280
import sdcard
import os
from machine import I2C, Pin, SPI

# CONSTANTS
BMP_i2c = 1
BMP_scl = Pin(11)
BMP_sda = Pin(10)

RTC_i2c = 0
RTC_sda = Pin(16)
RTC_scl = Pin(17)

SD_spi = 1
SD_sck = Pin(14)
SD_mosi = Pin(15)
SD_miso = Pin(12)
SD_cs = Pin(13)

# Sensors initialization
bmp = bmp280.initialize_BMP(BMP_i2c, BMP_scl, BMP_sda)
rtc = urtc.initialize_RTC(RTC_i2c, RTC_scl, RTC_sda)
sd = sdcard.initialize_SD(SD_spi, SD_sck, SD_mosi, SD_miso, SD_cs)


while True:
    # RTC acquiring date and time
    current_datetime = rtc.datetime()
    
    # BMP acquiring temperature and pressure [comment when not using the sensor]
    bmp.use_case(bmp280.BMP280_CASE_WEATHER)
    T_t = bmp.temperature
    p_t = bmp.pressure
   
    # Format the date and time to print on cmd
    print(f"Date:{current_datetime.year:04d}-{current_datetime.month:02d}-{current_datetime.day:02d} ")
    print(f"Time:{current_datetime.hour:02d}:{current_datetime.minute:02d}:{current_datetime.second:02d} ")
    print(f"Temperature: {T_t} ") # [comment when not using the sensor]
    print(f"Pressure: {p_t} ")    # [comment when not using the sensor]
    
    # Writing data to CSV file
    file = open('/sd/text.csv', 'a')
    file.write(f"{current_datetime.year:04d}-{current_datetime.month:02d}-{current_datetime.day:02d}, {current_datetime.hour:02d}:{current_datetime.minute:02d}:{current_datetime.second:02d}, {T_t}, {p_t} \n")
    file.close()
    
    
    time.sleep(1)