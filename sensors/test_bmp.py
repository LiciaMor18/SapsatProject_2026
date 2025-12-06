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
T_0 = bmp.temperature
LAMBDA = -0.0065
R = 8.315
g = 9.8067
M = 0.0290
EXP = - (LAMBDA * R) / (g * M)



h_0 = T_0 / LAMBDA * (1 - 1**EXP)
print(f'p_0 = {p_0}, T_0 = {T_0}, h_0 = {h_0}, LAMBDA = {LAMBDA}, EXP = {EXP}, ')

while True:
    # Set sensor to weather monitoring mode
    bmp.use_case(bmp280.BMP280_CASE_WEATHER)
    
    T_t = bmp.temperature
    p_t = bmp.pressure
    h_t = T_0 / LAMBDA * (1 - (p_t / p_0)**EXP)

    # Print temperature and pressure data
    print(f'p_t = {p_t}, T_t = {T_t}, h_t = {h_t}')

    # Read data every second
    time.sleep_ms(1000)

