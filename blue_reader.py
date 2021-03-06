import os
import time
import datetime
import subprocess
import tempfile
import json
import redis

import lib.config as conf
import lib.blue_parser as blue_parser

config = conf.bluetooth
config_index = {}
stats = {}
names = {}
for item in config:
  if "mac" in config[item]:
    config_index[config[item]["mac"]] = item

hcitool_cmd = ["hcitool", "-i", "hci_device", "lescan", "--duplicates"]
hcidump_cmd = ["hcidump", "-i", "hci_device", "--raw", "hci"]

tempf = tempfile.TemporaryFile(mode="w+b")
devnull = open(os.devnull, "wb")

#Opening connections
hcitool = subprocess.Popen(
          hcitool_cmd, stdout=devnull, stderr=devnull
      )
hcidump = subprocess.Popen(
          hcidump_cmd,
          stdout=tempf,
          stderr=devnull
      )
r = redis.Redis()

print config_index

temp_dict = {}

#Infinite loop of scanning bluetooth
try:
  while True:
    c = 0
    time.sleep(1)
    tempf.flush()
    tempf.seek(0)
    data = ""
    for line in tempf:
      try:
        sline = line.decode()
        c += 1
        if sline.startswith(">"):
          data = sline.replace(">", "").replace(" ", "").strip()
        elif sline.startswith("< "):
          data = ""
        else:
          data += sline.replace(" ", "").strip()
        result = blue_parser.parse_raw_message(data)
        if result != None and "mac" in result and result["mac"] in config_index and "temperature" in result:
          result["data"] = data
          device_name = config_index[result["mac"]]
          if device_name not in temp_dict or temp_dict[device_name] != result['temperature']:
            r.set(device_name+"_temp", result['temperature'])
            ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            r.setex(device_name+"_hist_"+ts, 3600, result['temperature'])
            temp_dict[device_name] = result['temperature']
      except:
        pass
    tempf.truncate(0)
finally:
  # Closing connections
  hcidump.kill()
  hcidump.communicate()
  hcitool.kill()
  hcitool.communicate()
