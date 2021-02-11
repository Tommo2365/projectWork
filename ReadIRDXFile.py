import numpy as np
import struct
import matplotlib.pyplot as plt
import os


def ReadIRDXFile(fileName, imageHeight, imageWidth, startByte):

    #Function ReadIRDXFile 
    #Opens IRDXFile (single Image from ImagePro) 'fileName' of size imageHeight x imageWidth and resturns a 2D array of shape (imageHeight x imageWidth)
    #Inputs: fileName : string of fileName eg 'C:\Data\MyFile.erfx'
    #        imageHeight: integer the number of pixels (in vertical direction) eg for 640x480 image, imageHeight = 480
    #        imageWidth: integer the number of pixels (in horizontal direction) eg for 640x480 image, imageWidth = 640
    #        startByte: a hard coded magicNumber for erfx files, version 4, startByte = 218, eg header runs from bytes 1:217, image Starts at byte 218
    #Ouptuts: dataArray: float array of 2D Array data of shape (imageHeight x imageWidth)
    
    #Calculate the number of bytes in the frame
    endByte  = startByte + (imageHeight*imageWidth*2)#There are two bytes ber pixel
    
    #Define the number of elements in the output array (i.e. the total number of pixels per frame)
    totalElements = (imageHeight*imageWidth)#There are two bytes ber pixel

    ###############################################BEGIN READ DATA
    with open(fileName, mode='rb') as file: # b is important -> binary
        fileContent = file.read()
        data = struct.unpack('>' + str(totalElements) + 'H', fileContent[startByte:endByte])
    ############################################### END READ DATA

    #Reshape the array into a 3D dataCube
    dataArray = np.reshape(data, ( imageWidth, imageHeight))

    #display the image
    plt.imshow(dataArray)
    plt.title('ReadData')
    plt.colorbar()
    plt.show(block = True)

    return dataArray

