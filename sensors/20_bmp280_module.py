from machine import I2C, Pin
import bmp280
import time
import math

# Initialize I2C communication
i2c = I2C(1, sda=Pin(10), scl=Pin(11), freq=100000) # I2C bus 1, SDA pin GP10, SCL pin GP11,

# Configure BMP280 sensor
bmp = bmp280.BMP280(i2c)
bmp.oversample(bmp280.BMP280_OS_HIGH)

temp = 0
pressure = 0

p_0 = bmp.pressure
t_0 = bmp.temperature
LAMBDA = -0.0065
R = 8.315
g = 9.8067
M = 0.0290
EXP = (LAMBDA * R) / (g * M)



h_0 = t_0 / LAMBDA * (1 - 1**EXP)

while True:
    # Set sensor to weather monitoring mode
    bmp.use_case(bmp280.BMP280_CASE_WEATHER)
    
    temp = bmp.temperature
    pressure = bmp.pressure

    # Print temperature and pressure data
    print(f"tempC: {temp}")
    print(f"pressure: {pressure} Pa")

    # Read data every second
    time.sleep_ms(1000)

