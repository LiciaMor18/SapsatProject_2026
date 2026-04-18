import utime
from machine import Pin

buzzer= Pin(15, Pin.OUT)

while 1:
    buzzer.high()
    utime.sleep(1)
    buzzer.low()
    utime.sleep(1)