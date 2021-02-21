import os
import time
import datetime
import subprocess
import tempfile
import json

import config as c
import blue_parser

config = c.bluetooth
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

def read_thermometers():

  #Opening connections
  hcitool = subprocess.Popen(
            hcitool_cmd, stdout=devnull, stderr=devnull
        )
  hcidump = subprocess.Popen(
            hcidump_cmd,
            stdout=tempf,
            stderr=devnull
        )

  #Collecting data
  for i in range(20):
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
          for k, v in config[device_name].items():
            result[k] = v 
          stats[device_name] = result
      except:
        pass
    if len(stats) == len(config_index):
      break
    tempf.truncate(0)

  #Closing connections
  hcidump.kill()
  hcidump.communicate()
  hcitool.kill()
  hcitool.communicate()

  #We only need temperature for each thermometer, so no need to return all stats
  result = {}
  for device in stats:
    result[device] = stats[device]["temperature"]

  return result
