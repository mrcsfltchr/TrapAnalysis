#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 16:15:26 2019

@author: mjsf3
"""

import pandas as pd
import numpy as np
import os
from glob import glob
import sys



def sort_df(df,filepath,twodigitflag=False):
    
    dictionary = df.to_dict('list')
    if list(dictionary.keys())[0][:3] == 'Unn':
        dictionary.pop[list(dictionary.keys())[0]]
    
    if len(list(dictionary.keys())[0]) ==1:
        dictionary = append0tokeys(dictionary)
    if twodigitflag:
        dictionary = append2ndfigtokeys(filepath,dictionary)
        
    print(dictionary.keys())
    '''for key in dictionary.keys():
            
        dictionary[key].sort(reverse=True)
    ''' 
    
    df = pd.DataFrame.from_dict(dictionary)
    return df

def append0tokeys(dictionary):
    
    dictionary2 = {}
    
    for key in list(dictionary.keys()):
        dictionary2['0'+key] = dictionary.pop(key)
        
    return dictionary2
    
def append2ndfigtokeys(file_path,dictionary):
    
    index = file_path.find('Pos') +4
    try:
        int(file_path[index])
    except:
        return dictionary
    
    
    dictionary2 = {}
    
    for key in list(dictionary.keys()):
        if file_path[file_path.find('Pos')+3] == '0':
            dictionary2['0'+key] = dictionary.pop(key)
        else:    
            dictionary2[key[0]+str(file_path[index])+key[1:]] = dictionary.pop(key)
        
    return dictionary2

if __name__ == '__main__':
    
    if len(sys.argv) >3:
        path = sys.argv[1]
        file_pattern = sys.argv[2]
        output_name = sys.argv[3]
    else:
        path = '/home/mjsf3/Desktop/Control/2'
    try:
        os.chdir(path)
    except:
        print('No valid path input through CLI')
        sys.exit()
        
    print(os.getcwd())
    nums = np.arange(1,10)
    
    
    intensity_files = glob(file_pattern)
    print(intensity_files)
    ndigit = intensity_files[0][intensity_files[0].find('Pos') + 4]
        
    try:
        int(ndigit)
        print(int(ndigit))
        twodigitflag = True
    except ValueError:
        twodigitflag = False

    all_data = pd.read_csv(intensity_files[0])
    
    all_data = all_data.drop('Unnamed: 0',1)
    
    
    all_data = sort_df(all_data,intensity_files[0],twodigitflag)
    for file in intensity_files[1:]:
        print(file)
        ndigit = file[file.find('Pos') + 4]
        
        try:
            int(ndigit)
            print(ndigit)
            twodigitflag = True
        except ValueError:
            twodigitflag = False
        
        
        df = pd.read_csv(file)
        df= df.drop('Unnamed: 0',1)
        

        df = sort_df(df,file,twodigitflag)
        all_data = all_data.join(df)
        
        
        
    all_data.to_csv(output_name)
