import socket
import configparser
import argparse
import time
import ast

import numpy as np

class s2200():
	def __init__(self, config):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.settimeout(int(config['CONN_TIMEOUT_S']))
		self.s.connect((config['HOST'], int(config['PORT'])))
		self.config = config

	def __del__(self):
		self.s.close()

	def _send(self, cmd, rx_timeout, terminator):
		cmd += terminator
		cmd = cmd.encode('utf-8')
		cmd = ast.literal_eval(str(cmd).replace('\\\\', '\\'))
		self.s.sendall(cmd)

		terminator = terminator.encode('utf-8')
		terminator = ast.literal_eval(str(terminator).replace('\\\\', '\\'))

		buf = ''
		data = []
		st = time.time()
		while True:
			buf = self.s.recv(1)
			data.append(buf)
			if buf == chr(terminator[1]).encode('utf-8'):
				break
			elif time.time() - st > rx_timeout:
				return None
		return data

	def getProcessVariable(self):
		terminator = self.config['TERMINATOR']
		rx_timeout = int(self.config['RX_TIMEOUT_S'])
		cmd = 'PVAR1?'

		data = self._send(cmd, rx_timeout, terminator)
		if data is not None:
			data_ascii = ''.join([chr(ord(d)) for d in data])
			pv = float(data_ascii[:-2])
			return pv
		else:
			return None	

	def getSetpoint(self):
		terminator = self.config['TERMINATOR']
		rx_timeout = int(self.config['RX_TIMEOUT_S'])
		cmd = 'SETP1?'

		data = self._send(cmd, rx_timeout, terminator)
		if data is not None:
			data_ascii = ''.join([chr(ord(d)) for d in data])
			setpoint = float(data_ascii[:-2])
			return setpoint
		else:
			return None

	def run(self):
		terminator = self.config['TERMINATOR']
		rx_timeout = int(self.config['RX_TIMEOUT_S'])
		cmd = 'RUNM'

		data = self._send(cmd, rx_timeout, terminator)
		if data is not None:
			if data[0] == b'0':
				return True
			else:
				return False
		else:
			return False	

	def setSetpoint(self, temperature):
		# Note that the instrument must be sent a RUNM command before it loads 
		# the setpoint into the register.
		#
		terminator = self.config['TERMINATOR']
		rx_timeout = int(self.config['RX_TIMEOUT_S'])
		cmd = 'SETP1,' + str(temperature)

		data = self._send(cmd, rx_timeout, terminator)
		if data is not None:
			if data[0] == b'0':
				return True
			else:
				return False
		else:
			return False

	def stop(self):
		terminator = self.config['TERMINATOR']
		rx_timeout = int(self.config['RX_TIMEOUT_S'])
		cmd = 'STOP'

		data = self._send(cmd, rx_timeout, terminator)
		if data is not None:
			if data[0] == b'0':
				return True
			else:
				return False
		else:
			return True	

if __name__ == "__main__":
	config = configparser.ConfigParser()
	config.read('etc/config/config.ini')

	parser = argparse.ArgumentParser()
	parser.add_argument("--gsp", help="get setpoint", action='store_true')
	parser.add_argument("--gpv", help="get process variable", 
		action='store_true')
	parser.add_argument("--ssp", help="set process variable (deg C)", 
		type=int)
	parser.add_argument("--run", help="run", action='store_true')
	parser.add_argument("--stop", help="stop", action='store_true')

	args = parser.parse_args()

	thermotron = s2200(config['thermotron'])

	if args.ssp is not None:
		print(thermotron.setSetpoint(args.ssp))
	elif args.gsp:
		print(thermotron.getSetpoint())
	elif args.gpv:
		print(thermotron.getProcessVariable())
	elif args.run:
		print(thermotron.run())
	elif args.stop:
		print(thermotron.stop())





