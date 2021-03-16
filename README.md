# AutoMash
This code controls mashing

Components:
 - blue_reader.py: listens to bluetooth for thermometer readings, writes data into Redis
 - heater_control.py: gets kettle temperature and desired kettle temperature from Redis, turns heaters on/off to achieve it.
 Also checks if the kettle is cooling despite heaters turned on; raises 'kettle_empty' flag if it is the case
 - pump_control.py: very simple script, turns pumps on/off if redis variables are set
 - brewmaster.py: this is where all the logic is implemented

Redis variables:
<device> can be either kettle or mash tun
<device>_temp: latest temperature reading from the device's thermometer
<device>_min_temp: lower temperature threshold for this step
<device>_max_temp: higher temperature threshold for this step
<device>_hist_YYYYMMDDHH24MISS: every time temperature reading changes, this variable is added. Autoexpire in an hour
<device>_good: temperature inside the device meets this step's requirements. "1" if true
kettle_empty: kettle is empty. "1" if true
kettle2mash: if set to 1, pump_control.py will activate kettle->mash pump
mash2kettle: if set to 1, pump_control.py will activate mash->kettle pump
