#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  3 20:53:06 2018

@author: MarcusF
"""

from qtpy import QtCore, QtWidgets,QtGui

import qimage2ndarray as qnd
import tifffile
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import QWidget,QApplication,QSlider,QMainWindow,QLabel,QGridLayout,QLineEdit,QDoubleSpinBox,QVBoxLayout,QPushButton
from qtpy.QtCore import QTimer
import numpy as np
import sys
import os
from skimage.filters import threshold_otsu

class  livestream(QWidget):
    i = 0
    def __init__(self,qnd,images = None,annotations_on = True,annotate_coords = None,threshold_switch = False):
        QWidget.__init__(self)
        
        
        self.threshold_switch = threshold_switch
        self.video = images
        self.videobox = Label()
        if annotations_on and annotate_coords is not None:
            self.coords = annotate_coords

            self.videobox.switch = annotations_on
            self.videobox.activecoord = self.coords[0]

        
        
        if self.video is not None:
            self.videobox.activeframe = self.video[0]
            self.videobox.maxintens = np.max(self.video)
        else:
            self.videobox.activeframe = np.loadtxt(os.getcwd() + '/defaultimage.txt')
            print(self.videobox.activeframe.shape)
            self.videobox.maxintens = np.max(self.videobox.activeframe)


        self.videobox.setGeometry(QtCore.QRect(70, 80, 310, 310))
        self.videobox.h = 310
        self.videobox.w = 310
        
        self.lyt = QVBoxLayout()
        self.lyt.addWidget(self.videobox,5)
        
        
        self.setLayout(self.lyt)
        
        
        
        self.sl = QSlider(Qt.Horizontal)
        
        self.sl.setMinimum(0.0)
        if self.video is not None:
            self.sl.setMaximum(len(self.video))
            self.sl.valueChanged.connect(self.whenslidechanges)
        self.sl.setTickPosition(QSlider.TicksAbove)
        self.sl.setTracking(True)
        self.sl.setTickInterval(100)
        

        
        self.frame_counter = QDoubleSpinBox()
        if images is not None:
            self.frame = images[0]
            self.frame_counter.valueChanged.connect(self.video_time_update)
        self.frame_counter.setSingleStep(1)
        self.frame_counter.setRange(self.sl.minimum(),self.sl.maximum())
        self.frame_counter.valueChanged.connect(self.sl.setValue)

        
        self.video_time = QDoubleSpinBox()
        self.video_time.setSingleStep(30)
        self.video_time.setRange(self.sl.minimum(),30*self.sl.maximum())
        self.frameratetimer = QTimer()
        self.frameratetimer.setInterval(30)
        if self.video is not None:
            self.frameratetimer.timeout.connect(self.update_display)
        
        
        self.play_button = QPushButton('Play Video')
        self.play_button.clicked.connect(self.frameratetimer.start)
        
        self.stop_button = QPushButton('Stop Video')
        self.stop_button.clicked.connect(self.frameratetimer.stop)

        if self.video is not None:
            self.sl.valueChanged.connect(self.whenslidechanges)
       
        self.lyt.addWidget(self.play_button,0)
        self.lyt.addWidget(self.stop_button,1)
        self.lyt.addWidget(self.sl,2)
        self.lyt.addWidget(self.frame_counter,3)
        self.lyt.addWidget(self.video_time,4)
        
        self.show()
    
    def assign_images(self,images,centres = None):
    
        '''#first disconnect signals from eachother so nothing should change whilst video data is being updated
        self.sl.valueChanged.disconnect(self.video_time_update)
        self.frameratetimer.timeout.disconnect(self.update_display)
        self.frame_counter.valueChanged.disconnect(self.whenslidechanges)
        '''
        
        self.video = images
        self.coords = centres
        self.videobox.activeframe = self.video[0]
        if self.coords is not None:
            self.videobox.activecoord = self.coords[0]

        #readjust slider and ticker values to dimensions of video
        
        self.sl.setMaximum(len(self.video)-1)
        self.frame_counter.setRange(self.sl.minimum(),self.sl.maximum())
        self.video_time.setRange(self.sl.minimum(),30*self.sl.maximum())
        
        
        
        
        #connect slider and timer etc.
    
        self.sl.valueChanged.connect(self.whenslidechanges)
        self.frameratetimer.timeout.connect(self.update_display)
        self.frame_counter.valueChanged.connect(self.video_time_update)
        
        self.videobox.maxintens = np.max(self.video)
        self.videobox.update()
        
        
    def update_display(self):
        
        if self.threshold_switch:
            threshold = threshold_otsu(self.video[livestream.i])
            
            mask = np.zeros_like(self.video[livestream.i])
            mask[self.video[livestream.i] > threshold] = 1
            self.videobox.maxintens = 1
            self.videobox.activeframe = mask
        else:
            #if threshold switch is off display usual video, so change active frame source and reset maximum intensity for passing to qimage2ndarray
            self.videobox.activeframe = self.video[livestream.i]
            self.videobox.maxintens = np.max(self.video)
        try:
            self.videobox.activecoord = self.coords[livestream.i]

            if not self.videobox.switch:
                
            
                self.videobox.switch = True
                
        except:
            self.videobox.activecoord = None
            self.videobox.switch = False
            
            
        self.videobox.update()
        self.frame_counter.setValue(float(livestream.i))
        
        livestream.i+=1
       
    def whenslidechanges(self):
        
        if self.frameratetimer.isActive():
            self.frameratetimer.stop()
            
            livestream.i = self.sl.value()
        
            self.update_display()
            livestream.i -=1
            
            self.frameratetimer.start()
        else:
            
            livestream.i = self.sl.value()
        
            self.update_display()
            livestream.i -=1
    
    def video_time_update(self):
        self.video_time.setValue(30*self.frame_counter.value())
        
        
    def turn_on_threshold(self,threshold_switch):
        self.threshold_switch = threshold_switch
        self.update_display()
        

class Label(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super(Label, self).__init__(parent=parent)
        self.activeframe = None
        self.switch = False
        self.activecoord = None
        self.maxintens = None
        self.h = None
        self.w = None
        self.size = None
        self.pixsize = None
    def paintEvent(self, e):
        super().paintEvent(e)
        qp = QtGui.QPainter(self)
        
        img = qnd.gray2qimage(self.activeframe,normalize = (0,self.maxintens))
        self.size = img.size()
        pix = QtGui.QPixmap.fromImage(img).scaled(self.h,self.w,Qt.KeepAspectRatio)
        self.pixsize = pix.size()
        
        
        pos = QPoint(0,0)        
        qp.drawPixmap(pos,pix)         

        pen = QPen(Qt.red,2)
        qp.setPen(pen)
        
        if self.switch and self.activecoord is not None:

            qp.drawRect(10*(self.activecoord[1]-4),10*(self.activecoord[0]-4),10*8,10*8)
            
        qp.end()
        
if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    
    with tifffile.TiffFile('/Users/MarcusF/Downloads/nbd pc position _10ms_bin2_em30_1_MMStack_Pos0.ome.tif') as tif:
        images =tif.asarray()
    
    ls = livestream(qnd,images,annotations_on = False)

    app.exec_()
