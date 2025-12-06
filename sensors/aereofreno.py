import machine
import time

# PWM su GP2
servo = machine.PWM(machine.Pin(2))
servo.freq(50)  # 50Hz per i servomotori

# Conversion from angle -> duty cycle
def angle_to_duty(angle):
    # 0°=0.5ms, 180°=2.5ms
    pulse_width = 0.5 + (angle / 180) * 2.0  # ms
    duty = int((pulse_width / 20) * 65535)   # 20ms periodo
    return duty

def servo_write(angle):
    servo.duty_u16(angle_to_duty(angle))
    
#move servo to 0° angle
servo_write(0)
time.sleep(0.5)   # mezzo secondo per stabilizzarsi

# starts movement 0° to 70°
for angle in range(0, 70):  # 0 → 70
    servo_write(angle)
    time.sleep_ms(10)
    
for angle in range(70, -1, -1):  # 70 → 0
    servo_write(angle)
    time.sleep_ms(10)
