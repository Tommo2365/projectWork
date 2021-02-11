import numpy
import numpy as np
import matplotlib.pyplot as plt
import csv
from CSVRead import CSVRead
from ReadIRDXFile import ReadIRDXFile
from GetFileNames import GetFileNames
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
from ReadERFXFile import ReadERFXFile
import time
from RiseTimeFunc import FitRiseTime




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

data = CSVRead(fileNames[0], False, 0)
data = data[0]
distance = data[:,0]
nSteps = data[:,1]

plt.plot(distance, nSteps, 'x')
plt.show()

fitAmp, fitTau, popt, pcov  = FitRiseTime(distance,nSteps)

def riseTimeFunc(x, a, tau, offset):
    numpyX = numpy.array(x)
    X0 = numpyX[0]
    riseTime =  a*(1- np.exp(-((x-X0)/tau))) + offset
    return riseTime 

xVals = numpy.linspace(0.8, 20, 200)
riseTime = riseTimeFunc(xVals,popt[0], popt[1], popt[2])
plt.plot(distance,nSteps, 'x')
plt.plot(xVals,riseTime )
plt.ylabel("N steps from focus in position")
plt.xlabel("Distance to source")

plt.show()

a = 4




