from machine import Pin, PWM
# Importiamo le funzioni necessarie dalla libreria buzzer
from buzzer import playsong
from utime import sleep
import math

from message import *
class StateMachine:
    def __init__(self, buzzer_obj, specific_state='start'):
        self.state = specific_state
        self.buzzer = PWM(Pin(15))
        
        # Flag per evitare che la canzone riparta all'infinito in loop nell'ultimo stato
        self.song_played = False
        self.is_running =False #utile per il run

        self.allowed = {
            "start": "ascent",
            "ascent": "apogee",
            "apogee": "descent",
            "descent": "parachute",
            "parachute": "landing",
            "landing": "end",
            "end": "end"
        }

        self.logic = {
            "start": self._logic_start,
            "ascent": self._logic_ascent,
            "apogee": self._logic_apogee,
            "descent": self._logic_descent,
            "parachute": self._logic_parachute,
            "landing": self._logic_landing,
            "end": self._logic_end
        }

    def transition(self):
        old_state = self.state
        self.state = self.allowed.get(self.state, self.state)
        if old_state != self.state:
            print(f"TRANSITION: {old_state} -> {self.state}")

    # FUNZIONI

    def _logic_start(self,message: Message):

        tripla = message.accelerations # Esempio di valori
        ax, ay, az = tripla[0],tripla[1],tripla[2]
        accelerazione_totale = math.sqrt(ax ** 2 + ay ** 2 + az ** 2)
        if accelerazione_totale > 20 :
            print("accellerazione maggiore 20m/s^2")
            self.transition()

    def _logic_ascent(self,message: Message):

        altezze= message.heights
        if altezze[1] < altezze[0]:
            print("discesa iniziata")
            self.transition()

    def _logic_apogee(self, message: Message):
        pressioni= message.pressures
        if pressioni[1] > pressioni[0]:
            print("aereofreni attivati")
            self.transition()

    def _logic_descent(self, message: Message):

        tripla = message.accelerations
        ax, ay, az = tripla[0], tripla[1], tripla[2]
        accelerazione_totale = math.sqrt(ax ** 2 + ay ** 2 + az ** 2)
        if accelerazione_totale < -9:
            print("accellerazione minore di -9m/s^2")
            self.transition()

    def _logic_parachute(self, message:Message):

        altitudine= message.heights[1]
        if altitudine <200:
            print("Apertura paracadute")
            self.transition()


    def _logic_landing(self, message:Message):
        altitudine = message.heights[1]
        if altitudine < 5:
            print("quasi atterrati!")
            self.transition()

    def _logic_end(self, message:Message):
        # Eseguiamo la canzone solo una volta quando arriviamo alla fine
        altitudine = message.heights[1]
        if altitudine <1:
            #modo stupido per dire che siamo arrivati
            print("Missione completata! Riproduzione segnale acustico...")
            song = ["E5", "G5", "A5", "P", "E5", "G5", "B5", "A5"]
            playsong(self.buzzer, song)
            self.song_played = True
            self.is_running = True


    def acquisisci_sensori_template(self) -> Message:
        """
        Genera un oggetto MessaggioDati con valori di test verosimili.
        """
        # 1. Dati Ambientali
        pressione = 1013.25  # hPa (Livello del mare)
        altezza = 450.5  # metri
        temperatura = 22.4  # °C

        #
        # Pitch, Roll, Yaw
        angoli_xyz = (1.5, -0.2, 120.0)

        # Accelerazione (m/s²)
        #
        accel_xyz = (0.05, 0.02, 9.81)

        # Magnetometro
        mag_xyz = (22.5, -15.0, -35.2)

        # 5. Timestamp
        adesso = datetime.now()
        data_corrente = adesso.strftime("%d/%m/%Y")
        ora_corrente = adesso.strftime("%H:%M:%S")

        # Creazione e restituzione dell'oggetto
        return Message(
            pressione=pressione,
            altezza=altezza,
            temperatura=temperatura,
            angoli_xyz=angoli_xyz,
            accel_xyz=accel_xyz,
            mag_xyz=mag_xyz,
            data=data_corrente,
            ora=ora_corrente
        )
    def run(self):
        #dovrà prendere in input il message
        print("Avvio simulazione...")
        while not self.is_running:
            message = self.acquisisci_sensori_template() #funzione che ottiene i dati
            # Recupera la funzione logica per lo stato attuale
            execution_func = self.logic.get(self.state)
            
            if execution_func:
                # Eseguiamo la logica passandogli i dati
                execution_func(message)
            
           
            sleep(1)
            
        print("Simulazione completata.")
       

