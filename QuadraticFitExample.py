#NOT WORKING DUE TO X, Y SIZE ERROR, NEEDS DEBUGGING

import numpy as np
import scipy.linalg
from mpl_toolkits.mplot3d import Axes3D
from CSVRead import CSVRead
import matplotlib.pyplot as plt
import cv2

# some 3-dim points
mean = np.array([0.0,0.0,0.0])
cov = np.array([[1.0,-0.5,0.8], [-0.5,1.1,0.0], [0.8,0.0,1.0]])
data = np.random.multivariate_normal(mean, cov, 50)

#Read in some Data
fileName = 'C:\Data\TestData/Flatfield900_2.csv'
csvData = CSVRead(fileName)
xSize = csvData.shape[0]
ySize =  csvData.shape[1]
numElements = xSize*ySize
X1,Y1 = np.meshgrid(np.arange(-xSize/2, xSize/2, np.min(csvData)), np.arange(-ySize/2, ySize/2, np.max(csvData)))


x = np.linspace(-ySize/2, (+ySize/2)-1, ySize)
y = np.linspace(-xSize/2, (+xSize/2)-1, xSize)
xv, yv = np.meshgrid(x, y)
xx = xv.flatten()
yy = yv.flatten()
zz = csvData.flatten()

#Build up vector of x,y,z data
flattenData = []
for index in range(0, numElements-1):
    currentCoOrd = [xx[index], yy[index], zz[index]]
    flattenData.append(currentCoOrd)
    #print(xx[index])
    #print(flattenData)
flattenData = np.array(flattenData)
    

# regular grid covering the domain of the data
X,Y = np.meshgrid(np.arange(-3.0, 3.0, 0.5), np.arange(-3.0, 3.0, 0.5))
XX = X.flatten()
YY = Y.flatten()

#My grid
data = flattenData
XX = xx
YY = yy
X = xv
Y = yv

order = 2    # 1: linear, 2: quadratic
if order == 1:
    # best-fit linear plane
    A = np.c_[data[:,0], data[:,1], np.ones(data.shape[0])]
    C,_,_,_ = scipy.linalg.lstsq(A, data[:,2])    # coefficients
    
    # evaluate it on grid
    Z = C[0]*X + C[1]*Y + C[2]
    
    # or expressed using matrix/vector product
    #Z = np.dot(np.c_[XX, YY, np.ones(XX.shape)], C).reshape(X.shape)

elif order == 2:
    # best-fit quadratic curve
    A = np.c_[np.ones(data.shape[0]), data[:,:2], np.prod(data[:,:2], axis=1), data[:,:2]**2]
    C,_,_,_ = scipy.linalg.lstsq(A, data[:,2])
    
    # evaluate it on a grid
    #Z = np.dot(np.c_[np.ones(XX.shape), XX, YY, XX*YY, XX**2, YY**2], C).reshape(X.shape)
    Z1 = np.dot(np.c_[np.ones(XX.shape), XX, YY, XX*YY, XX**2, YY**2], C)
    Z = Z1.reshape(ySize, xSize)

fig =plt.figure
plt.imshow(Z)

# plot points and fitted surface
fig = plt.figure()
ax = fig.gca(projection='3d')

ax.plot_surface(X, Y, Z, rstride=1, cstride=1, alpha=0.2)
#ax.scatter(data[:,0], data[:,1], data[:,2], c='r', s=50)
plt.xlabel('X')
plt.ylabel('Y')
ax.set_zlabel('Z')
ax.axis('equal')
ax.axis('tight')
plt.show()