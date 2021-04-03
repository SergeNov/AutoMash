import os
import sys
import time
import datetime
import config
import redis
import ads

r = redis.Redis()
log_dir = config.params["log_dir"]

script_name = os.path.basename(sys.argv[0]).replace('.py','')
log_file = log_dir + '/' + script_name + '_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.log'
log_fh = open(log_file, 'w')

last_message = ""

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
  print(ts+" "+message)
  log_only(message)

def oneliner(message):
  ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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

def cycle(heat_seconds):
  log('Beginning cycle')
  log('Heating up for '+str(heat_seconds)+" seconds")
  r.setex('heater1', heat_seconds, 1)
  r.setex('heater2', heat_seconds, 1)
  time.sleep(heat_seconds)
  log(get_status())
  log('Moving wort from kettle to mash')
  r.setex('kettle2mash', 300, 1)
  time.sleep(300)
  log(get_status())
  log('Moving wort from mash to kettle')
  r.setex('mash2kettle', 900, 1)
  time.sleep(900)
  log(get_status())
  log('Cycle complete')

def brew(seconds):
  kettle_temp = float(r.get('kettle_temp'))
  if kettle_temp <= 99:
    r.setex('heater1', seconds, 1)
  if kettle_temp <= 5:
    r.setex('heater2', seconds, 1)
  r.setex('kettle2mash', int(seconds/4), 1)
  time.sleep(seconds)
  log(get_status())
