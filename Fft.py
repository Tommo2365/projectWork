

import numpy as np
from skimage.measure import profile_line
from skimage import io
import matplotlib.pyplot as plt
import cv2
import math

def Fft(dataArray1D, bPlotSpectrum, xStep):

    nPoints = len(dataArray1D)

    t = np.arange(nPoints)
    #t = t*pixelSizeMm

    n = dataArray1D.size
    timestep = xStep
    freq = np.fft.fftfreq(n, d=timestep)
    
   
    modSquared = abs(np.fft.fft(dataArray1D))**2
    #freq = np.fft.fftfreq(t.shape[-1])
    #modSquared = abs(realData*imagData)
    powerSig = modSquared[0:round(nPoints/2)]
    frequency = freq[0:round(nPoints/2)]
    
    if(bPlotSpectrum == True):
        plt.plot(frequency,np.log(powerSig), 'xk')  
        plt.plot(frequency,np.log(powerSig))  
        plt.xlabel("Frequency (1/NPixels)", fontsize=12)
        plt.ylabel("Log Power (a.u.)", fontsize=12)
        plt.tick_params(axis='both', which='major', labelsize=12)
        plt.axis([0, 1e4, -10, 20])
        plt.show(block = True) 

        
    return powerSig, frequency