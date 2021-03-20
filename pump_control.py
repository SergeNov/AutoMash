import sys
import json
import time
import datetime
import redis

import lib.config as config
import lib.relay as relay

r = redis.Redis()
try:
  while True:
    time.sleep(0.1)
    k2m = r.get("kettle2mash")
    if k2m == "1":
      k2m = True
    else:
      k2m = False

    m2k = r.get("mash2kettle")
    if m2k == "1":
      m2k = True
    else:
      m2k = False

    if k2m:
      relay.enable("kettle->mash")     
    else:
      relay.disable("kettle->mash")

    if m2k:
      relay.enable("mash->kettle")
    else:
      relay.disable("mash->kettle")

finally:
  relay.disable('kettle->mash')
  relay.disable('mash->kettle')
