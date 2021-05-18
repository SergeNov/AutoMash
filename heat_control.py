import sys
import json
import time
import datetime
import redis
import lib.utils as utils

r = redis.Redis()
slowdown_degrees = utils.slowdown_degrees

while True:
  try:
    mash_temp = float(r.get('mash_temp'))
    kettle_temp = float(r.get('kettle_temp'))
    mash_target = float(r.get('mash_target'))
    kettle_target = float(r.get('kettle_target'))
  except:
    continue
  if mash_temp == None or kettle_temp == None or mash_target == None or kettle_target == None:
    continue
  r.setex('kettle2mash', 10, 1)
  r.setex('mash2kettle', 10, 1)
  time.sleep(1)

  if mash_temp >= mash_target:
    r.setex('heater1', 10, 0)
    r.setex('heater2', 10, 0)
    continue
  if kettle_temp >= kettle_target:
    r.setex('heater1', 10, 0)
    r.setex('heater2', 10, 0)
    continue
  
  r.setex('heater1', 10, 1)
  if kettle_temp <= kettle_target - slowdown_degrees:
    r.setex('heater2', 10, 1)
