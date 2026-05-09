import math
import machine
import struct
import time

class QMC5883P:
    def __init__(self, i2c_bus=0, scl=5, sda=4, address=0x2C, declination=(0, 0)):
        self.i2c = machine.I2C(i2c_bus, scl=machine.Pin(scl), sda=machine.Pin(sda), freq=100000)
        self.address = address
        
        # Soft Reset del sensore per pulire letture sporche
        self.i2c.writeto_mem(self.address, 0x0A, b'\x80')
        time.sleep(0.05)
        
        # Configurazione Registro di Controllo 1 (0x0A)
        # 0xCF imposta: Modalità Continua, ODR 200Hz, OSR 512, Range +/- 30 Gauss
        self.i2c.writeto_mem(self.address, 0x0A, b'\xCF')
        time.sleep(0.05)
        
        # Converti la declinazione in radianti
        self.declination = (declination[0] + declination[1] / 60) * math.pi / 180

    def read(self):
        # Legge 6 byte a partire dal registro 0x01 (X_LSB, X_MSB, Y_LSB, Y_MSB, Z_LSB, Z_MSB)
        data = self.i2c.readfrom_mem(self.address, 0x01, 6)
        
        # Decodifica rapida in Little Endian (simbolo '<') per 3 interi con segno a 16 bit ('hhh')
        x, y, z = struct.unpack('<hhh', data)
        
        return x, y, z

    def heading(self, x, y):
        # Gestisce il caso in cui x e y siano esattamente 0 (evita divisioni per zero)
        if x == 0 and y == 0:
            return 0, 0
            
        heading_rad = math.atan2(y, x)
        heading_rad += self.declination

        # Correzione dell'angolo
        if heading_rad < 0:
            heading_rad += 2 * math.pi
        elif heading_rad > 2 * math.pi:
            heading_rad -= 2 * math.pi

        heading = heading_rad * 180 / math.pi
        degrees = math.floor(heading)
        minutes = round((heading - degrees) * 60)
        return degrees, minutes

    def format_result(self, x, y, z):
        degrees, minutes = self.heading(x, y)
        return 'X: {:>6}, Y: {:>6}, Z: {:>6} | Direzione: {}° {}′'.format(x, y, z, degrees, minutes)