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



allPixelTemps = []
#User select the folder of images
root = Tk()
root.withdraw()
folderName = filedialog.askdirectory()
print(folderName)
os.lstat(folderName)


#Get the file names of the images
fileType = '.erfx'
fileNames = GetFileNames(folderName, fileType)
nFiles = len(fileNames)
print(nFiles)
print(fileNames)

count = 0
allSetTemps = []

for currentFileName in fileNames:
    #read the csv irdx file
    imageHeight = 640
    imageWidth= 480
    startByte = 218
   
    #CalculateSomeStuff
    frameSize = (imageHeight*imageWidth*2)
    endByte  = startByte + (imageHeight*imageWidth*2)#There are two bytes ber pixel
    N=600
    starByteFrameN = 218+ frameSize*N
    


    NthFrameFrame = ReadIRDXFile(currentFileName, imageHeight, imageWidth, starByteFrameN)


    allFrames, nFrames = ReadERFXFile(currentFileName, imageHeight, imageWidth, startByte)
    #csvData = CSVRead(currentFileName)
#plt.colorbar()
for k in range(int(0), nFrames-1):
    plt.imshow(allFrames[k])
    plt.title('Frame1')
    
    plt.show()
    time.sleep(0.3)


exit(0)
    



    ##sigma clip the data to find hot pixels
    #maskData = sigma_clip(img, sigma=3, maxiters=5)
    #plt.imshow(maskData)
    #plt.title('image after background subtraction and clip')
    #plt.colorbar()
    #plt.show(block = True)

    ##remove hot pixels
    #dataHPR = RemoveHotPixels(maskData.data,maskData.mask)

    #plt.imshow(dataHPR)
    #plt.title('image after hot pixel removal')
    #plt.colorbar()
    #plt.show(block = True)



    
     

    
    
  
#    #find the Temp from the filename
#    number = re.findall(r'\d+', currentFileName)
#    currentTemp = float(number[0]) 
#    allSetTemps.append(currentTemp)
#    print(currentFileName + 'HasTemp ' + str(number[0]) )
    
#    #build a file name to save a png
#    fileNamePNG = [currentFileName[0:-4] + '.png']
#    fileNamePNG = fileNamePNG[0]

#    #save the csv data as png
#    cv2.imwrite(fileNamePNG, csvData)

#    #Re-load the image..!
#    im = cv2.imread(fileNamePNG)
#    count = count + 1

#    if count == 1:
#        #Select a rectangular ROI for the first region. Assumes all images are aligned..
#        fromCenter = False
#        r = cv2.selectROI(im, fromCenter)
#        #cv2.waitKey(0)
#    imSize = csvData.shape
#    csvDataCrop = csvData[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
#    pixelTempsVector = csvDataCrop.flatten()
#    allPixelTemps.append(pixelTempsVector)

#    #print(np.shape(allPixelTemps))

#print('Finished Loading Data')

##conert from list to np Array
#allPixelTemps = np.array(allPixelTemps)
#arraySize = allPixelTemps.shape
#nPixels = arraySize[1]
#print('Number of Pixels ' + str(nPixels))
#allSetTemps = np.array(allSetTemps)

#fig = plt.figure()
#plt.ion()

#allGrads = []
#allIntercepts = []
##Do fit to temperatrure for each pixel
#for pixelIndex in range(0, nPixels):
#    xData = allPixelTemps[:,pixelIndex]
#    yData = allSetTemps
#    fitParams = np.polyfit(xData, yData, 1)
#    yFit = np.polyval(fitParams,xData)
#    plt.plot(xData,yData, 'xr' )
#    plt.plot(xData,yFit, 'b' )
#    plt.draw()
    
#    #print(fitParams)
#    allGrads.append(fitParams[0])
#    allIntercepts.append(fitParams[1])
##convert to np array
#allGrads = np.array(allGrads)
#allIntercepts = np.array(allIntercepts)
#plt.show(block = True)
#plt.hist(allGrads, bins='auto')
#plt.show(block = True)

#cropSize =np.array([])
#cropSize1 = r[2]
#cropSize2 = r[3]
#print(cropSize1)
#print(cropSize2)
#gainArray = np.reshape(allGrads, (cropSize1,cropSize2))
#plt.imshow(gainArray)
#plt.colorbar()
#plt.show(block = True)
