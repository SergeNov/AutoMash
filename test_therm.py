import sys
import json
import datetime
import lib.config as config
import lib.bluetooth as bluetooth
import lib.relay as relay

log_file=open("./therm.log", "w")


config.log("Reading thermometers")
while True:
  thermometers = bluetooth.read_thermometers()
  ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  output = ts+"\t"+str(thermometers['kettle'])
  log_file.write(output+"\n")
  sys.stdout.write(output+"\r")
  sys.stdout.flush()
