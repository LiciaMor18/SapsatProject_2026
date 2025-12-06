# 🚀 Sapsat 2026 - Sapienza Space Team

## Introduction

The SapSat project is a design-build-fly competition that provides teams with an opportunity to
experience the design life-cycle of an aerospace system. It is designed to reflect a typical
aerospace program on a small scale and includes all its aspects, from the preliminary design
review to post flight review.
The mission and its requirements are designed to reflect various aspects of real world missions
including telemetry, communications, and autonomous operations. Each team will be scored
on real-world deliverables such as schedules, design review presentations, and demonstration
flights.

## Mission Overview

Design a SapSat that consists of payload for a rocket. The payload shall deploy from the rocket
when the rocket reaches peak altitude and the rocket motor ejection forces a separation.
The payload shall descend at a rate of no more than 20 meters/second deploying an heatshield
that deploys at separations (automatically or forced).
At 200 meters the payload release a parachute and the descend rate shall be 5 meters/second.
The SapSat shall collect sensor data during ascent and descent in an SD card and transit
telemetry to the ground station.
The sensor data shall include interior temperature, battery voltage, altitude, acceleration, rate,
angular rate, magnetic field.
Bonus tasks:
The SapSat shall collect sensor data during ascent and descent in an external memory (no
SD).
A video camera shall show the descend of the payload.

## Environmental Tests

1. Drop test:
    This test is designed to verify that the parachute and attachment point will
    survive the deployment. Component mounts and battery mount will also be tested. The
    drop test generates about 30 Gs of shock to the system.

2. Fit test:
    This test is designed to verify deployment operation of the payload and to check the
    correct analysis of tolerances. The rocket airframe will be provided for the test. The payload
    must be designed to fit into the rocket for the ascent phase and must be capable of detaching
    from the rocket without any friction or protruding parts that could obstruct its exit from it.

## Score Evaluation

The work will be evaluated by judges using a score associated with various aspects of the mission,
such as:
+ PDR
+ Presentations
+ Environmental tests
+ Launch
+ Post flight review
+ Nice name
+ Bonus

## Requirements

+ Total mass of the SatSap shall be maximum 400grams

+ SapSat shall fit in a cylindrical envelope of 90 mm diameter x 300 mm
length. Tolerances are to be included to facilitate container deployment
from the rocket fairing.

+ The payload shall not have any sharp edges to cause it to get stuck in
the rocket payload section which is made of cardboard.

+ The probe shall be solid and fully enclose the science probes. Small
holes to allow access to turn on the science probes are allowed. The
end of the probe where the probe deploys may be open.

+ The rocket airframe shall not be used to restrain any deployable parts
of the SapSat.

+ The rocket airframe shall not be used as part of the SapSat
operations.

+ 0 altitude reference shall be at the launch pad.

+ All structures shall be built to survive 15 Gs of launch acceleration

+ All structures shall be built to survive 30 Gs of shock

+ All electronics and mechanical components shall be hard mounted
using proper mounts such as standoffs, screws, or high performance
adhesives

+ All mechanisms shall be capable of maintaining their configuration or
states under all forces.

+ Mechanisms shall not use pyrotechnics or chemicals.

+ Mechanisms that use heat (e.g., nichrome wire) shall not be exposed to
the outside environment to reduce potential risk of setting vegetation on
fire.

+ The probe shall be labeled with team contact information including
email address.

+ Cost of the SapSat shall be low. Ground support and analysis tools are
not included in the cost. Equipment from previous years shall be
included in this cost, based on current market value.


+ The probe shall include an easily accessible power switch that can be
accessed without disassembling the cansat and science probes and in
the stowed configuration.

+ The shall include a power indicator such as an LED or sound
generating device that can be easily seen or heard without
disassembling the cansat and in the stowed state.

+ An audio beacon is required for the probe. It shall be powered after
landing.

+ An easily accessible battery compartment shall be included allowing
batteries to be installed or removed in less than a minute and not
require a total disassembly of the SapSat.

+ If spring contacts are used for making electrical connections to
batteries, make sure they do not disconnect.
Shock forces can cause momentary disconnects.

+ The SapSat shall operate during the environmental tests .

+ The SapSat shall operate for a minimum of one hour when integrated
into the rocket.

+ The probe shall release after the apogee.

+ The probe shall deploy a heat shield after leaving the rocket.

+ The heat shield shall be used as an aerobrake and limit the descent
rate to 20 m/s or less.

+ At 200 meters, the probe shall release a parachute to reduce the
descent rate to 5 m/s +/- 1m/sec

+ The probe telemetry shall include altitude, internal temperature, battery
voltage, rate, angular rate, acceleration, magnetic field.

+ The SatSap shall have a funny name, inspired by an animal. (exp:
ParaonoidSalamander, MeticolousFerret, TiburonBorracho) the coiche
of the name and language shall be explained in detail to the jury

## Sensors 

- [ ] HMC5883L – Magnetometer

    - Measures Earth’s magnetic field and heading.

    - Used for orientation and detecting attitude changes.

    - States: q0, q1, q2, q3, q4, q5

    - Needs calibration in q0
      
- [ ] MPU6050 – Accelerometer + Gyroscope

    - Measures acceleration and angular velocity.

    - Essential for detecting liftoff, apogee, free-fall, and descent stabilization.

    - States: q0, q1, q2, q3, q4, q5

    - Needs calibration in q0
     
- [x] BME280 – Pressure / Temperature
    
    - Measures pressure for altitude computation.

    - Detects liftoff, apogee, and 200m deployment point.

    - States: q0, q1, q2, q3, q4, q5
      
- [x] Servo 1 – Airbrake Deployment
    
    - Deployed at apogee (55–70°).

    - State: q2
      
- [x] Servo 2 – Container / Parachute Deployment
    
    - Activated around 200 m altitude (45–90°).

    - State: q4
     
- [ ] Buzzer
    
    - Acoustic feedback at startup and state transitions.

    - States: q0 → q6 (optional)

- [ ] IRM-H6xxT – IR Receiver

    - Allows remote activation (low priority).

    - State: q0

## ⚙️ Non-Programmable Components

- SW_SPDT_321 – Emergency Switch: Turns SapSAT ON/OFF (not programmable)

- LM2936 3.3V – Voltage Regulator: Provides stable 3.3V supply (not programmable)

- BC107 – BJT Transistor: Used in electrical circuitry (not programmable)

- Neopixel THT LED Strip (optional): Visual feedback (optional)

- Raspberry Pi Pico: Main microcontroller running state machine q0–q6
