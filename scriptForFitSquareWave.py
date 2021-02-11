import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import pandas as pd
from CSVRead import CSVRead
from MovingAverageConvolve import MovingAverageConvolve
from SimSineWave import SimSineWave
from SimPulseWave import SimPulseWave
from SimSquareWaveEquation import SimSquareWaveEquation
from SimSquareWaveEquationFixed import SimSquareWaveEquationFixed
from scipy import optimize
import os


#Define File name to read the data from
#fileName = 'C:\\Data\\PicoLog\\CSV Ambient test of boards original orientation repeated.csv'
#fileName =  'Z:\\VERSION 10 (C390)\\Physics\\Work Area\Heimann compensation combination\\Response Time Data\\picologger revisited dec 2019\\Aperture Internal filter\\D 100 cm gain tbd, no aperture internal filter.csv'
#fileName = 'Z:\\VERSION 10 (C390)\\Physics\\Work Area\\Heimann compensation combination\\Response Time Data\\picologger revisited dec 2019\\External filter\\D 100cm gain 3 repeat fast hand removal.csv'
folderName = 'C:\Data'
fileID = '20200722_12_35_12DualBoardV3C_130_Data.csv'

folderNamePath = os.path.normpath(folderName)

fileName = folderNamePath + '\\' + fileID



fileNameFigure =  folderNamePath + "\\"  +fileID +"_"+ "GainCal.png"
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
CompSignalData = data[:,2]
CompSignalDataFloat = CompSignalData.astype('float')
CompSignalDataFloat = CompSignalDataFloat - np.min(CompSignalDataFloat[:])
#CompSignalDataFloat = CompSignalDataFloat/np.max(CompSignalDataFloat[:])

#Signal Data
SignalData = data[:,1]
SignalDataFloat = SignalData.astype('float')
SignalDataFloat = SignalDataFloat - np.min(SignalDataFloat[:])
#SignalDataFloat = SignalDataFloat/np.max(SignalDataFloat[:])

##Thermistor Data
#ThermistorData = data[:,4]
#ThermistorDataFloat = ThermistorData.astype('float')

#Extract Signal Data column and convert to float
MathSignalData = data[:,3]
MathSignalDataFloat = MathSignalData.astype('float')


#Filter the dta to remove noise and calculate to gradient of the data
filteredData = MovingAverageConvolve(SignalDataFloat, 3, True)
gradientData = np.gradient(filteredData)


#Find the FWHM using the maximum and minimum of the gradients
minIndex = np.where(gradientData == gradientData.min())[0]
minIndex = minIndex[0]
maxIndex = np.where(gradientData == gradientData.max())[0]
maxIndex = maxIndex[-1]
FWHM = int(maxIndex-minIndex)

#For plotting points of FWHM
maxData = np.max(SignalDataFloat[:])
yAverage= maxData/2

#Use the symetry and FWHM of the dip to find the indices to crop the data
startCropIndex= int(minIndex-np.round(FWHM/2))
endCropIndex = int(maxIndex + np.round(FWHM/2))

#Normalize the data by the median value of amplitude of the dip
normFactorStart = np.median(SignalDataFloat[startCropIndex-FWHM:startCropIndex])
normFactorEnd = np.median(SignalDataFloat[endCropIndex:endCropIndex+FWHM])
normFactor = np.mean([normFactorStart,normFactorEnd])
#SignalDataFloat = SignalDataFloat/normFactor

#Normalize the comp data
normFactorStartComp = np.median(CompSignalDataFloat[startCropIndex-FWHM:startCropIndex])
normFactorEndComp = np.median(CompSignalDataFloat[endCropIndex:endCropIndex+FWHM])
normFactorComp = np.mean([normFactorStartComp,normFactorEndComp])
#CompSignalDataFloat = CompSignalDataFloat/normFactorComp
#CompSignalDataFloat = CompSignalDataFloat

#Crop the data down to be centred on the dip
croppedData = SignalDataFloat[startCropIndex:endCropIndex]
croppedDataComp = CompSignalDataFloat[startCropIndex:endCropIndex] 


nDataPoints = (endCropIndex-startCropIndex)
xData = np.linspace(0, nDataPoints, num=nDataPoints)
nHarmonics = int(nDataPoints/2)
bPlot = True
phaseOffset = -nDataPoints/4
amplitude = normFactor
simData = SimSquareWaveEquation(xData, FWHM,  nHarmonics, phaseOffset ,amplitude)
plt.plot(croppedData, 'x')
plt.plot(simData)
plt.plot(croppedDataComp, 'x')
plt.legend(["original data", "simulated square", "second thermopile signal"])
plt.show()


minimumGain = 0
maximumGain = 10
gainStep = 0.01


def FindGainFactor(simData, croppedData, croppedDataComp, minimumGain, maximumGain , gainStep, amplitude):
    nGains = int(round((maximumGain-minimumGain)/gainStep))
    allRms = np.array([])
    gainFactor = minimumGain
    allGains = np.array([])


    for w in range(0, nGains+1):
        gainFactor = minimumGain + w*gainStep
        compWave =  croppedData - (gainFactor*croppedDataComp)
        compWaveAboveThreshIndices = np.where(compWave >= 0.75*np.max(compWave))[0]
        compWaveAmplitudes = compWave[compWaveAboveThreshIndices]
        compWaveAmplitude = np.median(compWaveAmplitudes)
        compWave = compWave/compWaveAmplitude

        compWave = amplitude*compWave

        differenceWave = abs(simData-compWave)
        rms = np.sum(differenceWave)
        allRms = np.append(allRms, rms)#append the array
        allGains= np.append(allGains, gainFactor)
        #plt.plot(compWave)
        #plt.plot(simData)
        
        #plt.legend(["Gain " + str(gainFactor)])
        #plt.show()
    #gainFactor = np.min(allRms)
    #gainFactor = np.mean(gainFactor[:])
    gainOutIndex = np.where(allRms == np.min(allRms[:]))[0]
    gainOutIndex = gainOutIndex[0]
    gainOut = allGains[gainOutIndex]
    compWave = croppedData - (gainOut*croppedDataComp)
    compWaveAboveThreshIndices = np.where(compWave >= 0.75*np.max(compWave))[0]
    compWaveAmplitudes = compWave[compWaveAboveThreshIndices]
    compWaveAmplitude = np.median(compWaveAmplitudes)
    compWave = compWave/compWaveAmplitude

    compWaveOut = amplitude*compWave

    #plt.plot(allRms)
    #plt.show()
    return gainOut, compWaveOut

gainOut, compWaveOut = FindGainFactor(simData, croppedData, croppedDataComp, minimumGain, maximumGain , gainStep, amplitude)

params, params_covariance = optimize.curve_fit(SimSquareWaveEquationFixed, xData,compWaveOut,  p0=[FWHM, phaseOffset, amplitude])

fitWave = SimSquareWaveEquation(xData, round(params[0]),  nHarmonics, round(params[1]) ,round(params[2]))
simData = SimSquareWaveEquation(xData, FWHM,  nHarmonics, phaseOffset ,amplitude)

hFig = plt.figure()
plt.plot(croppedData, 'x')
plt.plot(compWaveOut, 'x')
plt.plot(simData)
#plt.plot(croppedData)
#plt.plot(fitWave)

plt.legend(["original data", ["corrected signal Gain_" + str(gainOut)],"simulated square"])
plt.show()
hFig.savefig(fileNameFigure, dpi=hFig.dpi)


