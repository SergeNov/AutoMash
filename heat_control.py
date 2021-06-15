import sys
import json
import time
import datetime
import redis
import lib.utils as utils

r = redis.Redis()
slowdown_degrees = utils.slowdown_degrees
mash2kettle_min_temp = utils.mash2kettle_min_temp
mash2kettle_max_temp = utils.mash2kettle_max_temp
kettle2mash_min_temp = utils.kettle2mash_min_temp
kettle2mash_max_temp = utils.kettle2mash_max_temp

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

  if mash_temp < mash_target and kettle_temp < kettle_target:
    r.setex('heater1', 10, 1)
    if kettle_temp <= kettle_target - slowdown_degrees and mash_temp <= mash_target - slowdown_degrees:
      r.setex('heater2', 10, 1)
    #Turn on pumps depending on temperature range
    if kettle_temp >= mash2kettle_min_temp and kettle_temp <= mash2kettle_max_temp:
      r.setex('mash2kettle', 10, 1)
    else:
      r.setex('mash2kettle', 10, 0)

    if kettle_temp >= kettle2mash_min_temp and kettle_temp <= kettle2mash_max_temp:
      r.setex('kettle2mash', 10, 1)
    else:
      r.setex('kettle2mash', 10, 0)
  else:
    #Turn off both heaters
    r.setex('heater1', 10, 0)
    r.setex('heater2', 10, 0)
    #Turn on both pumps - to cool faster, and in case one of the pumps is unprimed
    r.setex('kettle2mash', 10, 1)
    r.setex('mash2kettle', 10, 1)
    
  time.sleep(1)
