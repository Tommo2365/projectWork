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
gainArrayFileName = 'C:\Data\GainArray/totalGainArray.csv'
nFiles = len(fileNames)
print(nFiles)

totalGainArray =CSVRead(gainArrayFileName)

for currentFileName in fileNames:
    #read the csv file
    csvData = CSVRead(currentFileName)
    normFactor = np.median(csvData)


    #Test Total gain array
    testIm = csvData*totalGainArray
   
    #Do Quadratic Fit
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



    exit(0)
     