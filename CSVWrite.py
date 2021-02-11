import numpy
import numpy as np
import matplotlib.pyplot as plt
import csv

def CSVWrite(fileName, numpyArray):
    
    print('WritingFile File:    ' + fileName)

    with open(fileName,'w', newline = '') as csv_file:
        csv_writer= csv.writer(csv_file, delimiter = ',')
        
       # line_count = 0
        for row in numpyArray:
            csv_writer.writerow(row)
    
