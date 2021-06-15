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
mash2kettle_min_temp = config.params["mash2kettle_min_temp"]
mash2kettle_max_temp = config.params["mash2kettle_max_temp"]
kettle2mash_min_temp = config.params["kettle2mash_min_temp"]
kettle2mash_max_temp = config.params["kettle2mash_max_temp"]

script_name = os.path.basename(sys.argv[0]).replace('.py','')
log_file = log_dir + '/' + script_name + '_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.log'
log_fh = open(log_file, 'w')

last_message = ""

last_cycle_target = 0

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
