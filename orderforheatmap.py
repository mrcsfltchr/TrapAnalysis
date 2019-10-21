#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 13:44:39 2019

@author: mjsf3
"""

import numpy as np
import pandas as pd
import sys
import os
import time



#This module uploads an Excel sheet using the pandas DataFrame object. This DataFrame object is exported to a numpy array
if __name__ == '__main__':
    
    if len(sys.argv) > 3:
        directory = sys.argv[1]
        filepath = sys.argv[2]
        output = sys.argv[3]
    elif len(sys.argv) == 3:
        directory = sys.argv[1]
        filepath = sys.argv[2]
        output = 'output_'+filepath   
    else:
        directory = '/storage/All data- for analysis/Control/2'
        filepath  = 'collatefiltered.csv'      
    '''else:
        
        print('python orderforheatmap.py <dir> <filepath> <output file path>')
        
        sys.exit()
    '''

    

    df = pd.read_csv(directory+'/'+filepath)
    
    labels = np.array(list(df.columns))
    data = df.to_numpy(float)
    columns = data[:,0]
    print(data.shape)
    
    data = data[:,1:]
    labels = labels[1:]
    

    #lifetimes = np.sum(data > 0.5,axis = 0)
    lifetimes = []
    for j in range(0,data.shape[1]):
        row = data[:,j]
        lessthanhalf = np.nonzero(row < 0.5)
        
        if lessthanhalf[0].shape[0] ==0:
            lengthofdata = row.shape[0]
        else:    
            lengthofdata = lessthanhalf[0][0]
        
        lifetimes.append(lengthofdata)


    lifetimes = np.array(lifetimes)



    
    #delete traces where a vesicle has reappeared in the view of the intensity extractor, after the initial vesicle has burst/moved
    indices_to_remove = []
    for i in range(0,data.shape[1]):
        if lifetimes[i] == data[:,i].shape[0]:
            continue
        
        expected_lessthan_half_I = data[lifetimes[i]:,i]
        #remove nan values
        expected_lessthan_half_I = expected_lessthan_half_I[np.isnan(expected_lessthan_half_I) == False]
        
        #look for presence of intensity values above 0.5 intensity in the region of the trace expected to be lower than half intensity, if we find values greater than 0.5 we delete that row
        if np.sum(expected_lessthan_half_I[5:] > 0.5) !=0:
            indices_to_remove.append(i)
    print(labels[indices_to_remove])
    
    #delete the rows which are suspected to have had a second vesicle appear after the first disappears
    indices_to_remove = np.array(indices_to_remove)
    #all these indices are offest from the first row of data which does not count the frame numbers

    lifetimes = np.delete(lifetimes,indices_to_remove)

    
    
    
    data = np.delete(data,indices_to_remove,axis = 1)   
    
    labels = np.delete(labels,indices_to_remove)
    
    data = np.vstack((labels[np.argsort(lifetimes)[::-1]],data[:,np.argsort(lifetimes)[::-1]])) 
    columns = np.concatenate((['frame'],columns))   
    print(columns.shape)
    print(data.shape)        
    data = np.hstack((columns.reshape((columns.shape[0],1)),data))
    
        
    df2 = pd.DataFrame(data)
    labels = ['Unnamed: 0','Unnamed: 0.1']
    try:
        df2 = df2.drop(labels, axis = 1)
    except:
        try:
            labels = 'Unnamed: 0'
            df2 = df2.drop(labels = labels,axis = 1)    
        except:
    	    
            pass

    

    print(df2)
    df2.to_csv(directory + '/'+output)
