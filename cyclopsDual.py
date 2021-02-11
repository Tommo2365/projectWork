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

    


        

        



   

    def ambientScan(self, cmd_timeout):
        print('hello')
        thermotron = s2200(config['thermotron'])#initialise the ambinet chamber
        ambientGetTemp = []
        ambientSetTemp = []
        allAmbientGetTemp = []
        allAmbientSetTemp = []
        rampEveryMins = float(180)
        ambientRampInterval = float(10)
        startTemp = float(30)
        ambientGetTemp = thermotron.getProcessVariable()
        ambientSetTemp = startTemp
        print("startup Ambient Set Temp: " + str(ambientSetTemp))
        print("startup Ambient Get Temp: " + str(ambientGetTemp))

        numpyAllT = numpy.array([])
        numpyThisSIG = numpy.array([])
        numpyThisBLD = numpy.array([])
        numpyThisAMB = numpy.array([])
        numpyThisTMP = numpy.array([])
        numpyThisComp = numpy.array([])

        numpyAllSIG = numpy.array([])
        numpyAllBLD = numpy.array([])
        numpyAllAMB = numpy.array([])
        numpyAllTMP = numpy.array([])
        numpyAllComp = numpy.array([])

        GainFactor = float(4.5)
        
        
        
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


        

        hFig = plt.figure()
        plt.ion()
        plt.ylabel('Temp')
        hFig2 = plt.figure()
        plt.ion()
       # plt.show()
        

        t.tic() #Start timer

        ambientGetTemp = thermotron.getProcessVariable()
        if ambientSetTemp > 50:
            print("Ambient Set temp exeeds 50 degrees limits, restting to startTemp")
            ambientSetTemp = startTemp


        with open(fileName, 'w') as hFile: # Use hfile to refer to the file object
            while (elapsedTime < measurementTime):
                plt.clf()
                
                
                
                bkeyPress = keyboard.is_pressed('q')
                if bkeyPress:
                        bBurstMode = False
                else:
                    try:

                        rawDataLine = self._read().decode('ASCII').strip(',\r\n')

                        thisData = rawDataLine.split(',')#breaks up into an array removing commas
                        print(thisData)
                        #exit(0)

    
                        
                        #allData.append(thisData)
                        #print(thisData)
                        #print(len(thisData) )
                        #exit(0)
                        
                        if(len(thisData) != 4):
                            continue# we are expecting 4 elements

                        for index in range(0,4):
                            dataN = thisData[index]
                            print(dataN)
                            lableString = dataN[0:3]
                            valueString = dataN[4::]
                        
                            print(lableString)
                            print(valueString)

                            if(lableString == 'SIG'):
                                if(len(valueString) == 5):
                                    currentSIG = float(valueString)
                            
                                #sprint(str(lableString))
                            elif(lableString== 'BLD'):
                                if(len(valueString) == 5):
                                    currentBLD = float(valueString)
                            
                            elif(lableString== 'AMB'):
                                if(len(valueString) == 5):
                                    currentAMB = float(valueString)
                            elif(lableString == 'TMP'):
                                if(len(valueString) == 5):
                                    currentTMP = float(valueString)
                            

                            else:
                            
                                continue 
                        elapsedTime = t.tocvalue()
                        elapsedTime = float(elapsedTime)
                        print(this_T)

                    except ValueError:
                        
                        print('Beam blocked')
                        currentSIG = 100
                        continue
                
                    
            

                
                #print(currentSIG)
                #print(currentBLD)
                #print(currentAMB)
                #exit(0)
                
                
                count = count + 1
                print(str(elapsedTime))




                #Example 1:  6%2 evaluates to 0 because there's no remainder if 6 is divided by 2 ( 3 times ).

                #elapsedTimeMins = float(round(elapsedTime/60))
                elapsedTimeMins = math.floor(elapsedTime/60)
                print(str(elapsedTimeMins))
                previousElapsedTimeInMins = numpyAllMins[-1]#get the previous mins BEFORE APPEND
                numpyAllMins = numpy.append(numpyAllMins, elapsedTimeMins)#append the array
                
               
                thisElapsedTimeInMins = numpyAllMins[-1]# get the mins now

                
                

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
                    if ambientSetTemp > 50:
                        ambientSetTemp = startTemp
                        print("Ambient Set temp exeeds 50 degrees limits, resetting to startTemp")
                        
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
                    if ambientSetTemp > 50:
                        print("Ambient Set temp exeeds 50 degrees limits")
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
                #allTime.append(elapsedTime)
                numpyAllT =numpy.append(numpyAllT, numpyThisT)
                

                numpyThisSIG = np.array(currentSIG)
                numpyThisBLD = np.array(currentBLD)
                numpyThisAMB = np.array(currentAMB)
                numpyThisTMP = np.array(currentTMP)

                numpyThisComp = numpyThisSIG-GainFactor*numpyThisBLD

                numpyAllSIG =numpy.append(numpyAllSIG, numpyThisSIG)
                numpyAllBLD =numpy.append(numpyAllBLD, numpyThisBLD)
                numpyAllAMB =numpy.append(numpyAllAMB, numpyThisAMB)
                numpyAllTMP =numpy.append(numpyAllTMP, numpyThisTMP)

                numpyAllComp = numpy.append(numpyAllComp, numpyThisComp)

                allTime.append(elapsedTime)

                print(numpyAllSIG)
                #exit(0)

                

            

                #print(this_T)
               
                medT = np.median(numpyAllSIG)
                maxT = np.max(numpyAllSIG)
                minT = np.min(numpyAllComp)

                
                yLimUp = maxT
                yLimDown = minT
                #yLimDown = 400
                #print(str(yLimDown))

                count = count + 1
                if(count == 1):
                    arrayOut = 'Time' + "," + "SIG"  + ',' + 'BLD'+ ',' + 'AMB' + ',' + 'TMP' + ',' + 'AmbientGET' +',' + 'AmbientSET''\n'
                    hFile.write(arrayOut)

                arrayOut = str(elapsedTime)+ ','+ str(currentSIG) + ',' + str(currentBLD) + ','+ str(currentAMB) + ','+ str(currentTMP) + "," + str(currentAmbient) + "," + str(ambientSetTemp) + '\n' 

                #arrayOut = str(elapsedTime) + ","  + str(numpyThisT) + "," + str(currentAmbient) + "," + str(ambientSetTemp) +  '\n'
                hFile.write(arrayOut)
                bkeyPress = keyboard.is_pressed('q')
                plt.figure(1)
                if count < nDataPoints:
                    plt.axis([0,measurementTime,yLimDown,yLimUp])
                else:
                    plt.axis([allTime[0],allTime[len(allTime)-1],yLimDown,yLimUp])


                
                plt.figure(1)

                #print(len(allTime))
                #print(len(numpyAllSIG))
                #exit(0)
                
                plt.plot(allTime, numpyAllSIG, linestyle='dashed', marker='x', color =  'b')
                plt.plot(allTime, numpyAllComp, linestyle='dashed', marker='x', color =  'r')
                #plt.plot(allTime, numpyAllComp, linestyle='dashed', marker='x', color =  'k')

                plt.xlabel("Time (seconds)")
                plt.ylabel("Signal ADU")
                plt.draw()
                plt.pause(0.01)
                plt.legend(["cyclops T: " + str(currentSIG)])


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


    



    def getRawData(self, cmd_timeout):
        bBurstMode = True
        nDataPoints = 500
        count = 0
        numpyAllT = numpy.array([])
        numpyThisSIG = numpy.array([])
        numpyThisBLD = numpy.array([])
        numpyThisAMB = numpy.array([])
        numpyThisTMP = numpy.array([])
        numpyThisComp = numpy.array([])

        numpyAllSIG = numpy.array([])
        numpyAllBLD = numpy.array([])
        numpyAllAMB = numpy.array([])
        numpyAllTMP = numpy.array([])
        numpyAllComp = numpy.array([])

        GainFactor = float(4)

        numpyTimeAxis = numpy.array([nDataPoints])

        valueString = float(0)
        allTime = []
        allMeanTime = []
        allMeanTemp = []
        rawDataArray = [0,0,0,0]
        allData = []
        allT  = []
        this_T = 0
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


        with open(fileName, 'w') as hFile: # Use hfile to refer to the file object
            while (elapsedTime < measurementTime):
                plt.clf()
                
                

                try:

                    #for k in range(0, 3):
                    
                    #thisData = self._read().decode('ASCII').strip(',\r\n').split()
                    rawDataLine = self._read().decode('ASCII').strip(',\r\n')

                    thisData = rawDataLine.split(',')#breaks up into an array removing commas

    
                        
                    allData.append(thisData)
                    print(thisData)
                    print(len(thisData) )
                    #exit(0)
                        
                    if(len(thisData) != 4):
                        continue# we are expecting 4 elements

                    for index in range(0,4):
                        dataN = thisData[index]
                        print(dataN)
                        lableString = dataN[0:3]
                        valueString = dataN[4::]
                        
                        print(lableString)
                        print(valueString)

                        if(lableString == 'SIG'):
                            if(len(valueString) == 5):
                                currentSIG = float(valueString)
                            
                            #sprint(str(lableString))
                        elif(lableString== 'BLD'):
                            if(len(valueString) == 5):
                                currentBLD = float(valueString)
                            
                        elif(lableString== 'AMB'):
                            if(len(valueString) == 5):
                                currentAMB = float(valueString)
                        elif(lableString == 'TMP'):
                            if(len(valueString) == 5):
                                currentTMP = float(valueString)
                            

                        else:
                            
                            continue 

                    elapsedTime = t.tocvalue()
                        #print(elapsedTime)
                    elapsedTime = float(elapsedTime)

                    count = count + 1
                    if(count == 1):
                        arrayOut = 'Time' + "," + "SIG"  + ',' + 'BLD'+ ',' + 'AMB' + ',' + 'TMP' + '\n'
                        hFile.write(arrayOut)

                    arrayOut = str(elapsedTime)+ ','+ str(currentSIG) + ',' + str(currentBLD) + ','+ str(currentAMB) + ','+ str(currentTMP) + '\n' 
                    hFile.write(arrayOut)
                        

           
                except ValueError:
                    print('Beam blocked')
                    this_T = 0
                    
                

              
                
                numpyThisSIG = np.array(currentSIG)
                numpyThisBLD = np.array(currentBLD)
                numpyThisAMB = np.array(currentAMB)
                numpyThisTMP = np.array(currentTMP)

                numpyThisComp = numpyThisSIG-GainFactor*numpyThisBLD 

                numpyAllSIG =numpy.append(numpyAllSIG, numpyThisSIG)
                numpyAllBLD =numpy.append(numpyAllBLD, numpyThisBLD)
                numpyAllAMB =numpy.append(numpyAllAMB, numpyThisAMB)
                numpyAllTMP =numpy.append(numpyAllTMP, numpyThisTMP)

                numpyAllComp = numpy.append(numpyAllComp, numpyThisComp)



                allTime.append(elapsedTime)


               

                if count > nDataPoints:
                    #numpyAllT = numpyAllT[len(numpyAllT)-nDataPoints:len(numpyAllT)]
                    numpyAllSIG = numpyAllSIG[1:nDataPoints]
                    numpyAllBLD = numpyAllBLD[1:nDataPoints]
                    numpyAllComp = numpyAllComp[1:nDataPoints]

                    allTime = allTime[1:nDataPoints]
                #matArray = numpy.array(allT,dtype='f')
                #allT = matArray/10
                # allT = [x/10 for x in allT]
                yLimUp = max(numpyAllSIG)+ 0.1*max(numpyAllSIG)
                #yLimDown = min(numpyAllT)
                medT = np.median(numpyAllSIG)
                
                #yLimUp = float(medT)+0.2*float(medT)
                #yLimDown = float(medT)-0.05*float(medT)
                yLimDown = 6500
                #print(str(yLimDown))

               
                if count < nDataPoints:
                    plt.axis([0,measurementTime,yLimDown,yLimUp])
                else:
                    plt.axis([allTime[0],allTime[len(allTime)-1],yLimDown,yLimUp])
                
                averagingWindowSize = int(8)
                if count > averagingWindowSize+1:
                    lastNTemps = numpyAllSIG[-averagingWindowSize:-1]
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


                plt.plot(allTime, numpyAllSIG, linestyle='dashed', marker='x', color =  'b')
                plt.plot(allTime, numpyAllBLD, linestyle='dashed', marker='x', color =  'r')
                plt.plot(allTime, numpyAllComp, linestyle='dashed', marker='x', color =  'k')
                
                plt.xlabel("Time (seconds)")
                plt.ylabel("Raw signal")
                
                plt.draw()
                plt.pause(0.01)
                
        
                continue   
                

       
        hFig.savefig(fileNameFigure, dpi=hFig.dpi)
        plt.show(block = True)
        

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
    parser.add_argument("--ambientScan", help="run Ambient scan", action='store_true')
    parser.add_argument("--raw", help="get raw signal Engineers mode",action='store_true')
               
           

    args = parser.parse_args()

    cyclops = L(config['cyclops'])

    if args.on:
        print(cyclops.triggerOn())
    if args.off:
        print(cyclops.triggerOff())
    elif args.get is not None:
        print(cyclops.getTemperature(args.get, 
            int(config['cyclops']['CMD_TIMEOUT_S'])))
    
    if args.ambientScan is True:
        print(cyclops.ambientScan(int(config['cyclops']['CMD_TIMEOUT_S'])))
    
    if args.raw is True:
        print(cyclops.getRawData(int(config['cyclops']['CMD_TIMEOUT_S'])))
   