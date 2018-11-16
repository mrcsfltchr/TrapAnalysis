import sys
import time

import numpy as np

from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
                                                    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
                                                    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from qtpy.QtWidgets import QMessageBox, QToolBar



# Goal is to create a generic Qt Canvas which can be embedded inside another Qt application.

#Takes in a plotting function and the required data upon initiation or in a set function later.



class Plotter(QtWidgets.QWidget):

    def __init__(self,xdata = None,ydata = None,params = None,morethan1 = True):
        #Accepts a dictionary of plotting data and label data or just arrays of plotting data
        #Labels should contain structure [xlabel,ylabel,title]
        super().__init__()
        
        
        self.warning = QMessageBox()
        self.layout = QtWidgets.QVBoxLayout()
        self.figure = Figure(figsize = (5,3))
        self.canvas = FigureCanvas(self.figure)
        self.num_sub_plots = None
        self.compare_methods = False
        
        self.turn_on_comparison = QtWidgets.QPushButton('Compare')
        self.turn_on_comparison.clicked.connect(self.turn_on_compare)
        
        '''
        self.tlbar = TlBar(self.canvas)
        
        self.layout.addWidget(self.tlbar)
        '''
        
        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.turn_on_comparison)
        
        self.setLayout(self.layout)
        
        
        
        #check whether we need to create more than one subplot
        if morethan1:
        
            try:
                self.num_sub_plots = len(list(xdata.keys()))
            
            except:
                self.warning.setText('Selected multiple plot mode, but have not supplied valid data.\n Plot data must be supplied in a dictionary')
                self.warning.show()
        
        
        else:
            self.num_sub_plots = 1
        
        
        
        #either way give the data to the plotter.
        self.xdata = xdata
        self.ydata = ydata
        self.params = params
        self.morethan1 = morethan1
        

                



    def turn_on_compare(self):
        if not self.compare_methods:
            self.compare_methods = True
            self.turn_on_comparison.setText('Turn Off')
        
        
        else:
            self.compare_methods = False
            self.turn_on_comparison.setText('Compare')
            
            
    def load_data(self,xdata,ydata,params,morethan1 = True):
    
        self.num_sub_plots = None
        self.xdata = xdata
        self.ydata = ydata
        self.params = params
        self.morethan1 = morethan1
    
    
        self.canvas.figure.clf()
    
        try:
            self.num_sub_plots = len(list(self.xdata.keys()))
        except:
            self.warning.setText('Selected multiple plot mode, but have not supplied valid data.\n Plot data must be supplied in a dictionary')
            self.warning.show()
                                
                                
        self.create_axes()
                                
    def create_axes(self):

        if self.num_sub_plots is not None:
            self.axes = self.canvas.figure.subplots(self.num_sub_plots,1,sharex = True)
            print(type(self.axes))

                                
                                
    def plotIAforaves(self,xdata, ydata,params,compare_xdata = None,compare_ydata = None,compare_labels = None):


        
        
        if xdata is not None:
            
            
            self.num_sub_plots = len(list(xdata.keys()))
            self.create_axes()
            
            for index, key  in enumerate(list(ydata.keys())):
                print(ydata[key])
                
                print(self.figure.axes)
                self.axes[index].set_xlabel(params[key][0])
                self.axes[index].set_ylabel(params[key][1])


                
                self.axes[index].set_yticks([int(np.min(ydata[key])),int(0.5*(np.max(ydata[key])-np.min(ydata[key]))),int(np.max(ydata[key]))])
                self.axes[index].set_xticks(np.array([0,int(len(ydata[key])),len(ydata[key])])*30)
                
                
                self.axes[index].plot(xdata[key],ydata[key],c = 'k',alpha = 0.7,label = params[key][2])
                
                

                if self.compare_methods and compare_xdata is not None and compare_ydata is not None:
                    self.axes[index].plot(compare_xdata[key],compare_ydata[key], c= 'r',alpha = 0.6,label = compare_labels[key])
                    self.axes[index].legend()

                    
                self.axes[index].figure.canvas.draw()
            self.canvas.figure.tight_layout()
                
            

                
                
    
        else:

            self.warning.setText('Data to plot is invalid!')

            self.warning.show()





    def purge_axes(self):

        self.canvas.figure.clf()

        self.xdata = None
        self.ydata = None

        self.params = None
        self.morethan1 = None


class TlBar(QToolBar):

    def __init__(self,canvas):

        super().__init__()

        toolbar = NavigationToolbar( canvas,self)

        self.vbox = QtWidgets.QVBoxLayout()

        self.vbox.addWidget(toolbar)
        

        self.setLayout(self.vbox)




    def update_canvas(self,canvas):

        self.canvas = canvas

        self.canvas.update()

