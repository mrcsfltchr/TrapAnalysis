#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 13:29:15 2020

@author: marcus
"""

# This file defines functions used to find the bursting time of guvs from columns of individual GUV intensity time series
# It is assumed that the data is normalised between 0 and 1. 
# Bursting time is defined as the time taken for normalised intensity to fall below 0.5

import pandas as pd


def get_bursting_time(df):
    
    dictionary1 = {}
    
    for name in df.columns.values[1:]:
        df1 = df[name]
        datalength = len(df1)
        
        df1 = df1[df1 < 0.5]
        
        if len(df1.index) > 0:
            dictionary1[name] = df1.index[0]
        else:
            dictionary1[name] = datalength
            
    print(dictionary1)
    df_out = pd.DataFrame.from_dict(dictionary1,orient = 'index').transpose()
    
    return df_out

