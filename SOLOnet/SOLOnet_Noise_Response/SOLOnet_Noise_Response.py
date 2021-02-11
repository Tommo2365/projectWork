
#########################################  READ ME  #####################################################

# This software version only deals with the case where you are logging two variables at once. i.e ambient and target temperatures
##  To work in conjunction with Realterm. The 'display as' fucntion MUST be Acsii

#########################################  READ ME  #####################################################


import os
import re
import numpy as np
import pandas as pd
import string
import regex as rx
import time
from datetime import datetime
import array
import matplotlib.pyplot as plt
from matplotlib.pyplot import plot, draw, show, ion
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

# Open a diffrent directory
path = r'C:\temp'
os.chdir(path)
print("Please select a .txt file..." )

infile = filedialog.askopenfilename()

# print(os.getcwd())              # where is this file?
# print(os.listdir())             # list all the files in that directory

# Create a timestamp on the save file
now = datetime.now() 
timestamp = now.strftime("%Y%m%d_%H_%M_%S_")

# Open selected file and remove speical characters and spaces

#infile = "txtfile.txt"
outfile = timestamp + "Data.txt"

delete_list = ["\x03", "\x02", "\x01"," "] # choose strings to replace with, " "
fin = open(infile)
fout = open(outfile, "w+")
for line in fin:
    for word in delete_list:
       line = line.replace(word, "")
    fout.write(line)
fin.close()
fout.close()

# Reopen file

newfile = timestamp + "Data.csv"

refile = open(outfile)
nfile =  open(newfile, "w+")

# Keep track of number of lines
lc = 0                                                            
data = []

# Create an array
for row in refile:                              
    data.append(row) 
    lc+=1                                                       
refile.seek(0)                                  
nRows = len(data)

output = np.array([])

for index in range(0, nRows):
    thisElement = data[index]
    splitString = thisElement.split('x01')
    #print(thisElement)
    splitString2 = thisElement.split('\n')
    valueString = splitString2[0]
    #value = float(valueString)
    output = np.append(valueString,output)

#output2 = np.reshape(output, (int(nRows/2),2))

np.savetxt(timestamp + 'Data.csv', output, delimiter=',', fmt=['%s'], header=[])

print("Done...")


# Anaconda Prompt

#p#arser = argparse.ArgumentParser()
#parser.parse_args()

#parser.add_argument("run")
#args = parser.parse_args()
#print("working...")


