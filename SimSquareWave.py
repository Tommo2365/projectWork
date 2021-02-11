import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import pandas as pd
from CSVRead import CSVRead


def SimSquareWave(amplitude, nDataPoints, startDip, dipLength):
    # x axis values 
    x = [0,600,600.1,700,700.1,1000] 
    # corresponding y axis values 
    y = [0.34,0.34,0,0,0.34,0.34] 
  
    # plotting the points  
    plt.plot(x, y) 
  
    # naming the x axis 
    plt.xlabel('x - axis') 
    # naming the y axis 
    plt.ylabel('y - axis') 
  
    # giving a title to my graph 
    plt.title('perfect square wave!') 
  
    # function to show the plot 
    plt.show() 
    
    #Make a wave of amplitude 1 for all time
    simData = ....
    #Make the dip in the wave using the startDip and DipLength
    #simData[25:50] = 0...
    #Scale the waqve by the amplitude
    #multiple t
    #return simData