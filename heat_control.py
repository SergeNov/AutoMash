import sys
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
    ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    h1 = r.get('heater1')
    h2 = r.get('heater2')
    if h1 == '1':
      heater1 = True
    else:
      heater1 = False
    if h2 == '1':
      heater2 = True
    else:
      heater2 = False

    if heater1:
      relay.enable('heater1')
    else:
      relay.disable('heater1')
      r.set('heater1_last_off', ts)
    if heater2:
      relay.enable('heater2')
    else:
      relay.disable('heater2')
      r.set('heater2_last_off', ts)

    time.sleep(0.1)

    amp = ads.measure_current(0)
    heaters_running = 0
    if amp > 10:
      heaters_running = 1
    if amp > 25:
      heaters_running = 2
    r.setex('heaters_running', 60, str(heaters_running))
finally:
  print("Disabling heaters")
  relay.disable('heater1')
  relay.disable('heater2')
