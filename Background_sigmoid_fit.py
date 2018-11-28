#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 17:38:32 2018

@author: MarcusF
"""

import tifffile as tf
from matplotlib import pyplot as plt
from BackgroundFinder import BackgroundFinder


with tf.TiffFile('/Users/MarcusF/Desktop/TrapAnalysis/260522_CecB-  PCPG vesicles- after flushing_1_MMStack_Pos31.ome-1.tif') as tif:
    frames = tif.asarray()
    
bgf = BackgroundFinder()

bgf.get_background(frames)

bgf.get_data_gradient()
bgf.find_correct_gaussian_scale()

bgf.plot_gradient()

print(bgf.peak_max_arg,bgf.width,bgf.peak_begin_frame)
plt.show()

bgf.plot_background_intensity()

plt.show()
