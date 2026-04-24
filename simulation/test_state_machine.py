from machine import I2C, Pin
from state_machine import StateMachine
import bmp280  

LAUNCH_MODE = 0
SIM_MODE = 1

bmp_i2c = I2C(1, sda=Pin(10), scl=Pin(11), freq=100000) # I2C bus 1, SDA pin GP10, SCL pin GP11,
bmp = bmp280.BMP280(bmp_i2c)

# Testing
if __name__ == '__main__':
    sm = StateMachine(bmp, LAUNCH_MODE, 'initialize')
    print(sm)
    sm.esegui()
