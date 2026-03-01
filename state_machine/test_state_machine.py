from state_machine import StateMachine
from bmp280 import *

bmp_i2c = I2C(1, sda=Pin(10), scl=Pin(11), freq=100000) # I2C bus 1, SDA pin GP10, SCL pin GP11,

# Testing
if __name__ == '__main__':
    sm = StateMachine(initialize, bmp_i2c)
    
