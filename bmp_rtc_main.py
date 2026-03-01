import time
import urtc
import bmp280 
from machine import I2C, Pin


rtc = urtc.initialize_RTC()
bmp = bmp280.initialize_BMP()


while True:
    # RTC
    current_datetime = rtc.datetime()
    
    # BMP
    bmp.use_case(bmp280.BMP280_CASE_WEATHER)
    T_t = bmp.temperature
    p_t = bmp.pressure
   
    # Format the date and time
    print(
        f"Date:{current_datetime.year:04d}-{current_datetime.month:02d}-{current_datetime.day:02d} "
        f"Time:{current_datetime.hour:02d}:{current_datetime.minute:02d}:{current_datetime.second:02d} "
        f"Temperature: {T_t} "
        f"Pressure: {p_t} "
    )
    
    
    
    time.sleep(1)