import numpy as np
from scipy import ndimage


def NearestNeighbourAverage(data, bHot):
    
    #kernel for 8 neighrest neightbours 
    kernel = np.ones((3, 3))
    kernel[1, 1] = 0

    result = ndimage.generic_filter(data, np.nanmean, footprint=bHot, mode='constant', cval=np.NaN)

    return result
