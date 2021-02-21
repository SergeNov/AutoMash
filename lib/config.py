import os
import json
import datetime

home = os.path.expanduser("~")

fh = open(home+"/.mash/relay", "r")
relay = json.loads(fh.read())
for relay_device in relay:
  relay[relay_device]['off'] = not(relay[relay_device]['on'])  

fh = open(home+"/.mash/bluetooth", "r")
bluetooth = json.loads(fh.read())

def log(message):
  ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  print(ts+" "+message)
