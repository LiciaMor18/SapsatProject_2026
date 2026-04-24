from machine import I2C, Pin
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
devices = i2c.scan()

if len(devices) == 0:
    print("No I2C devices found!")
else:
    print("I2C devices found:", [hex(device) for device in devices])