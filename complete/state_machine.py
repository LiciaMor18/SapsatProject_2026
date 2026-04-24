from machine import Pin, PWM
# Importiamo le funzioni necessarie dalla libreria buzzer
from buzzer import playsong
from utime import sleep
import math
import servo
import bmp280
import urtc

from message import *

class StateMachine:
    def __init__(self, buzzer_obj, bmp, rtc, mpu, sd, aerobrake, parachute, p_0, specific_state='start'):
        self.state = specific_state
        self.buzzer = buzzer
        self.bmp = bmp
        self.rtc = rtc
        self.mpu = mpu
        self.sd = sd
        self.aerobake = aerobake
        self.parachute = parachute
        self.p_0 = p_0
        self.height = 0
        
        
        # Flag per evitare che la canzone riparta all'infinito in loop nell'ultimo stato
        self.song_played = False
        self.is_running = False #utile per il run

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
        tripla = message.get_accelerations() # Esempio di valori
        print(f'id:{message._id_counter} tripla {tripla}')
        ax, ay, az = tripla[0],tripla[1],tripla[2]
        accelerazione_totale = math.sqrt(ax ** 2 + ay ** 2 + az ** 2)
        
        if (message._id_counter == 6):
           accelerazione_totale = 60
            
        if accelerazione_totale > 20 :
            print("accellerazione maggiore 20m/s^2")
            self.transition()

    def _logic_ascent(self,message: Message):
        altezze = message.get_heights()
        print(f'id:{message._id_counter} altezze:{altezze}')
        
        if (message._id_counter == 9):
           altezze[1] = 300
        
        if altezze[1] < altezze[0]:
            print("raggiunto apogeo")
            self.transition()

    def _logic_apogee(self, message: Message):
        pressioni= message.get_pressures()
        print(f'id:{message._id_counter} pressioni:{pressioni}')
        
        if (message._id_counter == 13):
           pressioni[1] = 3000
           
        if pressioni[1] > pressioni[0]:
            print("aereofreni attivati")
            # FUNZIONE AEROFRENO
            servo.deploy_aerobrake(self.aerobrake)
            print("discesa iniziata")
            self.transition()

    def _logic_descent(self, message: Message):
        az = message.get_accelerations()[2]
        
        print(f'id:{message._id_counter} az:{az}')
        
        if (message._id_counter == 17):
           az = -10
        
        if az < -6:
            print("accelerazione minore di -9m/s^2")
            self.transition()

    def _logic_parachute(self, message:Message):
        altitudine= message.get_heights()[1]
        
        print(f'id:{message._id_counter} altitudine:{altitudine}')
        
        if (message._id_counter == 21):
           altitudine = 30
        
        if altitudine <200:
            print("Apertura paracadute")
            # FUNZIONE PARACADUTE
            servo.deploy_parachute(self.parachute)
            self.transition()


    def _logic_landing(self, message:Message):
        altitudine= message.get_heights()[1]
        
        print(f'id:{message._id_counter} altitudine:{altitudine}')
        
        if (message._id_counter == 24):
           altitudine = 15
        
        if altitudine < 20:
            print("quasi atterrati!")
            self.transition()

    def _logic_end(self, message:Message):
        # Eseguiamo la canzone solo una volta quando arriviamo alla fine
        altitudine = message.get_heights()[1]
        
        print(f'id:{message._id_counter} altitudine:{altitudine}')
        
        if (message._id_counter == 28):
           altitudine = 5
        
        if altitudine < 10:
            #modo stupido per dire che siamo arrivati
            print("Missione completata! Riproduzione segnale acustico...")
            song = ["E5", "G5", "A5", "P", "E5", "G5", "B5", "A5"]
            # playsong(self.buzzer, song)
            self.song_played = True
            self.is_running = True
    
    def get_data(self) -> Message:
        T_t = bmp.temperature
        p_t = bmp.pressure
        h_t = bmp280.altitude(T_0, p_t, p_0)
        curr_time = rtc.datetime()
        angles = [0, 0, 0]
        acc_x, acc_y, acc_z = imu.update_gyro(mpu)
        acc = [acc_x, acc_y, acc_z]
        mag = [0, 0, 0]
        
        if (p_t != self.p_0):
            press = [self.p_0, p_t]
            self.p_0 = p_t
        else:
            press = [0, self.p_0]
            
        if (h_t != 0):
            height = [0, h_t]
            self.height = h_t
        else:
            press = [0, self.p_0]
            
        msg = Message(press, height, T_t, angles, acc, mag, curr_time)
        
        return msg
            

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
        data_corrente = "oggi"
        ora_corrente = "ora"

        # Creazione e restituzione dell'oggetto
        return Message(
            [pressione, pressione],
            [altezza,altezza],
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
       

