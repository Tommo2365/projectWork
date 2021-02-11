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

root = Tk()
root.withdraw()
folderName = filedialog.askdirectory()
print(folderName)
os.lstat(folderName)


#Get the file names of the images
fileType = '.txt'
fileNames = GetFileNames(folderName, fileType)
nFiles = len(fileNames)
print(nFiles)
print(fileNames)

count = 0

allInstTemps = np.array([])
allTOffset = np.array([])
for currentFileName in fileNames:
    #read the csv file
    f = open(currentFileName, "r")
    currentText  = f.read()
    index = currentText.find("ChopperTOffset = ")
    chopperTOffsetReadLine = currentText[index+17:index+ 23]
    newLine = chopperTOffsetReadLine.find("\n")
    chopperTOffsetString = chopperTOffsetReadLine[0:newLine]
    ChopperTOffsetValue = float(chopperTOffsetString)/10
    if(ChopperTOffsetValue < -50):
        continue

    index2 = currentText.find("Instrument Ambient = ")
    instAmbReadLine = currentText[index2+21:index2+ 27]
    newLine2 = instAmbReadLine.find("\n")
    instAmbString = instAmbReadLine[0:newLine2]
    instAmbValue = float(instAmbString)

    allInstTemps = np.append(instAmbValue, allInstTemps)
    allTOffset = np.append(ChopperTOffsetValue, allTOffset)
    #print(currentText)
    #print("############")
    #print(currentFileName)
    #print(ChopperTOffsetValue)
    #print(instAmbValue)
    #if(ChopperTOffsetValue < -10):
       # print(currentFileName)
   # print("############")


print('finshed loading files')

counts, bins = np.histogram(allInstTemps)
plt.hist(bins[:-1], bins, weights=counts)
plt.xlabel("Inst Temp degrees")
plt.ylabel("N")
plt.show()

counts, bins = np.histogram(allTOffset)
plt.hist(bins[:-1], bins, weights=counts)
plt.xlabel("Chopper T Offset")
plt.ylabel("N")
plt.show()

plt.plot(allInstTemps, allTOffset, 'x')
plt.title('Scatter TOffset with Ambient Temp')
plt.xlabel("Inst Temp degrees")
plt.ylabel("Chopper T Offset degrees")
plt.show()