import numpy as np
import struct
import matplotlib.pyplot as plt
import os


def ReadERFXFile(fileName, imageHeight, imageWidth, startByte):

    #Function ReadERFXFile 
    #Opens ERFXFile (movie from ImagePro) 'fileName' of size imageHeight x imageWidth and resturns a 3D array of shape (nFrames x imageHeight x imageWidth)
    #Inputs: fileName : string of fileName eg 'C:\Data\MyFile.erfx'
    #        imageHeight: integer the number of pixels (in vertical direction) eg for 640x480 image, imageHeight = 480
    #        imageWidth: integer the number of pixels (in horizontal direction) eg for 640x480 image, imageWidth = 640
    #        startByte: a hard coded magicNumber for erfx files, version 4, startByte = 218, eg header runs from bytes 1:217, image Starts at byte 218
    #Ouptuts: dataArray: float array of 3D movie data of shape (nFrames x imageHeight x imageWidth)
    #         nFramesInt, the number of frames of movie data, calulated from the fileSize-headerSize-footerSize
    
    #Calculate the number of bytes in 1 frame
    endByte  = startByte + (imageHeight*imageWidth*2)#There are two bytes ber pixel
    
    #Define the number of elements in the output array (i.e. the total number of pixels per frame)
    totalElements = (imageHeight*imageWidth)#There are two bytes ber pixel

    #Calculate fileSize in bytes
    statinfo = os.stat(fileName)
    statinfo.st_size

    #Use the modulo to work out the number of bytes in the footer
    metaDataNoBytes = (statinfo.st_size- startByte)%(2*totalElements)

    #Calculate the numnber of frames by subtracting the header and footer( metaData) from the total file size
    nFrames = np.floor((statinfo.st_size-(startByte)-metaDataNoBytes)/(2*totalElements))

    #Ensure the number of frames is an integer for indexing
    nFramesInt = int(nFrames)

    #Calculate the byte at which the frame data ends (last byte before footer metaData)
    endMovieByte = startByte + (nFramesInt*(imageHeight*imageWidth*2))

    ###############################################BEGIN READ DATA

    with open(fileName, mode='rb') as file: # b is important -> binary
        fileContent = file.read()
        #Read the first frame (for testting)
        dataFrame1 = struct.unpack('>' + str(totalElements) + 'H', fileContent[startByte:endByte])
        #Extract all the data in 'H':float format with >: big Endian
        allData =  struct.unpack('>' + str(nFramesInt*totalElements) + 'H', fileContent[startByte:endMovieByte])
    ############################################### END READ DATA
   
    
    #Reshape the array into a 3D dataCube
    dataArray = np.reshape(allData, (nFramesInt, imageWidth, imageHeight))

    return dataArray, nFramesInt

