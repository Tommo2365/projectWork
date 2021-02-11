

import numpy as np
from skimage.measure import profile_line
from skimage import io
import matplotlib.pyplot as plt
import cv2

def LineProfile(dataArray, startPoint, endPoint, lineWidth):
    #startPoint = (y1, x1) i.e. columns, rows
    #endPoint =  (x2, y2)
    #LineWidth, number of pixels normal to the profile
    #Example
    #profile = profile_line(csvData, (240, 0), (240,640), 5)
    profile = profile_line(dataArray, startPoint, endPoint, 5)
    return profile