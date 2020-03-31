import RPi.GPIO as GPIO
from time import sleep
import board
import time
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import sys, time

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c)
#single ended analog input mode
chan1 = AnalogIn(ads, ADS.P1)

#Motor
motorA=24
motorB=23
motorE=25
GPIO.setup(motorA,GPIO.OUT)
GPIO.setup(motorB,GPIO.OUT)
GPIO.setup(motorE,GPIO.OUT)

def clockwise():
	GPIO.output(motorA,GPIO.HIGH)
	GPIO.output(motorB,GPIO.LOW)
	GPIO.output(motorE,GPIO.HIGH)

def counterClockwise():
	GPIO.output(motorA,GPIO.LOW)
	GPIO.output(motorB,GPIO.HIGH)
	GPIO.output(motorE,GPIO.HIGH)

def stop():
	GPIO.output(motorE,GPIO.LOW)

def getLight():
	lightVal = 0
	for i in range(100):
		lightVal += chan1.value
	return lightVal/100


def turnOnLED(pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

def turnOffLED(pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

#LEDs
red = 17
green = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(red, GPIO.OUT)
GPIO.output(red, GPIO.LOW)
GPIO.setup(green, GPIO.OUT)
GPIO.output(green, GPIO.LOW)

while True:
    lightVal = getLight()

#    if(lightVal > 6000):
#        clockwise()
#        turnOnLED(green)
#        sleep(0.05)
#        turnOffLED(green)

#    else:
#        counterClockwise()
#        turnOnLED(green)
#        sleep(0.4)
#        turnOffLED(green)

    print(lightVal)

