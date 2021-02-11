import numpy as np

def String2Float(csvData):
    #Find the numnber of rows of numeric data
    numDataRows = len(csvData)
    
    #Pull out the data
    data = csvData[0:numDataRows]
    numberCols = np.shape(data)[1]-1
    dataArray = np.ones([numDataRows,numberCols])

    for k in range (0,numDataRows):
        for w  in range(0, numberCols):
            thisElement = data[k,w]
            thisFloat = float(thisElement)
            dataArray[k,w] = thisFloat
    return dataArray