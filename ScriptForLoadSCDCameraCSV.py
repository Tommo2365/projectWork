import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import pandas as pd
#from CSVRead import CSVRead
from astropy.stats import sigma_clip
#from String2Float import String2Float
import tkinter as tk
from pathlib import Path
from tkinter import filedialog as fd
import easygui
from easygui import msgbox, multenterbox

import os
import matplotlib.pyplot as plt
import numpy as np



##Scipt that loads a csv file containging am image, does hot pixel removal and displays the resulting image
#Example Data 
#Image Capture										
#SCDCameraToolkitV2.00	Cols=	640	Rows=	480	Det Temp=	48207	Shutter Temp=	0		
#4214	4193	4196	4210	4206	4194	4189	4201	4193	4197	4209....
#4214	4197	4205	4203	4197	4194	4180	4185	4196	4199	4190....
#.....
#.....


#Inputs    Enter the number of header rows: [int], or example above the number of header rows = 1, for gains files, the number of header rows may be 0 or 2

#Useage
#Run the Script eg in anbaconda prompt python ScriptForLoadSCDCameraCSV.py
#You will be promted to select a SINGLE CSV FILE csv file which contains N rows of header text, followed by LXM columnsxrows of image data (eg 640x480)

#Outputs.
#Saves a jpg of the hot pixels and of the image (after hot pixel removal)

#ancillary functions- all contained within the stand alone file
#String2Float
#CSVRead
#MovingAverageConvolve
#RemoveHotPixels


def MovingAverageConvolve(data, windowSize, bPlot):
    fig, ax = plt.subplots()
    nPoints = len(data)
    xData = np.linspace(0, nPoints, nPoints, endpoint=True)
    ax.plot(xData, data, label="Original")
    # Compute moving averages using different window sizes
    window_lst = ([windowSize])
    y_avg = np.zeros((len(window_lst) , nPoints))
   
    avg_mask = np.ones(windowSize) / windowSize
    y_avg[0, :] = np.convolve(data, avg_mask, 'same')
    # Plot each running average with an offset of 50
    # in order to be able to distinguish them
    y_avg[0, 0:windowSize] = data[0:windowSize]
    y_avg[0, -windowSize:] = data[-windowSize:]
    ax.plot(xData, y_avg[0, :] , label=windowSize)
    # Add legend to plot
    
    ax.legend()
    plt.show()
    
    y_avg = y_avg[0]
    return y_avg

def CSVRead(fileName, bHeader, nHeaderRows):
    
    print('Loading File:    ' + fileName)

    #data = numpy.array([])
    listData = []
    #data = []

    with open(fileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = ',')
        #print(csv_reader)
        line_count = 0
        for row in csv_reader:
        # print(row)
            listData.append(row)
            #data = np.append(data, row)
            line_count += 1
        if(bHeader == True):
            # Assume the header is the first row, take the 2nd row to to end for the data
            csvData = np.array(listData[nHeaderRows:len(listData)])
            #csvData = csvData.astype('float')
            header =  np.array(listData[0:nHeaderRows])
        elif(bHeader == False):
            csvData = np.array(listData)
            try:
                csvData = csvData.astype('float')
            except:
                try:
                    csvData = String2Float(csvData)
                except:
                    return csvData


            header =  ''
        print(f'Processed {line_count} lines ' + 'arraySize ' + str(csvData.shape))
        # plt.imshow(csvData)
        # plt.colorbar()
        # plt.show()
        return csvData, header

def RemoveHotPixels(data, bHot):
    #function RemoveHotPixels
    #Inputs:  data: 2D numpy array eg an image
    #         bHot: a numpy array of booleans eg bArray =  np.zeros((4, 4), dtype=bool) for array of FALSE
    #Ouputs:
    #        data: the data with hot pixels replaced by mean of nearest neihgbours  with 3x3 kernal size 
    
    #Find the total number of hot pixels in the array data
    nHotPixels = sum(sum(bHot))

    #Find the indices of the hot pixels
    hotPixelIndices = np.where(bHot == True)
    hotPixelIndices = np.array(hotPixelIndices)

    #Main loop through each of the hot pixels
    for n in range(0,nHotPixels):
        #Initalise some loop variables
        count = 0
        pixelVal = []
        currentPixelCoOrd = hotPixelIndices[:, n]
        
        #Loop through rows and columns of 3x3 neighbourhood of pixels
        for rows in [currentPixelCoOrd[0]- 1, currentPixelCoOrd[0], currentPixelCoOrd[0]+1]:
            for columns in [currentPixelCoOrd[1]- 1, currentPixelCoOrd[1], currentPixelCoOrd[1]+1]:
                if rows == currentPixelCoOrd[0]:
                    if columns == currentPixelCoOrd[1]:
                        #If the current pixel co-ordinate in the loop is the same as the hot pixel 
                        continue
                if rows < 0 or rows > (data.shape[0])-1:#make sure the row index is within bounds
                    print(rows)
                    continue
                if columns < 0 or columns > (data.shape[1])-1: #make sure the column index is within bounds
                    print(columns)
                    continue
                #row all rows and columns in the neighbourhood find the pixel value
                neighbourPixelVal = data[rows, columns]

                if type(neighbourPixelVal) == type(True):
                    #skip if this pixel is also a hot pixel
                    continue
                    
                
                #sum up the pixel values (to calculate mean later)
                pixelVal.append(neighbourPixelVal) 
                
                #counter of the number of pixels used in the cummulative seum
                count = count + 1
                
        #calulte the median of the neigbourhood pixels
        replacementValue = np.median(np.array(pixelVal))
        
        #replace the hot pixel by the mean
        data[currentPixelCoOrd[0],currentPixelCoOrd[1]] = replacementValue

    return data

def String2Float(csvData):
    #Find the numnber of rows of numeric data
    numDataRows = len(csvData)
    
    #Pull out the data
    data = csvData[0:numDataRows]
    numberCols = np.shape(data)[1]
    dataArray = np.ones([numDataRows,numberCols])

    for k in range (0,numDataRows):
        for w  in range(0, numberCols):
            thisElement = data[k,w]
            if(not thisElement):
                continue
            thisFloat = float(thisElement)
            dataArray[k,w] = thisFloat
    return dataArray
    
    

#Define File name to read the data from
root = tk.Tk()
#root.withdraw()
fileName = fd.askopenfilename()
root.destroy()
#fileName = 'I:\\7001 0325 EX 3.9um Borescope\\Physics\\Work Area\\2ft 3.9 Borescope P1\\CalFiles\\Gains.csv'
print(fileName)
filePath = os.path.dirname(fileName)
k=0
saveFileName1 = filePath + '/' + 'HotPixels' + '.jpg'
saveFileName2 = filePath + '/' + 'Image' + '.jpg'

#Read in the csv file as an numpy array of strings
bHeader = True
fieldValues = ['2']
fieldNames = ["Enter the number of rows in the header (0 if none)"]
fieldValues = list(multenterbox(msg='Fill in values for the fields.', title='Enter', fields=(fieldNames)))
msgbox(msg=(fieldValues), title = "Results")
numberofHeaderRows = int(2)#default

try:
    numberofHeaderRows = int(fieldValues[0])
except ValueError:
    numberofHeaderRows = int(2)
bHeader = True
if(numberofHeaderRows == 0):
    bHeader = False

csvData, header = CSVRead(fileName,bHeader,numberofHeaderRows)

#Pull out the column headers
columnHeaders = csvData[0]

#Find the numnber of rows of numeric data
numDataRows = len(csvData)
numberCols = np.shape(csvData)[1]-1

#Convert the array of strings into a numpy array
dataArray =  String2Float(csvData)

       


maskData = sigma_clip(dataArray, sigma=10, maxiters=5)

fig1 = plt.figure(figsize=(10,8))
plt.imshow(1*(maskData.mask))
nClippedPixes = int(sum(sum(maskData.mask)))
plt.title(str(nClippedPixes)  + 'Highlighted five sigma pixels')
plt.colorbar()
plt.show(block = True)
fig1.savefig(saveFileName1, dpi=fig1.dpi)
   
#remove hot pixels
dataHPR = RemoveHotPixels(maskData.data,maskData.mask)

fig2 = plt.figure(figsize=(10,8))
plt.imshow(dataHPR)
plt.title('image after correction')
plt.colorbar()
plt.show(block = True)
fig2.savefig(saveFileName2, dpi=fig2.dpi)




#plt.plot(SimSquareWave)

    

