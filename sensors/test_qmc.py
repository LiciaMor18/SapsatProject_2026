from qmc5883p import QMC5883P
import time

# Usa la tua declinazione locale (qui mantenuta a 3 gradi e 14 minuti)
sensore = QMC5883P(i2c_bus=0, scl=5, sda=4, declination=(3, 14))

print("Inizio lettura del sensore QMC5883P...")

while True:
    x, y, z = sensore.read()
    print(sensore.format_result(x, y, z))
    time.sleep(0.2)