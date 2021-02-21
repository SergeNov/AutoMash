import sys
import lib.config as config
import lib.bluetooth as bluetooth
import lib.relay as relay

config.log("Reading thermometers")
thermometers = bluetooth.read_thermometers()
print thermometers

config.log("Testing relay")
for i in range(2):
  relay.activate("valve", 1)
  relay.activate("pump", 2)
config.log("all ok")
