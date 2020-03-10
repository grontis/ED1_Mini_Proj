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


#Light sensor bounds
lowerBound = 4000
upperBound = 5000

#passcode variables
ps = 0
passcode = [2, 2, 2, 2, 2]
set = [1, 0, 1, 0]
last = 2

#Motor Output
motor1 = 22
motor2 = 5
GPIO.setup(motor1, GPIO.OUT)
GPIO.output(motor1, GPIO.LOW)

GPIO.setup(motor2, GPIO.OUT)
GPIO.output(motor2, GPIO.LOW)

#LEDs
red = 17
green = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(red, GPIO.OUT)
GPIO.output(red, GPIO.LOW)
GPIO.setup(green, GPIO.OUT)
GPIO.output(green, GPIO.LOW)

motorOn = 2

def main(passcode, ps, last, set, red, green, motorOn):

    #Read light

    lightReading = getLight()

    #Check light reading

    #High: less shade, value 1
    #Low: max shade, value 0

    #No shade
    if lightReading < lowerBound:
        if last == 1: #Light hand wave
            passcode[ps] = 1
            print("1: Far motion")
            blink_red_high(red)
            ps = ps + 1
            if ps == 5:
                ps = 0
                print("Passcode is: ", *passcode)
                set, motorOn = check_action(passcode, motorOn, set, red, green)
                passcode = [2, 2, 2, 2, 2]
        elif last == 0: #Dark hand wave
            passcode[ps] = 0
            print("0: Close motion")
            blink_red_low(red)
            ps = ps + 1
            if ps == 5:
                ps = 0
                print("Passcode is: ", *passcode)
                #print(*passcode)
                set = check_action(passcode, motorOn, set, red, green)
                passcode = [2, 2, 2, 2, 2]
        last = 2

    #A little shade
    elif lightReading <= upperBound and lowerBound <= lightReading:
        if last == 2:
            last = 1

    #Max shade
    elif lightReading > upperBound:
        last = 0

    #Checking motor state
    #if motorOn == 0:

    #elif motorOn == 1:

    return passcode, ps, last, set


def reset_password(set, red, last = 2):
    print("Reset your password:")
    n = 0
    old = [0, 0, 0, 0]
    old[0] = set[0]
    old[1] = set[1]
    old[2] = set[2]
    old[3] = set[3]

    # Check light reading
    while n < 4:
        lightReading = getLight()
        # No shade
        if lightReading < lowerBound:
                if last == 1:  # Light hand wave
                    set[n] = 1
                    print("1: Far motion")
                    blink_red_high(red)
                    n += 1
                elif last == 0:  # Dark hand wave
                    set[n] = 0
                    print("0: Close motion")
                    blink_red_low(red)
                    n += 1
                last = 2
        # A little shade
        elif lightReading <= upperBound and lowerBound <= lightReading:
            if last == 2:
                last = 1
        # Max shade
        elif lightReading > upperBound:
            last = 0
    if ((set[0] == 1 and set[1] == 1 and set[2] == 1 and set[3] == 1) or (set[0] == 0 and set[1] == 0 \
                                                         and set[2] == 0 and set[3] == 0)):
        print(*set, "is already a required command, not resetting password")
        return old
    else:
        print("The new password is: ", *set)
        return set




def getLight():
    lightVal = 0
    for i in range(100):
        lightVal += lightChannel.value
    return lightVal / 100

def check_action(p, motorOn, set, red, green):
    print("P: ", p)
    print("Set: ", set)
    if p[0] == set[0] and p[1] == set[1] and p[2] == set[2] and p[3] == set[3]:
        if p[4] == 1:
            motorOn = 1  #Clockwise
            #blink_green_fast(green)
            print("Motor Clockwise")
            return set, motorOn
        if p[4] == 0:
            motorOn = 0  #Counterclockwise
            #blink_green_slow(green)
            print("Motor Counterclockwise")
            return set, motorOn
    elif p[0] == 0 and p[1] == 0 and p[2] == 0 and p[3] == 0 and p[4] == 0:
        #green_off(green)
        motorOn = 2
        print("Motor Off")
        return set, motorOn
    elif p[0] == 1 and p[1] == 1 and p[2] == 1 and p[3] == 1 and p[4] == 1:
        set = reset_password(set, red)
        return set, motorOn
    else:
        print("Password not recognized")
        return set, motorOn

def blink_red_high(red):
    turnOn(red)
    time.sleep(0.03)
    turnOff(red)
    time.sleep(0.03)
    turnOn(red)
    time.sleep(0.03)
    turnOff(red)

def blink_red_low(red):
    turnOn(red)
    time.sleep(0.1)
    turnOff(red)

def blink_green_fast(green):
    turnOn(green)
    time.sleep(0.03)
    turnOff(green)
    time.sleep(0.03)

def blink_green_slow(green):
    turnOn(green)
    time.sleep(0.1)
    turnOff(green)
    time.sleep(0.1)

def green_off(green):
    turnOff(green)


#Pin commands

def turnOn(pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

def turnOff(pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

#Motor command

def moveForward(motor1, motor2):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(motor1, GPIO.OUT)
    GPIO.output(motor1, GPIO.LOW)
    GPIO.setup(motor2, GPIO.OUT)
    GPIO.output(motor2, GPIO.HIGH)


print("Current first 4 passcode digits: HLHL")
print("Then use H for clock-wise and L for counter-clockwise")
print("Stop motor with LLLLL")
print("Reset password with HHHHH")
while(True):
    passcode, ps, last, set = main(passcode, ps, last, set, red, green, motorOn)
