class StateMachine:
    def __init__(self, specific_state='q0'):
        self.state = specific_state
        # In case we want to initialize the machine in state different from q1

        self.states = {
            "q0": self.func1,
            "q1": self.func2,
            "q2": self.func3,
            "q3": self.func4,
            "q4": self.func5,
            "q5": self.func6,
            "q6": self.func7
        }

    def transition(self):
        allowed = {
            "q0": "q1",
            "q1": "q2",
            "q2": "q3",
            "q3": "q4",
            "q4": "q5",
            "q5": "q6",
            "q6": "q6"
        }

        new_state = allowed.get(self.state)
        self.state = new_state

        return new_state


    def check(self,variable):
        # if the state and the variable are the same, returns true that
        # suggest to change the state
        result = { #placeholders
            "q0": 5,
            "q1": 7,
            "q2": 8,
            "q3": 9,
            "q4": 10,
            "q5": 11,
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








    def __str__(self):
        return f"Current state: {self.state}"

    def func1(self): return self.state
    def func2(self): return self.state
    def func3(self): return self.state
    def func4(self): return self.state
    def func5(self): return self.state
    def func6(self): return self.state
    def func7(self): return self.state

