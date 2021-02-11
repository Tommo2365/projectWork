import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import pandas as pd
from CSVRead import CSVRead
from MovingAverageConvolve import MovingAverageConvolve
#from SimSquareWave import SimSquareWave

#Define File name to read the data from
fileName = 'C:\\Data\\PicoLog\\CSV Ambient test of boards original orientation repeated.csv'
fileName =  'Z:\\VERSION 10 (C390)\\Physics\\Work Area\Heimann compensation combination\\Response Time Data\\picologger revisited dec 2019\\Aperture Internal filter\\D 100cm gain 5 response test internal filter aperture.csv'
print(fileName)

#Read in the csv file as an numpy array of strings
bHeader = True
csvData, header = CSVRead(fileName,bHeader,0)

#Pull out the column headers
columnHeaders = csvData[0]

#Find the numnber of rows of numeric data
numDataRows = len(csvData) -1

#Pull out the data
data = csvData[1:numDataRows]

#TimeData
timeData = data[:,0]

#CompData
CompSignalData = data[:,1]
CompSignalDataFloat = CompSignalData.astype('float')

#Signal Data
SignalData = data[:,2]
SignalDataFloat = SignalData.astype('float')

##Thermistor Data
#ThermistorData = data[:,4]
#ThermistorDataFloat = ThermistorData.astype('float')

#Extract Signal Data column and convert to float
MathSignalData = data[:,3]
MathSignalDataFloat = MathSignalData.astype('float')

#Plot the original signals
plt.plot(SignalDataFloat)
plt.plot(CompSignalDataFloat)
plt.ylabel('Signal (V)')
plt.show()

#Try some filtering
filteredData = MovingAverageConvolve(CompSignalDataFloat, 10, True)

gainStart = float(3)
gainEnd = float(7)
numberOfGains = 20
gainStep = float((gainEnd-gainStart)/numberOfGains)

print(CompSignalDataFloat)
#thisGain= np.array([])
arrayOfGains= np.array([])
arrayOfStdevs = np.array([])
#mySquareWave = SimSquareWave(input1, input2, ..)
for k in range(0,numberOfGains):
    thisGain = gainStart+ k*gainStep
    arrayOfGains = np.append(arrayOfGains, thisGain)
    
    print(thisGain)
    correctedSignal = SignalDataFloat-thisGain*CompSignalDataFloat
    correctedSignalPlot = correctedSignal/np.median(correctedSignal)
    thisStdev = np.std(correctedSignalPlot)
    arrayOfStdevs = np.append(arrayOfStdevs, thisStdev)
    print(correctedSignal)
    plt.plot(correctedSignalPlot)
    plt.plot(PerfectSignalDataFloat)
    plt.show()
    
    
    #stdev = 
    arrayOfStdevs = np.append(stdev, arrayOfStdevs)
plt.plot(arrayOfGains, arrayOfStdevs)
plt.show()
#plt.plot(SimSquareWave)

    

