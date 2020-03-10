from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import logging
import time
import json
import argparse
import datetime
import threading

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
lowerBound = 3000
upperBound = 5000

#passcode variables
ps = 0
passcode = [2, 2, 2, 2, 2]
set = [1, 0, 1, 0]
last = 2

#Motor Output

#Motor
motorA=24
motorB=23
motorE=25
GPIO.setup(motorA,GPIO.OUT)
GPIO.setup(motorB,GPIO.OUT)
GPIO.setup(motorE,GPIO.OUT)

#LEDs
red = 17
green = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(red, GPIO.OUT)
GPIO.output(red, GPIO.LOW)
GPIO.setup(green, GPIO.OUT)
GPIO.output(green, GPIO.LOW)

motorOn = 2
greenState = 0

def main(passcode, ps, last, set, red, green, motorOn, greenState):

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
                set, motorOn, greenState = check_action(passcode, motorOn, set, red, green, greenState)
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
                set, motorOn, greenState = check_action(passcode, motorOn, set, red, green, greenState)
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
    #Record time from 0 state, collect time intervals to toggle light

    if motorOn != 2:
        greenLight(green, motorOn, greenState)
        greenState += 1
        #print("GS: ", greenState)
    return passcode, ps, last, set, motorOn, greenState


def reset_password(set, red, greenState, last = 2):
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
        if motorOn != 2:
            greenState = greenLight(green, motorOn, greenState)
    if ((set[0] == 1 and set[1] == 1 and set[2] == 1 and set[3] == 1) or (set[0] == 0 and set[1] == 0 \
                                                         and set[2] == 0 and set[3] == 0)):
        print(*set, "is already a required command, not resetting password")
        return old, greenState
    else:
        print("The new password is: ", *set)
        return set, greenState


def getLight():
    lightVal = 0
    for i in range(100):
        lightVal += lightChannel.value
    return lightVal / 100

def check_action(p, motorOn, set, red, green, greenState):
    print("P: ", p)
    print("Set: ", set)
    if p[0] == set[0] and p[1] == set[1] and p[2] == set[2] and p[3] == set[3]:
        if p[4] == 1:
            motorOn = 1  #Clockwise
            clockwise()
            #blink_green_fast(green)
            print("Motor Clockwise")
            return set, motorOn, greenState
        if p[4] == 0:
            motorOn = 0  #Counterclockwise
            counterClockwise()
            #blink_green_slow(green)
            print("Motor Counterclockwise")
            return set, motorOn, greenState
    elif p[0] == 0 and p[1] == 0 and p[2] == 0 and p[3] == 0 and p[4] == 0:
        #green_off(green)
        motorOn = 2
        motorStop()
        print("Motor Off")
        return set, motorOn, greenState
    elif p[0] == 1 and p[1] == 1 and p[2] == 1 and p[3] == 1 and p[4] == 1:
        set, greenState = reset_password(set, red, greenState)
        return set, motorOn, greenState
    else:
        print("Password not recognized")
        return set, motorOn, greenState

def blink_red_high(red):
    turnOn(red)
    time.sleep(0.1)
    turnOff(red)
    time.sleep(0.1)
    turnOn(red)
    time.sleep(0.1)
    turnOff(red)

def blink_red_low(red):
    turnOn(red)
    time.sleep(0.2)
    turnOff(red)


#def greenLight(e, t, green):
    #while e.isSet():
        #time.sleep(.1)
        #event_set = e.is_set() #####
        #if event_set:


def greenLight(green, motorOn, greenState):
    if motorOn == 0: #Counterclockwise
        if greenState % 4 == 0:
            turnOn(green)
        elif greenState % 2 == 0:
            turnOff(green)
    else: #Clockwise
        if greenState % 2 == 0:
            turnOn(green)
        elif greenState % 1 == 0:
            turnOff(green)
    greenState += 1


def turnOn(pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

def turnOff(pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def clockwise():
    GPIO.output(motorA,GPIO.HIGH)
    GPIO.output(motorB,GPIO.LOW)
    GPIO.output(motorE,GPIO.HIGH)

def counterClockwise():
    GPIO.output(motorA,GPIO.LOW)
    GPIO.output(motorB,GPIO.HIGH)
    GPIO.output(motorE,GPIO.HIGH)

def motorStop():
    GPIO.output(motorE,GPIO.LOW)


print("Current first 4 passcode digits: HLHL")
print("Then use H for clock-wise and L for counter-clockwise")
print("Stop motor with LLLLL")
print("Reset password with HHHHH")
while(True):
    passcode, ps, last, set, motorOn, greenState = main(passcode, ps, last, set, red, green, motorOn, greenState)
