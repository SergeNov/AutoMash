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
    message = ""
    k2m = r.get("kettle2mash")
    if k2m == "1":
      k2m = True
      message += "kettle -> mash: on; "
    else:
      k2m = False
      message += "kettle -> mash: off; "

    m2k = r.get("mash2kettle")
    if m2k == "1":
      m2k = True
      message += "mash -> kettle: on; "
    else:
      m2k = False
      message += "mash -> kettle: off; "

    config.oneliner(message)

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
