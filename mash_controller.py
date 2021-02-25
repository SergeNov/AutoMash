import sys
import json
import lib.config as config
import lib.bluetooth as bluetooth
import lib.relay as relay

schedule_path = sys.argv[1]
fh = open(schedule_path, "r")
schedule =  json.loads(fh.read())

def step(step_properties):
  name = step_properties["name"]
  config.log("Step: "+name)
  # 1. Make sure kettle temperature is within range

  # 2. Make sure mash temperature is within range

  # 3. Sleep


config.log("Reading thermometers")
thermometers = bluetooth.read_thermometers()
print thermometers

config.log("Testing relay")
for i in range(3):
  relay.activate_timed("valve", 1)
  relay.activate_timed("pump", 1)
  relay.activate_timed("heater", 1)
config.log("all ok")

config.log("Beginning schedule")
for step_properties in schedule:
  step(step_properties)
