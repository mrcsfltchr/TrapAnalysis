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




#This module uploads an Excel sheet using the pandas DataFrame object. This DataFrame object is exported to a numpy array
if __name__ == '__main__':
    
    if len(sys.argv) > 3:
        directory = sys.argv[1]
        filepath = sys.argv[2]
        output = sys.argv[3]
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

    print(labels)
    lifetimes = np.sum(data > 0.5,axis = 0)
    
    data = np.vstack((labels[np.argsort(lifetimes)],data[:,np.argsort(lifetimes)]))
    
    
    df2 = pd.DataFrame(data[1:],columns = data[0])
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
