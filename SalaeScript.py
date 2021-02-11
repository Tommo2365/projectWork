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
measurementTime = int(1200)
#measurementTime = int(120)
pauseDuration = float(0)
sampleRate = 1e3*float(125)
sampleDurationMs = float(100)
NRepeats = int(5)
nDataPoints = 500
        

#Constants
host='localhost'
port=10429
chopperFreq = 340
sampleTime = 1/sampleRate
digitalChannelList = []
analogChannelList = [2,3]
lowCut = 100
highCut = 3e3

config = configparser.ConfigParser()
config.read('etc/config/config.ini')

##Initialize the ambient chamber
thermotron = s2200(config['thermotron'])#initialise the ambinet chamber
thermotron = s2200(config['thermotron'])#initialise the ambinet chamber
#ambientGetTemp = []
#ambientSetTemp = []
#allAmbientGetTemp = []
#allAmbientSetTemp = []
#rampEveryMins = float(180)
#ambientRampInterval = float(10)
#startTemp = float(30)
#ambientGetTemp = thermotron.getProcessVariable()
#ambientSetTemp = startTemp




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




# initalize Salae Drive
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

#Build folder timestmap structure
folder = "C:\\Data"
now = datetime.now() 
timestamp = now.strftime("%Y%m%d_%H_%M_%S")
fileName =  folder + "/" +  timestamp + serialNumberString + "_" +str(measurementTime) + "_"  + "Data.csv"
fileNameStats =  folder + "/" +  timestamp + serialNumberString + "_" +str(measurementTime) + "_"  + "DataStats.csv"

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

#start the clock
t.tic() #Start timer

with open(fileName, 'w') as hFile: # Use hfile to refer to the file object

        #UI user input
    fieldNames2 = ["FurnaceTemp" ,"AmbientTemp"]
    fieldValues2 = list(multenterbox(msg='Fill in values for the fields.', title='Enter', fields=(fieldNames2)))
    furnaceTempString = fieldValues2[0]
    ambientTempString = fieldValues2[1]
    count = 0

    while (elapsedTime < measurementTime):
        #plt.clf()

        count = count +1
        
        for k in range(0, NRepeats):
            
            #Capture Data from Salae drive
            print("Starting a capture")
            # Also consider capture_start_and_wait_until_finished for non-demo apps
            s.capture_start()
            while not s.is_processing_complete():
                print("\t..waiting for capture to complete")
                time.sleep(1)
            print("Capture complete")
            saveFileNameRawData = fileNameRawDataPrefix + "FurnaceTemp_"+ furnaceTempString + str(k) + ".csv"
            

            #Save raw data to csv
            print('exporting data to ' + saveFileNameRawData)
            s.export_data2(saveFileNameRawData)
            print("capture complete.")
            time.sleep(1)

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

            #Signal Data
            signalData = csvData[:,2]
            signalData = signalData.astype('float')

            #thermistor signal
            thermistorsignal = csvData[:,1]
            thermistorsignal = thermistorsignal.astype('float')
            thermistorsignal = thermistorsignal*100
            thermistorsignal = np.median(thermistorsignal)


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

            elapsedTime = t.tocvalue()
            elapsedTime = float(elapsedTime)

            arrayOut = str(elapsedTime) + ","  + str(furnaceTempString) + ","  + str(thermistorsignal) + "," + str(signalFAmp) + "," + str(signalFourierAmplitude) + '\n'
           # arrayOut = str(elapsedTime) + ","  + str(furnaceTempString) + ","   + str(signalFAmp) + "," + str(signalFourierAmplitude) + '\n'
           # arrayOut = str(elapsedTime) + ","  + str(numpyThisT) + "," + str(currentAmbient) + "," + str(ambientSetTemp) +  '\n'
            hFile.write(arrayOut)

            peakToPeakSignal = 2*np.mean(numpyAllFourierSignal)
            peakToPeakNoise = 2*np.std(numpyAllFourierSignal)
            signalToNoise = peakToPeakSignal/peakToPeakNoise



            allTime.append(elapsedTime)
          
            plt.figure(1)
            plt.plot(allTime, numpyAllFourierSignal, linestyle='dashed', marker='o', color =  'b')
            plt.xlabel("Time (seconds)")
            plt.ylabel("rms signal mV")
            plt.draw()
            plt.pause(0.01)
            plt.legend(["Stdev: " + str(peakToPeakNoise)])

            hFig.savefig(fileNameFigure, dpi=hFig.dpi)

            print(count)

    with open(fileNameStats, 'w') as hFile2: # Use hfile to refer to the file object
        statsOut = "TotalTime(s)" + ","  + "meanPeakToPeak" + ","  + "stdev peak to peak" + "," "SN Ratio"  + '\n'
        hFile2.write(statsOut)
        statsOut = str(elapsedTime) + ","  + str(peakToPeakSignal) + ","  + str(peakToPeakNoise) + "," + str(signalToNoise) + '\n'
        hFile2.write(statsOut)



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



