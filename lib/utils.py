import os
import sys
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
