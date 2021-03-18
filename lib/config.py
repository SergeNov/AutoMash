import os
import sys
import json
import datetime

home = os.path.expanduser("~")

fh = open(home+"/.mash/relay", "r")
relay = json.loads(fh.read())
for relay_device in relay:
  relay[relay_device]['off'] = not(relay[relay_device]['on'])  
fh.close()

fh = open(home+"/.mash/bluetooth", "r")
bluetooth = json.loads(fh.read())
fh.close()

fh = open(home+"/.mash/params", "r")
params = json.loads(fh.read())
fh.close()

log_dir = params["log_dir"]

script_name = os.path.basename(sys.argv[0]).replace('.py','')
log_file = log_dir + '/' + script_name + '_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.log'
log_fh = open(log_file, 'w')

last_message = ""

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
