import sys
import json
import time
import datetime
import redis
import lib.config as config

schedule_path = sys.argv[1]
fh = open(schedule_path, "r")
schedule =  json.loads(fh.read())

r = redis.Redis()

def control_mash(temp_range, kettle_range):
  min_temp = float(temp_range['min_temp'])
  max_temp = float(temp_range['max_temp'])
  avg_temp = (min_temp + max_temp) / 2
  temp_mash = float(r.get('mash_temp'))
  temp_kettle = float(r.get('kettle_temp'))
  message = "Kettle temp: "+str(temp_kettle)+"; Mash temp: "+str(temp_mash)+"; "
  kettle_good = r.get('kettle_good')
  if kettle_good!='1':
    message += "Kettle is at wrong temperature - waiting.."
    config.oneliner(message)
    return False
  if temp_mash>=max_temp:
    return False # If temperature above upper limit, nothing to do but wait
  if temp_mash>=min_temp:
    return True # Mash is at the right temperature
  temp_to_go = avg_temp - temp_mash
  temp_delta = temp_kettle - temp_mash
  message += "Kettle is "+str(temp_delta)+"C hotter; "
  message += "Need to warm up Mash by "+str(temp_to_go)+"C; "
  # Now that we know temperature difference, come up with duration to open the pump for
  # this is a really iffy part, since we don't know how much water is in the mash, and
  # how much water is transferred per second
  if temp_delta < 1:
    return False # If the kettle is about the same temperature as mash, pumping water is pointless
  k = 50
  duration = int(k * temp_to_go/temp_delta)
  if duration < 5:
    duration = 5
  if duration > 60:
    duration = 60
  message += "Activating kettle->mash pump for "+str(duration)+" seconds"
  config.log(message)
  r.setex('kettle->mash', duration, "1")
  config.log("Waiting for temperature to stabilize")
  # let's assume that if the temperature doesn't change for a minute, it is good
  while True:
    #make sure to do kettle control
    config.oneliner("temperature fluctuated by "+str(abs(mash_temp_1 - mash_temp_2))+"C")
    #let's assume that if temperature changed by 1C or less, it is stable
    if abs(mash_temp_1 - mash_temp_2) <= 1:
      if mash_temp_2 >= min_temp and mash_temp_2 <= max_temp:
        return True
      else:
        return False

def step(step_properties):
  name = step_properties["name"]
  kettle_min_temp = step_properties["kettle"]["min_temp"]
  kettle_max_temp = step_properties["kettle"]["max_temp"]
  config.log("Step: "+name)
  while True:
    # 1. make sure the kettle controller knows target temperature
    r_kettle_min_temp = r.get('kettle_min_temp')
    r_kettle_max_temp = r.get('kettle_min_temp')
    if r_kettle_min_temp != kettle_min_temp or r_kettle_max_temp != kettle_max_temp:
      r.set('kettle_min_temp', kettle_min_temp)
      r.set('kettle_max_temp', kettle_max_temp)
      r.set('kettle_good', "0")
    else:
      if r.get("kettle_good") != "1": #If kettle is not within target range, do not continue
        time.sleep(1)
        continue
    # 2. Make sure mash temperature is within range
    mash_pass = control_mash(step_properties['mash'], step_properties['kettle'])
    if not mash_pass:
      continue
    # 3. Sleep
    step_start = datetime.datetime.now()
    step_end = step_start+datetime.timedelta(seconds=step_properties["duration"])
    config.log("temperature in range. waiting "+str(step_properties["duration"])+" seconds")
    while datetime.datetime.now() < step_end:
      control_kettle(step_properties['kettle'])
      control_mash(step_properties['mash'], step_properties['kettle'])
    # 4. Flush
    if 'flush' in step_properties and step_properties['flush']:
      flush()
    config.log("Step "+name+" complete")
    return True


config.log("Beginning schedule")
for step_properties in schedule:
  step(step_properties)
