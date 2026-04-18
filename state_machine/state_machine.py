from machine import Pin, PWM
# Importiamo le funzioni necessarie dalla libreria buzzer
from buzzer import playsong
from utime import sleep

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

    def _logic_start(self, data):
        if data> 30:

            self.transition()

    def _logic_ascent(self, data):
        self.transition()

    def _logic_apogee(self, data):
        print("Aereofreni attivati!")
        self.transition()
        

    def _logic_descent(self, data): self.transition()
    def _logic_parachute(self, data): self.transition()
    def _logic_landing(self, data): self.transition()

    def _logic_end(self, data):
        # Eseguiamo la canzone solo una volta quando arriviamo alla fine
        if not self.song_played:
            print("Missione completata! Riproduzione segnale acustico...")
            song = ["E5", "G5", "A5", "P", "E5", "G5", "B5", "A5"]
            playsong(self.buzzer, song)
            self.song_played = True
            self.is_running= True

#def lettura dati
    def run(self):
        #dovrà prendere in input il message
        print("Avvio simulazione...")
        while not self.is_running:
            #richiama la funzione di estrazione dati e poi ogni funzione estrae quelli che servono
            current_data = 35 
            
            # Recupera la funzione logica per lo stato attuale
            execution_func = self.logic.get(self.state)
            
            if execution_func:
                # Eseguiamo la logica passandogli i dati
                execution_func(current_data)
            
           
            sleep(1)
            
        print("Simulazione completata.")
       

