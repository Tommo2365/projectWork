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
#from RiseTimeFunc import FitRiseTime 
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
try:
    from LAND_comms_equipment.eurothermModbus import s2000Modbus
except:
    from eurothermModbus import s2000Modbus
import math
from CSpot import CSpot

#Initialize the Spot 
config = configparser.ConfigParser()
config.read('etc/config/config.ini')
spot = CSpot(config['spot'])#make a spot instance
allSpotRawValues, spotElapsedTime = spot.ReadRegister(1, 100, 246) #246

modbusAddressBrightD1 = int(204)
modbusAddressDarkD1 =  int(200)

modbusAddressBrightD2 = int(206)
modbusAddressDarkD2 =  int(202)

print(str(allSpotRawValues))
            

 

