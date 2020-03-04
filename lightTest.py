import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import sys, time
import RPi.GPIO as GPIO

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c)
#single ended analog input mode
chan1 = AnalogIn(ads, ADS.P0)


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

def moveForward(motor1, motor2):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(motor1, GPIO.OUT)
    GPIO.output(motor1, GPIO.LOW)
    GPIO.setup(motor2, GPIO.OUT)
    GPIO.output(motor2, GPIO.HIGH)


#LEDs
red = 17
green = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(red, GPIO.OUT)
GPIO.output(red, GPIO.LOW)
GPIO.setup(green, GPIO.OUT)
GPIO.output(green, GPIO.LOW)


#Motor Output
motor1 = 22
motor2 = 5
GPIO.setup(motor1, GPIO.OUT)
GPIO.output(motor1, GPIO.LOW)

GPIO.setup(motor2, GPIO.OUT)
GPIO.output(motor2, GPIO.LOW)


while True:
    lightVal = getLight()
    if(lightVal > 5000):
        turnOnLED(red)
        turnOffLED(green)

    else:
        turnOnLED(green)
        turnOffLED(red)

    GPIO.setup(motor2, GPIO.OUT)
    GPIO.output(motor2, GPIO.HIGH)

    print(lightVal)
