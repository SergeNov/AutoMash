import os
import sys
import time
import datetime
import config
import redis
import ads

r = redis.Redis()
log_dir = config.params["log_dir"]
slowdown_degrees = config.params["slowdown_degrees"]

script_name = os.path.basename(sys.argv[0]).replace('.py','')
log_file = log_dir + '/' + script_name + '_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.log'
log_fh = open(log_file, 'w')

last_message = ""

last_cycle_target = 0

def get_status():
  kettle_temp = r.get('kettle_temp')
  mash_temp = r.get('mash_temp')
  heater1 = r.get('heater1')
  heater2 = r.get('heater2')
  heaters_working = r.get('heaters_running')
  pump_k2m = r.get('kettle2mash')
  pump_m2k = r.get('mash2kettle')
  message = "Temperature:\n"
  message += "  Kettle: "+kettle_temp+"\n"
  message += "  Mash: "+mash_temp+"\n"

  message += "Heaters:\n"
  message += "  Heater1: "
  if heater1 == "1":
    message += "On"
  else:
    message += "Off"
  message+="\n"
  message += "  Heater2: "
  if heater2 == "1":
    message += "On"
  else:
    message += "Off"
  message+="\n"
  message += "  Heaters working: "+str(heaters_working)+"\n"

  message += "Pumps:\n"
  message += "  Kettle -> Mash: "
  if pump_k2m == "1":
    message += "On"
  else:
    message += "Off"
  message+="\n"
  message += "  Mash -> Kettle: "
  if pump_m2k == "1":
    message += "On"
  else:
    message += "Off"
  message+="\n"
  return message

def log(message):
  ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  sys.stdout.write("\033[K")
  print(ts+" "+message)
  log_only(message)

def oneliner(message):
  ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  sys.stdout.write("\033[K")
  sys.stdout.write(ts+" "+message+"\r")
  sys.stdout.flush()
  log_only(message)

def log_only(message):
  global last_message
  if message == last_message:
    return
  ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  log_fh.write(ts+" "+message+"\n")
  log_fh.flush()
  last_message = message

def cycle(target_temp):
  global last_cycle_target
  global heat_seconds_per_degree
  log('    Moving wort from mash to kettle')
  r.setex('mash2kettle', mash_to_kettle_seconds, 1)
  time.sleep(mash_to_kettle_seconds)

  mash_temp = float(r.get('mash_temp'))
  heat_seconds = 0
  log('    Mash temp: ' + str(mash_temp) + '; Target temp: '+str(target_temp))

  if last_cycle_target > 0:
    if mash_temp > last_cycle_target: 
      heat_seconds_per_degree -= 10
      log('    Decreasing heat duration to '+str(heat_seconds_per_degree))
    else:
      heat_seconds_per_degree += 10
      log('    Increasing heat duration to '+str(heat_seconds_per_degree))

  if mash_temp < target_temp:
    temp_diff = target_temp - mash_temp
    heat_seconds = temp_diff * heat_seconds_per_degree
    if heat_seconds < min_heat_seconds:
      heat_seconds = min_heat_seconds
    if heat_seconds > max_heat_seconds:
      heat_seconds = max_heat_seconds
  heat_seconds = int(heat_seconds)
  if heat_seconds > 0:
    log('    Heating up for '+str(heat_seconds)+" seconds")
    r.setex('heater1', heat_seconds, 1)
    r.setex('heater2', heat_seconds, 1)
    time.sleep(heat_seconds)

  log('    Moving wort from kettle to mash')
  r.setex('kettle2mash', kettle_to_mash_seconds, 1)
  time.sleep(kettle_to_mash_seconds)

  # set global variables
  last_cycle_target = target_temp
  return heat_seconds

def brew(seconds):
  kettle_temp = float(r.get('kettle_temp'))
  if kettle_temp <= 99:
    r.setex('heater1', seconds, 1)
  if kettle_temp <= 90:
    r.setex('heater2', seconds, 1)
  r.setex('kettle2mash', int(seconds/4), 1)
  time.sleep(seconds)
  log(get_status())
