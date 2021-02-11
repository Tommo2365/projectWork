import numpy as np


import matplotlib.pyplot as plt
from matplotlib.pyplot import plot, draw, show, ion
import statistics
#from RiseTimeFunc import FitRiseTime 
import matplotlib.animation as animation
from matplotlib import style
from tkinter.filedialog import askdirectory
import scipy
from scipy.optimize import curve_fit
from pytictoc import TicToc
#import rhinoscriptsyntax as rs
#from rhino import rhinoscriptsyntax
import easygui
from easygui import msgbox, multenterbox
import math
import numpy as np
import scipy
from scipy import ndimage
from ImageHandling.SimAperture import SimAperture
from ImageHandling.RadialAverage import CalculateRadialAverage


data = np.load('C:\Data\Im1.npy') 
fftData= np.log(np.abs(np.fft.fft2(data)))
maxFFT = np.max(fftData)
fftData = fftData/maxFFT
fftData = np.fft.fftshift(fftData)
N = len(fftData)
#MTF_x = np.fft.fftfreq(N)[:N//2]

plt.subplot(221)
plt.title("Data")
#plt.xlabel("x (px)")
plt.ylabel("y (px)")
plt.imshow(data)
           

plt.subplot(222)
plt.title("FFTData")
#plt.xlabel("x (px)")
plt.ylabel("y (px)")
plt.imshow(fftData)
plt.colorbar()





#aperture = SimAperture(np.shape(fftData), 50) #FromImageHandling
radialAverage = CalculateRadialAverage(fftData)
plt.subplot(223)
plt.plot(radialAverage)
plt.title("PowerSpectrum")
plt.xlabel("radius (px)")
plt.ylabel("Average Power (au)")
plt.show()






disp('Finsihed')
