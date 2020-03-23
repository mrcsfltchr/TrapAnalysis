#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 17:18:50 2019

@author: mjsf3
"""
import numpy as np
import pandas as pd

from glob import glob
import tifffile as tf
import sys
from scipy.optimize import curve_fit
import os



def get_flowrate_paths(dir_path):
    
    #first change the current working directory to the path. This is not essential now but for saving we want to make
    #new subdirectories in this directory to organise the files.
    
    initial_dir = os.getcwd()
    print(initial_dir)

    try:
        print('dirpath: ' , dir_path)
        os.chdir(dir_path)
    except FileNotFoundError:
        print('Alert! File path does not exist, please try again')
        ret = -1
        return -1, None, None,None
    #next assign  video paths in the directory to a list
    
    flow_filenames = os.listdir(os.getcwd())
    
    #its possible that in this list there are erroneous files (i.e there are files that are not videos)
    
    #check files end with .tif and raise warning if not.
    
    ret = 0
    delete_indices = []
    for i in range(0,len(flow_filenames)):
        file = flow_filenames[i]
        if file[-4:] != '.csv':
            delete_indices.append(i)
            ret = -2
            
    flow_filenames = np.array(flow_filenames)
    flow_filenames = np.delete(flow_filenames,delete_indices)
    flow_filenames = flow_filenames.tolist()
    
    if len(flow_filenames) == 0:
        ret = -1
            
        
    
    os.chdir(initial_dir)
    
    return ret, flow_filenames, dir_path, initial_dir

if __name__ == '__main__':
    
    
    #first collect path form CLI
    
    if len(sys.argv) >=2:
        dir_path = sys.argv[1]
        
    else:
        print("No directory path find")
        
    
    ret, files, _ , _ = get_flowrate_paths(dir_path) 
    
    print(ret)
    file_count = 0
    flow_file = open('./flowbychamber.csv','w')
    
    for file in files:
        
        print(file)
            
        
        df = pd.read_csv(dir_path+file)
        data = df.to_numpy()
        print(data)

        flowrates = data[0,2:]
        
        flow_file.write(file[-6:-4]+ ','+str(np.mean(flowrates))+'\n') 
        
    flow_file.close()
    
    
            
        
         
        
        
