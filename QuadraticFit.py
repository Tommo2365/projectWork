

import itertools
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.colors import LightSource
from CSVRead import CSVRead
from astropy.stats import sigma_clip
from RemoveHotPixels import RemoveHotPixels

def QuadraticFit(csvData, bPlot):

    #function QuadraticFit. Takes an N x M numpy array, eg an image and fits a quadratic surface to the pixel values.
    #Inputs:  csvData: 2D numpy array eg an image with size N x M of temperatures
    #         bPlot: a boolean == True if you want to plot the outputs 
    #Ouputs:
    #        bgSubtratedData: a 2D numpy array which has had a the quadratic background removed 
    #        background: a 2D numpy array which is the fitted background function.
    

    #Ancillary function that creates matrix for least sqaures
    def poly_matrix(x, y, order=2):
        """ generate Matrix use with lstsq """
        ncols = (order + 1)**2
        G = np.zeros((x.size, ncols))
        ij = itertools.product(range(order+1), range(order+1))
        for k, (i, j) in enumerate(ij):
            G[:, k] = x**i * y**j
        return G
    #Find the size of the image array
    xSize = csvData.shape[0]
    ySize =  csvData.shape[1]
    numElements = xSize*ySize

    #Build up vector of x,y,z data
    x = np.linspace(-ySize/2, (+ySize/2)-1, ySize)
    y = np.linspace(-xSize/2, (+xSize/2)-1, xSize)
    xv, yv = np.meshgrid(x, y)
    xx = xv.flatten()
    yy = yv.flatten()
    zz = csvData.flatten()

    #Very over contorted way of building of a nx3 vector of x,y,z data, where n = N x M (number of pixels in the image)
    flattenData = []

    #flattenData = [xx,yy,zz]
    for index in range(0, numElements-1):
        currentCoOrd = [xx[index], yy[index], zz[index]]
        flattenData.append(currentCoOrd)
        #print(xx[index])
        #print(flattenData)
    flattenData = np.array(flattenData)
    
    #The data usef for the fit is the nx3 vector
    data = flattenData

    ordr = 2  # order of polynomial, used in the poly_matrix function
    
    #split up the data again into the x,y,z components and transpose to be 3xn
    x, y, z = data.T
    #x, y = x - x[0], y - y[0]  # this improves accuracy

    # make Matrix:
    G = poly_matrix(x, y, ordr)
    # Solve for np.dot(G, m) = z:
    m = np.linalg.lstsq(G, z, rcond=None)[0]

    if bPlot == True:
        # Evaluate it on a grid for plotting...
        
        #Make a small meshgrid to evalute the fit
        nx, ny = 30, 30
        xx, yy = np.meshgrid(np.linspace(x.min(), x.max(), nx),
                             np.linspace(y.min(), y.max(), ny))
        GG = poly_matrix(xx.ravel(), yy.ravel(), ordr)
        backgroundSubSample = np.reshape(np.dot(GG, m), xx.shape)

        # Plotting (see http://matplotlib.org/examples/mplot3d/custom_shaded_3d_surface.html):
        fg, ax = plt.subplots(subplot_kw=dict(projection='3d'))
        ls = LightSource(270, 45)
        rgb = ls.shade(backgroundSubSample, cmap=cm.gist_earth, vert_exag=0.1, blend_mode='soft')
        surf = ax.plot_surface(xx, yy, backgroundSubSample, rstride=1, cstride=1, facecolors=rgb,
                               linewidth=0, antialiased=False, shade=False)
        ax.plot3D(x, y, z, "o")

        fg.canvas.draw()
        plt.show(block = True)

    # Evaluate the fit on a grid...
    nx, ny = ySize, xSize
    xx, yy = np.meshgrid(np.linspace(x.min(), x.max(), nx),
                         np.linspace(y.min(), y.max(), ny))
    GG = poly_matrix(xx.ravel(), yy.ravel(), ordr)
    background = np.reshape(np.dot(GG, m), xx.shape)
    bgSubtratedData = csvData-background

    offset = np.min(bgSubtratedData[:])
    bgSubtratedData = bgSubtratedData-offset
    background = background - offset



    

    if bPlot == True:
        #filter the data
        #sigma clip the data to find hot pixels
        maskData = sigma_clip(bgSubtratedData, sigma=5, maxiters=5)

        #remove hot pixels
        dataHPR = RemoveHotPixels(maskData.data,maskData.mask)
        dataHPR = dataHPR -np.min(dataHPR[:])


        plt.imshow(dataHPR)
        plt.title('image after background subtraction and clip')
        plt.colorbar()
        plt.show(block = True)

    return bgSubtratedData, background
   