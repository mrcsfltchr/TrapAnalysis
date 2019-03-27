#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 12:24:16 2019

@author: mjsf3
"""

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import sys




if __name__== '__main__':
    
    #the python interpreter will take the following command line arguments. <this script> <directory> <file of circularity data>
    
    
    
    if len(sys.argv) == 3:
        
        dpath = sys.argv[1]
        fpath = sys.argv[2]
        
    else:
        print('the python interpreter will take the following command line arguments. <this script> <directory> <file of circularity data>')
        
        
    df = pd.read_csv(dpath+ '/' + fpath)
    fig = plt.figure()
    data = df.to_dict('list')
    print(df)
    for datalist in data.keys():
        
        plotdata = data[datalist]
        print(plotdata)
        plt.clf()
        
        plt.subplot(111)
        plt.title(datalist)
        
        plt.plot(plotdata)
        
        plt.show()
        
        
        