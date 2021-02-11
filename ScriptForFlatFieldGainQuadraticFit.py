import numpy
import numpy as np
import matplotlib.pyplot as plt
import csv
from CSVRead import CSVRead
from CSVWrite import CSVWrite
from GetFileNames import GetFileNames
from QuadraticFit import QuadraticFit
from NearestNeighbourAverage import NearestNeighbourAverage
#from Convolve2DKernal import Convolve2DKernal
from RemoveHotPixels import RemoveHotPixels
import cv2
from tkinter import filedialog
from tkinter.filedialog import askdirectory
from tkinter import *
import os
import re
from cv2_rolling_ball import subtract_background_rolling_ball
from astropy.stats import sigma_clip
from scipy import ndimage
from skimage.measure import profile_line
from skimage import io
from LineProfile import LineProfile
from Fft import Fft
from QuadraticFit import QuadraticFit

allPixelTemps = []
#User select the folder of images
root = Tk()
root.withdraw()
folderName = filedialog.askdirectory()
print(folderName)
os.lstat(folderName)


#Get the file names of the images
fileType = '.csv'
fileNames = GetFileNames(folderName, fileType)
nFiles = len(fileNames)
print(nFiles)
print(fileNames)

count = 0
allSetTemps = []

for currentFileName in fileNames:
    #read the csv file
    csvData = CSVRead(currentFileName)
    csvDataOrig = csvData
    zVals = np.ravel(csvData)
    centreCoOrd1 = csvData.shape[0]/2
    centreCoOrd2 = csvData.shape[0]/2
    
    normFactor = csvData[int(centreCoOrd1), int(centreCoOrd2)]
    totalGainArray = np.ones(csvData.shape)
    saveFileName = folderName + '/' + 'totalGainArray.csv' 
    CSVWrite(saveFileName, totalGainArray)

    for iterations in range(0,3):
    
        bPlot = False
        backgroundSubtractedData, background = QuadraticFit(csvData,bPlot)

        #sigma clip the data to find hot pixels
        maskData = sigma_clip(backgroundSubtractedData, sigma=3, maxiters=5)
   
        #remove hot pixels
        dataHPR = RemoveHotPixels(maskData.data,maskData.mask)
        plt.imshow(dataHPR)
        plt.title('image after background subtraction and clip')
        plt.colorbar()
        #plt.show(block = True)
         
        #convert into a gain
        flatFieldGainArray = 1/((dataHPR +normFactor)/ normFactor)

        totalGainArray = flatFieldGainArray*totalGainArray
        plt.imshow(totalGainArray)
        plt.title('Total Gain Array')
        plt.colorbar()
        #plt.show(block = True)

        testIm = csvData*flatFieldGainArray
        plt.imshow(testIm)
        plt.title('Corrected Im')
        plt.colorbar()
        #plt.show(block = True)


        bPlot = False
        backgroundSubtractedData, background = QuadraticFit(testIm,bPlot)

        #sigma clip the data to find hot pixels
        maskData = sigma_clip(backgroundSubtractedData, sigma=3, maxiters=5)
   
        #remove hot pixels
        dataHPR = RemoveHotPixels(maskData.data,maskData.mask)
        plt.imshow(dataHPR)
        plt.title('image after correction')
        plt.colorbar()
        #plt.show(block = True)

        csvData = testIm
   

    #Test Total gain array
    bPlot = True
    testIm = csvDataOrig*totalGainArray
    plt.imshow(testIm)
    plt.title('Corrected Im')
    plt.colorbar()
    plt.show(block = True)


    bPlot = True
    backgroundSubtractedData, background = QuadraticFit(testIm,bPlot)

    #sigma clip the data to find hot pixels
    maskData = sigma_clip(backgroundSubtractedData, sigma=3, maxiters=5)
   
    #remove hot pixels
    dataHPR = RemoveHotPixels(maskData.data,maskData.mask)
    plt.imshow(dataHPR)
    plt.title('image after correction')
    plt.colorbar()
    plt.show(block = True)

     #remove hot pixels
   
    plt.imshow(totalGainArray)
    plt.title('Total Gain Array')
    plt.colorbar()
    plt.show(block = True)

    CSVWrite(saveFileName, totalGainArray)





    exit(0)
     