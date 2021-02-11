import numpy as np
from scipy.signal import convolve2d
from scipy.ndimage import generic_filter
import time

def Convolve2DKernal(data):
    kernel = np.ones((3, 3))
    kernel[1, 1] = 0

    neighbor_sum = convolve2d(data, kernel, mode='same',boundary='fill', fillvalue=0)

    num_neighbor = convolve2d(np.ones(data.shape), kernel, mode='same',boundary='fill', fillvalue=0)

    return neighbor_sum / num_neighbor
