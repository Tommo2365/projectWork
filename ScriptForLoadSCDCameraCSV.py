import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import pandas as pd
from CSVRead import CSVRead
from MovingAverageConvolve import MovingAverageConvolve
from RemoveHotPixels import RemoveHotPixels
from astropy.stats import sigma_clip
#from SimSquareWave import SimSquareWave

#Define File name to read the data from
#fileName = 'C:\\Data\\PicoLog\\CSV Ambient test of boards original orientation repeated.csv'
fileName = 'C:\\Users\\thutchinson\\Desktop\\3.9B Cal\\Light_Frame.csv'
print(fileName)

#Read in the csv file as an numpy array of strings
bHeader = True
csvData, header = CSVRead(fileName,bHeader,2)

#Pull out the column headers
columnHeaders = csvData[0]

#Find the numnber of rows of numeric data
numDataRows = len(csvData)
numberCols = np.shape(csvData)[1]-1

#Pull out the data
data = csvData[0:numDataRows]
numberCols = np.shape(data)[1]-1
dataArray = np.ones([numDataRows,numberCols])

for k in range (0,numDataRows):
    for w  in range(0, numberCols):
        thisElement = data[k,w]
        thisFloat = float(thisElement)
        dataArray[k,w] = thisFloat
        

plt.imshow(dataArray)
plt.title('Frame1')
plt.show()
#time.sleep(0.3)

maskData = sigma_clip(dataArray, sigma=5, maxiters=5)
plt.imshow(1*(maskData.mask))
nClippedPixes = int(sum(sum(maskData.mask)))
plt.title([str(nClippedPixes)  + 'five sigma pixels'])
plt.colorbar()
plt.show(block = True)
   
#remove hot pixels
dataHPR = RemoveHotPixels(maskData.data,maskData.mask)


plt.imshow(dataHPR)
plt.title('image after correction')
plt.colorbar()
plt.show(block = True)




#plt.plot(SimSquareWave)

    

