from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import logging
import time
import json
import argparse
import datetime

import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import sys, time
import RPi.GPIO as GPIO

GPIO.cleanup()

#CONFIGURE ADS CONVERTER WITH RASPBERRY PI
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c)
#single ended analog input mode
lightChannel = AnalogIn(ads, ADS.P0)


#closeLowerBound = 20000.0
#farLowerBound = 10000.0
#farUpperBound = 16000.0

#Light sensor bounds
lowerBound = 5000
upperBound = 7000

#passcode variables
ps = 0
passcode = [2, 2, 2, 2, 2]

#Initialize RGB LEDs to off at start
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, GPIO.LOW)
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, GPIO.LOW)
GPIO.setup(22, GPIO.OUT)
GPIO.output(22, GPIO.LOW)

def main(passcode, ps):

    #led2 = LEDController(17, 27, 22)

    #Read light

    lightReading = getLight()

    #Check light reading

    #No shade
    if lightReading < lowerBound:
        print("None: No motion " + str(lightReading))
        time.sleep(0.05)
    #A little shade
    elif lightReading <= upperBound and lowerBound <= lightReading:
        print("1: Far motion " + str(lightReading))
        if passcode[0] == 2:
            passcode[ps] = 1
            ps = ps + 1
        elif passcode[ps] == 0:
            print("spot 1")
            ps = ps + 1
            passcode[ps] = 1
            if ps == 4:
                print("spot 3")
                ps = 0
                print("Passcode is: " + passcode)
                print("Passcode is now being reset.")
                passcode = [2, 2, 2, 2, 2]
        time.sleep(0.05)
    #Max shade
    elif lightReading > upperBound:
        print("0: Close motion " + str(lightReading))
        if passcode[0] == 2:
            passcode[ps] = 0
            ps = ps + 1
        elif passcode[ps] == 1:
            print("spot 2")
            ps = ps + 1
            passcode[ps] = 0
            if ps == 4:
                print("spot 4")
                ps = 0
                print("Passcode is: ")
                print(*passcode)
                print("Passcode is now being reset.")
                passcode = [2, 2, 2, 2, 2]
        time.sleep(0.05)

        #if motionInput == passcode[passcodeSequence] and motionInput != '' and passcodeEntered == False:
        #    if len(passcode) - 1 == passcodeSequence:
        #        passcodeEntered = True
        #        passcodeSequence = 0
        #    else:
        #        passcodeSequence += 1
        #    led2.greenOn()
        #    time.sleep(0.2)
        #    led2.greenOff()
        #elif motionInput != passcode[passcodeSequence] and motionInput != '' and passcodeEntered == False:
        #    print("Mistake in passcode sequence")
        #    passcodeSequence = 0
        #    led2.redOn()
        #    time.sleep(1)
        #    led2.redOff()

        #if passcodeEntered:
        #    led2.greenOn()
        #    print("Password entered correctly.")
        #time.sleep(0.2)

    #if passcodeEntered:
    #    tempReading = getTemp()

        #led1 = LEDController(17, 27, 22)
        #if tempReading< threshold - 8:
        #    led1.allOff()
        #    led1.magentaOn()
        #elif threshold-8 < tempReading < threshold-4:
        #    led1.allOff()
        #    led1.blueOn()
        #elif threshold-4 < tempReading < threshold-2:
        #    led1.allOff()
        #    led1.cyanOn()
        #elif threshold-2 < tempReading < threshold + 2:
        #    led1.allOff()
        #    led1.greenOn()
        #elif threshold+2 < tempReading < threshold+4:
        #    led1.allOff()
        #    led1.yellowOn()
        #elif threshold+4 < tempReading:
        #    led1.allOff()
        #    led1.redOn()

        #print(tempReading)
        #currentTime = datetime.datetime.now()
        #currentTime = currentTime.strftime("%m/%d/%Y, %H:%M:%S")
        #print(currentTime)
        #payload = {"state": {"reported": {"temp": str(tempReading),"time": currentTime}}}
        #deviceShadowHandler.shadowUpdate(json.dumps(payload), customShadowCallback_Update, 5)


    time.sleep(1.5)
    print("Current Passcode:")
    print(*passcode)
    print("Current ps Index: " + ps)
    return passcode, ps

def getTemp():
    tempF = 0
    for i in range(20):
        #get celsius reading from sensor
        temp = (tempChannel.voltage - .5) /.01
        #then convert to F
        tempF += temp * (1.8) + 32
    #average 5 readings
    tempF = tempF / 20
    tempF = tempF - 4
    return tempF

def getLight():
    lightValue = 0
    for i in range(5):
        lightValue += lightChannel.value
    return lightValue/5

class LEDController:
    def __init__(self, redpin, greenpin, bluepin):
        self.redPin = redpin
        self.greenPin = greenpin
        self.bluePin = bluepin

    def blink(self, pin):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)

    def turnOff(self, pin):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

while(True):
    passcode, ps = main(passcode, ps)
