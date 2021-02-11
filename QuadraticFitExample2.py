import itertools
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.colors import LightSource
from CSVRead import CSVRead
from astropy.stats import sigma_clip
from RemoveHotPixels import RemoveHotPixels

def poly_matrix(x, y, order=2):
    """ generate Matrix use with lstsq """
    ncols = (order + 1)**2
    G = np.zeros((x.size, ncols))
    ij = itertools.product(range(order+1), range(order+1))
    for k, (i, j) in enumerate(ij):
        G[:, k] = x**i * y**j
    return G


#Read in some Data
fileName = 'C:\Data\TestData/Flatfield900_2.csv'
csvData = CSVRead(fileName)


#filter the data
#sigma clip the data to find hot pixels
maskData = sigma_clip(csvData, sigma=5, maxiters=5)
plt.imshow(maskData)
plt.title('image after background subtraction and clip')
plt.colorbar()
plt.show(block = True)


#remove hot pixels
dataHPR = RemoveHotPixels(maskData.data,maskData.mask)

csvData = dataHPR

xSize = csvData.shape[0]
ySize =  csvData.shape[1]
numElements = xSize*ySize

#Build up vector of x,y,z data
#My grid
x = np.linspace(-ySize/2, (+ySize/2)-1, ySize)
y = np.linspace(-xSize/2, (+xSize/2)-1, xSize)
xv, yv = np.meshgrid(x, y)
xx = xv.flatten()
yy = yv.flatten()
zz = csvData.flatten()

flattenData = []
for index in range(0, numElements-1):
    currentCoOrd = [xx[index], yy[index], zz[index]]
    flattenData.append(currentCoOrd)
    #print(xx[index])
    #print(flattenData)
flattenData = np.array(flattenData)
print(flattenData[0])
print(flattenData[1])
data = flattenData



#Example points
#points = np.array([[-320, -240, 1000],
#                   [-319, -240, 1001],
#                   ....
#                   [320, -240, 999]])

ordr = 2  # order of polynomial
x, y, z = data.T
#x, y = x - x[0], y - y[0]  # this improves accuracy

# make Matrix:
G = poly_matrix(x, y, ordr)
# Solve for np.dot(G, m) = z:
m = np.linalg.lstsq(G, z)[0]


# Evaluate it on a grid...
nx, ny = 30, 30
xx, yy = np.meshgrid(np.linspace(x.min(), x.max(), nx),
                     np.linspace(y.min(), y.max(), ny))
GG = poly_matrix(xx.ravel(), yy.ravel(), ordr)
zz = np.reshape(np.dot(GG, m), xx.shape)

# Plotting (see http://matplotlib.org/examples/mplot3d/custom_shaded_3d_surface.html):
fg, ax = plt.subplots(subplot_kw=dict(projection='3d'))
ls = LightSource(270, 45)
rgb = ls.shade(zz, cmap=cm.gist_earth, vert_exag=0.1, blend_mode='soft')
surf = ax.plot_surface(xx, yy, zz, rstride=1, cstride=1, facecolors=rgb,
                       linewidth=0, antialiased=False, shade=False)
ax.plot3D(x, y, z, "o")

fg.canvas.draw()
plt.show(block = True)

# Evaluate it on a grid...
nx, ny = 640, 480
xx, yy = np.meshgrid(np.linspace(x.min(), x.max(), nx),
                     np.linspace(y.min(), y.max(), ny))
GG = poly_matrix(xx.ravel(), yy.ravel(), ordr)
zz = np.reshape(np.dot(GG, m), xx.shape)




bgSubtratedData = csvData-zz

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