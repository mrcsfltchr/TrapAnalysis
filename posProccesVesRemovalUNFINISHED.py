#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 14:13:59 2019

@author: mjsf3
"""
import numpy as np
import pandas as pd
from AnalyserGUI import AnalyserPanel
import sys
from glob import glob

if __name__ == '__main__':
    
    
    if len(sys.argv) > 3:
        dpath = sys.argv[1]
        fpath = sys.argv[2]
        opath = sys.argv[3]

    else:
        print('Required input: python postProcessVesRemoval.py <directory of files > <file Wildcard pattern> <output file name> ')
        
        sys.exit()
        
        
        
    file_list = glob(fpath)
    
    for file in file_list:
        
        df = pd.read_csv(file)
        
        dictionary = df.to_dict('list')
        
        