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
    from LAND_comms_equipment.eurothermModbus import s2000Modbus
except:
    from eurothermModbus import s2000Modbus
import math

#Initialize the furnace chamber
config = configparser.ConfigParser()
config.read('etc/config/config.ini')
eurothermModbus = s2000Modbus(config['eurothermModbus'])#initialise the furnace chamber

#Initalize variables
furnaceGetTemp = numpy.array([])
furnaceSetTemp = numpy.array([])
allfurnaceGetTemp = numpy.array([])
allfurnaceSetTemp = numpy.array([])
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
    fieldNames2 = ["FurnaceTemp" ,"furnace Start Temp", "N furnace Temps", "furnace Step Temp", "furnace Dwell Time Mins", "Pause time (to warm)" ,"Total Duration Hours", "MeasurmentIntervalS"]
    fieldValues2 = list(multenterbox(msg='Fill in values for the fields.', title='Enter', fields=(fieldNames2)))
    
    #furnace Temp
    furnaceTempString = fieldValues2[0]
    
    #furnace Conditions
    furnaceTempString = fieldValues2[1]
    furnaceStartTemp = float(furnaceTempString)
    
    nfurnaceString = fieldValues2[2]
    nfurnace = int(nfurnaceString) 
    
    furnaceStepString = fieldValues2[3]
    furnaceStep = int(furnaceStepString)

    furnaceDwellMinsString = fieldValues2[4]
    furnaceDwellMins = float(furnaceDwellMinsString)

    totalDurationHoursString = fieldValues2[5]
    totalDurationHours = float(totalDurationHoursString)

    measurmentIntervalString = fieldValues2[6]
    measurmentInterval = float(measurmentIntervalString)

    #Long winded non pythonean way of making an array!!
    for n in range(0, nfurnace ):
        thisValue =furnaceStartTemp + n*furnaceStep
        allfurnaceSetTemp =numpy.append(allfurnaceSetTemp, thisValue)
    print(allfurnaceSetTemp) 
    
    
    count = 0

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
            
            

            #Setup clock structure
            furnaceDwellClock = TicToc()

            currentfurnaceDurationMins = float(0)

            furnaceDwellClock.tic()

            while currentfurnaceDurationMins < furnaceDwellMins:

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

                elapsedTime = t.tocvalue()
                elapsedTime = float(elapsedTime)
                elapsedTimeMins = elapsedTime/60
                elapsedTimeHours = elapsedTime/3600
                print("Elapsed_" + str(elapsedTimeHours))
                print("Duration" + str(totalDurationHours))

                #print("Writing to csv file " + str(fileName) )
                arrayOut = str(elapsedTimeMins) +  "," + str(furnaceSetTemp) + ","  + str(currentfurnace)  + '\n'
                hFile.write(arrayOut)

                #build up arrays for plotting
                allTime = numpy.append(allTime, elapsedTime)
                allfurnaceGetTemp = numpy.append(allfurnaceGetTemp, currentfurnace) 
                furnaceTemps = numpy.append(furnaceTemps, furnaceSetTemp)
                
                
                plt.figure(1)
                plt.plot(allTime, allfurnaceGetTemp, linestyle='dashed', marker='o', color =  'b')
                
                plt.plot(allTime, furnaceTemps, 'r')
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
eurothermModbus.run()
time.sleep(1)
eurothermModbus.stop()
        
print('Finished')



    






