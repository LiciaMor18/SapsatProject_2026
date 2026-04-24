from machine import I2C, Pin
import bmp280
import time
import math


def altitude(T_0, p_t, p_0):
    return (T_0 / LAMBDA) * (1 - (p_t / p_0)**EXP)

def compute_p0_T0(bmp):
    print(f'Computing initial pressure')
    p_tot = 0
    T_tot = 0
    for i in range(CALIBRATION_SAMPLES):
        p_tot += bmp.pressure
        T_tot += bmp.temperature
        
    p_tot /= CALIBRATION_SAMPLES
    T_tot /= CALIBRATION_SAMPLES
    print(f'Initial pressure: {p_tot}')
    print(f'Initial temperature: {T_tot}')
    return p_tot, T_tot
    
        
def initialize_BMP(i2c_ch, scl, sda):
    # Initialize I2C communication
    i2c_BMP = I2C(i2c_ch, sda = sda, scl = scl, freq=100000)

    # Configure BMP280 sensor
    bmp = bmp280.BMP280(i2c_BMP)
    bmp.oversample(bmp280.BMP280_OS_HIGH)
    bmp.use_case(bmp280.BMP280_CASE_INDOOR)
    bmp.power_mode = bmp280.BMP280_POWER_NORMAL
    
    p_0, T_0 = compute_p0_T0(bmp)
    
    print('BMP correctly initialized')
    return bmp, p_0, T_0

# Constants
LAMBDA = 0.0065   # Gradiente termico (K/m)
R = 8.31446       # Costante dei gas (J/(mol·K))
g = 9.80665       # Gravità (m/s^2)
M = 0.0289644     # Massa molare dell'aria (kg/mol)
EXP = (R * LAMBDA) / (g * M)

CALIBRATION_SAMPLES = 50

BMP_i2c = 0
BMP_sda = Pin(4)
BMP_scl = Pin(5)

# Configure BMP280 sensor
bmp, p_0, T_0 = initialize_BMP(BMP_i2c, BMP_scl, BMP_sda)

time.sleep(1)

h_0 = altitude(T_0, bmp.pressure, p_0)

print(f'p_0 = {p_0}, T_0 = {T_0}, h_0 = {h_0}, LAMBDA = {LAMBDA}, EXP = {EXP}')

while True:        
    T_t = bmp.temperature
    p_t = bmp.pressure
    h_t = altitude(T_0, p_t, p_0)

    # Print temperature and pressure data
    print(f'p_t = {p_t}, T_t = {T_t}, h_t = {h_t}')

    # Read data every second
    time.sleep_ms(1000)

