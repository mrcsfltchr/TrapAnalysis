#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 09:35:36 2019

@author: mjsf3
"""

from Analyser import Analyser
from BackgroundFinder import BackgroundFinder
import numpy as np
import tifffile as tf
import sys



if __name__ == '__main__':
    if len(sys.argv) > 1:
        videopath = sys.argv[1]
    A = Analyser(videopath)
    A.bgf= BackgroundFinder()
    
    A.frames, A.videolength = A.load_frames()
    
    A.bgf.get_background(A.frames)      
    A.bgf.get_data_gradient()   
    A.bgf.find_correct_gaussian_scale()
    
    
    A.sett0frame(A.bgf.peak_begin_frame)
    A.videopos = videopath[videopath.find('Pos') +3]
    A.get_traps(A.bgf.peak_begin_frame)
    
    A.get_clips_alt()
    A.sett0frame(A.bgf.peak_max_arg)
    A.classify_clips()
    A.analyse_frames(A.bgf.peak_max_arg+1200,just_area=True)
    