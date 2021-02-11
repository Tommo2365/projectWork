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
#from RiseTimeFunc import FitRiseTime 
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
    from LAND_comms_equipment.eurothermModbus import s2000Modbus
except:
    from eurothermModbus import s2000Modbus
import math
from CSpot import CSpot

#Initialize the furnace chamber
config = configparser.ConfigParser()
config.read('etc/config/config.ini')
eurothermModbus = s2000Modbus(config['eurothermModbus'])#initialise the furnace chamber

#Initialize the Spot 
config = configparser.ConfigParser()
config.read('etc/config/config.ini')
spot = CSpot(config['spot'])#make a spot instance


#Initalize variables
furnaceGetTemp = numpy.array([])
furnaceSetTemp = numpy.array([])
allfurnaceGetTemp = numpy.array([])
allfurnaceSetTemp = numpy.array([])
allSpotMeanTemps = numpy.array([])
allSpotStdevTemps = numpy.array([])
furnaceTemps = numpy.array([])
allTime = numpy.array([])
allElapsedTimeMins = float(0)
elapsedTime = float(0)
maxfurnace = 550


#Build folder timestamp structure
folder = "C:\\Data"
now = datetime.now() 
timestamp = now.strftime("%Y%m%d_%H_%M_%S")
fileName =  folder + "/" +  timestamp + "_"  + "Data.csv"
fileNameFigure =  folder + "/" + timestamp + "furnaceTempFigure.png"
fileNamePrefixSpotRawData = folder + "/" +  timestamp + "_"  + "RawTempData_"

#Setup clock structure
t = TicToc()


#Create figure
hFig = plt.figure()
plt.ion()
plt.ylabel('Temp')


#start the clock
t.tic() #Start timer

with open(fileName, 'w') as hFile: # Use hfile to refer to the file object
    #UI user input
    fieldNames2 = ["furnace Start Temp", "N furnace Temps", "furnace Step Temp",  "Pause before measure time (mins)", "Total Duration Hours", "MeasurmentInterval between repeats (s)", "Spot N temps ", "Spot Sample Rate (ms)", "Spot N repeats at each temp"]
    fieldValues2 = list(multenterbox(msg='Fill in values for the fields.', title='Enter', fields=(fieldNames2)))
    
     
    #furnace Conditions
    furnaceTempString = fieldValues2[0]
    furnaceStartTemp = float(furnaceTempString)
    
    nfurnaceString = fieldValues2[1]
    nfurnace = int(nfurnaceString) 
    
    furnaceStepString = fieldValues2[2]
    furnaceStep = float(furnaceStepString)

    #furnaceDwellMinsString = fieldValues2[3]
    #furnaceDwellMins = float(furnaceDwellMinsString)

    furnacePauseTimeMinsString = fieldValues2[3]
    furnacePauseTimeMins = float(furnacePauseTimeMinsString)

    totalDurationHoursString = fieldValues2[4]
    totalDurationHours = float(totalDurationHoursString)

    #How often to repeat measurments of furnace 
    measurmentIntervalString = fieldValues2[5]
    measurmentInterval = float(measurmentIntervalString)

    #Spot conditions
    spotNReadingsString = fieldValues2[6]# the number of spot readings to acquire- linked to duration of readings
    spotNReadings = int(spotNReadingsString) 

    spotSampleRateMsString = fieldValues2[7]# the sample rate at which to acquire the spot readings
    spotSampleRateMs = float(spotSampleRateMsString)

    spotNRepeatsString = fieldValues2[8] # The number of times to repeat a 'burst' of spotNReadings, ie. how many times to log at each temperature.
    spotNRepeats = int(spotNRepeatsString)

    count = 0

    #Long winded non pythonean way of making an array!!
    for n in range(0, nfurnace ):
        thisValue =furnaceStartTemp + n*furnaceStep
        allfurnaceSetTemp =numpy.append(allfurnaceSetTemp, thisValue)
    print(allfurnaceSetTemp) 
    
    
    

    elapsedTimeHours = 0

    while (elapsedTimeHours < totalDurationHours):
        
        for n in range(0, nfurnace ):
            #Get the current furnace set point from the list
            furnaceSetTemp = allfurnaceSetTemp[n]
            furnaceSetTemp = furnaceSetTemp
            print("Setting furnace to" + str(furnaceSetTemp))
            if furnaceSetTemp > maxfurnace:
                furnaceSetTemp = furnaceStartTemp
                if furnaceStartTemp > maxfurnace:
                    furnaceSetTemp = 23
            
            
            #Set the furnace Set point
            eurothermModbus.setSetpoint(furnaceSetTemp) 
            time.sleep(1)
            #eurothermModbus.run()
            time.sleep(1)

            setPointValue = float(eurothermModbus.getSetpoint())
            if setPointValue != furnaceSetTemp:
                print("FAILURE IN SETPOINT")
            else:
                print("furnace SetPoint set to" + str(setPointValue))

            
            print("Pausing to allow furnace to warm for_" + furnacePauseTimeMinsString + "_Mins")
            time.sleep(furnacePauseTimeMins*60)
            
            

            #Setup clock structure
            furnaceDwellClock = TicToc()

            currentfurnaceDurationMins = float(0)

            furnaceDwellClock.tic()

            for k in range(0,spotNRepeats):
                #count = count + 1

                #Try to check the furnace has been set correctly
                try:
                    currentfurnace = eurothermModbus.getProcessVariable()
                except ValueError:
                    print("Error Reading eurothermModbus furnace caught in value error")
                    continue

                if currentfurnace == False:
                    print("Error Reading eurothermModbus furnace")
                        #currentfurnace = nan
                        #allfurnaceGetTemp.append(currentfurnace)
                        #allfurnaceSetTemp.append(furnaceSetTemp)
                    continue

            
                print("furnace set point is" + str(setPointValue))
                print("furnace Temp gpv is" + str(currentfurnace))

                #Get the spot readings

                allSpotRawValues, spotElapsedTime = spot.ReadRegister(spotNReadings, spotSampleRateMs)
                allSpotRawValues = allSpotRawValues/10 #Remove decimal place
                allSpotRawValues = np.transpose(allSpotRawValues[:])
                
                
                bSaveRawData = False

                if bSaveRawData:

                    lengthValues = len(allSpotRawValues)
                    writeString = ''
                    for w in range(0,lengthValues):
                        thisValue = allSpotRawValues[w]
                        thisString = str(thisValue)  + "\n"
                        writeString = writeString + thisString


                    #Save the raw spot values
                    fileNameRawData = fileNamePrefixSpotRawData + str(setPointValue) + "_" + str(n) + "_" + str(k) + "_" + str(count) + "_" + "RawData.csv"
                    with open(fileNameRawData, 'w') as hFileRawData: # Use hfile to refer to the file object
                        hFileRawData.write(str(writeString))



                

                spotMeanValue = np.mean(allSpotRawValues)
                spotNoiseValue = np.std(allSpotRawValues)

                elapsedTime = t.tocvalue()
                elapsedTime = float(elapsedTime)
                elapsedTimeMins = elapsedTime/60
                elapsedTimeHours = elapsedTime/3600
                print("Elapsed_" + str(elapsedTimeHours))
                print("Duration" + str(totalDurationHours))

                if count == 0:
                    count = count + 1
                    arrayOut = "ElapsedTime" + "," + "furnaceSetTemp" + "," + "FurnaceGetTemp" + "," + "Spot Measured mean" + "," + "Spot Measured Stdev" + "\n"
                    hFile.write(arrayOut)

                print("Writing to csv file " + str(fileName) )
                arrayOut = str(elapsedTimeMins) +  "," + str(furnaceSetTemp) + ","  + str(currentfurnace) + "," + str(spotMeanValue) + "," + str(spotNoiseValue) + "\n"
                hFile.write(arrayOut)

                #build up arrays for plotting
                allTime = numpy.append(allTime, elapsedTime)
                allfurnaceGetTemp = numpy.append(allfurnaceGetTemp, currentfurnace) 
                furnaceTemps = numpy.append(furnaceTemps, furnaceSetTemp)
                allSpotMeanTemps = np.append(allSpotMeanTemps, spotMeanValue)
                
                
                plt.figure(1)
                plt.plot(allTime, allSpotMeanTemps, linestyle='dashed', marker='o', color =  'b')
                
                plt.plot(allTime, allfurnaceGetTemp, 'r')
                #plt.plot(1, 1)
                plt.xlabel("Time (seconds)")
                plt.ylabel("furnace Temp")
                plt.draw()
                plt.pause(0.01) 
                hFig.savefig(fileNameFigure, dpi=hFig.dpi)
            
                currentfurnaceDurationS = furnaceDwellClock.tocvalue()
                currentfurnaceDurationMins = float(currentfurnaceDurationS)/60
                
                time.sleep(measurmentInterval)

                
                #print("Current furnace elapsed time_ Mins" + str(currentfurnaceDurationMins))
                #print("Dwell time_" + str(furnaceDwellMins))

#Set the furnace Set point
eurothermModbus.setSetpoint(furnaceStartTemp) 
time.sleep(1)
#eurothermModbus.run()
time.sleep(1)
#eurothermModbus.stop()
        
print('Finished')



    






