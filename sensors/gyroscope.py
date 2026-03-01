from machine import I2C, Pin
from imu import MPU6050
import time
import math

# Configurazione Hardware e Costanti 
i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=400000)
mpu = MPU6050(i2c)

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

def MPU_Init():
    i2c.writeto_mem(MPU_ADDR, PWR_MGMT_1, b'\x01')
    i2c.writeto_mem(MPU_ADDR, CONFIG, b'\x03')

def advanced_calibrate(samples=1000):
    global bx, by, bz
    MPU_Init()
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