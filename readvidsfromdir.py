#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 11:11:59 2019

@author: MarcusF
"""

import os

def get_video_paths(dir_path):
    
    #first change the current working directory to the path. This is not essential now but for saving we want to make
    #new subdirectories in this directory to organise the files.
    
    initial_dir = os.getcwd()
    try:
        os.chdir(dir_path)
    except FileNotFoundError:
        print('Alert! File path does not exist, please try again')
        ret = -1
        return -1, None
    #next assign  video paths in the directory to a list
    
    video_filenames = os.listdir(os.getcwd())
    
    #its possible that in this list there are erroneous files (i.e there are files that are not videos)
    
    #check files end with .tif and raise warning if not.
    
    ret = 0
    
    for file in video_filenames:
        if file[-8:] != '.ome.tif' and  file[-10:] != '.ome-1.tif':
            ret = -1
            
        
    
            
    return ret, video_filenames, dir_path, initial_dir
    
    
    