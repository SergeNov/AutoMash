import sys
import json
import time
import datetime
import redis
import lib.utils as utils

mash_target = int(sys.argv[1])
kettle_target = int(sys.argv[2])

r = redis.Redis()

try:
  while True:
    r.setex("mash_target", 10, mash_target)
    r.setex("kettle_target", 10, kettle_target)
    time.sleep(3)
finally:
  r.setex("mash_target", 10, 0)
  r.setex("kettle_target", 10, 0)
