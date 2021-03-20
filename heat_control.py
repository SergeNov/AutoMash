import sys
import json
import time
import datetime
import redis

import lib.config as config
import lib.relay as relay
import lib.ads as ads

r = redis.Redis()
is_heating=False
heat_start = datetime.datetime.now()
try:
  while True:
    time.sleep(0.1)
    try:
      min_temp = float(r.get('kettle_min_temp'))
      max_temp = float(r.get('kettle_max_temp'))
      avg_temp = (min_temp + max_temp) / 2
      temp = float(r.get('kettle_temp'))
    except:
      config.log("Warning: No thermometer data")
      time.sleep(1)
      continue
    message = ""
    if temp >= max_temp:
      relay.disable('heater1')
      is_heating = False
      message += "heater1: off; "
      heat_start = datetime.datetime.now()
    else:
      message += "heater1: on; "
      relay.enable('heater1')
      is_heating = True
    if temp >= avg_temp:
      message += "heater2: off; "
      relay.disable('heater2')
    else:
      message += "heater2: on; "
      relay.enable('heater2')

    if temp >= min_temp and temp <= max_temp:
      r.setex('kettle_good', 60, 1)
      message += "Kettle within range - "+str(temp)+" is between ("+str(min_temp)+" and "+str(max_temp)+")"
    else:
      message += "Kettle outside range - "+str(temp)+" is not between ("+str(min_temp)+" and "+str(max_temp)+")"
      r.setex('kettle_good', 60, 0)
    config.oneliner(message)
    if not is_heating:
      continue

    # Check if kettle might be empty
    if is_heating and datetime.datetime.now() - heat_start > datetime.timedelta(seconds=10): # If heaters are on, and have been on for at least 10 seconds
      amp = ads.measure_current(0)
      if amp < 5:
        r.setex('kettle_empty', 60, 1)
      else:
        r.setex('kettle_empty', 60, 0)
    else:
      r.setex('kettle_empty', 60, 0)
finally:
  print("Disabling heaters")
  relay.disable('heater1')
  relay.disable('heater2')
