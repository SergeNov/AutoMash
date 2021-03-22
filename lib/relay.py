# import GPIO and time
import RPi.GPIO as GPIO
import config
import time

# set GPIO numbering mode and define output pins

GPIO.setmode(GPIO.BCM)

relay=config.relay
for relay_device in relay:
  relay[relay_device]['off'] = not(relay[relay_device]['on'])

def init():
  GPIO.setwarnings(False)
  for relay_device in relay:
    params = relay[relay_device]
    off = params['off']
    on = params['on']
    pin = params['pin']
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin, off)

def cleanup():
  GPIO.cleanup()

def activate(relay_device, duration):
  # activate device for N seconds. mainly for pumps
  params = relay[relay_device]
  off = params['off']
  on = params['on']
  pin = params['pin']
  GPIO.output(pin, on)
  time.sleep(duration)
  GPIO.output(pin, off)

def enable(relay_device):
  params = relay[relay_device]
  off = params['off']
  on = params['on']
  pin = params['pin']
  GPIO.output(pin, on)

def disable(relay_device):
  params = relay[relay_device]
  off = params['off']
  on = params['on']
  pin = params['pin']
  GPIO.output(pin, off)

init()
