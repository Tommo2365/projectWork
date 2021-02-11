import numpy
import numpy as np
import matplotlib.pyplot as plt
import csv
from CSVRead import CSVRead
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
    zVals = np.ravel(csvData)

    #startPoint = (240, 0)
    #endPoint= (240,639)
    #lineWidth = 5
    #profile = LineProfile(csvData, startPoint, endPoint, lineWidth)
    #plt.plot(profile)
    #plt.ylabel('Intensity (Degrees)', fontsize=12)
    #plt.xlabel('line path (Pixels)', fontsize=12)
    #plt.tick_params(axis='both', which='major', labelsize=12)
    #plt.show()
   
    #bPlotSpectrum = True
    #powerSig, freq = Fft(profile, bPlotSpectrum, 1)
    

    bPlot = True
    backgroundSubtractedData, background = QuadraticFit(csvData,bPlot)

    #convert data to 8Bit
    minData = np.min(csvData)
    maxData = np.max(csvData)
    csvDataN = csvData - minData
    csvDataN = csvDataN/(maxData-minData)
    csvDataN = 255*csvDataN
    csvData8Bit = np.uint8(csvDataN)

    #Flatten the Data with a rolling ball
    ballRadius = 100 
    img, background = subtract_background_rolling_ball(csvData8Bit, ballRadius, light_background=False, use_paraboloid=False, do_presmooth=False)
 
    plt.imshow(img)
    plt.title('Rolling Ball Image')
    plt.colorbar()
    plt.show(block = True)

    #sigma clip the data to find hot pixels
    maskData = sigma_clip(img, sigma=5, maxiters=5)
    plt.imshow(maskData)
    plt.title('image after background subtraction and clip')
    plt.colorbar()
    plt.show(block = True)

    #remove hot pixels
    dataHPR = RemoveHotPixels(maskData.data,maskData.mask)

    plt.imshow(dataHPR)
    plt.title('image after hot pixel removal')
    plt.colorbar()
    plt.show(block = True)

    #convert the 8 bit offsets back into a gain
    offsetTemp= ((dataHPR*(maxData-minData))/255)+minData
    flatFieldGainArray = 1/(offsetTemp/np.median(offsetTemp))

    plt.imshow(flatFieldGainArray)
    plt.title('Gain Array')
    plt.colorbar()
    plt.show(block = True)

    testIm = csvData*flatFieldGainArray
    plt.imshow(testIm)
    plt.title('Corrected Im')
    plt.colorbar()
    plt.show(block = True)


    #convert back to 8 bit
    
    #convert data to 8Bit
    minData = np.min(testIm)
    maxData = np.max(testIm)
    csvDataN = csvData - minData
    csvDataN = csvDataN/(maxData-minData)
    csvDataN = 255*csvDataN
    csvData8Bit = np.uint8(csvDataN)


    #Flatten the Data with a rolling ball
    ballRadius = 100 
    img, background = subtract_background_rolling_ball(csvData8Bit, ballRadius, light_background=False, use_paraboloid=False, do_presmooth=False)


    #sigma clip the data to find hot pixels
    maskData = sigma_clip(img, sigma=5, maxiters=5)
    plt.imshow(maskData)
    plt.title('image after correction')
    plt.colorbar()
    plt.show(block = True)



    exit(0)
     