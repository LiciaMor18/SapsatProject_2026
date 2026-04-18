from machine import I2C, Pin
from imu import MPU6050
import time
import math

class KalmanFilter:
    def __init__(self, q_angle=0.001, q_bias=0.003, r_measure=0.03):
        self.q_angle = q_angle
        self.q_bias = q_bias
        self.r_measure = r_measure
        self.angle = 0.0
        self.bias = 0.0
        self.P = [[0.0, 0.0], [0.0, 0.0]]

    def update(self, new_angle, new_rate, dt):
        # Step 1: Predizione
        rate = new_rate - self.bias
        self.angle += dt * rate
        self.P[0][0] += dt * (dt * self.P[1][1] - self.P[0][1] - self.P[1][0] + self.q_angle)
        self.P[0][1] -= dt * self.P[1][1]
        self.P[1][0] -= dt * self.P[1][1]
        self.P[1][1] += self.q_bias * dt
        # Step 2: Aggiornamento
        y = new_angle - self.angle
        s = self.P[0][0] + self.r_measure
        k = [self.P[0][0] / s, self.P[1][0] / s]
        self.angle += k[0] * y
        self.bias += k[1] * y
        p00_temp = self.P[0][0]
        p01_temp = self.P[0][1]
        self.P[0][0] -= k[0] * p00_temp
        self.P[0][1] -= k[0] * p01_temp
        self.P[1][0] -= k[1] * p00_temp
        self.P[1][1] -= k[1] * p01_temp
        return self.angle

# CONFIGURAZIONE HARDWARE 
i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=400000)
mpu = MPU6050(i2c)

# Inizializzazione del filtro Kalman per lo Yaw
kalman_yaw_filter = KalmanFilter()

MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B
CONFIG = 0x1A

# COSTANTI E VARIABILI DI STATO 
RAD_TO_DEG = 180 / math.pi 
ALPHA = 0.98           # Filtro Complementare
GYRO_DEADZONE = 0.05   # Riduce il drift dello Yaw

bx = by = bz = 0.0     # Offset calibrazione
pitch = roll = yaw = 0.0
last_time = time.ticks_ms()

# INIZIALIZZAZIONE E CALIBRAZIONE 
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
            print(f"Calibrazione: {int((i/samples)*100)}%")
        time.sleep_ms(2) 
    
    bx, by, bz = sum_gx / samples, sum_gy / samples, sum_gz / samples
    print("Calibrazione completata con successo!\n")

def update_gyro():
    global pitch, roll, yaw, last_time
    
    # 1. Calcolo del tempo
    current_time = time.ticks_ms()
    dt = time.ticks_diff(current_time, last_time) / 1000.0
    last_time = current_time
    if dt <= 0: return

    # 2. Lettura sensore
    ax, ay, az = mpu.accel.x, mpu.accel.y, mpu.accel.z
    gx = mpu.gyro.x - bx
    gy = mpu.gyro.y - by
    gz = mpu.gyro.z - bz

    # 3. Calcolo Filtro Complementare (Pitch/Roll)
    accel_pitch = math.atan2(ay, math.sqrt(ax**2 + az**2)) * RAD_TO_DEG
    accel_roll  = math.atan2(-ax, math.sqrt(ay**2 + az**2)) * RAD_TO_DEG

    pitch = ALPHA * (pitch + gx * dt) + (1 - ALPHA) * accel_pitch
    roll  = ALPHA * (roll + gy * dt) + (1 - ALPHA) * accel_roll

    # 4. Calcolo Yaw con Filtro di Kalman
    # Integriamo gz per avere un "angolo grezzo" da dare a Kalman
    raw_yaw_increment = 0
    if abs(gz) > GYRO_DEADZONE:
        raw_yaw_increment = gz * dt
    
    # Aggiorniamo lo yaw usando il filtro di Kalman
    # Passiamo lo yaw attuale + l'incremento, la velocità angolare e il dt
    yaw = kalman_yaw_filter.update(yaw + raw_yaw_increment, gz, dt)
    
    print(f"Update: P:{pitch:5.1f} R:{roll:5.1f} Y:{yaw:5.1f}")

# GETTER FUNCTIONS 
def get_pitch(): return pitch
def get_roll():  return roll
def get_yaw():   return yaw
def reset_yaw():
    global yaw
    yaw = 0.0
    kalman_yaw_filter.angle = 0.0
