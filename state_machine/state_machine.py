class StateMachine:
    def __init__(self, specific_state='q0'):
        self.state = specific_state
        global current_yaw
        # some values need to be checked everywhere
        # In case we want to initialize the machine in state different from q1

        self.states = {
            "start": self.func1,
            "ascent": self.func2,
            "apogee": self.func3,
            "descent": self.func4,
            "parachute": self.func5,
            "landing": self.func6,
            "end": self.func7
        }

    def transition(self):
        allowed = {
            "start": "ascent",
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

    def check_start(yaw_angle):
        if yaw_angle >30:
            return True
        else:
            return False

    def check_global(self,variable):
        # if the state and the variable are the same, returns true that
        # suggest to change the state
        result = { #placeholders
            "start": 5,
            "ascent": 7,
            "apogee": 8,
            "descent": 9,
            "parachute": 10,
            "landing": 11,
            "end": 12
        }
        if result[self.state] == variable:
            return True
        return False

    def run(self):
        while True:
            current_state = self.state
            match current_state:
                case "start":


            funzione = self.states[self.state]  # get the function attach to the state
            output = funzione()  # execute the function
            mark=self.check(output) # check if the it needs a change in the status
            if mark:
                new_state=self.transition()
                if new_state == None:
                    break

                self.state = new_state
                continue


    def __str__(self):
        # print tha current state, useful for debugging
        return f"Current state: {self.state}"

    def func1(self): return self.state
    def func2(self): return self.state
    def func3(self): return self.state
    def func4(self): return self.state
    def func5(self): return self.state
    def func6(self): return self.state
    def func7(self): return self.state

