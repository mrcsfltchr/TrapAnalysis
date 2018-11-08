#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 14:01:04 2018

@author: MarcusF
"""

import sys
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import qimage2ndarray as qnd
from qtpy import QtWidgets,QtGui,QtCore






class Label(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super(Label, self).__init__(parent=parent)

    def paintEvent(self, e):
        super().paintEvent(e)
        qp = QtGui.QPainter(self)
        
        img = qnd.gray2qimage(A.frames[1300],normalize = True)
        
        qp.drawPixmap(img.rect(),QtGui.QPixmap.fromImage(img)) 
        pen = QPen(Qt.red,12)
        qp.setPen(pen)

        
        for i in np.arange(len(A.trapgetter.trap_positions)):
            pos = QPoint(A.trapgetter.trap_positions[i][1]-10,A.trapgetter.trap_positions[i][0]-15)
            qp.drawText(pos,str(A.trapgetter.labels[i]))
            
            
        pen = QPen(Qt.white,2)
        qp.setPen(pen)
        
        for i in np.arange(len(A.trapgetter.trap_positions)):
            qp.drawRect(A.trapgetter.trap_positions[i][1]-10,A.trapgetter.trap_positions[i][0]-15,30,30)
        
        qp.end()
        
class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        layout = QHBoxLayout(self)
        self.label = Label()

        layout.addWidget(self.label)
        

if __name__ == '__main__':
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()

    window = Window()
    window.show()


