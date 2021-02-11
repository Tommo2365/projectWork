import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import pandas as pd

from astropy.stats import sigma_clip
import tkinter as tk
from pathlib import Path
from tkinter import filedialog as fd
import easygui
from easygui import msgbox, multenterbox
from scipy import signal, interpolate, stats, optimize
import sys
import os
import math


##Scipt that loads a csv file containging Knife edge data and calulcates the Edge spread. Each row in the csv should be raw data from an ROI concatonated together. Multipe roi's (rows) are allowed.
#Example Data 
#Time	    Det Temp C	 Shutter Temp C	    Cursor Box Mean	    Cursor Array																																																																																																																																																																																																																																																															
#29:29.6	55.999	     45.0	            3387	            3089	3085	3085	3105........Nth value
#29:39.6	55.999	     45.0	            3387	            3089	3085	3085	3105........Nth value

#The cursor box arry starts in column 5, and for a 15*15 pixel roi would have 225 columns of data. 
#Inputs    numberofHeaderRows = int(fieldValues[0])
    #oversamplingFactor : int for oversampling the data, default 1, no oversampling
    #pixelPitch : [float] pixel pitch on the detector in um
    #dataStartCol : [int] column for which to start reading the roi data from, default 5 (as per above)
    #roiSize : [int] the size in pixles of the side of the square roi, eg for a 15x15 roi, roiSize=15
    #detectorRes = [int] number in of pixels accross the x direction. Ege for a 640x480 detector, detectorRes=640 
    #fieldOfView = [float] angle in degrees accross the x-direction. Eg, 90
    #targetDistance = [float] diatnce to the target. Used to output the smallest resolvable object at this distance.

#Useage
#Run the Script eg in anbaconda prompt python CalculateEdgeSpreadFunction.py
#You will be promted to select the csv file of interest.

#Outputs.
#Edge spread and various other metrics are saved as figures. There is a figure output per ROI.

#ancillary functions- all contained within the stand alone file
#String2Float
#CSVRead
#CalculateEdgeSpreadFunctionFromCSV
   
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
#Ancillary functions#####################################################
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
#Ancillary functions#####################################################
def CalculateEdgeSpreadFunctionFromCSV(data, oversamplingFactor, pixelPitch, saveFileName):
    #Taken from imtool analyses py, and made to work with standalone csv 

    try:
        # Orientate KE.
        #
        halfWidth = int(data.shape[1]/2)
        halfHeight = int(data.shape[0]/2)
        top = np.mean(data[0:halfHeight, :])
        bottom = np.mean(data[halfHeight:, :])
        left = np.mean(data[:, 0:halfWidth])
        right = np.mean(data[:, halfWidth:])

        if np.abs(top-bottom) > np.abs(left-right):
            # edge likely to be horizontal, so rotate
            data = np.rot90(data)

        left = np.mean(data[:, 0:halfWidth])
        right = np.mean(data[:, halfWidth:])

        if np.abs(left) < np.abs(right):
            # if bright on right, flip
            data = np.fliplr(data)

        # Fit peaks of KE line found by using column derivative.
        #
        KE_coordinates_x = []
        KE_coordinates_y = []
        for row_idx, row in enumerate(data):
            if len(row) > 0:
                # Need to discount 0s from the analysis (by interpolation), 
                # otherwise can be identified as erroneous argmin().
                #
                x = np.arange(len(row))[np.where(row>0)]
                y = row[np.where(row>0)]
                f = interpolate.interp1d(
                    x, y, 
                    kind='linear',
                    bounds_error=False,
                    fill_value="extrapolate")
                row_interpolated = f(range(len(row)))

                # Apply savgol filter to piecewise smooth the input.
                #
                sg = signal.savgol_filter(row_interpolated, 5, 3)

                # Find the edge at pixel scales.
                #
                col_idx = x[np.nanargmin(np.gradient(sg))]

                # Use bicubic spline to upsample around this edge to 
                # find subpixel edge position.
                #
                subpixel_x = x[col_idx-2:col_idx+3]
                subpixel_y = y[col_idx-2:col_idx+3]
                try:
                    subpixel_f = interpolate.interp1d(
                        subpixel_x, subpixel_y,
                        kind='cubic')
                    subpixel_interp_x = np.arange(
                        subpixel_x[0], subpixel_x[-1], 0.1)
                    subpixel_interp_y = subpixel_f(subpixel_interp_x)
                except ValueError:
                    continue            

                col_idx_subpixel = subpixel_interp_x[
                    np.argmin(np.gradient(subpixel_interp_y))]

                KE_coordinates_x.append(col_idx_subpixel)
                KE_coordinates_y.append(row_idx)

        KE_fit, residuals, _, _, _ = np.polyfit(
            KE_coordinates_y, KE_coordinates_x, deg=1, full=True)

        # Get supersampled distance by working out how far each 
        # pixel lies from KE line.
        #
        # The following only applies for deg=1 (straight line) fits.
        #
        yy, xx = np.mgrid[0:data.shape[0], 
            0:data.shape[1]]
        d = (KE_fit[1] + KE_fit[0]*yy - xx)/ \
            (np.sqrt((KE_fit[0]**2) + 1))

        ESF_x = d.flatten()
        ESF_y = data.flatten()/ np.max(data.flatten())

        # Filter out 0s
        #
        ESF_x = ESF_x[np.where(ESF_y>0)]
        ESF_y = ESF_y[np.where(ESF_y>0)]

        # Oversample (by binning)
        #
        bin_edges = np.arange(
            np.min(ESF_x), 
            np.max(ESF_x)+1./oversamplingFactor, 
            1./oversamplingFactor)
        ESF_y_binned, _, _ = stats.binned_statistic(
            ESF_x, ESF_y, bins=bin_edges, statistic='median')
        ESF_x_binned  = [x0+((x1-x0)/2) for x0, x1 in zip(
            bin_edges[:-1], bin_edges[1:])]

        # Differentiate to get LSF from ESF.
        # 
        LSF_y = np.gradient(ESF_y_binned)
        LSF_x = ESF_x_binned

        # Apply hamming window to suppress ringing artifacts from taking fft of 
        # infinite series.
        #
        LSF_y_hamming = LSF_y*np.hamming(len(LSF_y))

        # Zero and normalise.
        #
        LSF_y_hamming_zeroed = LSF_y_hamming - np.min(LSF_y_hamming)
        LSF_y_hamming_zeroed_norm = LSF_y_hamming_zeroed/np.sum(
            LSF_y_hamming_zeroed)

        # Absolute magnitude of LSF FFT = MTF.
        #
        MTF_y = np.abs(np.fft.fft(LSF_y_hamming_zeroed_norm))
        N = len(MTF_y)

        # Take only positive frequencies.
        # 
        MTF_y = MTF_y[:N//2]

        # Without oversampling, the spatial frequency unit is cycles/px.
        # With oversampling, the spatial frequency unit is 
        # cycles/(1/oversamplingFactor)px, i.e. we need to multiply by the 
        # oversamplingFactor to get into units of cycles/px.
        #
        MTF_x = 2*np.fft.fftfreq(N)[:N//2]*oversamplingFactor

        # To go to cycles/mm from cycles/px, divide by pixel pitch. This is 
        # in IMAGE SPACE. As such, if object space resolution is required 
        # for determination of minimum resolvable sizes, one would need to 
        # factor in the system magnification. 
        #

        #TMG Hack
        detectorSizeMM = detectorRes*pixelPitch*1e-3

        filedOfViewM = 2*math.tan(math.radians(fieldOfView/2))*targetDistance

        mag = filedOfViewM/(detectorSizeMM*1e-3)

        pixelPitchMM = 1e-3*pixelPitch

        MTF_x_lpmm = MTF_x / pixelPitchMM

        MTF_x_lpmm_Object = MTF_x_lpmm/mag

        minDistanceBetweenObjects = 0.5*(1/MTF_x_lpmm_Object)#half due to line pairs into mm

        # Plots.
        # 
        fig = plt.figure(figsize=(10,8))
        fig.canvas.set_window_title('Analysis: MTF')

        plt.subplot(221)
        plt.title("Data")
        plt.xlabel("x (px)")
        plt.ylabel("y (px)")
        plt.imshow(data)
        plt.plot(KE_coordinates_x, KE_coordinates_y, 'wx', 
            label='knife edge peaks')
        plt.plot(np.polyval(KE_fit, KE_coordinates_y), 
                    KE_coordinates_y, 'r-', label='knife edge line')
        plt.legend(loc='upper right')
        plt.colorbar()

        f = interpolate.interp1d(ESF_y_binned, ESF_x_binned, kind='linear')
        plt.subplot(222)
        plt.title("ESF")
        plt.xlabel("x (px)")
        plt.ylabel("intensity (arbitrary)")
        plt.plot(ESF_x, ESF_y, 'kx', label='data')
        plt.plot(ESF_x_binned, ESF_y_binned, 'ro', label='binned')   

        ESF90 = np.min(ESF_y_binned) + \
            0.90*(np.max(ESF_y_binned)-np.min(ESF_y_binned))
        ESF10 = np.min(ESF_y_binned)+ \
            0.10*(np.max(ESF_y_binned)-np.min(ESF_y_binned))
        plt.hlines(ESF90, -10, 10, colors='b', linestyles='--',
            label="ESF90-ESF10=" + str(round(float(f(ESF90)-f(ESF10)), 1)))
        plt.plot([f(ESF10), f(ESF90)], [ESF10, ESF90], 'bx')
        plt.hlines(ESF10, -10, 10, colors='b', linestyles='--')
        plt.legend(loc='upper right')
        plt.xlim((-10, 10))

        plt.subplot(223)
        plt.title("LSF")
        plt.xlabel("x (px)")
        plt.ylabel("intensity (arbitrary)")
        plt.plot(LSF_x, LSF_y_hamming_zeroed_norm, 'kx-', label='data')
        plt.xlim((-10, 10))
        plt.gca().set_ylim(bottom=0)

        plt.subplot(224)
        plt.title("MTF")
        plt.xlabel("object size (mm)")
        plt.ylabel("Normalised MTF (contrast)")
        plt.plot(
            minDistanceBetweenObjects, 
            MTF_y, 
            'kx-', label='empirical')

        f = interpolate.interp1d(MTF_y, minDistanceBetweenObjects, kind='linear')
        MTF50 = f(0.5)
        plt.hlines(0.5, 0, MTF50, colors='r', linestyles='--')
        plt.vlines(MTF50, 0, 0.5, 
            colors='r', linestyles='--', 
            label="MTF50=" + str(round(float(MTF50), 1)))
        MTF30 = f(0.3)
        plt.hlines(0.3, 0, MTF30, colors='b', linestyles='--')
        plt.vlines(MTF30, 0, 0.3, 
            colors='b', linestyles='--', 
            label="MTF30=" + str(round(float(MTF30), 1)))

        plt.ylim([0,1])
        plt.gca().set_xlim(left=0)
        plt.legend(loc='upper right')

        plt.tight_layout()
        plt.subplots_adjust(hspace=0.3)

        plt.show()
         
        fig.savefig(saveFileName, dpi=fig.dpi)
    except Exception as e:
        print("error during MTF analysis. " +str(e))


#Main SCRIPT#####################################################

root = tk.Tk()
#root.withdraw()
fileName = fd.askopenfilename()
root.destroy()
#fileName = 'I:\\7001 0325 EX 3.9um Borescope\\Physics\\Work Area\\2ft 3.9 Borescope P1\\CalFiles\\Gains.csv'
print(fileName)


#Read in the csv file as an numpy array of strings
bHeader = True
fieldValues = ['1']
fieldNames = ["Enter the number of rows in the header (0 if none)",  "Enter oversamplingFactor factor", "Enter Pixel Pitch (um)", "Enter ROI start column index", "Enter ROi side length (pixels)", "Enter the detector resoltion x (pixels)", "Enter detector file of view (degrees)", "Enter Distance to knife edge (m)"]
fieldValues = list(multenterbox(msg='Fill in values for the fields.', title='Enter', fields=(fieldNames), values= (1,1,17, 5, 16, 640,90,1)))
        #msgbox(msg=(fieldValues), title = "Results")

try:
    numberofHeaderRows = int(fieldValues[0])
    oversamplingFactor = int(fieldValues[1]) 
    pixelPitch = float(fieldValues[2])
    dataStartCol = int(fieldValues[3])
    roiSize = int(fieldValues[4])
    detectorRes = int(fieldValues[5])
    fieldOfView = float(fieldValues[6])
    targetDistance = float(fieldValues[7])
except ValueError:
    print('Values not entered correctly, using defaults')
    numberofHeaderRows = int(2)#default
    oversamplingFactor = int(1)#default
    pixelPitch = int(17)#default 17um
    dataStartCol = int(5)
    roiSize = int(15)
    detectorRes = int(640)
    fieldOfView = float(90)
    targetDistance = float(1)

bHeader = True
if(numberofHeaderRows == 0):
    bHeader = False

csvData, header = CSVRead(fileName,bHeader,numberofHeaderRows)
nPixels = np.shape(csvData)[1]
csvDataImage = csvData[:, (dataStartCol)-1:nPixels-1]
dataArray = String2Float(csvDataImage)

nImages = np.shape(dataArray)[0]

for k in range(0, nImages):
    flattenedData =  dataArray[k,:]
    im = np.reshape(flattenedData, (roiSize,roiSize))
    #plt.imshow(im);plt.show()
    filePath = os.path.dirname(fileName)
    saveFileName = filePath + '/' + 'ESF' + str(k) + '.jpg'
    CalculateEdgeSpreadFunctionFromCSV(im, oversamplingFactor, pixelPitch, saveFileName)

print('Program Complete see' + filePath)



