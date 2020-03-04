import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c)
#single ended analog input mode
chan1 = AnalogIn(ads, ADS.P0)


def getLight():
	lightVal = 0
	for i in range(100):
		lightVal += chan1.value
	return lightVal/100



print(getLight())