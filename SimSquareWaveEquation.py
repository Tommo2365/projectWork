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
import easygui
from easygui import msgbox, multenterbox

pi = numpy.pi
#pi =1
def SimSquareWaveEquation(xData, pulseWidth, nHarmonics, phaseOffset, amplitude):
    simData = np.zeros(len(xData))
    thisHarmonic = np.array([])
    for n in range(1, nHarmonics+1):
        k = (2*n)-1
        thisHarmonic = (1/k)*np.sin((k*pi*(xData-phaseOffset)/pulseWidth))

        simData = simData + thisHarmonic
    simData = (2/pi)*simData
    

    simData = simData+0.5
    simData = amplitude*simData
    
    bPlot = False
    if bPlot == True:
        plt.plot(simData)
        plt.show()   
    return simData