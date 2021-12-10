#!/usr/bin/env python3.6
import os
import time
import random
import pyvisa
import MySQLdb
import argparse
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser()

parser.add_argument(
    "--table",
    help = "create or edit table in working database",
    type = str,
    default = "test"
)
parser.add_argument(
    "--db",
    help = "working database",
    type = str,
    default = "keysight"
)

args = parser.parse_args()

db_name = args.db
tb_name = args.table

def monitor():
	rm = pyvisa.ResourceManager('/lib64/libiovisa.so')
	# Print what instruments are connected to computer
	print(rm.list_resources())
	
	# Connect to instrument
	power_supply = rm.open_resource('USB0::0x2A8D::0x3302::MY59001082::0::INSTR')
	print(power_supply.query('*IDN?'))
	
	# Print measured voltage and current
	print(power_supply.query('MEAS:VOLT?'))
	print(power_supply.query('MEAS:CURR?'))

	mydb = MySQLdb.connect(host="localhost", user="grafanaWriter", passwd="wimp2021", db=db_name)
	mycursor = mydb.cursor()

	try:
		while True:
			now = datetime.now()
			current_time = now.strftime("%Y-%m-%d %H:%M:%S")	
			#tmp_volt = ( random.random() - 0.5 ) * 100
			tmp_volt = power_supply.query('MEAS:VOLT?')
			cmd = "INSERT INTO "+tb_name+"(time, voltage ) VALUES('%s', %s);"%(current_time, tmp_volt )
			print ( cmd )
			mycursor.execute( cmd )
			mydb.commit()
			time.sleep(1)
		
	except KeyboardInterrupt:
		print ('Interrupting data-taking')
		
	mycursor.execute("select * from %s"%tb_name)
	print(mycursor.fetchall())

def create_table():
	mydb = MySQLdb.connect(host="localhost", user="grafanaWriter", passwd="wimp2021", db=db_name)
	mycursor = mydb.cursor()
	try:
		mycursor.execute("CREATE TABLE %s (id INT PRIMARY KEY AUTO_INCREMENT, time DATETIME, voltage FLOAT);"%tb_name)
	except:
		print ( 'Table %s already exists.'%tb_name )

create_table()
monitor()
