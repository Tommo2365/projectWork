import sys
import cv2
import numpy as np
import glob
from String2Float import String2Float
from CSVRead import CSVRead
import matplotlib.pyplot as plt
from cv2_rolling_ball import subtract_background_rolling_ball
import affine6p
import tkinter 
from tkinter import filedialog as fd
from pathlib import Path
from Affine_Fit import Affine_Fit
from affine import Affine
import nudged
import os
import easygui
from easygui import msgbox, multenterbox
import fnmatch
import time
from datetime import datetime
import pylab as plt
import pandas as pd
import dictionary
import csv
import shutil


# input fields
fieldNames = ["Serial number:", "Working directory:", "Focal distance(mm):", "Lower threshold:", "boolean plot images?", "boolean use rolling ball?"]
fieldValues = list(multenterbox(msg='Fill in values for the fields.', title='Enter', fields=(fieldNames), values=["","C:\Data", "400", "25", "0","1"] ))

serialNum = str(fieldValues[0])
dircIm = str(fieldValues[1]) + '\\*.csv'
dircIm2 = str(fieldValues[1])
focalDistance = float((fieldValues[2]))
lowerThresh = float(fieldValues[3])
bPlotImages = float(fieldValues[4])
rBall = float(fieldValues[5])

# count number of valid files
print('Number of files:')
print(len(fnmatch.filter(os.listdir(dircIm2), '*.csv')))

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# grid size
objp = np.zeros((7*7,3), np.float32)
objp[:,:2] = (1/3)*128*np.mgrid[0:7,0:7].T.reshape(-1,2)

objpoints = [] # 3D point in real world space
imgpoints = [] # 2D points in image plane.


# load images from given wokring directory  
images = glob.glob(dircIm)            

firstImage = images[0]
filePath = os.path.dirname(firstImage)

for fname in images:
  
    
    img,header = CSVRead(fname, 1,2)
    img2 = np.array(img)
    #Remove emptry string appended to end of images
    img2 = img2[:, 0:np.shape(img2)[1]-1]
    img3 = String2Float(img2)
    greyScaleIm = img3
    greyScaleIm = np.repeat(greyScaleIm,3,axis=1)
    greyScaleIm = greyScaleIm.reshape(np.shape(img3)[0], np.shape(img3)[1], 3)
    print("Processing image...")
    try:
        greyScaleIm = greyScaleIm/np.max(greyScaleIm[:,:,:])
    except Exception as inst:
        print("ERROR!  Ensure only .csv images are present in working directory, " + dircIm2)
    else:
        print("...")

    #greyScaleIm = greyScaleIm/np.max(greyScaleIm[:,:])
    greyScaleIm = greyScaleIm*255
    greyScaleIm = greyScaleIm.astype('uint8')
    
    grey = greyScaleIm

    prefix = fname.split('.csv')[0]
    writeFileName2 = prefix + '.jpg'
    cv2.imwrite(writeFileName2, grey)

    
    img = cv2.imread(writeFileName2)

    img = img.astype('uint8')
    grey = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    grey = cv2.medianBlur(grey,7)
    grey = cv2.GaussianBlur(grey, (3,3), 0)
    #cv2.imwrite(writeFileName2, grey)
    
    #Flatten the Data with a rolling ball
    if rBall == 1:
        ballRadius = 200 
        print("Applying rolling ball")
        print("Please wait...")
        rollingBallIm, background = subtract_background_rolling_ball(grey, ballRadius, light_background=False, use_paraboloid=False, do_presmooth=False)
        writeFileName3 = prefix + 'P' + '.jpg'
        print("Rolling ball applied...")
        print("")
        rollingBallImSave = rollingBallIm/np.max(rollingBallIm[:,:])
        #greyScaleIm = greyScaleIm/np.max(greyScaleIm[:,:])
        rollingBallImSave = rollingBallImSave*255
        rollingBallImSave = rollingBallImSave.astype('uint8')

        cv2.imwrite(writeFileName3, rollingBallImSave)
        

    elif rBall == 0:
        #ballRadius = 200 
        rollingBallIm = (grey)
        writeFileName3 = prefix + 'P' + '.jpg'
        rollingBallImSave = rollingBallIm/np.max(rollingBallIm[:,:])
        #greyScaleIm = greyScaleIm/np.max(greyScaleIm[:,:])
        rollingBallImSave = rollingBallImSave*255
        rollingBallImSave = rollingBallImSave.astype('uint8')

        cv2.imwrite(writeFileName3, rollingBallImSave)
        offset = 0.66*255
        lowerThresh = lowerThresh + offset

        
    ret1,threshIm = cv2.threshold(rollingBallIm,lowerThresh,255,cv2.THRESH_BINARY)

    
    #dp Resolution of the accumulator array. Votes cast are binned into squares set by dp size. Set too small and only perfect circles are found, 
    #set too high and noise collaborates to vote for non-circles.
    dp = 1

    #minDist Minimum distance between the center (x, y) coordinates of detected circles. 
    #If the minDist is too small, multiple circles in the same neighborhood as the original may be (falsely) detected. If the minDist is too large, then some circles may not be detected at all.
    minDist = 20


    #param1: Is a number forwarded to the Canny edge detector (applied to a grayscale image) that represents the threshold1 passed to Canny(...). 
    #Canny uses that number to guide edge detection: http://docs.opencv.org/2.4/modules/imgproc/doc/feature_detection.html?highlight=canny
    cannyThresh = 10

    #param2: Accumulator threshold value for the cv2.HOUGH_GRADIENT method. The smaller the threshold is, the more circles will be detected (including false circles). 
    #The larger the threshold is, the more circles will potentially be returned.
    param2 = 20

    #minRadius: Minimum size of the radius in pixels. Don't set minRadius and maxRadius far apart unless you want all possible circles that might be found in that range.
    #maxRadius: Maximum size of the radius (in pixels). Don't set minRadius and maxRadius far apart unless you want all possible circles found in that range.
    minRadius=7
    maxRadius=13

    edges = cv2.Canny(threshIm, cannyThresh, 10)
    #plt.imshow(edges);plt.show()

    edgesCrop = edges[1:478, 1:638];
    #plt.imshow(edgesCrop);plt.show()

    threshImCrop = threshIm[2:477, 2:637];
    #plt.imshow(threshImCrop);plt.show()

    #FindCirclesGrid
    bUseCircleGridDet = True
    if(bUseCircleGridDet == True):
        params = cv2.SimpleBlobDetector_Params()
        #params	=	cv2.SimpleBlobDetector_create()
        #params.maxArea = 1000# for medium short to medium long
        params.minArea = 0;
        params.maxArea = 1000

        params.minThreshold = 0
        params.maxThreshold = 255
        params.minDistBetweenBlobs = 7;     ##DELETED: 5
   
    
        params.blobColor = 0 #for dark blobs 1 for light blobs
        params.minCircularity = 0.1
        params.maxCircularity = 2
    
    
        params.filterByColor = True
        params.filterByCircularity = False
        params.filterByConvexity = False
        params.filterByInertia = False
        params.filterByArea = True
        params.thresholdStep = 1

        detector = cv2.SimpleBlobDetector_create(params)

    
        inverseIm = 255-threshImCrop 
        flags = cv2.CALIB_CB_CLUSTERING
        flags = cv2.CALIB_CB_SYMMETRIC_GRID 
        flags = cv2.CALIB_CB_ASYMMETRIC_GRID
        #flags, centres  = cv2.findCirclesGrid(inverseIm, (5,5),flags=cv2.CALIB_CB_ASYMMETRIC_GRID,blobDetector=detector)
        #flags, centres  = cv2.findCirclesGrid(inverseIm, (5,5),cv2.CALIB_CB_CLUSTERING,blobDetector=detector)
        flags, centres  = cv2.findCirclesGrid(inverseIm, (7,7),cv2.CALIB_CB_SYMMETRIC_GRID,blobDetector=detector)
        #flags, centres  = cv2.findCirclesGrid(inverseIm, (5,5),cv2.CALIB_CB_ASYMMETRIC_GRID,blobDetector=detector)
        if(flags ==  True):
            if(centres.all != None):
                if(bPlotImages == 1):
                    plt.imshow(inverseIm)
                for k in range(0, len(centres)):
                    thisPoint = centres[k]
                    thisPoint = thisPoint[0]
                    x = thisPoint[1]
                    y = thisPoint[0]
                    if(bPlotImages == 1):
                        plt.imshow(inverseIm);plt.plot(y,x, 'x' );
                #plt.show()
                if(len(centres) != 49):
                    print('Not found 49 blobs skipping image')
                    continue
            else:
                print('No centres found skipping image')
                continue

        else:
            print('bad image,skipping image')
            continue

    
    bManualCircleDetect = False
    output = centres
    objpoints.append(objp)
    imgpoints.append(output)
    
####end of read images

# change working directory
newDir = serialNum + "_distortionData" 

path = os.path.join(dircIm2, newDir)

try:
    os.mkdir(path)
except OSError:
       print("New direcotry failed to manifest...")
else:
    print("New directory created:       " + str(path))
print("")

os.chdir(path)

###############################################################################################################################################################################
#                     APPLY CALIBRATION AND WRITE FILES
###############################################################################################################################################################################

np.shape(imgpoints)

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, grey.shape[::-1], None, None)

img = cv2.imread(writeFileName3)
h, w = img.shape[:2]

map1, map2 = cv2.initUndistortRectifyMap(mtx, dist, None, None, (w,h), cv2.CV_32FC1)

dsts = []
funcs = ("cv2.INTER_NEAREST", "cv2.INTER_LINEAR", "cv2.INTER_CUBIC", "cv2.INTER_LANCZOS4")
for f in funcs:
	start = time.time()
	dst = cv2.remap(img, map1, map2, eval(f))
	dsts.append(dst)
	print(f, '\t', str(round((time.time()-start)*1000, 1)) + "ms")


# Show comparison images
plt.figure()

un = cv2.remap(img, map1, map2,0 )
plt.subplot(1, 2, 1)
plt.title('Corrected Image')
plt.xlabel('Number of pixels, x')
plt.ylabel('Number of pixels, y')
plt.imshow(dst)

plt.subplot(1, 2, 2)
#plt.text(1, 0.5,'Comparison of Images Before and After Lens Calibration')
plt.title('Original Image')
plt.xlabel('Number of pixels, x')
plt.ylabel('Number of pixels, y')
plt.imshow(img)
plt.show()

# create a timestamp on the save file
now = datetime.now() 
timeStamp = now.strftime("%Y%m%d_")

# write 'dist' and 'mtx' to csv 
mtxValcsv = timeStamp + serialNum + '_distortionMatrix.csv'
np.savetxt(mtxValcsv, mtx, delimiter=',', fmt=['%s', '%s', '%s'], header=[])

distValcsv = timeStamp + serialNum + '_distortionCoeff.csv'
np.savetxt(distValcsv, dist[0] , delimiter=',', fmt=['%s'], header=[])

# write distortion coeffs to csv
fx = mtx[0][0]
fy = mtx[1][1]

cx = mtx[0][2]
cy = mtx[1][2]

k1 = dist[0][0]
k2 = dist[0][1]
k3 = dist[0][3]

kVals = ["FX", fx, "FY", fy, "CX", cx, "CY", cy, "K1", k1, "K2", k2, "K3", k3, "END", ""]
#kValNames = ["FX", "FY", "CX", "CY", "K1", "K2", "K2", "END"]

print("")
print('Distortion Coeffs:')
print('fx = {} fy = {} cx = {} cy = [] k1 = {} k2 = {} k3 = {}'.format(fx, fy, cx, cy, k1, k2, k3))


kValcsv = 'DistortionCoeffs.csv'
kVals2 = np.reshape(kVals, (8,2))
np.savetxt(kValcsv, kVals2, delimiter=',', fmt=['%s', '%s'], header=[])


#print('Number of files compleated:')
#print(len(fnmatch.filter(os.listdir(dircIm2), 'P' + '*.jpg')))

print('Fin')

#######################################################################################################################





