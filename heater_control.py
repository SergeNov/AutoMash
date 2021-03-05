import sys
import json
import time
import datetime
import redis

import lib.config as config
import lib.relay as relay

r = redis.Redis()
is_heating=False
try:
  while True:
    if not is_heating:
      for key in r.scan_iter("kettle_history_*"):
        r.delete(key)
    try:
      min_temp = float(r.get('kettle_min_temp'))
      max_temp = float(r.get('kettle_max_temp'))
      avg_temp = (min_temp + max_temp) / 2
      temp = float(r.get('kettle_temp'))
    except:
      config.log("Warning: No thermometer data")
      time.sleep(1)
      continue
    if temp >= max_temp:
      relay.disable('heater1')
      is_heating = False
    else:
      relay.enable('heater1')
      is_heating = True
    if temp >= avg_temp:
      relay.disable('heater2')
    else:
      relay.enable('heater2')

    if temp >= min_temp and temp <= max_temp:
      r.setex('kettle_good', 60, 1)
    else:
      r.setex('kettle_good', 60, 0)

    if not is_heating:
      continue

    # Check if kettle might be empty
    keys = r.keys("kettle_hist_*")
    keys.sort()
    try:
      old_temp = float(r.get(keys[1]))
      if old_temp>temp:
        #looks like the kettle is cooling
        r.setex('kettle_empty', 60, 1)
      else:
        r.setex('kettle_empty', 60, 0)
    except:
        config.log("Warning: No thermometer history")
        time.sleep(1)
        continue
finally:
  relay.disable('heater1')
  relay.disable('heater2')
