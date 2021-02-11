import serial
import configparser
import argparse
import numpy as np
import pymodbus
from pymodbus.client.sync import ModbusTcpClient
import matplotlib.pyplot as plt
from matplotlib.pyplot import plot, draw, show, ion
import time
from datetime import datetime
import numpy as np
from pytictoc import TicToc
class CSpot():
    # CSpot: class used to read a spot modbus register
    def __init__(self, config):
        
        self.host = config['HOST']#use the host ip address defined in etc/config (default is '10.1.10.50')
        
        timeout=int(config['CONN_TIMEOUT_S'])#define a connection timeout (not currently used)
        #self.modBusRegToRead = int(config['READ_MODBUS_REG'])
        self.config = config # make the config accessabile

  

    def ReadRegister(self, nReadings, sampleInteveralMs, address):
        self.client = ModbusTcpClient(self.host)# use ModbusTcpClient from pymodbus 
        #Method to read nReadings of a single modbus regeister at a sample interval sampleInteveralMs
        #Uses a pause of sampleInterval rather than re-sampling
        
        #Make an array for the the NReadings of values read from the register
        allValues = np.ones(nReadings)
        allValues = allValues*np.NAN
        t = TicToc()
        t.tic() #Start timer
        registerValue = np.NAN

        #bug fix - read a registor once, to set the correct registor address
        request = self.client.read_holding_registers(address,1) 
        registerValue = request.registers
        registerValue = np.NAN

        for k in range(0, nReadings):
            try:
                #address = int(self.config['READ_MODBUS_REG'])
                request = self.client.read_holding_registers(address,1) 
                registerValue = request.registers
            except: 
                registerValue = np.NAN # return Nan if the register can't be read
            #print(registerValue)
            #print(type(registerValue))
            #print(allValues)
            #exit(0)
            allValues[k] = registerValue[0]
            time.sleep(sampleInteveralMs/1e3)#pause before next reading. NB we are consitently sampling the same phase of the chopper
        #Return the array of nReadings of a single modbus register and the time taken to acquire.   
        elapsedTime = t.tocvalue()
        time.sleep(1)#Dwell to allow return of reponse
        self.client.close()
        
        return allValues, elapsedTime  



if __name__ == "__main__":
    #The main function
    
    config = configparser.ConfigParser()#Use the config parser to read in a config file
    config.read('etc/config/config.ini')

    parser = argparse.ArgumentParser()
    #Set the deafualt sample interval to 100nms
    parser.add_argument("--setSampleInterval", help = "Set the dwell time between successfive readings of a modbus register", default = 100, type = float)
    parser.add_argument("--setModbusAddress", help = "Set the value of the modbus address to read", default = 246, type = int)
    parser.add_argument("--get", help="Read Modbus Register Input nReadings and sample interval (ms) and address, default address is 246", type = int)
    args = parser.parse_args()
    #Build an isnatnce of the spot
    spot = CSpot(config['spot'])

    if args.get is not None:
        
        allValues, elapsedTime = spot.ReadRegister(args.get, args.setSampleInterval, args.setModbusAddress)
        print("Mean value_" + str(np.mean(allValues)), "Stdev value_" + str(np.std(allValues)))
        print("Measurment Duration S_" + str(elapsedTime))

