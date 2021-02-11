import numpy as np

def RemoveHotPixels(data, bHot):
    #function RemoveHotPixels
    #Inputs:  data: 2D numpy array eg an image
    #         bHot: a numpy array of booleans eg bArray =  np.zeros((4, 4), dtype=bool) for array of FALSE
    #Ouputs:
    #        data: the data with hot pixels replaced by mean of nearest neihgbours  with 3x3 kernal size 
    
    #Find the total number of hot pixels in the array data
    nHotPixels = sum(sum(bHot))

    #Find the indices of the hot pixels
    hotPixelIndices = np.where(bHot == True)
    hotPixelIndices = np.array(hotPixelIndices)

    #Main loop through each of the hot pixels
    for n in range(0,nHotPixels):
        #Initalise some loop variables
        count = 0
        pixelVal = []
        currentPixelCoOrd = hotPixelIndices[:, n]
        
        #Loop through rows and columns of 3x3 neighbourhood of pixels
        for rows in [currentPixelCoOrd[0]- 1, currentPixelCoOrd[0], currentPixelCoOrd[0]+1]:
            for columns in [currentPixelCoOrd[1]- 1, currentPixelCoOrd[1], currentPixelCoOrd[1]+1]:
                if rows == currentPixelCoOrd[0]:
                    if columns == currentPixelCoOrd[1]:
                        #If the current pixel co-ordinate in the loop is the same as the hot pixel 
                        continue
                if rows < 0 or rows > (data.shape[0])-1:#make sure the row index is within bounds
                    print(rows)
                    continue
                if columns < 0 or columns > (data.shape[1])-1: #make sure the column index is within bounds
                    print(columns)
                    continue
                #row all rows and columns in the neighbourhood find the pixel value
                neighbourPixelVal = data[rows, columns]

                if type(neighbourPixelVal) == type(True):
                    #skip if this pixel is also a hot pixel
                    continue
                    
                
                #sum up the pixel values (to calculate mean later)
                pixelVal.append(neighbourPixelVal) 
                
                #counter of the number of pixels used in the cummulative seum
                count = count + 1
                
        #calulte the median of the neigbourhood pixels
        replacementValue = np.median(np.array(pixelVal))
        
        #replace the hot pixel by the mean
        data[currentPixelCoOrd[0],currentPixelCoOrd[1]] = replacementValue

    return data

