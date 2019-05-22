#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 14:18:04 2019

@author: mjsf3
"""
from __future__ import print_function   # Used for "print" function compatibility between Python 2.x and 3.x versions
import sys
 
from qtpy import QtCore, QtWidgets,QtGui
from qtpy.QtWidgets import QWidget,QApplication,QSlider,QMainWindow,QLabel,QGridLayout,QLineEdit,QDoubleSpinBox,QVBoxLayout,QPushButton
 
from qtpy.QtCore import *
from qtpy.QtCore import QTimer
import numpy as np

import qimage2ndarray as qnd

import platform                         # Library used for x64 or x86 detection
import time                             # Time library, use of sleep function
import ctypes                           # Used for variable definition types
from ctypes import *                    # Used to load dynamic linked libraries
import os
 
 

 
os.chdir('C:\Users\ka451')
sys.path.append('C:/Program Files/Micro-Manager-1.4')
sys.path.append('Z:qimage2ndarray')
sys.path.append('C:\Users\ka451\moviepy')
sys.path.append('C:\Users\ka451\\tiffile')


 
import MMCorePy


class  livestream(QWidget):
     
    def __init__(self,mmc,qnd,initial_frame):
        QWidget.__init__(self)
         
         
        self.image = qnd.gray2qimage(initial_frame,normalize = True)
        self.videobox = QLabel()
         
        self.videobox.setPixmap(QtGui.QPixmap.fromImage(self.image))
         
        self.lyt = QGridLayout()
        self.lyt.addWidget(self.videobox,0,0)
         
        self.setLayout(self.lyt)
         
        self.show()
        
        
    def update_display(self):
         
 
         
        frame = mmc.getLastImage()
         
        self.image = qnd.gray2qimage(frame,normalize = True)
        self.videobox.setPixmap(QtGui.QPixmap.fromImage(self.image))
         
        
        
if __name__ =='__main__':
 
     
 
 
    mmc = MMCorePy.CMMCore()
 
    mmc.reset()
    mmc.loadDevice('evolve','PVCAM','Camera-1')
 
 
    mmc.initializeAllDevices()
 
 
 
    mmc.setCameraDevice('evolve')
 
 
     
    mmc.startContinuousSequenceAcquisition(1)
    time.sleep(1)
     
    initial_frame = mmc.getLastImage()
     
    time.sleep(2)
     
 
 
 
 
 
    global app
    app = QApplication.instance()
     
    names = ['1','2','3','4']
     
    ls = livestream(mmc,qnd,initial_frame)
    if app is None:
        app = QApplication(sys.argv)
        
        