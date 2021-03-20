import time
import Adafruit_ADS1x15
adc = Adafruit_ADS1x15.ADS1115()

def read_ads(port):
  value = adc.read_adc(port, gain=1)
  return value

def measure_current(port):
  min_value = 100000
  max_value = 0
  for i in range(50):
    value = read_ads(port)
    if min_value > value:
      min_value = value
    if max_value < value:
      max_value = value
    time.sleep(0.01)
  current = float(max_value - min_value) / 100
  return current
