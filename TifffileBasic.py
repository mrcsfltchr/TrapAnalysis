#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 19 16:10:33 2020

@author: marcus
"""

# HOw to load an image stack to a N x I x H
    
import tifffile as tf


tif = tf.Tifffile('/path/to/video/') # This opens a buffer to the image stuck file, from which individual frames can be loaded into memory (RAM) individually

frames = tif.asarray() # Load frames all at once into RAM into a numpy array of shape ( N x Image Height x Image Width)

frame = tif.asarray(slice(1,10)) # Load just frames indexed 1 to 10 into RAM into a numpy array of shape (9 x Height x width)


