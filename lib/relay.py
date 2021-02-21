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
  config.log("Initiating relay")
  GPIO.setwarnings(False)
  for relay_device in relay:
    params = relay[relay_device]
    off = params['off']
    on = params['on']
    pin = params['pin']
    config.log("Initialize pin "+str(pin)+" ("+relay_device+")")
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin, off)

def cleanup():
  GPIO.cleanup()

def activate(relay_device, duration):
  config.log("  Activate "+relay_device)
  params = relay[relay_device]
  off = params['off']
  on = params['on']
  pin = params['pin']
  GPIO.output(pin, on)
  time.sleep(duration)
  config.log("  Disable "+relay_device)
  GPIO.output(pin, off)

init()
