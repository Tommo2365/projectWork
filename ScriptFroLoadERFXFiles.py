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
from RiseTimeFunc import FitRiseTime 
import matplotlib.animation as animation
from matplotlib import style
from tkinter.filedialog import askdirectory
import numpy
import scipy
from scipy.optimize import curve_fit
from pytictoc import TicToc

from reader import ERFX
fileName = 'C:\\Users\\tgodden\\Desktop\\ERFXfiles\\Flatfield.erfx' 
erf = ERFX(fileName)
header = erf.header.dump()
print(header)
nFrames = erf.nFrames
frameTemperatures, frameMetaDatas = erf.getMultiFrames(0, 20-1)
plt.imshow(frameTemperatures[0])
plt.show()

disp('')

