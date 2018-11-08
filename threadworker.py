from qtpy import QtCore
from PyQt5.QtCore import pyqtSignal


#In the QThread construct, one needs to pass an object with a method called run to the thread object. When the standard method of the thread , .start(), is called, it looks for a method in the worker called .run to process.

#In this generic worker class we pass an instance of an object, with all its access to data and member function definitions to
class myworker(QtCore.QObject):
    sig1 = pyqtSignal()
    def __init__(self,func):
        QtCore.QObject.__init__(self)
        
        self.func = func
    
    def run(self):
        
        self.func()
        print('I am in the thread!')
        
        
        self.sig1.emit()
