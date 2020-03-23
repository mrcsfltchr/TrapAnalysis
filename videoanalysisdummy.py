#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 15:11:32 2019

@author: mjsf3
"""

import numpy as np



frames = np.arange(1,1000000,1)

noofvesicles = 5000
    
for num in frames:
    
    img = np.random.rand(512,512)
    
    for ves in range(0,noofvesicles):
        
        v = np.arange(1,30*30,1)*2
        
    if num%10 == 0:
        print("analysed "+str(num)+" frames")
        
        
    
    