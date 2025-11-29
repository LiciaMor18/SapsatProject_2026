from state_machine import StateMachine

# Testing
if __name__ == '__main__':
    sm = StateMachine()
    
    print(sm)  # Current state: q0
    sm.transition()
    print(sm)  # Current state: q1
    sm.transition()
    print(sm)  # Current state: q2
    sm.transition()
    print(sm)  # Current state: q3
    sm.transition()
    print(sm)  # Current state: q4
    sm.transition()
    print(sm)  # Current state: q5
    sm.transition()
    print(sm)  # Current state: q6
    sm.transition()
    
    sm2 = StateMachine('q4')
    print(sm2) # Current state: q4
