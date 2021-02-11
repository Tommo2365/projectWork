import numpy
import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy.signal import butter, lfilter
from scipy.signal import freqz
from scipy.signal import sosfreqz
from scipy.signal import blackman

def BandPassFilter(data, lowcut, highcut, fs, order, bWindowData):
   
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')

    b=b/a[0]
    a= a/a[0]
    #For higher order filters use second order signal
    sos = butter(6, [low, high], btype='bandpass', output='sos')
    w, h = sosfreqz(sos, round(fs/2))
    
    if bWindowData == True:
        #Uss a blackman window accross the data
        window = blackman(len(data))
        data = data*window
    


    
    #w, h = freqz(b, a, round(fs/2))
    plt.plot((fs * 0.5 / np.pi) * w, abs(h), label="order = %d" % order)

    plt.plot([0, 0.5 * fs], [np.sqrt(0.5), np.sqrt(0.5)],
             '--', label='sqrt(0.5)')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Gain')
    plt.grid(True)
    plt.legend(loc='best')
    plt.show()

    fData = lfilter(b, a, data)

    
    
   
    return fData




    
    
