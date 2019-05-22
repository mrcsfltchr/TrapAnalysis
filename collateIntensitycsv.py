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

def get_unique_id_prefix(filename):
    
    integer = filename[filename.find('Pos') + 3]
    
    try:
        integer = int(integer)
        

            
    except ValueError:
        print('Check if the file path is correct, this code assumes that the filepath is of the form ...PosN.. where N is a valid integer')
    
    #check if next character is also an integer    
    nextdigit = filename[filename.find('Pos') + 4] 
        
    try:
        nextdigit = int(nextdigit)
        
        #if there are two digits, we could have 00 0N or NM where N,M are single digit integers
        key_to_append = str(integer)+str(nextdigit)
        
    except ValueError:
        #if next character can't be made to an integer we must only have one integer present. Now we know this we have to append a 0 to the front to make it a unique id
        
        key_to_append = '0'+str(integer)
        
    #if there are two digits, we could have 00 0N or NM where N,M are single digit integers

    
    return key_to_append



def create_unique_id(dictionary,keytoappend):
    
    dictionary2 = {}
    
    for key in list(dictionary.keys()):
        dictionary2[keytoappend+key] = dictionary.pop(key)
    
    
    df = pd.DataFrame.from_dict(dictionary2)
    return df  
    
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

    
    key_to_append = get_unique_id_prefix(intensity_files[0])  
    
    all_data = pd.read_csv(intensity_files[0])
    
    all_data = all_data.drop('Unnamed: 0',1)
    print(all_data.keys())
    all_data = create_unique_id(all_data,key_to_append)
    
    #DEPRECATED: all_data = sort_df(all_data,intensity_files[0],twodigitflag)

    for file in intensity_files[1:]:


        key_to_append = get_unique_id_prefix(file)
        
        
        df = pd.read_csv(file)
        df= df.drop('Unnamed: 0',1)
        temp_dict = df.to_dict()
        
        df= create_unique_id(temp_dict,key_to_append)
        print(all_data.keys())
        all_data = all_data.join(df)
        
        
        
    all_data.to_csv(output_name)
