import socket
import configparser
import argparse
import time
import minimalmodbus
import serial
import time

import numpy as np

class s2000Modbus():
	def __init__(self, config):


		COMPORT = config['SERIAL_COM_PORT']

		SERIAL_BAUDRATE = int(config['SERIAL_BAUDRATE'])

		SLAVEADDRESS = int(config['SLAVEADDRESS'])


			

		if int(config['SERIAL_BYTESIZE']) == 8:
			bytesize = int(8)
			
		elif int(config['SERIAL_BYTESIZE']) == 7:
			bytesize = int(7)

		if int(config['SERIAL_STOPBITS']) == 1:
			stopbits = 1
		elif int(config['SERIAL_STOPBITS']) == 2:
			stopbits = 2
		
		if int(config['NDECIMALS']) == 2:
			nDecimals =2
		elif int(config['NDECIMALS']) == 1:
			nDecimals =1

		if config['SERIAL_PARITY'] == 'NONE':
			parity = serial.PARITY_NONE
		elif config['SERIAL_PARITY'] == 'ODD':
			parity = serial.PARITY_ODD
		elif config['SERIAL_PARITY'] == 'EVEN':
			parity = serial.PARITY_EVEN
		elif config['SERIAL_PARITY'] == 'MARK':
			parity = serial.PARITY_MARK
		
		if config['MODE'] == 'RTU':
			mode = minimalmodbus.MODE_RTU

		self.instrument = minimalmodbus.Instrument(port = COMPORT,slaveaddress = SLAVEADDRESS)
		
		self.instrument.serial.baudrate=SERIAL_BAUDRATE
		#timeout=int(config['SERIAL_RX_TIMEOUT_S']),
		#write_timeout=int(config['SERIAL_TX_TIMEOUT_S']),
		self.instrument.serial.MODE_RTU = mode
		self.instrument.serial.bytesize=bytesize
		self.instrument.serial.stopbits=stopbits
		self.instrument.serial.parity=parity
		self.instrument.serial.clear_buffers_before_each_transaction = True
		self.config = config  


	#Private methods
	def _read(self, modbusAddress, nDecimals):
		nTries = 0
		maxTries  = 10
		while nTries < maxTries:
			try:
				output = self.instrument.read_register(modbusAddress, nDecimals) # Registernumber, number of decimals
				return output
			except:
				print("connection attempt" + str(nTries))
				nTries = nTries + 1
				time.sleep(0.01)
		output = None
			


		

		
	def _write(self, modbusAddress, value, nDecimals):
		nTries = 0
		maxTries  = 10
		while nTries < maxTries:
			try:
				self.instrument.write_register(modbusAddress, value, nDecimals) # Registernumber, number of decimals
			except:
				nTries = nTries + 1
				time.sleep(0.01)

		
		
	#public methods
	def getProcessVariable(self, registerAddress = 1):
		
		## Read temperature (PV = ProcessValue) ##
		pv = self._read(registerAddress, 2) # Registernumber, number of decimals
		#print(temperature)
		return pv
	
	def getSetpoint(self, registerAddress = 24):
		
		## get the set point 1 (sp1)
		sp1 = self._read(registerAddress, 2) # Registernumber, number of decimals
		#print(temperature)
		return sp1
	
	def setSetpoint(self, value, registerAddress = 24,  nDecimals=2):

		#set the set point
		self._write(registerAddress, value, nDecimals) # Registernumber, number of decimals
		#print(temperature)
		


if __name__ == "__main__":
	config = configparser.ConfigParser()
	config.read('etc/config/config.ini')

	parser = argparse.ArgumentParser()
	parser.add_argument("--gsp", help="get setpoint", action='store_true')
	parser.add_argument("--gpv", help="get process variable", 
		action='store_true')
	parser.add_argument("--ssp", help="set process variable (deg C)", 
		type=int)

	args = parser.parse_args()

	eurothermModbus = s2000Modbus(config['eurothermModbus'])

	if args.ssp is not None:
		print(eurothermModbus.setSetpoint(args.ssp))
	elif args.gsp:
		print(eurothermModbus.getSetpoint())
	elif args.gpv:
		print(eurothermModbus.getProcessVariable())




	
