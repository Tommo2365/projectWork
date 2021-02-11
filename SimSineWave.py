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

def SimSineWave(xData, amplitude, frequency, phase, offset):
    simData = amplitude*np.sin((frequency*xData) + phase) + offset
    return simData