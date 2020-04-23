#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 14:43:25 2020

@author: marcus
"""

import pandas as pd
from glob import glob
import sys
import numpy as np

#This script is written to collate the data of initial areas vs bursting times

def getvidUID(filename):
    numdict = np.arange(1,10).astype(str)
    #position ids go from 0 to 63. May be one or two numbers
    potid = filename[filename.find('.csv')-2:filename.find('.csv')]
    if potid[0]=='_':
        uid = potid[0]
        #print('single digit position, assigning uid: ', uid)
    elif any(numdict==potid[0]):
        uid = potid[0]+potid[1]
        
        
    return uid      
        

def getpervidUID(label):
    label = int(label)
    label = str(label)

    if len(label)==0:
        print ('no label given')
        return
    if len(label) == 1:
        label =  '00'+label
        
    elif len(label) == 2:
        label = '0'+label
        
    return label

def getUID(filename,label):
    return getvidUID(filename)+getpervidUID(label)


def getMap(filename,df):
    #columntitles should be a pandas dataframe column name array
    mapping = {}
    
    columntitles=df.columns.values
    
    for title in columntitles:
        label = df[title].iloc[0]
        mapping[title]=getUID(filename,label)
    
    return mapping


mapforRownames = {'Unnamed: 0': 'PerVidLabel', 0: 'Size', 0.1: 'Bursting Time'}
if __name__ == '__main__':
    
    
    debug = True
    Anameroot = "Initial_Areas_vs_Bursting_Times_Pos*.csv"
    
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
        
        
        
    Afile_list = glob(dpath+Anameroot)
    
    for i in range(0,len(Afile_list)):
        Afile = Afile_list[i]
        if i == 0:
            
            df = pd.read_csv(Afile).T
            print(df)
            mapping0 = getMap(Afile,df)
            df = df.rename(columns=mapping0)
            
        else:
            dfA = pd.read_csv(Afile).T
            mapping = getMap(Afile,dfA)
            dfA = dfA.rename(columns =mapping)
            
            #add this dataframe to df
            
            df = pd.concat([df,dfA],axis = 1)
            
        
            
            
        #print(df)
       
    df.rename(mapforRownames)
    
    df.to_csv(dpath+opath)
    
    