#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 09:52:51 2019

@author: mjsf3
"""
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import tifffile as tf
from ifvesiclemoves import findmovedvesicles
import sys

#This module contains a function which looks for large differences between consecutive values in a vesicle intensity trace


def findjump(vesintens, threshold):
    #This function will receive an intensity trace and a value which will define the threshold for which the differences in consecutive intensity values, if above it, will be found and the frame numbers at which they occured will be recorded
    #vesintens should be a 1D numpy array.
    #threshold is a float. It is the value above which the difference between consecutive values in the intensity trace should be considered to be caused by a disappearance of a vesicle
    
    #threshold should be a negative value!
    
    
    differences = vesintens[1:] - vesintens[:-1]
    
    sorted_diffs = np.sort(differences)
    
    sorted_diff_args = np.argsort(differences)
    
    large_diff_args = sorted_diff_args[sorted_diffs < threshold]
    
    #large_diff_args is an array of frames indices where the difference between frame i and i+1 is greater then the threshold.
    #the first value in this array should be the largest
    
    return large_diff_args,differences




if __name__ == '__main__':
    
        


    if len(sys.argv) > 3:
        dpath = sys.argv[1]
        fpath = sys.argv[2]
        vpath = sys.argv[3]

    else:
        print('Required input: python postProcessVesRemoval.py <directory of files > <videofilepath>')
        
    
        sys.exit()
  
    if vpath[-4:]== '.csv':
        vpathfortiff = vpath[:-4]
        
    df = pd.read_csv(fpath) 
    
    dictionary = df.to_dict('list')
    
    bookendpath = 'bookendtimes'+vpath
    
    t0tmax = np.loadtxt(dpath+'/'+bookendpath)
    
    t0 = t0tmax[0]
    
    del dictionary['Unnamed: 0']
    
    jump_frames = []
    
    for key in dictionary.keys():
        
        vesintens = np.array(dictionary[key])
        vesintens -= np.min(vesintens)
        vesintens = vesintens/np.max(vesintens)
        
        large_jumps, diffs  = findjump(vesintens,threshold = -0.07)
        
        if large_jumps.shape[0] > 0:
            print('t0 is ',t0)
            jump_frames.append([key,large_jumps[0]+t0,diffs[large_jumps[0]]])
            

    tif = tf.TiffFile(dpath +'/'+ vpathfortiff)
    tbk = []
    for frame_datum in jump_frames:
        print(jump_frames)
        images= tif.asarray(key = slice(int(frame_datum[1]),int(frame_datum[1])+2))
        
        subtracted_images = images[0]-images[1]
        

        tbk.append(findmovedvesicles(subtracted_images))

        
    for i in range(0,len(tbk)):
        
        try: 
            tbk[i][0]
            del dictionary[jump_frames[i][0]]
    
            
        except TypeError:
            continue
      
        
    df2 = pd.DataFrame.from_dict(dictionary,orient = 'index').transpose().fillna('')
    
    df2.to_csv(dpath+'/detected_at_beginning_unfiltered_removed_Intensities'+vpath)
    
    