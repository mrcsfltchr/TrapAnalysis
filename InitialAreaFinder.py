#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 16:19:38 2020

@author: marcus
"""
# Plan is to load a csv file containing columns of time series data, where data in each column is the measured Area of a GUV over the course of the experiment.
# We aim to determine the initial area of the GUV from this data. This will be taken to be the average area over an appropriate number of time points from the start of data recorded.
# The conclusion of the script will be to output this initial area and a reference, the GUV label, so that we can later correlate the initial area with the time at which each GUV burst.



import pandas as pd
import sys
import glob
from getBurstingTime import get_bursting_time
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
    Aname_root = "Detected_at_beginning_non_filtered_Areas*.csv"
    
    
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
        
print(dpath+'/'+Aname_root)
Afile_list = glob.glob(dpath+'/'+Aname_root)

#to ensure that complementary Intensity data and Area data files are handle simulateneously 
# we construct the list of INtensity file paths from the Area file paths found
Ifile_list = []

for file in Afile_list:
    Ifile_list.append(dpath+'/'+'detected_at_beginning_non_filtered_Intensities_'+file[file.find('Areas')+5:])
    



if debug:
    
    print(Afile_list[2])
    print(Ifile_list[2])
    
    
for i in range(0,len(Afile_list)):
    
    Afile = Afile_list[i]
    Ifile = Ifile_list[i]
    
    dfA = pd.read_csv(Afile)
    dfI = pd.read_csv(Ifile)
    
    #get initial areas from the Area data
    
    nearstart_df = dfA.iloc[:5]
    
    initial_areas = nearstart_df.mean(axis = 0)
    
    initial_areas = initial_areas.to_frame()
    
    initial_areas = initial_areas.T.iloc[:,1:]
    #initial_area_dict = {}
    
    #for col in initial_areas.columns.values:
     #   initial_area_dict[col] = initial_areas[col]
        
    #initial_areas = pd.DataFrame.from_dict(initial_area_dict,  orient='index').transpose()
    
    
    # get bursting times from Intensity time series
    
    dfBT = get_bursting_time(dfI)
    
    #add a bursting times data to the initial areas data
    

    #initial_areas = initial_areas.append(dfBT)
    
    areasvsT = pd.concat([initial_areas,dfBT], axis = 0)
    
    areasvsT = areasvsT.T
    
    print(areasvsT)
    uid = getUID(Afile)
    
    areasvsT.to_csv(dpath+'/'+'Initial_Areas_vs_Bursting_Times_Pos'+opath+'_'+str(uid)+'.csv')
    
    
