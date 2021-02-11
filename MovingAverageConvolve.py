import os
import matplotlib.pyplot as plt
import numpy as np


def MovingAverageConvolve(data, windowSize, bPlot):
    fig, ax = plt.subplots()
    nPoints = len(data)
    xData = np.linspace(0, nPoints, nPoints, endpoint=True)
    ax.plot(xData, data, label="Original")
    # Compute moving averages using different window sizes
    window_lst = ([windowSize])
    y_avg = np.zeros((len(window_lst) , nPoints))
   
    avg_mask = np.ones(windowSize) / windowSize
    y_avg[0, :] = np.convolve(data, avg_mask, 'same')
    # Plot each running average with an offset of 50
    # in order to be able to distinguish them
    y_avg[0, 0:windowSize] = data[0:windowSize]
    y_avg[0, -windowSize:] = data[-windowSize:]
    ax.plot(xData, y_avg[0, :] , label=windowSize)
    # Add legend to plot
    
    ax.legend()
    plt.show()
    
    y_avg = y_avg[0]
    return y_avg

    
    
