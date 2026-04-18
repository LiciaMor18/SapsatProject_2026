from datetime import datetime

class Message:
    # Variabile di classe per gestire l'incremento globale
    _id_counter = 1

    def __init__(self, pressione, altezza, temperatura,
                 angoli_xyz, accel_xyz, mag_xyz, data=None, ora=None):
        # Gestione ID automatico
        self.id_campione = Message._id_counter
        Message._id_counter +=1

        # Dati sensori
        self.pressure = pressione
        self.height = altezza
        self.temperature = temperatura

        # Terne XYZ (tupla)
        # lo spacchettamento verrà fatto direttamente nelle funzioni della state machine
        self.angles= angoli_xyz
        self.accelerations= accel_xyz
        self.mag = mag_xyz

        # Gestione Data e Ora (se non fornite, usa quelle attuali)
        now = datetime.now()
        self.data = data if data else now.strftime("%d/%m/%Y")
        self.ora = ora if ora else now.strftime("%H:%M:%S")

        #self.sanity_check = ottiene in base ai dati che sono stati ottenuti

def get_pressure(self):
    return self.pressure

def get_height(self):
    return self.height

def get_temperature(self):
    return self.temperature

def get_angles(self):
    return self.angles

def get_accelerations(self):
    return self.accelerations

def get_mag(self):
    return self.mag
