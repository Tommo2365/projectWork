import serial
import configparser
import argparse
import time
from datetime import datetime
import numpy as np
import keyboard  # using module keyboard
import matplotlib.pyplot as plt
from matplotlib.pyplot import plot, draw, show, ion
import statistics
from RiseTimeFunc import FitRiseTime 
import matplotlib.animation as animation
from matplotlib import style
from tkinter.filedialog import askdirectory
import numpy
import scipy
from scipy.optimize import curve_fit
from pytictoc import TicToc
#import rhinoscriptsyntax as rs
#from rhino import rhinoscriptsyntax
import easygui
from easygui import msgbox, multenterbox
try:
    from LAND_comms_equipment.thermotron import s2200
except:
    from thermotron import s2200
import math

class L():
    def __init__(self, config):
        if int(config['SERIAL_BYTESIZE']) == 8:
            bytesize = serial.EIGHTBITS
        elif int(config['SERIAL_BYTESIZE']) == 7:
            bytesize = serial.SEVENBITS

        if int(config['SERIAL_STOPBITS']) == 1:
            stopbits = serial.STOPBITS_ONE
        elif int(config['SERIAL_STOPBITS']) == 2:
            stopbits = serial.STOPBITS_TWO

        if config['SERIAL_PARITY'] == 'NONE':
            parity = serial.PARITY_NONE
        elif config['SERIAL_PARITY'] == 'ODD':
            parity = serial.PARITY_ODD
        elif config['SERIAL_PARITY'] == 'EVEN':
            parity = serial.PARITY_EVEN
        elif config['SERIAL_PARITY'] == 'MARK':
            parity = serial.PARITY_MARK

        self.s = serial.Serial(config['SERIAL_COM_PORT'],
            baudrate=config['SERIAL_BAUDRATE'],
            timeout=int(config['SERIAL_RX_TIMEOUT_S']),
            write_timeout=int(config['SERIAL_TX_TIMEOUT_S']),
            bytesize=bytesize,
            stopbits=stopbits,
            parity=parity,
            rtscts=0)
        self.config = config        

    def __del__(self):
        self.s.close()

    def _read(self):
        self.s.reset_input_buffer()
        return self.s.readline()

    def _send(self, cmd):
        if self.s.is_open:
            self.s.reset_output_buffer()
            cmd = (cmd + '\r\n')
            self.s.write(cmd.encode('utf-8'))

            return self._read()

    def getTemperature(self, nreadings, cmd_timeout):
        T = []
        st = time.time()
        emptyT = str('_ _ _')
        while (True):
            try:
                try:
                    this_T = float(self._read().decode('ASCII').split(
                        '+')[1].strip('\r\n'))
                except ValueError:
                    print(this_T)
                    print('Remove cap')
                    
                
            except IndexError:   
                return None
            T.append(this_T)
            if len(T) == nreadings:
                break
            elif time.time() - st > cmd_timeout:         
               return None
        return T  

    

    def getBurstTemperatureE2(self ,cmd_timeout,measurementTime):
        bBurstMode = True
        nDataPoints = 1000
        count = 0
        numpyAllT = numpy.array([])
        numpyThisT = numpy.array([])
        numpyTimeAxis = numpy.array([nDataPoints])
        allTime = []
        allT  = []
        IR100 = []
        ISIG = []
        DAMB = []
        allData = []
        #folder = askdirectory()
        folder = "C:\Data"
        now = datetime.now() 
        timestamp = now.strftime("%Y%m%d_%H_%M_%S")
        fileName =  folder + "/" + timestamp + "Data.csv"
        fileNameFigure =  folder + "/" + timestamp + "TempData.png"
        print(timestamp)
        print(fileName)
        t = TicToc()
        elapsedTime = float(0)
        
        hFig = plt.figure()
       
        plt.ion()
       # plt.show()
        plt.ylabel('Temp')

        t.tic() #Start timer
        print(measurementTime)

        with open(fileName, 'a') as hFile: # Use hfile to refer to the file object
            
            
            while (elapsedTime < measurementTime):
                plt.clf()
                
                
                bkeyPress = keyboard.is_pressed('q')
                if bkeyPress:
                        bBurstMode = False
                else:
                    try:
                    
                        
                        thisData = self._read().decode('ASCII').strip(',\r\n').split()
                        allData.append(thisData)
                        print(thisData)
                        
                        if(len(thisData) != 2):
                            continue
                        lableString = thisData[0]
                        valueString = (thisData[1])
                        valueString.strip("[]")
                        value = float(valueString)

                        elapsedTime = t.tocvalue()
                        #print(elapsedTime)
                        elapsedTime = float(elapsedTime)

                        count = count + 1

                        if(count == 1):
                            arrayOut = 'Time' + "," + "IR100" + "," + "IR" + "," + "ISIG"  + "," + "DAMB" + "," +"Temp" +'\n'
                            hFile.write(arrayOut)
                        
                        if(lableString == 'IR100'):
                            #IR100 = value
                            arrayOut = str(elapsedTime) + ","  + str(value) + '\n'
                            hFile.write(arrayOut)
                        elif(lableString== 'IR'):
                            #ISIG.append(value)
                            arrayOut = str(elapsedTime) + "," + "," + str(value) + '\n'
                            hFile.write(arrayOut)
                        
                        elif(lableString== 'ISIG'):
                            #ISIG.append(value)
                            arrayOut = str(elapsedTime) + "," + "," + "," + str(value) + '\n'
                            hFile.write(arrayOut)
                        elif(lableString == 'DAMB'):
                           # DAMB.append(value)
                            arrayOut = str(elapsedTime) + "," + "," + "," + ", " + str(value) + '\n'
                            hFile.write(arrayOut)
                        elif(lableString == 'TEMP'):
                           # DAMB.append(value)
                            arrayOut = str(elapsedTime) + "," + "," + "," + "," + ","  + str(value) + '\n'
                            hFile.write(arrayOut)

                        else:
                            
                            continue 

                        
                        
                        print(count)
                   
                    
                    

                    except ValueError:
                        continue
        print('end of acqusition')
        
        
  
        #rowOne = len(allData)
        #print(rowOne)
        #print('output')
        """ count2 = -1
        while(count2 < len(allData)):
            count2 = count2+1
            thisData = allData[count2]
            print('current data is')
            print(thisData)
            if(len(thisData) != 2):
                    continue
            lableString = thisData[0]
            value = float(thisData[1])
            if(lableString == 'IR100'):
                IR100.append(value)
            elif(lableString== 'ISIG'):
                ISIG.append(value)
            elif(lableString == 'DAMB'):
                DAMB.append(value)
            else:
                continue
 """
        #print(IR100)
       # print('here')

        #plt.plot(IR100)
        #plt.xlabel("Time (seconds)")
        #plt.ylabel("Temp degrees")
        #plt.draw()
        #plt.pause(0.01)
        #plt.show
        #hFig.savefig(fileNameFigure, dpi=hFig.dpi)
        
        

        



    def getBurstTemperatureE(self, cmd_timeout):
        bBurstMode = True
        nDataPoints = 1000
        count = 0
        numpyAllT = numpy.array([])
        numpyThisT = numpy.array([])
        numpyTimeAxis = numpy.array([nDataPoints])
        allTime = []
        callT  = []
        #folder = askdirectory()
        folder = "C:\Data"
        now = datetime.now() 
        timestamp = now.strftime("%Y%m%d_%H_%M_%S")
        fileName =  folder + "/" + timestamp + "Data.csv"
        fileNameFigure =  folder + "/" + timestamp + "TempData.png"
        print(timestamp)
        print(fileName)
        t = TicToc()
        
        hFig = plt.figure()
        plt.ion()
       # plt.show()
        plt.ylabel('Temp')

        t.tic() #Start timer


        with open(fileName, 'a') as hFile: # Use hfile to refer to the file object
            while (bBurstMode):
                plt.clf()
                
                
                bkeyPress = keyboard.is_pressed('q')
                if bkeyPress:
                        bBurstMode = False
                else:
                    try:
                       
                        this_T = self._read().decode('ASCII').strip('\r\n')
                        #this_T = float(self._read().decode('ASCII').split(
                         #   '+')[1].strip('\r\n'))
                        elapsedTime = t.tocvalue()
                        elapsedTime = float(elapsedTime)
                        
                        
                        if not this_T: 
                            print(str(elapsedTime) + "Time")
                            continue

                        #this_TInt = int(this_T)
                        #if this_TInt < 1000:
                          #  continue
                        
                        
                        count = count + 1
                        #print(elapsedTime)
                        
                        numpyThisT = this_T
                        numpyThisT = float(numpyThisT)/float(10)
                        #allT.append(this_T)
                        numpyAllT =numpy.append(numpyAllT, numpyThisT)
                        allTime.append(elapsedTime)

                        print(this_T)
                        #print(allT)
                        if count > nDataPoints:
                            #numpyAllT = numpyAllT[len(numpyAllT)-nDataPoints:len(numpyAllT)]
                            numpyAllT = numpyAllT[1:nDataPoints]
                            allTime = allTime[1:nDataPoints]
                        #matArray = numpy.array(allT,dtype='f')
                        #allT = matArray/10
                       # allT = [x/10 for x in allT]
                        yLimUp = max(numpyAllT)
                        yLimDown = min(numpyAllT)
                        arrayOut = str(elapsedTime) + ","  + str(numpyThisT) + '\n'
                        hFile.write(arrayOut)
                        bkeyPress = keyboard.is_pressed('q')
                       
                        plt.plot(allTime, numpyAllT)
                        plt.xlabel("Time (seconds)")
                        plt.ylabel("Temp degrees")
                        plt.legend([str(this_T)])
                        plt.draw()
                        plt.pause(0.01)
                        #plt.show(block=False)
                        plt.axis([0,nDataPoints,yLimDown,yLimUp])

                        hFig.savefig(fileNameFigure, dpi=hFig.dpi)


                    except ValueError:
                        print('Not in engineers mode or beam blocked')
                
        return None

    def getBurstTemperatureEStandard(self, cmd_timeout):
        bBurstMode = True
        nDataPoints = 1000
        count = 0
        numpyAllT = numpy.array([])
        numpyThisT = numpy.array([])
        numpyTimeAxis = numpy.array([nDataPoints])
        allTime = []
        callT  = []
        #folder = askdirectory()
        folder = "C:\Data"
        now = datetime.now() 
        timestamp = now.strftime("%Y%m%d_%H_%M_%S")
        fileName =  folder + "/" + timestamp + "Data.csv"
        fileNameFigure =  folder + "/" + timestamp + "TempData.png"
        print(timestamp)
        print(fileName)
        t = TicToc()
        
        hFig = plt.figure()
        plt.ion()
       # plt.show()
        plt.ylabel('Temp')

        t.tic() #Start timer


        with open(fileName, 'a') as hFile: # Use hfile to refer to the file object
            while (bBurstMode):
                plt.clf()
                
                
                bkeyPress = keyboard.is_pressed('q')
                if bkeyPress:
                        bBurstMode = False
                else:
                    try:
                       
                        this_T = self._read().decode('ASCII')
                        print(this_T)
                        return
                        #this_T = float(self._read().decode('ASCII').split(
                         #   '+')[1].strip('\r\n'))
                        elapsedTime = t.tocvalue()
                        elapsedTime = float(elapsedTime)
                        
                        
                        if not this_T: 
                            print(str(elapsedTime) + "Time")
                            continue

                        this_TInt = int(this_T)
                        if this_TInt < 1000:
                            continue
                        
                        
                        count = count + 1
                        #print(elapsedTime)
                        
                        numpyThisT = this_T
                        numpyThisT = float(numpyThisT)/float(10)
                        #allT.append(this_T)
                        numpyAllT =numpy.append(numpyAllT, numpyThisT)
                        allTime.append(elapsedTime)

                        print(this_T)
                        #print(allT)
                        if count > nDataPoints:
                            #numpyAllT = numpyAllT[len(numpyAllT)-nDataPoints:len(numpyAllT)]
                            numpyAllT = numpyAllT[1:nDataPoints]
                            allTime = allTime[1:nDataPoints]
                        #matArray = numpy.array(allT,dtype='f')
                        #allT = matArray/10
                       # allT = [x/10 for x in allT]
                        yLimUp = max(numpyAllT)
                        yLimDown = min(numpyAllT)
                        arrayOut = str(elapsedTime) + ","  + str(numpyThisT) + '\n'
                        hFile.write(arrayOut)
                        bkeyPress = keyboard.is_pressed('q')
                       
                        plt.plot(allTime, numpyAllT)
                        plt.xlabel("Time (seconds)")
                        plt.ylabel("Temp degrees")
                        plt.legend([str(this_T)])
                        plt.draw()
                        plt.pause(0.01)
                        #plt.show(block=False)
                        plt.axis([0,nDataPoints,yLimDown,yLimUp])

                        hFig.savefig(fileNameFigure, dpi=hFig.dpi)


                    except ValueError:
                        print('Not in engineers mode or beam blocked')
                
        return None

    def getBurstTemperature(self, cmd_timeout):
        bBurstMode = True
        nDataPoints = 500
        count = 0
        numpyAllT = numpy.array([])
        numpyThisT = numpy.array([])
        numpyTimeAxis = numpy.array([nDataPoints])
        allTime = []
        pauseDuration = 10
        allT  = []
        this_T = []
        #folder = askdirectory()
        fieldNames = ["SerialNumer" ,"MeasurementDuraration", "pauseDuration"]
        fieldValues = list(multenterbox(msg='Fill in values for the fields.', title='Enter', fields=(fieldNames)))
        #msgbox(msg=(fieldValues), title = "Results")
        serialNumberString = fieldValues[0]
        measurementTime = int(fieldValues[1])
        pauseDuration = float(fieldValues[2])
        #numpyFieldValues = numpy.array(fieldValues)
        #print(numpyFieldValues[0])
        
        


        folder = "C:\Data"
        now = datetime.now() 
        timestamp = now.strftime("%Y%m%d_%H_%M_%S")
        fileName =  folder + "/" +  timestamp + "_" + serialNumberString + "_" +str(measurementTime) + "_"  + "Data.csv"
        fileNameFigure =  folder + "/" +  timestamp + "_" + serialNumberString + "_" +str(measurementTime) + "_"  + "TempData.png"
        print(timestamp)
        print(fileName)
        t = TicToc()
        #measurementTime = 30
        elapsedTime = 0

        fieldNames = ["Name","Street Address","City","State","ZipCode"]
        fieldValues = ['']


        

        hFig = plt.figure()
        plt.ion()
       # plt.show()
        plt.ylabel('Temp')

        t.tic() #Start timer


        with open(fileName, 'a') as hFile: # Use hfile to refer to the file object
            while (elapsedTime < measurementTime):
                plt.clf()
                
                
                bkeyPress = keyboard.is_pressed('q')
                if bkeyPress:
                        bBurstMode = False
                else:
                    try:
                       
                        #this_T = self._read().decode('ASCII').strip('\r\n')
                        this_T = float(self._read().decode('ASCII').split(
                            '+')[1].strip('\r\n'))
                        elapsedTime = t.tocvalue()
                        elapsedTime = float(elapsedTime)
                        print(this_T)

                    except ValueError:
                        print('Beam blocked')
                        this_T = 400
                    
            

                
                #this_TInt = int(this_T)
                if 0 < this_T < 100:
                    print('single digit temp from serial')
                    continue
                
                
                count = count + 1
                print(str(elapsedTime))
                
                numpyThisT = this_T
                numpyThisT = float(numpyThisT)
                #allT.append(this_T)
                numpyAllT =numpy.append(numpyAllT, numpyThisT)
                allTime.append(elapsedTime)

                print(this_T)
                #print(allT)
                if count > nDataPoints:
                    #numpyAllT = numpyAllT[len(numpyAllT)-nDataPoints:len(numpyAllT)]
                    numpyAllT = numpyAllT[1:nDataPoints]
                    allTime = allTime[1:nDataPoints]
                #matArray = numpy.array(allT,dtype='f')
                #allT = matArray/10
                # allT = [x/10 for x in allT]
                #yLimUp = max(numpyAllT)
                #yLimDown = min(numpyAllT)
                medT = np.median(numpyAllT)
                
                yLimUp = float(medT)+0.05*float(medT)
                yLimDown = float(medT)-0.05*float(medT)
                #yLimDown = 400
                #print(str(yLimDown))

                arrayOut = str(elapsedTime) + ","  + str(numpyThisT) + '\n'
                hFile.write(arrayOut)
                bkeyPress = keyboard.is_pressed('q')
                if count < nDataPoints:
                    plt.axis([0,measurementTime,yLimDown,yLimUp])
                else:
                    plt.axis([allTime[0],allTime[len(allTime)-1],yLimDown,yLimUp])

                

                plt.plot(allTime, numpyAllT, linestyle='dashed', marker='o', color =  'b')
                plt.xlabel("Time (seconds)")
                plt.ylabel("Temp degrees")
                plt.draw()
                plt.pause(0.01)

                time.sleep(pauseDuration)
                
                #plt.show(block=False)
                #plt.axis([0,nDataPoints,yLimDown,yLimUp])

                

                    #except ValueError:
                        #print('Not in engineers mode or beam blocked')
                continue   
                
        hFig.savefig(fileNameFigure, dpi=hFig.dpi)
        #return None

        #minT = min(numpyAllT)
        #medT = np.median(numpyAllT)
        
        #allT = float(numpyAllT)
        #bTempArray = numpy.all((numpyAllT > 400))
        #tempArray = numpyAllT[bTempArray]
        
        #minTIndex = np.argmin(numpyAllT)
        minTIndex = np.where(numpyAllT == numpyAllT.min())[0]

        #non400Index = np.where(numpyAllT > 400 )[0]
        minTIndex2 = minTIndex[-1]
        print(str(minTIndex2))

       
        yData = numpyAllT[minTIndex2+1:-1]
        xData = allTime[minTIndex2+1:-1]

        fitAmp, fitTau = FitRiseTime(xData, yData)
        
        print(str(fitAmp))
        print(str(fitTau))
        
        
        plt.show(block = True)
        hFig.savefig(fileNameFigure, dpi=hFig.dpi)

        
        #hFig2 = plt.figure()    
        
        #plt.ion()  
        #plt.axis([allTime[0],allTime[len(allTime)-1],yLimDown,yLimUp])
        #plt.axis([min(xData),max(xData),min(yData),yLimUp])


        #plt.plot(xData, yData)
        #plt.show(block = True)
        #plt.xlabel("Time (seconds)")
        #plt.ylabel("Temp degrees")
        #plt.show(block = True)
        #plt.pause(0.01)
        print('Finished')

    def ambientScan(self, cmd_timeout):
        print('hello')
        thermotron = s2200(config['thermotron'])#initialise the ambinet chamber
        ambientGetTemp = []
        ambientSetTemp = []
        allAmbientGetTemp = []
        allAmbientSetTemp = []
        rampEveryMins = float(60)
        ambientRampInterval = float(5)
        startTemp = float(30)
       
        ambientGetTemp = thermotron.getProcessVariable()
        ambientSetTemp = startTemp
        maxAmbient = 70
        print("startup Ambient Set Temp: " + str(ambientSetTemp))
        print("startup Ambient Get Temp: " + str(ambientGetTemp))
        
        
        
        bBurstMode = True
        nDataPoints = 500
        count = 0
        numpyAllT = numpy.array([])
        numpyThisT = numpy.array([])
        numpyAllMins = numpy.array([0])
        #numpyAllMins[0] = float(0)
        numpyTimeAxis = numpy.array([nDataPoints])
        allTime = []
        allElapsedTimeMins = float(0)
        #pauseDuration = 10
        allT  = []
        this_T = []
        #folder = askdirectory()
        fieldNames = ["SerialNumer" ,"MeasurementDurarationHours", "pauseDuration", "rampEveryMins" ]
        fieldValues = list(multenterbox(msg='Fill in values for the fields.', title='Enter', fields=(fieldNames)))
        #msgbox(msg=(fieldValues), title = "Results")
        serialNumberString = fieldValues[0]
        measurementTime = int(3600*float(fieldValues[1]))
        pauseDuration = float(fieldValues[2])
        rampEveryMins = float(fieldValues[3])
        #numpyFieldValues = numpy.array(fieldValues)
        #print(numpyFieldValues[0])
        initialPauseMins = float(90)
       
        
        


        folder = "C:\Data"
        now = datetime.now() 
        timestamp = now.strftime("%Y%m%d_%H_%M_%S")
        fileName =  folder + "/" +  timestamp + serialNumberString + "_" +str(measurementTime) + "_"  + "Data.csv"
        fileNameFigure =  folder + "/" + timestamp + "TempData.png"
        fileNameFigure2 =  folder + "/" + timestamp + "Ambient.png"
        print(timestamp)
        print(fileName)
        t = TicToc()
        #measurementTime = 30
        elapsedTime = 0

        fieldNames = ["Name","Street Address","City","State","ZipCode"]
        fieldValues = ['']


        

        hFig = plt.figure()
        plt.ion()
        plt.ylabel('Temp')
        hFig2 = plt.figure()
        plt.ion()
       # plt.show()
        
        #time.sleep(60*initialPauseMins)

        thermotron.setSetpoint(startTemp) 
        time.sleep(1)
        thermotron.run()
        time.sleep(60*initialPauseMins)
        t.tic() #Start timer

        ambientGetTemp = thermotron.getProcessVariable()
        if ambientSetTemp > maxAmbient:
            print("Ambient Set temp exeeds maxAmbient degrees limits, restting to startTemp")
            ambientSetTemp = startTemp


        with open(fileName, 'a') as hFile: # Use hfile to refer to the file object
            while (elapsedTime < measurementTime):
                plt.clf()
                
                
                
                bkeyPress = keyboard.is_pressed('q')
                if bkeyPress:
                        bBurstMode = False
                else:
                    try:
                       
                        #this_T = self._read().decode('ASCII').strip('\r\n')
                        #rawData = float(self._read().decode('ASCII'))
                        #print(str(rawData))
                        rawDataString = (self._read().decode('ASCII'))
                        rawDataString = rawDataString.strip('\r\n')
                        splitDataString = rawDataString.split('+')
                        numberOfElements = len(splitDataString)
                        print(str(numberOfElements))
                        if numberOfElements != 2:
                            print("Error reading cyclops temperature")
                            continue
                        this_T = float(splitDataString[1])
                                

                        #this_T = float(self._read().decode('ASCII').split(
                        #    '+')[1].strip('\r\n'))
                        elapsedTime = t.tocvalue()
                        elapsedTime = float(elapsedTime)
                        print(this_T)

                    except ValueError:
                        
                        print('Beam blocked')
                        this_T = 400
                        continue
                
                    
            

                
                #this_TInt = int(this_T)
                if 0 < this_T < 100:
                    print('single digit temp from serial')
                    continue
                
                
                count = count + 1
                print(str(elapsedTime))




                #Example 1:  6%2 evaluates to 0 because there's no remainder if 6 is divided by 2 ( 3 times ).

                #elapsedTimeMins = float(round(elapsedTime/60))
                elapsedTimeMins = math.floor(elapsedTime/60)
                print(str(elapsedTimeMins))
                previousElapsedTimeInMins = numpyAllMins[-1]#get the previous mins BEFORE APPEND
                numpyAllMins = numpy.append(numpyAllMins, elapsedTimeMins)#append the array
                
               
                thisElapsedTimeInMins = numpyAllMins[-1]# get the mins now
                
                numpyThisT = this_T
                numpyThisT = float(numpyThisT)
                #allT.append(this_T)
                
                

                bIsIntegerOfRamptime = False
                rem = float(1)
                if elapsedTimeMins > 0:
                    rem = elapsedTimeMins % rampEveryMins
                    if rem == 0:
                        bIsIntegerOfRamptime = True
                        print(str(rem))
                        print("Mins are an integer of rampEveryMins")

                bChangeOfMins = False
                minsDiff = thisElapsedTimeInMins - previousElapsedTimeInMins
                if minsDiff != 0:
                    bChangeOfMins = True
                    print("Mins has changed")
                if bChangeOfMins & bIsIntegerOfRamptime:
                    ambientSetTemp = ambientSetTemp + ambientRampInterval
                    if ambientSetTemp > maxAmbient:
                        ambientSetTemp = startTemp
                        print("Ambient Set temp exeeds maxAmbient degrees limits, resetting to startTemp")
                        
                    print("Changing Ambient Chamber Set Point to" + str(ambientSetTemp))
                    #thermotron.stop()
                    time.sleep(1)

                    
                    thermotron.setSetpoint(ambientSetTemp) 
                    time.sleep(1)
                    thermotron.run()
                    time.sleep(1)
                    setPointValue = float(thermotron.getSetpoint())
                    if setPointValue != ambientSetTemp:
                        print("FAILURE IN SETPOINT")
                    else:
                        print("SetPoint set")
                   
               

                if count == 1:
                    ambientSetTemp = startTemp
                    if ambientSetTemp > maxAmbient:
                        print("Ambient Set temp exeeds maxAmbient degrees limits")
                        return
                    print("Changing Ambient Chamber Set Point to STARTUP TEMP_" + str(ambientSetTemp))
                    #thermotron.stop()
                    time.sleep(1)

                    
                    thermotron.setSetpoint(ambientSetTemp) 
                    time.sleep(1)
                    thermotron.run()
                    time.sleep(1)
                    setPointValue = float(thermotron.getSetpoint())
                    if setPointValue != ambientSetTemp:
                        print("FAILURE IN SETPOINT")
                    else:
                        print("SetPoint set")

                try:
                    currentAmbient = thermotron.getProcessVariable()
                except ValueError:
                    #currentAmbient = nan
                    
                    #allAmbientGetTemp.append(currentAmbient)
                   #allAmbientSetTemp.append(ambientSetTemp)
                    print("Error Reading Thermotron ambient caught in value error")
                    continue

                if currentAmbient == False:
                    print("Error Reading Thermotron ambient")
                    #currentAmbient = nan
                    #allAmbientGetTemp.append(currentAmbient)
                    #allAmbientSetTemp.append(ambientSetTemp)
                    continue


                print("current Ambient Set Temp: " + str(ambientSetTemp))
                print("current Ambient Get Temp: " + str(currentAmbient))
                allAmbientGetTemp.append(currentAmbient)
                allAmbientSetTemp.append(ambientSetTemp)
                allTime.append(elapsedTime)
                numpyAllT =numpy.append(numpyAllT, numpyThisT)

            

                print(this_T)
               
                medT = np.median(numpyAllT)
                maxT = np.max(numpyAllT)
                minT = np.min(numpyAllT)

                
                yLimUp = maxT
                yLimDown = minT
                #yLimDown = 400
                #print(str(yLimDown))

                arrayOut = str(elapsedTime) + ","  + str(numpyThisT) + "," + str(currentAmbient) + "," + str(ambientSetTemp) +  '\n'
                hFile.write(arrayOut)
                bkeyPress = keyboard.is_pressed('q')
                plt.figure(1)
                if count < nDataPoints:
                    plt.axis([0,measurementTime,yLimDown,yLimUp])
                else:
                    plt.axis([allTime[0],allTime[len(allTime)-1],yLimDown,yLimUp])


                
                plt.figure(1)
                plt.plot(allTime, numpyAllT, linestyle='dashed', marker='o', color =  'b')
                plt.xlabel("Time (seconds)")
                plt.ylabel("Temp degrees")
                plt.draw()
                plt.pause(0.01)
                plt.legend(["cyclops T: " + str(this_T)])


                plt.figure(2)
                yLimDown = 7
                yLimUp = 53
                plt.axis([0, measurementTime,yLimDown,yLimUp])
                plt.plot(allTime, allAmbientGetTemp, linestyle='dashed', marker='o', color =  'r')
                plt.plot(allTime, allAmbientSetTemp, linestyle='dashed', marker='x', color =  'b')
                plt.xlabel("Time (seconds)")
                plt.ylabel("Temp degrees")
                plt.draw()
                plt.legend(["ambient T: " + str(currentAmbient), "set point T: " + str(setPointValue)])
                plt.pause(0.01)


                time.sleep(pauseDuration)
                
                
                hFig.savefig(fileNameFigure, dpi=hFig.dpi)
                hFig2.savefig(fileNameFigure2, dpi=hFig.dpi)

        print("Measurmement duration exeeding, exiting logging")   
        #thermotron.stop()
        time.sleep(1)
        endTemp = float(20)
        thermotron.setSetpoint(endTemp) 
        time.sleep(1)
        thermotron.run()
        time.sleep(1)
        setPointValue = float(thermotron.getSetpoint())
        
                   
        currentAmbient = thermotron.getProcessVariable()
        print("current Ambient Set Temp: " + str(setPointValue))
        print("current Ambient Get Temp: " + str(currentAmbient))

  
        thermotron.stop()
        
        print('Finished')


    def ambientScanRaw(self, cmd_timeout):
        thermotron = s2200(config['thermotron'])#initialise the ambinet chamber
        ambientGetTemp = []
        ambientSetTemp = []
        allAmbientGetTemp = []
        allAmbientSetTemp = []
        rampEveryMins = float(180)
        ambientRampInterval = float(10)
        startTemp = float(10)
        ambientGetTemp = thermotron.getProcessVariable()
        ambientSetTemp = startTemp
        print("startup Ambient Set Temp: " + str(ambientSetTemp))
        print("startup Ambient Get Temp: " + str(ambientGetTemp))
        
        
        
        bBurstMode = True
        nDataPoints = 500
        count = 0
        numpyAllT = numpy.array([])
        numpyAllThermistorT= numpy.array([])
        numpyThisT = numpy.array([])
        numpyAllMins = numpy.array([0])
        #numpyAllMins[0] = float(0)
        numpyTimeAxis = numpy.array([nDataPoints])
        allTime = []
        allElapsedTimeMins = float(0)
        #pauseDuration = 10
        allT  = []
        this_T = []
        #folder = askdirectory()
        fieldNames = ["SerialNumer" ,"MeasurementDurarationHours", "pauseDuration", "rampEveryMins" ]
        fieldValues = list(multenterbox(msg='Fill in values for the fields.', title='Enter', fields=(fieldNames)))
        #msgbox(msg=(fieldValues), title = "Results")
        serialNumberString = fieldValues[0]
        measurementTime = int(3600*float(fieldValues[1]))
        pauseDuration = float(fieldValues[2])
        rampEveryMins = float(fieldValues[3])
        #numpyFieldValues = numpy.array(fieldValues)
        #print(numpyFieldValues[0])
        
        


        folder = "C:\Data"
        now = datetime.now() 
        timestamp = now.strftime("%Y%m%d_%H_%M_%S")
        fileName =  folder + "/" +  timestamp + serialNumberString + "_" +str(measurementTime) + "_"  + "Data.csv"
        fileNameFigure =  folder + "/" + timestamp + "TempData.png"
        fileNameFigure2 =  folder + "/" + timestamp + "Ambient.png"
        print(timestamp)
        print(fileName)
        t = TicToc()
        #measurementTime = 30
        elapsedTime = 0

        fieldNames = ["Name","Street Address","City","State","ZipCode"]
        fieldValues = ['']


        

        hFig = plt.figure()
        plt.ion()
        plt.ylabel('Temp')
        hFig2 = plt.figure()
        plt.ion()
       # plt.show()
        

        t.tic() #Start timer

        ambientGetTemp = thermotron.getProcessVariable()
        if ambientSetTemp > maxAmbient:
            print("Ambient Set temp exeeds maxAmbient degrees limits, restting to startTemp")
            ambientSetTemp = startTemp


        with open(fileName, 'a') as hFile: # Use hfile to refer to the file object
            while (elapsedTime < measurementTime):
                plt.clf()
                
                
                
                bkeyPress = keyboard.is_pressed('q')
                if bkeyPress:
                        bBurstMode = False
                else:
                    try:
                       
                        #this_T = self._read().decode('ASCII').strip('\r\n')
                        #rawData = float(self._read().decode('ASCII'))
                        #print(str(rawData))
                        rawDataString = (self._read().decode('ASCII'))
                        rawDataString = rawDataString.strip('\r\n')
                        splitDataString = rawDataString.split()
                        #return

                        numberOfElements = len(splitDataString)
                        print(str(numberOfElements))
                        if numberOfElements != 4:
                            print("Error reading cyclops temperature")
                            continue
                        if not splitDataString[0]:
                            print("Error reading cyclops temperature")
                            continue
                        if not splitDataString[1]:
                            print("Error reading cyclops temperature")
                            continue
                        if not splitDataString[2]:
                            print("Error reading cyclops temperature")
                            continue
                        if not splitDataString[3]:
                            print("Error reading cyclops temperature")
                            continue

                        count = count + 1
                        print(str(elapsedTime))

                        if(count ==  1 ):
                            firstT = float(splitDataString[2])
                            firstThermistorT = float(splitDataString[3])
                            arrayOut = str(serialNumberString) + '\n' +  "time" + "," + "detSignal" + "," + "ambientGet" + "," + "ambientSet" + "," + "thermistorSignal" +  '\n'
                            #arrayOut = str(serialNumberString) + "," + "detSignal" + "," + str(firstT) + "," + "thermistorSignal" + "," + str(firstThermistorT)  +   '\n'
                            hFile.write(arrayOut)
                         
                        this_T = float(splitDataString[2])
                        thermistorT = float(splitDataString[3])

                        
                                

                        #this_T = float(self._read().decode('ASCII').split(
                        #    '+')[1].strip('\r\n'))
                        elapsedTime = t.tocvalue()
                        elapsedTime = float(elapsedTime)
                        print(this_T)

                    except ValueError:
                        
                        print('Beam blocked')
                        this_T = 400
                        continue
                
                    
            

                
                #this_TInt = int(this_T)
                #if 0 < this_T < 100:
                   # print('single digit temp from serial')
                  #  continue
                
                
                




                #Example 1:  6%2 evaluates to 0 because there's no remainder if 6 is divided by 2 ( 3 times ).

                #elapsedTimeMins = float(round(elapsedTime/60))
                elapsedTimeMins = math.floor(elapsedTime/60)
                print(str(elapsedTimeMins))
                previousElapsedTimeInMins = numpyAllMins[-1]#get the previous mins BEFORE APPEND
                numpyAllMins = numpy.append(numpyAllMins, elapsedTimeMins)#append the array
                
               
                thisElapsedTimeInMins = numpyAllMins[-1]# get the mins now
                
                numpyThisT = this_T
                numpyThisT = float(numpyThisT)
                #allT.append(this_T)
                
                

                bIsIntegerOfRamptime = False
                rem = float(1)
                if elapsedTimeMins > 0:
                    rem = elapsedTimeMins % rampEveryMins
                    if rem == 0:
                        bIsIntegerOfRamptime = True
                        print(str(rem))
                        print("Mins are an integer of rampEveryMins")

                bChangeOfMins = False
                minsDiff = thisElapsedTimeInMins - previousElapsedTimeInMins
                if minsDiff != 0:
                    bChangeOfMins = True
                    print("Mins has changed")
                if bChangeOfMins & bIsIntegerOfRamptime:
                    ambientSetTemp = ambientSetTemp + ambientRampInterval
                    if ambientSetTemp > maxAmbient:
                        ambientSetTemp = startTemp
                        print("Ambient Set temp exeeds maxAmbient degrees limits, resetting to startTemp")
                        
                    print("Changing Ambient Chamber Set Point to" + str(ambientSetTemp))
                    #thermotron.stop()
                    time.sleep(1)

                    
                    thermotron.setSetpoint(ambientSetTemp) 
                    time.sleep(1)
                    thermotron.run()
                    time.sleep(1)
                    setPointValue = float(thermotron.getSetpoint())
                    if setPointValue != ambientSetTemp:
                        print("FAILURE IN SETPOINT")
                    else:
                        print("SetPoint set")
                   
               

                if count == 1:
                    ambientSetTemp = startTemp
                    if ambientSetTemp > maxAmbient:
                        print("Ambient Set temp exeeds maxAmbient degrees limits")
                        return
                    print("Changing Ambient Chamber Set Point to STARTUP TEMP_" + str(ambientSetTemp))
                    #thermotron.stop()
                    time.sleep(1)

                    
                    thermotron.setSetpoint(ambientSetTemp) 
                    time.sleep(1)
                    thermotron.run()
                    time.sleep(1)
                    setPointValue = float(thermotron.getSetpoint())
                    if setPointValue != ambientSetTemp:
                        print("FAILURE IN SETPOINT")
                    else:
                        print("SetPoint set")

                try:
                    currentAmbient = thermotron.getProcessVariable()
                except ValueError:
                    #currentAmbient = nan
                    
                    #allAmbientGetTemp.append(currentAmbient)
                   #allAmbientSetTemp.append(ambientSetTemp)
                    print("Error Reading Thermotron ambient caught in value error")
                    continue

                if currentAmbient == False:
                    print("Error Reading Thermotron ambient")
                    #currentAmbient = nan
                    #allAmbientGetTemp.append(currentAmbient)
                    #allAmbientSetTemp.append(ambientSetTemp)
                    continue


                print("current Ambient Set Temp: " + str(ambientSetTemp))
                print("current Ambient Get Temp: " + str(currentAmbient))
                allAmbientGetTemp.append(currentAmbient)
                allAmbientSetTemp.append(ambientSetTemp)
                allTime.append(elapsedTime)
                numpyAllT =numpy.append(numpyAllT, numpyThisT)

                numpyAllThermistorT = numpy.append(numpyAllThermistorT, thermistorT)

            

                print(this_T)
               
                medT = np.median(numpyAllT)
                maxT = np.max(numpyAllT)
                minT = np.min(numpyAllT)

                lowerLim = 0.25
                upperLim = 1.75

                
                yLimUp = maxT
                yLimDown = minT
                #yLimDown = 400
                #print(str(yLimDown))

                arrayOut = str(elapsedTime) + ","  + str(numpyThisT) + "," + str(currentAmbient) + "," + str(ambientSetTemp) + "," + str(thermistorT) +   '\n'
                hFile.write(arrayOut)
                bkeyPress = keyboard.is_pressed('q')
                bPlot = False
                if bPlot:
                    plt.figure(1)
                    if count < nDataPoints:
                        plt.axis([0,measurementTime,lowerLim,yLimUp])
                    else:
                        plt.axis([allTime[0],allTime[len(allTime)-1],lowerLim,upperLim])
               
                if bPlot:
                
                    plt.figure(1)
                    plt.plot(allTime, numpyAllT, linestyle='dashed', marker='o', color =  'b')
                    plt.plot(allTime, numpyAllThermistorT, linestyle='dashed', marker='o', color =  'r')
                    plt.xlabel("Time (seconds)")
                    plt.ylabel("Temp degrees")
                    plt.draw()
                    plt.pause(0.01)
                    plt.legend(["cyclops T: " + str(this_T)])


                    plt.figure(2)
                    yLimDown = 7
                    yLimUp = 53
                    plt.axis([0, measurementTime,yLimDown,yLimUp])
                    plt.plot(allTime, allAmbientGetTemp, linestyle='dashed', marker='o', color =  'r')
                    plt.plot(allTime, allAmbientSetTemp, linestyle='dashed', marker='x', color =  'b')
                    plt.xlabel("Time (seconds)")
                    plt.ylabel("Temp degrees")
                    plt.draw()
                    plt.legend(["ambient T: " + str(currentAmbient), "set point T: " + str(setPointValue)])
                    plt.pause(0.01)


                time.sleep(pauseDuration)
                
                if bPlot:
                    hFig.savefig(fileNameFigure, dpi=hFig.dpi)
                    hFig2.savefig(fileNameFigure2, dpi=hFig.dpi)

        print("Measurmement duration exeeding, exiting logging")   
        #thermotron.stop()
        time.sleep(1)
        endTemp = float(20)
        thermotron.setSetpoint(endTemp) 
        time.sleep(1)
        thermotron.run()
        time.sleep(1)
        setPointValue = float(thermotron.getSetpoint())
        
                   
        currentAmbient = thermotron.getProcessVariable()
        print("current Ambient Set Temp: " + str(setPointValue))
        print("current Ambient Get Temp: " + str(currentAmbient))

  
        thermotron.stop()
        
        print('Finished')



    def getRawData(self, cmd_timeout):
        bBurstMode = True
        nDataPoints = 500
        count = 0
        numpyAllT = numpy.array([])
        numpyThisT = numpy.array([])
        numpyTimeAxis = numpy.array([nDataPoints])
        allTime = []
        allMeanTime = []
        allMeanTemp = []
        allData = []
        allT  = []
        this_T = []
        #folder = askdirectory()
        fieldNames = ["SerialNumer" ,"MeasurementDuraration"]
        fieldValues = list(multenterbox(msg='Fill in values for the fields.', title='Enter', fields=(fieldNames)))
        #msgbox(msg=(fieldValues), title = "Results")
        serialNumberString = fieldValues[0]
        measurementTime = int(fieldValues[1])
        #numpyFieldValues = numpy.array(fieldValues)
        #print(numpyFieldValues[0])
        
        


        folder = "C:\Data"
        now = datetime.now() 
        timestamp = now.strftime("%Y%m%d_%H_%M_%S")
        fileName =  folder + "/" +  timestamp + serialNumberString + "_" +str(measurementTime) + "_"  + "Data.csv"
        fileNameFigure =  folder + "/" + timestamp + "TempData.png"
        print(timestamp)
        print(fileName)
        t = TicToc()
        #measurementTime = 30
        elapsedTime = 0

        fieldNames = ["Name","Street Address","City","State","ZipCode"]
        fieldValues = ['']


        

        hFig = plt.figure()
        plt.ion()
    # plt.show()
        plt.ylabel('Temp')

        t.tic() #Start timer


        with open(fileName, 'a') as hFile: # Use hfile to refer to the file object
            while (elapsedTime < measurementTime):
                plt.clf()
                
                
                bkeyPress = keyboard.is_pressed('q')
                if bkeyPress:
                        bBurstMode = False
                else:
                    try:
                    
                        thisData = self._read().decode('ASCII').strip(',\r\n').split()
                        print(thisData)
                        
                        allData.append(thisData)
                        #print(thisData)
                        
                        if(len(thisData) != 4):
                            continue
                        lableString = thisData[0]
                        valueString = (thisData[2])
                        valueString.strip("[]")
                        value = float(valueString)

                        elapsedTime = t.tocvalue()
                        #print(elapsedTime)
                        elapsedTime = float(elapsedTime)

                        count = count + 1

                        if(count == 1):
                            arrayOut = 'Time' + "," + "RAW" +'\n'
                            hFile.write(arrayOut)
                        
                        if(lableString == 'SG'):
                            #IR100 = value
                            arrayOut = str(elapsedTime) + ","  + str(value) + '\n'
                            hFile.write(arrayOut)
                            #print(str(value))
                            this_T = value
                            #sprint(str(lableString))
                        elif(lableString== 'AM'):
                            #ISIG.append(value)
                            arrayOut = str(elapsedTime) + "," + "," + str(value) + '\n'
                            hFile.write(arrayOut)
                        
                        elif(lableString== 'ISIG'):
                            #ISIG.append(value)
                            arrayOut = str(elapsedTime) + "," + "," + "," + str(value) + '\n'
                            hFile.write(arrayOut)
                        elif(lableString == 'DAMB'):
                           # DAMB.append(value)
                            arrayOut = str(elapsedTime) + "," + "," + "," + ", " + str(value) + '\n'
                            hFile.write(arrayOut)
                        elif(lableString == 'TEMP'):
                           # DAMB.append(value)
                            arrayOut = str(elapsedTime) + "," + "," + "," + "," + ","  + str(value) + '\n'
                            hFile.write(arrayOut)

                        else:
                            
                            continue 

                        
                        
                        print(count)
                        elapsedTime = t.tocvalue()
                        elapsedTime = float(elapsedTime)
                        print(this_T)

                    except ValueError:
                        print('Beam blocked')
                        this_T = 0
                    
            

                
                #this_TInt = int(this_T)
                #if 0 < this_T < 100:
                    #print('single digit signal from serial')
                    #continue
                
                
                count = count + 1
                print(str(elapsedTime))
                
                numpyThisT = this_T
                numpyThisT = float(numpyThisT)
                #allT.append(this_T)
                numpyAllT =numpy.append(numpyAllT, numpyThisT)
                allTime.append(elapsedTime)

                print(this_T)
                #print(allT)
                if count > nDataPoints:
                    #numpyAllT = numpyAllT[len(numpyAllT)-nDataPoints:len(numpyAllT)]
                    numpyAllT = numpyAllT[1:nDataPoints]
                    allTime = allTime[1:nDataPoints]
                #matArray = numpy.array(allT,dtype='f')
                #allT = matArray/10
                # allT = [x/10 for x in allT]
                yLimUp = max(numpyAllT)+ 0.1*max(numpyAllT)
                #yLimDown = min(numpyAllT)
                medT = np.median(numpyAllT)
                
                #yLimUp = float(medT)+0.2*float(medT)
                #yLimDown = float(medT)-0.05*float(medT)
                yLimDown = 0
                #print(str(yLimDown))

                arrayOut = str(elapsedTime) + ","  + str(numpyThisT) + '\n'
                hFile.write(arrayOut)
                bkeyPress = keyboard.is_pressed('q')
                if count < nDataPoints:
                    plt.axis([0,measurementTime,yLimDown,yLimUp])
                else:
                    plt.axis([allTime[0],allTime[len(allTime)-1],yLimDown,yLimUp])
                
                averagingWindowSize = int(8)
                if count > averagingWindowSize+1:
                    lastNTemps = numpyAllT[-averagingWindowSize:-1]
                    lastNTimes = allTime[-averagingWindowSize:-1]
                    
                    meanTemp = np.median(lastNTemps)
                    meanTime = np.median(lastNTimes)

                    allMeanTime.append(meanTime)
                    allMeanTemp.append(meanTemp)
                    numEl = int(len(allMeanTemp))
                    print(str(numEl))

                    plt.plot(allMeanTime, allMeanTemp, linestyle='dashed', marker='o', color =  'r')
                    plt.legend(["mean sig: " + str(meanTemp)])
                    plt.draw()


                plt.plot(allTime, numpyAllT, linestyle='dashed', marker='x', color =  'b')
                
                plt.xlabel("Time (seconds)")
                plt.ylabel("Raw signal")
                
                plt.draw()
                plt.pause(0.01)
                
                #plt.show(block=False)
                #plt.axis([0,nDataPoints,yLimDown,yLimUp])

                

                    #except ValueError:
                        #print('Not in engineers mode or beam blocked')
                continue   
                

        #return None

        #minT = min(numpyAllT)
        #medT = np.median(numpyAllT)
        
        #allT = float(numpyAllT)
        #bTempArray = numpy.all((numpyAllT > 400))
        #tempArray = numpyAllT[bTempArray]
        
        #minTIndex = np.argmin(numpyAllT)
        minTIndex = np.where(numpyAllT == numpyAllT.min())[0]

        #non400Index = np.where(numpyAllT > 400 )[0]
        minTIndex2 = minTIndex[-1]
        print(str(minTIndex2))

    
        yData = numpyAllT[minTIndex2+1:-1]
        xData = allTime[minTIndex2+1:-1]

        fitAmp, fitTau = FitRiseTime(xData, yData)
        hFig.savefig(fileNameFigure, dpi=hFig.dpi)

    # print(str(fitAmp))
        #print(str(fitTau))s
        
        #minTIndexEnd = minTIndex[0,len(minTIndex)-1]
        #print(str(AAA))

        plt.show(block = True)
        
        #hFig2 = plt.figure()    
        
    # plt.ion()  
        #plt.axis([allTime[0],allTime[len(allTime)-1],yLimDown,yLimUp])
        #plt.axis([min(xData),max(xData),min(yData),yLimUp])


        #plt.plot(xData, yData)
        #plt.show(block = True)
        #plt.xlabel("Time (seconds)")
        #.ylabel("Temp degrees")
        #plt.show(block = True)
        #plt.pause(0.01)
        print('Finished')

    def getRawDataEng(self, cmd_timeout):
        bBurstMode = True
        nDataPoints = 15
        count = 0
        numpyAllT = numpy.array([])
        numpyThisT = numpy.array([])
        numpyTimeAxis = numpy.array([nDataPoints])
        allTime = []
        allMeanTime = []
        allMeanTemp = []
        allData = []
        allT  = []
        this_T = []
        #folder = askdirectory()
        fieldNames = ["SerialNumer" ,"MeasurementDuraration"]
        fieldValues = list(multenterbox(msg='Fill in values for the fields.', title='Enter', fields=(fieldNames)))
        #msgbox(msg=(fieldValues), title = "Results")
        serialNumberString = fieldValues[0]
        measurementTime = int(fieldValues[1])
        #numpyFieldValues = numpy.array(fieldValues)
        #print(numpyFieldValues[0])
        
        


        folder = "C:\Data"
        now = datetime.now() 
        timestamp = now.strftime("%Y%m%d_%H_%M_%S")
        fileName =  folder + "/" +  timestamp + serialNumberString + "_" +str(measurementTime) + "_"  + "Data.csv"
        fileNameFigure =  folder + "/" + timestamp + "TempData.png"
        print(timestamp)
        print(fileName)
        t = TicToc()
        #measurementTime = 30
        elapsedTime = 0

        fieldNames = ["Name","Street Address","City","State","ZipCode"]
        fieldValues = ['']


        

        hFig = plt.figure()
        plt.ion()
    # plt.show()
        plt.ylabel('Temp')

        t.tic() #Start timer


        with open(fileName, 'a') as hFile: # Use hfile to refer to the file object
            while (elapsedTime < measurementTime):
                plt.clf()
                
                
                bkeyPress = keyboard.is_pressed('q')
                if bkeyPress:
                        bBurstMode = False
                else:
                    try:
                    
                        thisData = self._read().decode('ASCII').strip(',\r\n').split()
                        print(str(thisData) + 'data')
                        
                        
                        allData.append(thisData)
                        #print(thisData)

                        print(str(len(thisData)))
                        
                        if(len(thisData) != 2):
                            continue
                        lableString = thisData[0]
                        valueString = (thisData[1])
                        print(str(lableString))
                        print(str(valueString))

                        #value = [float(i) for i in valueString]

                        
                        #valueString.strip("[]")
                        value = valueString

                        elapsedTime = t.tocvalue()
                        #print(elapsedTime)
                        elapsedTime = float(elapsedTime)

                        count = count + 1

                        if(count == 1):
                            arrayOut = 'Time' + "," + "RAW" +'\n'
                            hFile.write(arrayOut)
                        
                        if(lableString == 'ISIG'):
                            #IR100 = value
                            arrayOut = str(elapsedTime) + ","  + str(value) + '\n'
                            hFile.write(arrayOut)
                            #print(str(value))
                            this_T = float(valueString)
                            value = this_T
                            #sprint(str(lableString))
                        
                        #elif(lableString== 'AM'):
                            #ISIG.append(value)
                         #   arrayOut = str(elapsedTime) + "," + "," + str(value) + '\n'
                          #  hFile.write(arrayOut)
                        
                        #elif(lableString== 'ISIG'):
                            #ISIG.append(value)
                         #   arrayOut = str(elapsedTime) + "," + "," + "," + str(value) + '\n'
                         #   hFile.write(arrayOut)
                        #elif(lableString == 'DAMB'):
                           # DAMB.append(value)
                         #   arrayOut = str(elapsedTime) + "," + "," + "," + ", " + str(value) + '\n'
                         #   hFile.write(arrayOut)
                        #elif(lableString == 'TEMP'):
                           # DAMB.append(value)
                         #   arrayOut = str(elapsedTime) + "," + "," + "," + "," + ","  + str(value) + '\n'
                         #   hFile.write(arrayOut)

                        else:
                            
                            continue 

                        
                        
                        print(count)
                        elapsedTime = t.tocvalue()
                        elapsedTime = float(elapsedTime)
                        print(this_T)

                    except ValueError:
                        print('Beam blocked')
                        this_T = 0
                    
            

                
                #this_TInt = int(this_T)
                #if 0 < this_T < 100:
                    #print('single digit signal from serial')
                    #continue
                
                
                count = count + 1
                print(str(elapsedTime))
                
                numpyThisT = this_T
                numpyThisT = float(numpyThisT)
                #allT.append(this_T)
                numpyAllT =numpy.append(numpyAllT, numpyThisT)
                allTime.append(elapsedTime)

                print(this_T)
                #print(allT)
                if count > nDataPoints:
                    #numpyAllT = numpyAllT[len(numpyAllT)-nDataPoints:len(numpyAllT)]
                    numpyAllT = numpyAllT[1:nDataPoints]
                    allTime = allTime[1:nDataPoints]
                #matArray = numpy.array(allT,dtype='f')
                #allT = matArray/10
                # allT = [x/10 for x in allT]
                yLimUp = max(numpyAllT)+ 0.1*max(numpyAllT)
                #yLimDown = min(numpyAllT)
                medT = np.median(numpyAllT)
                
                #yLimUp = float(medT)+0.2*float(medT)
                #yLimDown = float(medT)-0.05*float(medT)
                yLimDown = 0
                #print(str(yLimDown))

                arrayOut = str(elapsedTime) + ","  + str(numpyThisT) + '\n'
                hFile.write(arrayOut)
                bkeyPress = keyboard.is_pressed('q')
                if count < nDataPoints:
                    plt.axis([0,measurementTime,yLimDown,yLimUp])
                else:
                    plt.axis([allTime[0],allTime[len(allTime)-1],yLimDown,yLimUp])
                
                averagingWindowSize = int(8)
                if count > averagingWindowSize+1:
                    lastNTemps = numpyAllT[-averagingWindowSize:-1]
                    lastNTimes = allTime[-averagingWindowSize:-1]
                    
                    meanTemp = np.median(lastNTemps)
                    meanTime = np.median(lastNTimes)

                    allMeanTime.append(meanTime)
                    allMeanTemp.append(meanTemp)
                    numEl = int(len(allMeanTemp))
                    print(str(numEl))

                    plt.plot(allMeanTime, allMeanTemp, linestyle='dashed', marker='o', color =  'r')
                    plt.legend(["mean sig: " + str(meanTemp)])
                    plt.draw()


                plt.plot(allTime, numpyAllT, linestyle='dashed', marker='x', color =  'b')
                
                plt.xlabel("Time (seconds)")
                plt.ylabel("Raw signal")
                
                plt.draw()
                plt.pause(0.01)
                
                #plt.show(block=False)
                #plt.axis([0,nDataPoints,yLimDown,yLimUp])

                

                    #except ValueError:
                        #print('Not in engineers mode or beam blocked')
                continue   
                

        #return None

        #minT = min(numpyAllT)
        #medT = np.median(numpyAllT)
        
        #allT = float(numpyAllT)
        #bTempArray = numpy.all((numpyAllT > 400))
        #tempArray = numpyAllT[bTempArray]
        
        #minTIndex = np.argmin(numpyAllT)
        #minTIndex = np.where(numpyAllT == numpyAllT.min())[0]

        #non400Index = np.where(numpyAllT > 400 )[0]
        #minTIndex2 = minTIndex[-1]
        #print(str(minTIndex2))

    
        #yData = numpyAllT[minTIndex2+1:-1]
        #xData = allTime[minTIndex2+1:-1]

       # fitAmp, fitTau = FitRiseTime(xData, yData)
        hFig.savefig(fileNameFigure, dpi=hFig.dpi)

    # print(str(fitAmp))
        #print(str(fitTau))s
        
        #minTIndexEnd = minTIndex[0,len(minTIndex)-1]
        #print(str(AAA))

        plt.show(block = True)
        
        #hFig2 = plt.figure()    
        
    # plt.ion()  
        #plt.axis([allTime[0],allTime[len(allTime)-1],yLimDown,yLimUp])
        #plt.axis([min(xData),max(xData),min(yData),yLimUp])


        #plt.plot(xData, yData)
        #plt.show(block = True)
        #plt.xlabel("Time (seconds)")
        #.ylabel("Temp degrees")
        #plt.show(block = True)
        #plt.pause(0.01)
        print('Finished')


    def triggerOff(self): 
        rtn = self._send('DTO').decode('ASCII').strip().strip('\r\n')
        if (rtn == 'DTO,C'):
            return True
        else:
            print(rtn)
            return False

    def triggerOn(self): 
        rtn = self._send('DTP').decode('ASCII').strip().strip('\r\n')
        if (rtn == 'DTP,C'):
            return True
        else:
            print(rtn)
            return False


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('etc/config/config.ini')

    parser = argparse.ArgumentParser()
    parser.add_argument("--get", help="get readings", type=int)
    parser.add_argument("--measurementTime", help="store data", type=float, default = 5)
    parser.add_argument("--on", help="trigger on", action='store_true')
    parser.add_argument("--off", help="trigger off", action='store_true') 
    parser.add_argument("--burst", help="get burst readings", action='store_true')
    parser.add_argument("--ambientScan", help="run Ambient scan", action='store_true')
    parser.add_argument("--ambientScanRaw", help="run Ambient scan with Thermistor", action='store_true')
    parser.add_argument("--burstE", help="get burst readings Engineers mode", action='store_true')
    parser.add_argument("--burstEStandard", help="get burst readings Engineers mode", action='store_true')  
    parser.add_argument("--burstE2", help="get burst readings Engineers mode",action='store_true')
    parser.add_argument("--raw", help="get raw signal Engineers mode",action='store_true')
    parser.add_argument("--rawEng", help="get raw signal Engineers mode",action='store_true')              
           

    args = parser.parse_args()

    cyclops = L(config['cyclops'])

    if args.on:
        print(cyclops.triggerOn())
    if args.off:
        print(cyclops.triggerOff())
    elif args.get is not None:
        print(cyclops.getTemperature(args.get, 
            int(config['cyclops']['CMD_TIMEOUT_S'])))
    if args.burst is True:
        print(cyclops.getBurstTemperature(int(config['cyclops']['CMD_TIMEOUT_S'])))
    if args.burstE is True:
        print(cyclops.getBurstTemperatureE(int(config['cyclops']['CMD_TIMEOUT_S'])))
    if args.ambientScan is True:
        print(cyclops.ambientScan(int(config['cyclops']['CMD_TIMEOUT_S'])))
    if args.ambientScanRaw is True:
        print(cyclops.ambientScanRaw(int(config['cyclops']['CMD_TIMEOUT_S'])))
    if args.burstEStandard is True:
        print(cyclops.getBurstTemperatureEStandard(int(config['cyclops']['CMD_TIMEOUT_S'])))
    if args.burstE2 is True:
        print(cyclops.getBurstTemperatureE2(int(config['cyclops']['CMD_TIMEOUT_S']), args.measurementTime))
    if args.raw is True:
        print(cyclops.getRawData(int(config['cyclops']['CMD_TIMEOUT_S'])))
    if args.rawEng is True:
        print(cyclops.getRawDataEng(int(config['cyclops']['CMD_TIMEOUT_S'])))