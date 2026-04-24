class Message:
    # Variabile di classe per gestire l'incremento globale
    _id_counter = 1

    def __init__(self, pressioni, altezze, temperatura,
                 angoli_xyz, accel_xyz, mag_xyz, ora):
        # Gestione ID automatico
        self.id_campione = Message._id_counter
        Message._id_counter +=1

        # Dati sensori
        # devono essere liste di due elementi, indice 0 pressione precedente indice 1 pressione corrente
        self.pressures = pressioni
        self.heights = altezze

        self.temperature = temperatura

        # Terne XYZ ()
        # lo spacchettamento verrà fatto direttamente nelle funzioni della state machine
        self.angles= angoli_xyz
        self.accelerations= accel_xyz
        self.mag = mag_xyz

        # Gestione Ora (se non fornite, usa quelle attuali)
        self.ora = ora   # if ora else now.strftime("%H:%M:%S")

        #self.sanity_check = ottiene in base ai dati che sono stati ottenuti
        
    def get_pressures(self):
        return self.pressures

    def get_heights(self):
        return self.heights

    def get_temperature(self):
        return self.temperature

    def get_angles(self):
        return self.angles

    def get_accelerations(self):
        return self.accelerations

    def get_mag(self):
        return self.mag


