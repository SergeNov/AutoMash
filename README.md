# AutoMash
This code controls mashing

Components:
 - blue_reader.py: listens to bluetooth for thermometer readings, writes data into Redis
 - heater_control.py: gets kettle temperature and desired kettle temperature from Redis, turns heaters on/off to achieve it.
 Also checks if the kettle is cooling despite heaters turned on; raises 'kettle_empty' flag if it is the case
 - pump_control.py: very simple script, turns pumps on/off if redis variables are set
 - brewmaster.py: this is where all the logic is implemented
