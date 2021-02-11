import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import pandas as pd
from CSVRead import CSVRead
from MovingAverageConvolve import MovingAverageConvolve
from Fft import Fft
from BandPassFilter import BandPassFilter




#from SimSquareWave import SimSquareWave

#Define File name to read the data from
#fileName = 'I:\\physics\\Non Project Work\\3-5 System V\\Experimental Data\\Board V2\\Salae logged data\\40 degrees 25V ref\\data1.csv'
fileName= 'I:\\physics\\Non Project Work\\3-5 System V\\Experimental Data\\Board V2\\Salae logged data\\Ambient Dep\\25V\\Test\\test.csv'
fileName = 'I:\\physics\\Non Project Work\\3-5 System V\\Experimental Data\\Board V2\\Salae logged data\\Test\\test.csv'
print(fileName)

#Inputs
chopperFreq = 340

#Read in the csv file as an numpy array of strings
bHeader = True
nHeaderRows =2
csvData, header = CSVRead(fileName,bHeader, nHeaderRows)

#Pull out the column headers
columnHeaders = csvData[nHeaderRows]

#Find the numnber of rows of numeric data
numDataRows = len(csvData) -1


#TimeData
timeData = csvData[:,0]
timeData = timeData.astype(float)

#Signal Data
signalData = csvData[:,1]
signalData = signalData.astype('float')
lowCut = 100
highCut = 3e3
sampleFrequency = 125000
order = 3
bWindowData = False
fData = BandPassFilter(signalData, lowCut, highCut, sampleFrequency, order, bWindowData)
plt.close()


##Plot the original signals
#plt.plot(1e3*timeData, signalData, label='Original Data')
#plt.plot(1e3*timeData, fData,label='filtered Data')
#plt.ylabel('Signal (V)')
#plt.xlabel('time (ms)')
#plt.axis([0,10, -0.05, 0.05])
#plt.legend(loc='best')
#plt.show()
#plt.close()

sampleTime = 8e-6

powerSig, frequency = Fft(fData, False, sampleTime)
plt.axis([0, 1e3, -10, 10])

diffFreq = abs(frequency[:]-float(chopperFreq))
chopperFreqIndex = np.argmin(diffFreq)

#find the peak near the chopper frequency
chopperBandwidthAU = 10
subBand = powerSig[chopperFreqIndex-chopperBandwidthAU:chopperFreqIndex+chopperBandwidthAU]
maxComponent = np.max(subBand)
maxIndex = np.argmax(subBand)
signalFourierAmplitude = subBand[maxIndex]


meanSignal = np.mean(signalData)
signalDataN = signalData - meanSignal
signalDataN = np.asarray(signalDataN)
signalDataSquare = signalDataN*signalDataN
meanSignalDataSquare = np.mean(signalDataSquare)
rmsSignal = np.sqrt(meanSignalDataSquare)
signalAmp = np.sqrt(2)*rmsSignal*1e3

meanFSignal = np.mean(fData)
signalFDataN = fData - meanFSignal
signalFDataN = np.asarray(signalFDataN)
signalFDataSquare = signalFDataN*signalFDataN
meanSignalFDataSquare = np.mean(signalFDataSquare)
rmsFSignal = np.sqrt(meanSignalFDataSquare)
signalFAmp = np.sqrt(2)*rmsFSignal*1e3


print(signalFourierAmplitude)
print(signalAmp)

# Creates two subplots and unpacks the output array immediately
f, (ax1, ax2) = plt.subplots(1, 2)

ax1.plot(frequency,np.log(powerSig), 'xk', label="power = %d" % signalFourierAmplitude)  
ax1.plot(frequency,np.log(powerSig))  
ax1.set_xlabel("Frequency (1/NPixels)", fontsize=12)
ax1.set_ylabel("Log Power (a.u.)", fontsize=12)
#ax1.axis([0, 1e3, -10, 20])
ax1.set_title('Power spectrum')
ax1.legend(loc='best')
ax1.set_xlim([0, 1e3])
ax1.set_ylim([-10, 20])


#Plot the original signals
ax2.plot(1e3*timeData, 1e3*signalData, label="rms = %d" % signalAmp)
ax2.plot(1e3*timeData, 1e3*fData,label="rms = %d" % signalFAmp)
ax2.set_ylabel('Signal (V)',fontsize=12)
ax2.set_xlabel('time (ms)',fontsize=12)
#ax2.axis([0,10, -0.05, 0.05])
ax2.legend(loc='best')
ax2.set_xlim([0, 10])
ax2.set_ylim([-100, 100])



a =5









   

