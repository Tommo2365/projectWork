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

#Initialize the ambient chamber
config = configparser.ConfigParser()
config.read('etc/config/config.ini')
thermotron = s2200(config['thermotron'])#initialise the ambinet chamber

#Initalize variables
ambientGetTemp = numpy.array([])
ambientSetTemp = numpy.array([])
allAmbientGetTemp = numpy.array([])
allAmbientSetTemp = numpy.array([])
ambientTemps = numpy.array([])
allTime = numpy.array([])
allElapsedTimeMins = float(0)
elapsedTime = float(0)
maxAmbient = 50


#Build folder timestmap structure
folder = "C:\\Data"
now = datetime.now() 
timestamp = now.strftime("%Y%m%d_%H_%M_%S")
fileName =  folder + "/" +  timestamp + "_"  + "Data.csv"
fileNameFigure =  folder + "/" + timestamp + "AmbientTempFigure.png"

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
    fieldNames2 = ["FurnaceTemp" ,"Ambient Start Temp", "N Ambient Temps", "Ambient Step Temp", "ambient Dwell Time Mins", "Total Duration Hours", "MeasurmentIntervalS"]
    fieldValues2 = list(multenterbox(msg='Fill in values for the fields.', title='Enter', fields=(fieldNames2)))
    
    #furnace Temp
    furnaceTempString = fieldValues2[0]
    
    #Ambient Conditions
    ambientTempString = fieldValues2[1]
    ambientStartTemp = float(ambientTempString)
    
    nAmbientString = fieldValues2[2]
    nAmbient = int(nAmbientString) 
    
    ambientStepString = fieldValues2[3]
    ambientStep = int(ambientStepString)

    ambientDwellMinsString = fieldValues2[4]
    ambientDwellMins = float(ambientDwellMinsString)

    totalDurationHoursString = fieldValues2[5]
    totalDurationHours = float(totalDurationHoursString)

    measurmentIntervalString = fieldValues2[6]
    measurmentInterval = float(measurmentIntervalString)

    #Long winded non pythonean way of making an array!!
    for n in range(0, nAmbient ):
        thisValue =ambientStartTemp + n*ambientStep
        allAmbientSetTemp =numpy.append(allAmbientSetTemp, thisValue)
    print(allAmbientSetTemp) 
    
    
    count = 0

    elapsedTimeHours = 0

    while (elapsedTimeHours < totalDurationHours):
        for n in range(0, nAmbient ):
            #Get the current ambient set point from the list
            ambientSetTemp = allAmbientSetTemp[n]
            ambientSetTemp = ambientSetTemp
            print("Setting ambient to" + str(ambientSetTemp))
            if ambientSetTemp > maxAmbient:
                ambientSetTemp = ambientStartTemp
                if ambientStartTemp > maxAmbient:
                    ambientSetTemp = 23
            
            
            #Set the ambient Set point
            thermotron.setSetpoint(ambientSetTemp) 
            time.sleep(1)
            thermotron.run()
            time.sleep(1)

            setPointValue = float(thermotron.getSetpoint())
            if setPointValue != ambientSetTemp:
                print("FAILURE IN SETPOINT")
            else:
                print("Ambient SetPoint set to" + str(setPointValue))
            
            

            #Setup clock structure
            ambientDwellClock = TicToc()

            currentAmbientDurationMins = float(0)

            ambientDwellClock.tic()

            while currentAmbientDurationMins < ambientDwellMins:

                #Try to check the ambient has been set correctly
                try:
                    currentAmbient = thermotron.getProcessVariable()
                except ValueError:
                    print("Error Reading Thermotron ambient caught in value error")
                    continue

                if currentAmbient == False:
                    print("Error Reading Thermotron ambient")
                        #currentAmbient = nan
                        #allAmbientGetTemp.append(currentAmbient)
                        #allAmbientSetTemp.append(ambientSetTemp)
                    continue

            
                print("Ambient set point is" + str(setPointValue))
                print("Ambient Temp gpv is" + str(currentAmbient))

                elapsedTime = t.tocvalue()
                elapsedTime = float(elapsedTime)
                elapsedTimeMins = elapsedTime/60
                elapsedTimeHours = elapsedTime/3600
                print("Elapsed_" + str(elapsedTimeHours))
                print("Duration" + str(totalDurationHours))

                #print("Writing to csv file " + str(fileName) )
                if count == 0:
                    print('writing file header')
                    count = count + 1
                    with open(fileName, 'a') as hFile: # Use hfile to refer to the file object
                        arrayOut = "ElapsedTimeMins" + "," + "ambientSetTemp" + "," + "AmbientGetTemp" + "\n"
                        hFile.write(arrayOut)
                
                
                with open(fileName, 'a') as hFile: # Use hfile to refer to the file object
                    arrayOut = str(elapsedTimeMins) +  "," + str(ambientSetTemp) + ","  + str(currentAmbient)  + '\n'
                    hFile.write(arrayOut)
                    print('writing to file')

                 
                

                #build up arrays for plotting
                allTime = numpy.append(allTime, elapsedTime)
                allAmbientGetTemp = numpy.append(allAmbientGetTemp, currentAmbient)
                ambientTemps = numpy.append(ambientTemps, ambientSetTemp)
                
                
                plt.figure(1)
                plt.plot(allTime, allAmbientGetTemp, linestyle='dashed', marker='o', color =  'b')
                
                plt.plot(allTime, ambientTemps, 'r')
                #plt.plot(1, 1)
                plt.xlabel("Time (seconds)")
                plt.ylabel("Ambient Temp")
                plt.draw()
                plt.pause(0.01)
                hFig.savefig(fileNameFigure, dpi=hFig.dpi)
            
                currentAmbientDurationS = ambientDwellClock.tocvalue()
                currentAmbientDurationMins = float(currentAmbientDurationS)/60
                
                time.sleep(measurmentInterval)

                
                #print("Current ambient elapsed time_ Mins" + str(currentAmbientDurationMins))
                #print("Dwell time_" + str(ambientDwellMins))

#Set the ambient Set point
thermotron.setSetpoint(ambientStartTemp) 
time.sleep(1)
thermotron.run()
time.sleep(1)
thermotron.stop()
        
print('Finished')



    






