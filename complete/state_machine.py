from machine import Pin, PWM
# Importiamo le funzioni necessarie dalla libreria buzzer
from buzzer import playsong
from utime import sleep
import math
import servo
import bmp280
import urtc
import imu

from message import *

SD_MOUNT_PATH = '/sd'

class StateMachine:
    def __init__(self, buzzer, bmp, rtc, mpu, sd, qmc, aerobrake, parachute, p_0, T_0, h_0, specific_state='start'):
        self.state = specific_state
        self.buzzer = buzzer
        self.bmp = bmp
        self.rtc = rtc
        self.mpu = mpu
        self.sd = sd
        self.qmc = qmc
        self.aerobrake = aerobrake
        self.parachute = parachute
        self.p_0 = p_0
        self.T_0 = T_0
        self.h_0 = h_0
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
        acc = message.get_accelerations()
        print(f'id:{message._id_counter} acc: {acc}')
        ax, ay, az = acc[0],acc[1],acc[2]
        accelerazione_totale = math.sqrt(ax ** 2 + ay ** 2 + az ** 2)
        
        if (message._id_counter == 6):
           accelerazione_totale = 60
            
        if accelerazione_totale > 20 :
            print("accelerazione maggiore 20m/s^2")
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
        acc = message.get_accelerations()
        az = message.get_accelerations()[2]
        
        print(f'id:{message._id_counter} acc:{acc}')
        
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
            playsong(self.buzzer, song)
            self.song_played = True
            self.is_running = True
    
    def get_data(self) -> Message:
        T_t = self.bmp.temperature
        p_t = self.bmp.pressure
        h_t = bmp280.altitude(self.T_0, p_t, self.p_0)
        rtc_info = self.rtc.datetime()
        date = '' + str(rtc_info[1]) + '/' + str(rtc_info[2]) + '/' + str(rtc_info[0])
        time = '' + str(rtc_info[4]) + ':' + str(rtc_info[5]) + ':' + str(rtc_info[6])
        
        angles = [0, 0, 0]
        acc = imu.update_gyro(self.mpu)
        
        mag_xyz = self.qmc.read() # Da modificare con dati raccolti dal sensore qmc.read()
        
        
        if (p_t != self.p_0):
            press = [self.p_0, p_t]
            self.p_0 = p_t
        else:
            press = [0, self.p_0]
            
        if (h_t != self.h_0):
            height = [self.h_0, h_t]
            self.h_0 = h_t
        else:
            height = [0, self.h_0]
            
        msg = Message(press, height, T_t, angles, acc, mag_xyz, time) # DA CAMBIARE HOUR
        
        file_path = SD_MOUNT_PATH + '/data.csv'
        with open(file_path, 'a') as f:
            # f.write(f"{date}, {hour}:{minute}:{second}, {press[1]}, {height[1]}, {T_t}, {acc[0]}, {acc[1]}, {acc[2]}, {mag_xyz[0]}, {mag_xyz[1]}, {mag_xyz[2]}\n")
            f.write(
                f"{date:<15}"
                f"{time:<12}"
                f"{press[1]:<15}"
                f"{height[1]:<15.4f}"
                f"{T_t:<15}"
                f"{acc[0]:<15.4f}"
                f"{acc[1]:<15.4f}"
                f"{acc[2]:<15.4f}"
                f"{mag_xyz[0]:<10}"
                f"{mag_xyz[1]:<10}"
                f"{mag_xyz[2]:<10}\n"
            )
        f.close()
        
        # "Date, Time, Pressure, Altitude, Temperatura, Acc_x, Acc_y, Acc_z, Mag_x, Mag_y, Mag_z\n"
        
        return msg
            

    def acquisisci_sensori_template(self) -> Message:
        """
        Genera un oggetto MessaggioDati con valori di test verosimili.
        """
        # 1. Dati Ambientali
        # pressione = 1013.25  # hPa (Livello del mare)
        pressione = self.bmp.pressure
        altezza = 450.5  # metri
        temperatura = 22.4  # °C

        # Pitch, Roll, Yaw
        angoli_xyz = (1.5, -0.2, 120.0)

        # Accelerazione (m/s²)
        accel_xyz = imu.update_gyro(self.mpu)

        # Magnetometro
        mag_xyz = self.qmc.read()

        # 5. Timestamp
        ora_corrente = "ora"
        
        file_path = SD_MOUNT_PATH + '/data.csv'
        with open(file_path, 'a') as f:
            f.write(f"{pressione}\n")
        f.close()
    
        # Creazione e restituzione dell'oggetto
        return Message(
            [pressione, pressione],
            [altezza, altezza],
            temperatura=temperatura,
            angoli_xyz=angoli_xyz,
            accel_xyz=accel_xyz,
            mag_xyz=mag_xyz,
            ora=ora_corrente
        )
    def run(self):
        #dovrà prendere in input il message
        print("Avvio simulazione...")
        while not self.is_running:
            # message = self.acquisisci_sensori_template() #funzione che ottiene i dati
            message = self.get_data() #funzione che ottiene i dati
            # Recupera la funzione logica per lo stato attuale
            execution_func = self.logic.get(self.state)
            
            if execution_func:
                # Eseguiamo la logica passandogli i dati
                execution_func(message)
            
           
            sleep(1)
            
        print("Simulazione completata.")
       

