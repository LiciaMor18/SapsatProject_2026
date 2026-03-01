
from state_machine import StateMachine
from gyroscope import advanced_calibrate, update_gyro, get_current_yaw
import time
# Testing
def path_test(sm):
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

if __name__ == '__main__':
    
    sm = StateMachine('q0')
    print(sm)
    advanced_calibrate(1000)
    while True:
        update_gyro()
        if get_current_yaw() > 30:
            print("Soglia superata!")
            sm.transition()
            print(sm)
            break

        time.sleep_ms(20)
