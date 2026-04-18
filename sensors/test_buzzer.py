from machine import Pin, PWM
from buzzer.py import playsong


buzzer = PWM(Pin(15))

song = ["E5","G5","A5","P","E5","G5","B5","A5","P","E5","G5","A5","P","G5","E5"]

playsong(song)