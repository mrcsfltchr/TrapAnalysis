#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 16:19:38 2020

@author: marcus
"""
# Plan is to load a csv file containing columns of time series data, where data in each column is the measured Area of a GUV over the course of the experiment.
# We aim to determine the initial area of the GUV from this data. This will be taken to be the average area over an appropriate number of time points from the start of data recorded.
# The conclusion of the script will be to output this initial area and a reference, the GUV label, so that we can later correlate the initial area with the time at which each GUV burst.


import numpy as np
import pandas as pd
import sys
import glob

def getUID(filename):
    
    if filename[-14] == 's':
        uid = 0+int(filename[-13])
    else:
        uid = filename[-14:-12]
        
    return uid


if __name__ == '__main__':
    
    #construct a rudimentary CLI to enter options:
    #   - Directory path containing the sequence of files
    #   - Name of an output file naming pattern
    #   - other options as necessary
    
#hardcoded parameters:
    name_root = "Detected_at_beginning_non_filtered_Areas*.csv"
    
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
        
print(dpath+'/'+name_root)
file_list = glob.glob(dpath+'/'+name_root)
if debug:
    
    print(file_list)

for file in file_list:
    
    df = pd.read_csv(file)
    
    nearstart_df = df.iloc[:5]
    
    initial_areas = nearstart_df.mean(axis = 0)
    
    initial_areas = initial_areas.T
    
    uid = getUID(file)
    
    initial_areas.to_csv(dpath+'/'+'Initial_Areas_Pos'+opath+str(uid)+'.csv')
    
