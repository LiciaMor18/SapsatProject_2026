import time

class StateMachine:
    def __init__(self, bmp, mode, specific_state='initialize'):
        self.bmp = bmp
        self.mode = mode
        self.state = specific_state  # In case we want to initialize the machine in state different from initialize

        self.states = {
            "initialize": self.init_func,
            "ascent": self.ascent_func,
            "apogee": self.apogee_func,
            "descent": self.descent_func,
            "parachute": self.parachute_func,
            "landing": self.landing_func,
            "end": self.end_func
        }

    def transition(self):
        allowed = {
            "initialize": "ascent",
            "ascent": "apogee",
            "apogee": "descent",
            "descent": "parachute",
            "parachute": "landing",
            "landing": "end",
            "end": "end"
        }

        new_state = allowed.get(self.state)
        self.state = new_state

        return new_state


    def check(self,variable):
        # if the state and the variable are the same, returns true that
        # suggest to change the state
        result = { #placeholders
            "initialize": 5,
            "ascent": 7,
            "apogee": 8,
            "descent": 9,
            "parachute": 10,
            "landing": 11,
        }
        if result[self.state] == variable:
            return True
        return False

    def esegui(self):
        while True:
            funzione = self.states[self.state]  # get the function attach to the state
            output = funzione()  # execute the function
            mark=self.check(output) # check if the it needs a change in the status
            if mark:
                new_state=self.transition()
                if new_state == None:
                    break

                self.state = new_state
                continue
            time.sleep_ms(1000)

    def print_data(self):
        if self.mode == 0:
            print(f'p = {self.bmp.pressure}')
        else:
            print('p = 0')

    def __str__(self):
        return f"[{self.state}]:"

    def init_func(self):
        self.print_data()
        return self.state
    
    def ascent_func(self):
        return self.state
    
    def apogee_func(self):
        return self.state
    
    def descent_func(self):
        return self.state
    
    def parachute_func(self):
        return self.state
    
    def landing_func(self):
        return self.state
    
    def end_func(self):
        return self.state

