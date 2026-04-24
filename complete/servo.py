import machine
import time

AEROBRAKE_ANGLE = 65
PARACHUTE_ANGLE = 70

def interval_mapping(x, in_min, in_max, out_min, out_max):
    """
    Maps a value from one range to another.
    This function is useful for converting servo angle to pulse width.
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def servo_write(pin, angle):
    """
    Moves the servo to a specific angle.
    The angle is converted to a suitable duty cycle for the PWM signal.
    """
    pulse_width = interval_mapping(
        angle, 0, 270, 0.5, 1.5
    )  # Map angle to pulse width in ms
    duty = int(
        interval_mapping(pulse_width, 0, 20, 0, 65535)
    )  # Map pulse width to duty cycle
    pin.duty_u16(duty)  # Set PWM duty cycle

def deploy_aerobrake(servo):
    servo_write(servo, AEROBRAKE_ANGLE)
    
def deploy_parachute(servo):
    servo_write(servo, PARACHUTE_ANGLE)

# Example of use
# servo_write(servo, 270) # Vai direttamente a
# time.sleep(1)           # Aspetta che il motore arrivi fisicamente

