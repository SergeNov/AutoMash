import sys
import json
import time
import datetime
import redis
import lib.utils as utils

schedule_path = sys.argv[1]
fh = open(schedule_path, "r")
schedule =  json.loads(fh.read())

r = redis.Redis()

def heaters_ctl(on):
  if on:
    r.setex('heater1', 60, 1)
    r.setex('heater2', 60, 1)
  else:
    r.setex('heater1', 60, 0)
    r.setex('heater2', 60, 0)

def step(step_properties):
  heating = False
  mash_temp_reached = None
  mash_min_temp = step_properties['mash']['min_temp']
  duration = step_properties['duration']
  name = step_properties['name']
  utils.log("  Commencing step: " + name)
  while True:
    mash_min_temp = step_properties['mash']['min_temp']
    # Turn on the heaters if mash temperature is below threshold
    if mash_temp < mash_min_temp:
      heating = True
    else:
      heating = False

    heaters_ctl(heating)

    # Pump Control - make sure warer is being heated and constantly circulated
    heaters_running = r.get('heaters_running')
    if heating:
      #If heating is in progress, mash -> kettle pump must be turned on
      r.setex('mash2kettle', 60, 1)
      if heating and heaters_running == '0':
        #If heaters are on, but are not consuming power, it means kettle is empty
        #Turn off kettle -> mash pump till heaters are working
        r.setex('kettle2mash', 120, 0)
        #sleep a minute since mash2kettle transfer is much slower
        sleep(60)
      else:
        r.setex('kettle2mash', 120, 1)
    else: #If we are here, it means mash has reached desired temperature and heaters have been disabled
      #Turn off mash -> kettle pump; kettle -> mash pump should keep going for a while
      r.setex('mash2kettle', 60, 0)
      if mash_temp_reached == None:
        mash_temp_reached == datetime.datetime.now()
        utils.log("  Step: " + name + " - desired mash temperature reached")
    if mash_temp_reached != None:
      if datetime.datetime.now() >= mash_temp_reached + datetime.timedelta(seconds = duration):
        utils.log(" Step complete: " + step_properties['name'])
        return
    sleep(1)

utils.log("Beginning schedule: " + schedule_path)
for step_properties in schedule:
  utils.log("Commencing: " + step_properties['name'])
