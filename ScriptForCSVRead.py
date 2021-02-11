import numpy
import numpy as np
import matplotlib.pyplot as plt
import csv


def CVS.Read(fileName)
fileName = str('C:\Data')
print('Loading File:    ' + fileName)

data = numpy.array([])
listData = []
#data = []

with open(fileName) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter = ',')
    #print(csv_reader)
    line_count = 0
    for row in csv_reader:
       # print(row)
        listData.append(row)
        data = np.append(data, row)
        line_count += 1
    csvData = np.array(listData)
    csvData = test.astype('float')
    print(f'Processed {line_count} lines ' + 'arraySize ' + str(csvData.shape))
    plt.imshow(csvData)
    plt.colorbar()
    plt.show()
    return 

    
    
