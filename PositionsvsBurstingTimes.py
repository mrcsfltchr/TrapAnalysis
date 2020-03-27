#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 10:18:32 2020

@author: marcus
"""

# This file will define a script to correlate bursting time with position in a video.
# To ensure self completeness bursting times will be found from the raw intensity data in this script

import pandas as pd
import sys
import glob
from getBurstingTime import get_bursting_time
import numpy as np
from matplotlib import pyplot as plt

if __name__ == '__main__':
    # we use glob to get a list of file paths for the trap positions files. The name pattern is defined here.
    
    positions_names = 'trap_positions_*.csv'
    
    debug = True
    
    if len(sys.argv) > 1:
        dpath = sys.argv[1]

    else:
        print("Haven't entered directory path as Command Line option")
        sys.exit()
    
    if len(sys.argv) > 2:
        opath = sys.argv[2]
        if debug:
            print(opath)        
    else:
        print("Haven't given an output path name pattern as Command Line option")
        
        sys.exit()
    
    
TPfile_list = glob.glob(dpath+'/'+positions_names)

Ifile_list = []

for file in TPfile_list:
    Ifile_list.append(dpath+'/'+'detected_at_beginning_non_filtered_Intensities_'+file[file.find('tions')+6:])
    
if debug:
    
    print(TPfile_list[2])
    print(Ifile_list[2])
    
for i in range(0,len(TPfile_list)):
    
    # select matching file paths
    TPfile = TPfile_list[i]
    Ifile = Ifile_list[i]
    
    #load data
    positions =  np.loadtxt(TPfile,delimiter = ',')
    dfI = pd.read_csv(Ifile)
    
    #create a new data frame with bursting times
    
    dfBT = get_bursting_time(dfI)
    

    
    
    # ensure that the data frame is ordered same as the positions.
    
    BTarray = []
    missing_labels = []
    for i in range(0,len(positions[:,0])):
        #label = str(int(positions[:,0][i]))
        #need to force label to be in right format
        label = str(int(positions[:,0][i]))
        if len(label) == 1:
            label = '00'+label
        elif len(label) ==2:
            label = '0'+label
        
        try:
            BTarray.append(dfBT[label][0])
        except KeyError:
            print(label)
            missing_labels.append(i)
            continue

    BTarray  = np.array(BTarray)
    
    
    print('Bursting time numpy array ', BTarray)
    offset = 0
    print(missing_labels)
    for j in missing_labels:
        j -= offset
        print(positions.shape)        
        positions = np.vstack((positions[:j,:], positions[j+1:,:]))

        offset +=1
    plt.scatter(positions[:,2],positions[:,1],s=10,c=BTarray)
    
    plt.show()
    

