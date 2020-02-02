import time
import psycopg2
import numpy
import socket as s

def mod_data(data_str):
	"""
	#*Formats raw output from sensor to useable format for processing
	"""

	data_float = [float(_i.replace('[^0-9a-zA-Z]+', '').replace('}', '')) for _i in data_str.split(',')[1:]]
	return data_float

def data_cleaner(data):
	"""
	#*Uses prepared data from mod_data to configure output for clean format
	#to be inserted into PostgreSQL DB
	"""
	
	time0=data.pop(0)
	time_pack=numpy.ones(25)*0.01
	time_pack[0]=time0
	time_pack=numpy.cumsum(time_pack)
	return '%s' % str(tuple(zip(time_pack, data)))[1:-1]

aws_tt_db = psycopg2.connect(host="HOST!!!", 
			     port="PORT!!!", 
		 	     dbname="train_track_aws", 
			     user="postgres", 
			     password="FOO!!!")
db_runner = aws_tt_db.cursor()

port = 8888
hostipF = "/opt/settings/sys/ip.txt"
file = open(hostipF, 'r')
host = file.read().strip()
file.close()

HP = host + ":" + str(port)

sock = s.socket(s.AF_INET, s.SOCK_DGRAM | s.SO_REUSEADDR)
sock.bind((host, port))

while True:
	data, addr = sock.recvfrom(1024)
	db_input=data_cleaner(data=mod_data(data_str=data))
	psql_run='INSERT INTO public.ts2(time, seis) VALUES%s;'
	db_runner.execute(psql_run % db_input)
	aws_tt_db.commit()
