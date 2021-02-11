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
def SimPulseWave(xData, pulseWidth, dutyCycle, nHarmonics, bPlot):
    simData = np.zeros(len(xData))
    thisHarmonic = np.array([])
    for k in range(1, nHarmonics+1):
        thisHarmonic = (pulseWidth/dutyCycle + (2/k*pi)*np.sin((pi*k*pulseWidth)/dutyCycle)*np.cos(2*pi*k*xData/dutyCycle))

        simData = simData + thisHarmonic

    
    if bPlot == True:
        plt.plot(simData)
        plt.show()   
    return simData