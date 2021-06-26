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

def step(step_properties):
  mash_target = step_properties['mash_temp']
  kettle_target = step_properties['kettle_temp']
  duration = step_properties['duration']
  r.set("mash_target", mash_target)
  r.set("kettle_target", kettle_target)
  name = step_properties['name']
  mash_temp_reached = None
  utils.log("Starting step: " + name)
  while True:
    mash_temp = float(r.get("mash_temp"))
    kettle_temp = float(r.get("kettle_temp"))
    message = "  Mash temp: "+str(mash_temp)+"/"+str(mash_target)+"; Kettle temp: "+str(kettle_temp)+"/"+str(kettle_target)+"; "
    if mash_temp_reached != None:
      current_wait = (datetime.datetime.now() - mash_temp_reached).total_seconds()
      message += "Waiting " + str(int(current_wait)) + "/" + str(int(duration))
      if current_wait >= duration:
        utils.log("  Step: " + name + " completed successfully")
        return
    utils.oneliner(message)
    if mash_temp_reached == None:
      if mash_temp >= mash_target:
        mash_temp_reached = datetime.datetime.now()
        utils.log("  Step: " + name + " - desired mash temperature reached")

    time.sleep(1)

utils.log("Beginning schedule: " + schedule_path)
try:
  for step_properties in schedule:
    step(step_properties)
finally:
  r.setex("mash_target", 10, 0)
  r.setex("kettle_target", 10, 0)
