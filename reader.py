import os
import pprint
import struct
import argparse

import matplotlib.pyplot as plt
import numpy as np
import cv2

class Header():
    def __init__(self, data, bptr):
        self.data = data
        self.bptr = bptr
        self.keys = {
            'FileVersion': None,
            'ProductCode': None,
            'CameraType': None,
            'ImageWidth': None,
            'ImageHeight': None,
            'WindowTransmission': None,
            'FrameRate': None,
            'CalLabel1': None,
            'CalLabel2': None,
            'FrameDataType': None,
            'FrameMetaDataSize': None,
            'MetaDataPos': None
        }      
        self.HeaderSize = None

    def _readKeyASCII(self, data, bptr, nBytes):
        st = bptr
        end = st + nBytes
        key = struct.unpack(
            '<' + str(nBytes) + 's', data[st: end])[0].decode('ascii')
        return key, end    

    def _readKeyBoolean(self, data, bptr):
        st = bptr
        end = st + 1
        key = struct.unpack(
            '<?', data[st: end])[0]
        return key, end

    def _readKeyUInt16(self, data, bptr):
        st = bptr
        end = st + 2
        key = struct.unpack('<H', data[st: end])[0]
        return key, end

    def _readKeyUInt64(self, data, bptr):
        st = bptr
        end = st + 8
        key = struct.unpack('<q', data[st: end])[0]
        return key, end

    def dump(self):
        pprint.pprint(self.keys)

    def parse(self):
        self.keys['FileVersion'], self.bptr = self._readKeyUInt16(
            self.data, self.bptr)
        self.keys['ProductCode'], self.bptr = self._readKeyUInt16(
            self.data, self.bptr)
        self.keys['CameraType'], self.bptr = self._readKeyUInt16(
            self.data, self.bptr)
        self.keys['ImageWidth'], self.bptr = self._readKeyUInt16(
            self.data, self.bptr)
        self.keys['ImageHeight'], self.bptr = self._readKeyUInt16(
            self.data, self.bptr)
        self.keys['WindowTransmission'], self.bptr = self._readKeyUInt16(
            self.data, self.bptr)
        FrameRate, self.bptr = self._readKeyUInt16(
            self.data, self.bptr)
        self.keys['FrameRate'] = FrameRate//100

        # File versions dependent logic.
        #
        if self.keys['FileVersion'] == 1:
            self.keys['CalLabel1'], self.bptr = self._readKeyASCII(
                self.data, self.bptr, 32)
            self.keys['CalLabel2'], self.bptr = self._readKeyASCII(
                self.data, self.bptr, 32)
            self.keys['FrameMetaDataSize'] = 20
            self.keys['HeaderSize'] = 78          
        elif self.keys['FileVersion'] == 2:
            self.keys['CalLabel1'], self.bptr = self._readKeyASCII(
                self.data, self.bptr, 32)
            self.keys['CalLabel2'], self.bptr = self._readKeyASCII(
                self.data, self.bptr, 32)
            self.keys['FrameDataType'], self.bptr = self._readKeyBoolean(
                self.data, self.bptr)
            self.keys['FrameMetaDataSize'], self.bptr = self._readKeyUInt16(
                self.data, self.bptr)
            self.keys['HeaderSize'] = 81    
        elif self.keys['FileVersion'] == 3 or self.keys['FileVersion'] == 4:
            self.keys['CalLabel1'], self.bptr = self._readKeyASCII(
                self.data, self.bptr, 96)
            self.keys['CalLabel2'], self.bptr = self._readKeyASCII(
                self.data, self.bptr, 96)
            self.keys['FrameDataType'], self.bptr = self._readKeyBoolean(
                self.data, self.bptr)
            self.keys['FrameMetaDataSize'], self.bptr = self._readKeyUInt16(
                self.data, self.bptr)
            self.keys['MetaDataPos'], self.bptr = self._readKeyUInt64(
                self.data, self.bptr)
            self.keys['HeaderSize'] = 217

class Image():
    def __init__(self, data, header):
        self.data = data
        self.header = header

        self.FrameSizePixels = self.header.keys['ImageWidth'] * \
            self.header.keys['ImageHeight']
        self.FrameSizeBytes_Data = (self.FrameSizePixels * 2)
        self.FrameSizeBytes_Full = self.FrameSizeBytes_Data + \
            self.header.keys['FrameMetaDataSize']

    def _readFrameDataInt8(self, data, bptr, nBytes):
        st = bptr
        end = st + nBytes
        frameData = np.array(
            struct.unpack('<' + str(nBytes) + 'B', data[st: end]))
        return frameData, end

    def _readFrameMetaDouble(self, data, bptr):
        st = bptr
        end = st + 8
        key = struct.unpack('<d', data[st: end])[0]
        return key, end

    def _readFrameMetaFloat(self, data, bptr):
        st = bptr
        end = st + 4
        key = struct.unpack('<f', data[st: end])[0]
        return key, end

    def _readFrameMetaInt32(self, data, bptr):
        st = bptr
        end = st + 4
        key = struct.unpack('<i', data[st: end])[0]
        return key, end

    def read(self, index):
        bptr = self.header.keys['HeaderSize'] + (
            index * self.FrameSizeBytes_Full)
        frameData, bptr = self._readFrameDataInt8(
            self.data, bptr, self.FrameSizeBytes_Data)
        frameTemperature = frameData[::2] + (frameData[1::2] << 8)

        # Read footer metadata.
        #
        frameMetaData = {}
        frameMetaData['Ambient'], bptr = self._readFrameMetaFloat(
            self.data, bptr)
        if self.header.keys['FileVersion'] < 4:
            frameMetaData['Emissivity'], bptr = self._readFrameMetaFloat(
                self.data, bptr)
        else:
            frameMetaData['Emissivity'], bptr = self._readFrameMetaDouble(
                self.data, bptr)
        frameMetaData['BgTemp'], bptr = self._readFrameMetaFloat(
            self.data, bptr)
        frameMetaData['ThermocoupleTemp'], bptr = self._readFrameMetaFloat(
            self.data, bptr)
        frameMetaData['ThermocoupleStatus'], bptr = self._readFrameMetaInt32(
            self.data, bptr)
        frameMetaData['MaxTemp'], bptr = self._readFrameMetaFloat(
            self.data, bptr)
        frameMetaData['MeanTemp'], bptr = self._readFrameMetaFloat(
            self.data, bptr)
        frameMetaData['MinTemp'], bptr = self._readFrameMetaFloat(
            self.data, bptr)
        frameMetaData['MaxIndex'], bptr = self._readFrameMetaInt32(
            self.data, bptr)
        frameMetaData['MinIndex'], bptr = self._readFrameMetaInt32(
            self.data, bptr)

        return frameTemperature, frameMetaData

class ERFX():
    def __init__(self, filename):
        self.filename = filename
        self.data, self.bptr = self._read(filename)

        # Initialise header and parse.
        #
        self.header = Header(self.data, self.bptr)
        self.header.parse()

        # Initialise image.
        #
        self.image = Image(self.data, self.header)

        # Calculate number of frames.
        #
        fileSize = os.stat(filename).st_size
        self.nFrames = (fileSize - self.header.keys['HeaderSize']) // \
            self.image.FrameSizeBytes_Full
        
    def _read(self, filename):
        with open(filename, 'rb') as f:
            data = f.read() 
        return data, 0   

    def getSingleFrame(self, index):
        frameTemperature, frameMetaData = self.image.read(index)  
        frameTemperature = np.reshape(frameTemperature, newshape=(
            self.header.keys['ImageHeight'], 
            self.header.keys['ImageWidth']))
        return frameTemperature, frameMetaData

    def getMultiFrames(self, frameStart, frameEnd):
        frameTemperatures = []
        frameMetaDatas = []
        for idx in range(frameStart, frameEnd+1):
            print("Loading frame " + str(frameStart+idx+1) + " of " + \
                str(frameEnd-frameStart+1))
            frameTemperature, frameMetaData = self.getSingleFrame(idx)
            frameTemperatures.append(frameTemperature)
            frameMetaDatas.append(frameMetaData)
        return frameTemperatures, frameMetaDatas
                
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help="file name", action="store", default="text.erfx")
    parser.add_argument("-d", help="display", action="store_true")
    parser.add_argument("-s", help="start frame", action="store", default=0, type=int)
    parser.add_argument("-e", help="end frame", action="store", default=10, type=int)
    parser.add_argument("-fps", help="display fps", action="store", default=10, type=int)
    args = parser.parse_args()

    erf = ERFX(args.f)
    frameTemperatures, frameMetaDatas = erf.getMultiFrames(args.s, args.e)

    if args.d:
        delay = int(1000//float(args.fps))
        cv2.namedWindow('movie', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('movie', 800, 600)
        for ft in frameTemperatures:
            ft = cv2.normalize(
                ft, 
                dst=None,
                alpha=0, beta=255, 
                norm_type=cv2.NORM_MINMAX).astype(np.uint8)
            cv2.imshow("movie", ft)
            cv2.waitKey(delay)
    
    
