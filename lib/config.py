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
