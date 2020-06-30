#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 19 16:18:41 2020

@author: marcus
"""

# Using pandas dataframe to convert a list of numpy arrays to a dataframe and then remove nan's

import pandas as pd
import numpy as np
# Create dummy example list of numpy 1D arrays with different lengths



mylist = []

for i in range(1,10):
    
    mylist.append(np.arange(0,i)))
    
myDataFrame = pd.DataFrame(mylist).transpose() # Convert list to a data frame object. The gaps will be automatically filled with Nan values
    
myDataFrame.fillna('') #You can remove the nan values and replace them with a blank character. (Note this means your numbers will be of type string, not integers/floats, but this is fine for saving in excel)

