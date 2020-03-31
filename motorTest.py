import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

motorA = 16
motorB = 20
motorE = 21

GPIO.setup(motorA,GPIO.OUT)
GPIO.setup(motorB,GPIO.OUT)
GPIO.setup(motorE,GPIO.OUT)

GPIO.output(motorA,GPIO.HIGH)
GPIO.output(motorB,GPIO.LOW)
GPIO.output(motorE,GPIO.HIGH)

sleep(2)

GPIO.output(motorE,GPIO.LOW)

GPIO.cleanup()
