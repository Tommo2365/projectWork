import serial
import configparser
import argparse
import time
from datetime import datetime
import numpy as np
import keyboard  # using module keyboard
import matplotlib.pyplot as plt
from matplotlib.pyplot import plot, draw, show, ion
import statistics

import matplotlib.animation as animation
from matplotlib import style
from tkinter.filedialog import askdirectory
import numpy
import scipy
from scipy.optimize import curve_fit
from pytictoc import TicToc
#import rhinoscriptsyntax as rs
#from rhino import rhinoscriptsyntax
import easygui
from easygui import msgbox, multenterbox

def FitRiseTime(xData,yData):

    def riseTimeFunc(x, a, tau, offset):
        numpyX = numpy.array(x)
        X0 = numpyX[0]
        riseTime =  a*(1- np.exp(-((x-X0)/tau))) + offset
        return riseTime 
    yGuess = riseTimeFunc(xData, yData[-1] - yData[0], 0.2, yData[0])
    

    #xData = np.linspace(0, 4, 50)
    
    #yDataClean = riseTimeFunc(xData, 2.5, 1.3, offset)

    #np.random.seed(1729)
    #yNoise = 0.2 * np.random.normal(size=xData.size)
    #yData = yDataClean + yNoise

    #plt.plot(xData, yData)
    #plt.xlabel("Time (seconds)")
    #plt.ylabel("Temp degrees")

    #plt.draw()
    #plt.pause(0.01)

    maxY = float(max(yData))
    minY = min(yData)
    maxOffset = min(yData) + 2
    maxAmp = 10*float(maxY-minY)

    minTau = 0.2
    maxTau = 10*float(max(xData) - min(xData))

    X0 = xData[0]


   # popt, pcov = curve_fit(riseTimeFunc, xData, yData, bounds=(0, [maxAmp, maxTau, 1e6]))
    popt, pcov = curve_fit(riseTimeFunc, xData, yData)
    #popt, pcov = curve_fit(riseTimeFunc, xData, yData)
    fitAmp = popt[0]
    fitTau = popt[1]
    fitOffset = popt[2]
    #array([ 2.43708906,  1.        ,  0.35015434])
    #plt.plot(xData, riseTimeFunc(xData, *popt), label='fit: a=%5.3f, tau=%5.3f, off = %5.3f' % tuple(popt))
    plt.plot(xData,yGuess)
    plt.plot(xData, riseTimeFunc(xData, *popt))
    plt.plot(xData, yData, 'x')
    
    fitLegendString = 'Fit ' + 'Tau = ' + str(fitTau) + 'Amplitude ' + str(fitAmp)

    plt.legend(['Initial guess', 'fit guess', fitLegendString])
    plt.show()

    #popt, pcov = curve_fit(func, xdata, ydata, bounds=(0, [3., 1., 0.5]))

    #>>> plt.plot(xdata, func(xdata, *popt), 'g--',
    #...          label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))

    return fitAmp, fitTau, popt, pcov 