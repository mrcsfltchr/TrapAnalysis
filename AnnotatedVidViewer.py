#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 09:49:44 2018

@author: MarcusF
"""

from qtpy import QtCore, QtWidgets,QtGui

import qimage2ndarray as qnd
import tifffile
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtWidgets import QWidget,QApplication,QSlider,QMainWindow,QLabel,QGridLayout,QLineEdit,QDoubleSpinBox,QVBoxLayout,QPushButton
from qtpy.QtCore import QTimer,Qt
import numpy as np


class  TrapViewer(QWidget):
    i = 0
    def __init__(self,qnd,images,trap_positions = None,labels = None):
        QWidget.__init__(self)
        
        self.video = images # This is a file object buffer containing the images
        
        self.trap_positions = trap_positions
        self.labels = labels
        self.videobox = Label(trap_positions,labels)
        self.videobox.activeframe = images.asarray(key = TrapViewer.i)
        try:
            self.videobox.maxintens = int(images.imagej_metadata['max'])
        except KeyError:
            self.videobox.maxintens =int(np.max(self.videobox.activeframe))
            
            
        self.videobox.setGeometry(QtCore.QRect(70, 80, 200, 200))
        
        self.lyt = QVBoxLayout()
        self.lyt.addWidget(self.videobox,5)
        
        
        self.setLayout(self.lyt)
        
        
        
        self.sl = QSlider(Qt.Horizontal)
        
        self.sl.setMinimum(0.0)
        self.sl.setMaximum(self.video.imagej_metadata['frames'])
        
        self.sl.setTickPosition(QSlider.TicksAbove)
        self.sl.setTracking(True)
        self.sl.setTickInterval(100)
        
        self.sl.valueChanged.connect(self.whenslidechanges)
        
        self.frame_counter = QDoubleSpinBox()
        self.frame = self.videobox.activeframe
        self.frame_counter.setSingleStep(1)
        self.frame_counter.setRange(self.sl.minimum(),self.sl.maximum()-1)
        self.frame_counter.valueChanged.connect(self.sl.setValue)
        self.frame_counter.valueChanged.connect(self.video_time_update)
        
        self.video_time = QDoubleSpinBox()
        self.video_time.setSingleStep(30)
        self.video_time.setRange(self.sl.minimum(),30*self.sl.maximum()-1)
        self.frameratetimer = QTimer()
        self.frameratetimer.setInterval(50)
        self.frameratetimer.timeout.connect(self.update_display)
        
        
        self.play_button = QPushButton('Play Video')
        self.play_button.clicked.connect(self.frameratetimer.start)
        
        self.stop_button = QPushButton('Stop Video')
        self.stop_button.clicked.connect(self.frameratetimer.stop)
        self.sl.valueChanged.connect(self.whenslidechanges)
       
        self.lyt.addWidget(self.play_button,0)
        self.lyt.addWidget(self.stop_button,1)
        self.lyt.addWidget(self.sl,2)
        self.lyt.addWidget(self.frame_counter,3)
        self.lyt.addWidget(self.video_time,4)
        
        self.show()
        
    def update_display(self):
        

        
        self.frame = self.video.asarray(key = TrapViewer.i)
        self.videobox.activeframe = self.frame
        
        self.videobox.update()
        
        self.frame_counter.setValue(float(TrapViewer.i))
        
        TrapViewer.i+=1
       
    def whenslidechanges(self):
        
        if self.frameratetimer.isActive():
            self.frameratetimer.stop()
            
            TrapViewer.i = self.sl.value()
        
            self.update_display()
            TrapViewer.i -=1
            
            self.frameratetimer.start()
        else:
            
            TrapViewer.i = self.sl.value()
        
            self.update_display()
            TrapViewer.i -=1
    
    def video_time_update(self):
        self.video_time.setValue(30*self.frame_counter.value())
        
        

class Label(QtWidgets.QLabel):
    def __init__(self,trap_positions= None,labels = None, parent=None):
        super(Label, self).__init__(parent=parent)
        self.activeframe = None
        self.maxintens = 0
        self.trap_positions = trap_positions
        self.labels = labels
        self.setMinimumSize(1,1)
    def update_annotations(self,traps,labels):
        self.trap_positions = traps
        self.labels = labels
    
        self.update()
    
    def paintEvent(self, e):
        super().paintEvent(e)
        
        
        
        #raw image pixel dimensions
        default_w = 512
        default_h = 512
        
        
        img = qnd.gray2qimage(self.activeframe,normalize = (0,self.maxintens))
        pix = QtGui.QPixmap.fromImage(img)
        
        qp = QtGui.QPainter(pix)
        
        
        pen = QPen(Qt.red,12)
        qp.setPen(pen)

        
        
        if self.trap_positions is not None:
            for i in np.arange(len(self.trap_positions)):
                pos = QPoint((self.trap_positions[i][1]-10),(self.trap_positions[i][0]-15))
                qp.drawText(pos,str(self.labels[i]))
                
                
            pen = QPen(Qt.white,2)
            qp.setPen(pen)
            
            for i in np.arange(len(self.trap_positions)):
                
                qp.drawRect(self.trap_positions[i][1]-10,self.trap_positions[i][0]-15,30,30)
    
        qp.end()
        self.setPixmap(pix.scaled(self.size(),Qt.KeepAspectRatio))



class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        layout = QHBoxLayout(self)
        self.label = Label()

        layout.addWidget(self.label)        
        
        '''connect framecounter to slider, change slider layout, connect button properly... '''
