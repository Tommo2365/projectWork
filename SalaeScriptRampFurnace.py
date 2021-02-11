import configparser
import argparse
import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import pandas as pd
from CSVRead import CSVRead
from Fft import Fft
from BandPassFilter import BandPassFilter
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
import easygui
from easygui import msgbox, multenterbox
try:
    from LAND_comms_equipment.thermotron import s2200
except:
    from thermotron import s2200
import math

from eurothermModbus import s2000Modbus

#Imports from Salae
import sys
import matplotlib.pyplot as plt
import csv
import pandas as pd
import pandas as pd
import saleae
import bisect
import contextlib
import enum
import inspect
import os
import platform
import psutil
import shutil
import socket
import sys
import time
import warnings


#UI user input
#fieldNames = ["Prefix" ,"MeasurementDurarationHours", "pauseDurationMins", "sampleRateKhz", "sampleDurationMs", "NRepeats"]
#fieldValues = list(multenterbox(msg='Fill in values for the fields.', title='Enter', fields=(fieldNames)))
#serialNumberString = fieldValues[0]
#measurementTime = int(3600*float(fieldValues[1]))
#pauseDuration = float(fieldValues[2])
#sampleRate = 1e3*float(fieldValues[3])
#sampleDurationMs = float(fieldValues[4])
#NRepeats = int(fieldValues[5])
#nDataPoints = 500
serialNumberString = 'test'
measurementTime = int(120)
maxAmbient = float(60)
maxFurnaceTemp = 80
furnaceStartTemp = 20
#measurementTime = int(120)
pauseDuration = float(0)
sampleRate = 1e3*float(125)
sampleDurationMs = float(100)
NRepeats = int(5)
nDataPoints = 500
n100msSamples = 100
        

#Constants
host='localhost'
port=10429
chopperFreq = 340
sampleTime = 1/sampleRate
digitalChannelList = []
analogChannelList = [2,3, 1]
lowCut = 100
highCut = 3e3

config = configparser.ConfigParser()
config.read('etc/config/config.ini')

##Initialize the ambient chamber
thermotron = s2200(config['thermotron'])#initialise the ambinet chamber
#thermotron = s2200(config['thermotron'])#initialise the ambinet chamber
ambientGetTemp = numpy.array([])
ambientSetTemp = numpy.array([])
allAmbientGetTemp = numpy.array([])
allAmbientSetTemp = numpy.array([])

rampEveryMins = float(30)
ambientRampInterval = float(1)
startTemp = float(30)
ambientGetTemp = thermotron.getProcessVariable()
ambientSetTemp = startTemp




#Initialize the black body
eurothermModbus = s2000Modbus(config['eurothermModbus'])
furnaceGetTemp = eurothermModbus.getProcessVariable()
furnaceSetTemp = furnaceGetTemp
 



#Intialize loop variables
numpyAllSignal = numpy.array([])
numpyThisSignal = numpy.array([])
numpyAllFourierSignal = numpy.array([])
numpyThisFourierSignal = numpy.array([])
numpyAllMins = numpy.array([0])
numpyTimeAxis = numpy.array([nDataPoints])
allTime = []
allElapsedTimeMins = float(0)
elapsedTime = float(0)
allFurnaceGetTemp = numpy.array([])
allFurnaceSetTemp = numpy.array([])




# # initalize Salae Drive
# print("Running Saleae connection.\n")
# s = saleae.Saleae(host, port)
# print("Saleae connected.")
# devices = s.get_connected_devices()
# print("Connected devices")
# for device in devices:
#     print("\t{}".format(device))
# print("Setting active channels (digital={}, analog={})".format(digitalChannelList, analogChannelList))
# s.set_active_channels(digitalChannelList, analogChannelList)
# digital, analog = s.get_active_channels()
# print("Reading back active channels:")
# print("\tdigital={}\n\tanalog={}".format(digital, analog))
# sampleRateKHz = sampleRate/1e3
# sampledurationS = sampleDurationMs/1e3
# nSamples = sampleRate*sampledurationS
# print('Setting to capture 2e6 samples' +str(nSamples))
# s.set_num_samples(nSamples)
# #input("Press Enter to continue...\n")
# print('Setting to sample rate to at  digitial __, ' + 'analogue' + str(sampleRateKHz))
# rate = s.set_sample_rate_by_minimum(4e6, sampleRate)
# print("\tSet to", rate)
# #input("Press Enter to continue...\n")

#Build folder timestmap structure
folder = "C:\\Data"
now = datetime.now() 
timestamp = now.strftime("%Y%m%d_%H_%M_%S")
fileName =  folder + "/" +  timestamp + serialNumberString + "_" +str(measurementTime) + "_"  + "Data.csv"
fileNameStatsPrefix =  folder + "/" +  timestamp + serialNumberString + "_" 

fileNameRawDataPrefix = folder + "/" +  timestamp + serialNumberString + "_" +str(measurementTime) + "_"  + "ACSignal_"
fileNameFigure =  folder + "/" + timestamp + "SignalData.png"
fileNameFigure2 =  folder + "/" + timestamp + "FurnaceTemp.png"
print(timestamp)
print(fileName)


#Setup clock structure
t = TicToc()

# Creates two subplots and unpacks the output array immediately
#hFig1, (ax1, ax2) = plt.subplots(1, 2)

hFig = plt.figure()
plt.ion()
plt.ylabel('Temp')
#hFig2 = plt.figure()
#plt.ion()
# plt.show()


count = 0

with open(fileName, 'w') as hFile: # Use hfile to refer to the file object

    #UI user input
    fieldNames2 = ["FurnaceTemp" ,"Ambient Start Temp", "N Ambient Temps", "Ambient Step Temp", "ambient Dwell Time Mins", "Total Duration Hours"]
    fieldValues2 = list(multenterbox(msg='Fill in values for the fields.', title='Enter', fields=(fieldNames2)))
    
    #furnace Temp
    furnaceTempString = fieldValues2[0]

    ambientFurnaceDiffTemp = float(20)
	
    #Ambient Conditions
    ambientTempString = fieldValues2[1]
    ambientStartTemp = float(ambientTempString)
    
    nAmbientString = fieldValues2[2]
    nAmbient = int(nAmbientString) 
    
    ambientStepString = fieldValues2[3]
    ambientStep = int(ambientStepString)

    ambientDwellMinsString = fieldValues2[4]
    ambientDwellMins = int(ambientDwellMinsString)

    totalDurationHoursString = fieldValues2[5]
    totalDurationHours = float(totalDurationHoursString)

    #Lon winded non pythonean way of making an array!!
    for n in range(0, nAmbient ):
        thisValue =ambientStartTemp + n*ambientStep
        allAmbientSetTemp =numpy.append(allAmbientSetTemp, thisValue)
    print(allAmbientSetTemp) 
    
    
    
	#start the clock
    t.tic() #Start timer
    elapsedTimeHours = 0
    

    
    # while loop that aborts the program after a designated number of hours - to shutdown overnight for example
    while (elapsedTimeHours < totalDurationHours):
        fileNameStats = fileNameStatsPrefix + str(ambientSetTemp) + "Count" + str(count) + "DataStats.csv" 
        with open(fileNameStats, 'w') as hFile2: # Use hfile to refer to the file object

            if(count == 0):
                statsOut = "TotalTime(s)" + ","  + "meanPeakToPeak" + ","  + "stdev peak to peak"  + "," + "SN Ratio" + ","  + "ambient Temp" + "," + "furnace Temp" + "," + "ThermistorTemp" + "," + "mean DC" +'\n'
                hFile2.write(statsOut)

            count = count + 1

            for n in range(0, nAmbient ):
            	#initalize Salae Drive
                print("Running Saleae connection.\n")
                s = saleae.Saleae(host, port)
                print("Saleae connected.")
                devices = s.get_connected_devices()
                print("Connected devices")
                for device in devices:
                	print("\t{}".format(device))
				
                
                print("Setting active channels (digital={}, analog={})".format(digitalChannelList, analogChannelList))
                s.set_active_channels(digitalChannelList, analogChannelList)
                digital, analog = s.get_active_channels()
                print("Reading back active channels:")
                print("\tdigital={}\n\tanalog={}".format(digital, analog))
                sampleRateKHz = sampleRate/1e3
                sampledurationS = sampleDurationMs/1e3
                nSamples = sampleRate*sampledurationS
                print('Setting to capture 2e6 samples' +str(nSamples))
                s.set_num_samples(nSamples)
                #input("Press Enter to continue...\n")
                print('Setting to sample rate to at  digitial __, ' + 'analogue' + str(sampleRateKHz))
                rate = s.set_sample_rate_by_minimum(4e6, sampleRate)
                print("\tSet to", rate)
                #input("Press Enter to continue...\n")
				
				
                numpyAllSignal = numpy.array([])
                numpyThisSignal = numpy.array([])
                numpyAllFourierSignal = numpy.array([])
                numpyThisFourierSignal = numpy.array([])
                allTime = []
                numpyAllthermistorSignal = numpy.array([])
                numpyAllDCSignal = numpy.array([])
				
                
                #Get the current ambient set point from the list
                ambientSetTemp = allAmbientSetTemp[n]
                print("Setting ambient to" + str(ambientSetTemp))
                if ambientSetTemp > maxAmbient:
                    ambientSetTemp = ambientStartTemp
                    if ambientStartTemp > maxAmbient:
                        ambientSetTemp = 23
				
				#Set the furnace to be offset from the ambient
                bOffsetFurnace = True
                if bOffsetFurnace == True:
                	furnaceSetTemp = allAmbientSetTemp[n]+ ambientFurnaceDiffTemp
                	if furnaceSetTemp > maxFurnaceTemp:
                		furnaceSetTemp = furnaceStartTemp
                	eurothermModbus.setSetpoint(furnaceSetTemp)
                	time.sleep(1)
                	try:
                		currentFurnaceSet = eurothermModbus.getSetpoint()
                		time.sleep(1)
                	except ValueError:
                		print("Error Reading Eurotherm set point: caught in value error")
                		continue
                	if currentFurnaceSet == False:
                		print("Error Reading Eurotherm set point: set point returns empty")
                		continue

                
                #Set the ambient Set point
                thermotron.setSetpoint(ambientSetTemp) 
                time.sleep(1)
                thermotron.run()
                time.sleep(1)
                print("Dwelling for_" +  str(ambientDwellMins) + "_Mins")
                time.sleep(ambientDwellMins*60)
                print("Dwelling complete")

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
                
                if bOffsetFurnace == True:
                	try:
                		currentFurnace = eurothermModbus.getProcessVariable()
                		time.sleep(1)
                	except ValueError:
                		print("Error Reading Eurotherm set point: caught in value error")
                		continue
                	if currentFurnace == False:
                		currentFurnace = 22
                		print("Error Reading Eurotherm set point: set point returns empty")
                		continue


                
                setPointValue = float(thermotron.getSetpoint())
                if setPointValue != ambientSetTemp:
                    print("FAILURE IN SETPOINT")
                else:
                    print("Ambient SetPoint set to" + str(setPointValue))

                print("Ambient Temp gpv is" + str(currentAmbient))


                for m in range(0,n100msSamples):#number of 100ms measureents to record

                    

                    count = count +1
                    print("Begin of ambient repeat" + str(count))
                    
                    #for k in range(0, NRepeats):
                        
                    #Capture Data from Salae drive
                    print("Starting a capture")
                    # Also consider capture_start_and_wait_until_finished for non-demo apps
                    s.capture_start()
                    while not s.is_processing_complete():
                        print("\t..waiting for capture to complete")
                        time.sleep(1)
                    print("Capture complete")
                    saveFileNameRawData = fileNameRawDataPrefix + "FurnaceTemp_"+ str(currentFurnaceSet) +"AmbientTemp_" + str(setPointValue)   + ".csv"
                    

                    #Save raw data to csv
                    print('exporting data to ' + saveFileNameRawData)
                    s.export_data2(saveFileNameRawData)
                    print("capture complete.")
                    time.sleep(1)

                    print("calculating filtered signal amplitude")
                    #Read in the csv file as an numpy array of strings
                    bHeader = True
                    nHeaderRows =2
                    csvData, header = CSVRead(saveFileNameRawData,bHeader, nHeaderRows)

                    


                    #Pull out the column headers
                    columnHeaders = csvData[nHeaderRows]

                    #Find the numnber of rows of numeric data
                    numDataRows = len(csvData) -1


                    #TimeData
                    timeData = csvData[:,0]
                    timeData = timeData.astype(float)

					#DC Signal Data
                    dCData = csvData[:,1]
                    dCData = dCData.astype('float')
                    dCData =  np.median(dCData)


                    #Signal Data
                    signalData = csvData[:,3]
                    signalData = signalData.astype('float')

                    #thermistor signal
                    thermistorsignal = csvData[:,2]
                    thermistorsignal = thermistorsignal.astype('float')
                    thermistorsignal = thermistorsignal*100
                    thermistorsignal = np.median(thermistorsignal)

                    #thermistorAverage = np.mean(thermistorsignal)


                    #Filter the data
                    order = 3
                    bWindowData = False
                    bPlotFilter = False
                    fData = BandPassFilter(signalData, lowCut, highCut, sampleRate, order, bWindowData, bPlotFilter)
                    powerSig, frequency = Fft(fData, False, sampleTime)

                    #find the peak near the chopper frequency
                    diffFreq = abs(frequency[:]-float(chopperFreq))
                    chopperFreqIndex = np.argmin(diffFreq)
                    chopperBandwidthAU = 10
                    subBand = powerSig[chopperFreqIndex-chopperBandwidthAU:chopperFreqIndex+chopperBandwidthAU]
                    maxComponent = np.max(subBand)
                    maxIndex = np.argmax(subBand)
                    #signalFourierAmplitude = subBand[maxIndex]- ((subBand[maxIndex-1] +subBand[maxIndex+1])/2)
                    signalFourierAmplitude = subBand[maxIndex]

                    #Calculate the RMS signal
                    meanSignal = np.mean(signalData)
                    signalDataN = signalData - meanSignal
                    signalDataN = np.asarray(signalDataN)
                    signalDataSquare = signalDataN*signalDataN
                    meanSignalDataSquare = np.mean(signalDataSquare)
                    rmsSignal = np.sqrt(meanSignalDataSquare)
                    signalAmp = np.sqrt(2)*rmsSignal*1e3

                    #Calculate the Fourier Signal
                    meanFSignal = np.mean(fData)
                    signalFDataN = fData - meanFSignal
                    signalFDataN = np.asarray(signalFDataN)
                    signalFDataSquare = signalFDataN*signalFDataN
                    meanSignalFDataSquare = np.mean(signalFDataSquare)
                    rmsFSignal = np.sqrt(meanSignalFDataSquare)
                    signalFAmp = np.sqrt(2)*rmsFSignal*1e3



                    print(signalFourierAmplitude)
                    print(signalAmp)

                    numpyAllSignal = numpy.append(numpyAllSignal, signalAmp)
                    numpyAllFourierSignal = numpy.append(numpyAllFourierSignal, signalFAmp)
                    numpyAllthermistorSignal = numpy.append(numpyAllthermistorSignal, thermistorsignal)
                    numpyAllDCSignal = numpy.append(numpyAllDCSignal, dCData)

                    elapsedTime = t.tocvalue()
                    elapsedTime = float(elapsedTime)
                    elapsedTimeHours = elapsedTime/3600

                    print("Writing to csv file " + str(fileName) )
                    arrayOut = str(elapsedTime) + ","  + str(currentFurnace) + "," + str(ambientSetTemp) + ","  + str(thermistorsignal) + "," + str(dCData) + "," + str(signalFAmp) + '\n'

                    hFile.write(arrayOut)

                    peakToPeakSignal = 2*np.mean(numpyAllFourierSignal)
                    peakToPeakNoise = 2*np.std(numpyAllFourierSignal)
                    signalToNoise = peakToPeakSignal/peakToPeakNoise
                    averageThermistor = np.mean(numpyAllthermistorSignal)
                    averageDC= np.mean(numpyAllDCSignal)



                    allTime.append(elapsedTime)
                
                    plt.figure(1)
                    plt.plot(allTime, numpyAllDCSignal, linestyle='dashed', marker='o', color =  'b')
                    plt.xlabel("Time (seconds)")
                    plt.ylabel("rms signal mV")
                    plt.draw()
                    plt.pause(0.01)
                    plt.legend(["Stdev: " + str(peakToPeakNoise)])

                    hFig.savefig(fileNameFigure, dpi=hFig.dpi)

                    print(count)

                
        
                #fileNameStats = fileNameStatsPrefix + str(ambientSetTemp) + "Count" + str(count) + "DataStats.csv" 
                #with open(fileNameStats, 'w') as hFile2: # Use hfile to refer to the file object
                print("Writing Stats to" + str(fileNameStats))
                 
                statsOut = str(elapsedTime) + ","  + str(peakToPeakSignal) + ","  + str(peakToPeakNoise) + "," + str(signalToNoise) + "," + str(ambientSetTemp) + "," + str(furnaceSetTemp) + "," + str(averageThermistor) + "," + str(averageDC)+  '\n'
                hFile2.write(statsOut)

                print("closing Salae connection")
                s.kill_logic(True)
                print("Salae connection closed")
                time.sleep(20)
				
				



    exit(0)

        
            
          


            #ax1.plot(frequency,np.log(powerSig), 'xk', label="power = %d" % signalFourierAmplitude)  
            #ax1.plot(frequency,np.log(powerSig))  
            #ax1.set_xlabel("Frequency (1/NPixels)", fontsize=12)
            #ax1.set_ylabel("Log Power (a.u.)", fontsize=12)
            ##ax1.axis([0, 1e3, -10, 20])
            #ax1.set_title('Power spectrum')
            #ax1.legend(loc='best')
            #ax1.set_xlim([0, 1e3])
            #ax1.set_ylim([-10, 20])


            ##Plot the original signals
            #ax2.plot(1e3*timeData, 1e3*signalData, label="rms = %d" % signalAmp)
            #ax2.plot(1e3*timeData, 1e3*fData,label="rms = %d" % signalFAmp)
            #ax2.set_ylabel('Signal (V)',fontsize=12)
            #ax2.set_xlabel('time (ms)',fontsize=12)
            ##ax2.axis([0,10, -0.05, 0.05])
            #ax2.legend(loc='best')
            #ax2.set_xlim([0, 10])
            #ax2.set_ylim([-100, 100])




   
                
            #plt.figure(1)
            #if count < nDataPoints:
            #    plt.axis([0,measurementTime,yLimDown,yLimUp])
            #else:
            #    plt.axis([allTime[0],allTime[len(allTime)-1],yLimDown,yLimUp])



