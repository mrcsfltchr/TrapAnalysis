
from qtpy import QtGui,QtCore,QtWidgets
import numpy as np
from PyQt5.QtCore import pyqtSignal
from qtpy.QtWidgets import QMessageBox


class AnalysisLauncher(QtWidgets.QWidget):

    # This signal is going to let the parent AnalyserGUI panel know that the t0 and tmax frame Nos have been set and analysis can proceed. If this signal is not received analysis will not start and a message box should appear requesting the user to set valid values.
    
    
    donesig = pyqtSignal()
    multidonesig = pyqtSignal()
    
    def __init__(self,frames = None, headless= False):
        QtWidgets.QWidget.__init__(self)
        
        self.headless = headless
        self.msgbox = QtWidgets.QMessageBox()
        self.override_warning = OverrideWarningBox()
        self.has_been_overriden = False
        
        self.t0 = None
        self.tmax = None
        
        self.t0lbl = QtWidgets.QLabel('Select t0')
        self.t0selector = QtWidgets.QComboBox()
        
        self.tmaxlbl = QtWidgets.QLabel('Select tmax')
        
        self.tmaxselector = QtWidgets.QComboBox()
        
        
        self.tmaxselector.currentTextChanged.connect(self.update_exp_frames)
        self.t0selector.currentTextChanged.connect(self.override_check)
        
        
        #create button to trigger analysis
        self.go_btn = QtWidgets.QPushButton('Run Analysis')
        self.go_btn.clicked.connect(self.pre_analysis_check)
        
        '''
        #create alternative button for multivideo analysis
        self.go_btn_list = QtWidgets.QPushButton('Run Analysis: MultiVideo')
        self.go_btn_list.clicked.connect(self.pre_multi_check)
  

        self.multi_pressed_flag = False
        '''

        
        self.layout = QtWidgets.QGridLayout()
        
        self.layout.addWidget(self.t0lbl,0,0)
        self.layout.addWidget(self.t0selector,1,0)
        
        self.layout.addWidget(self.tmaxlbl,0,1)
        self.layout.addWidget(self.tmaxselector,1,1)
        self.layout.addWidget(self.go_btn,2,0)
        '''
        self.layout.addWidget(self.go_btn_list,2,1)
        '''
        
        self.setLayout(self.layout)
        
        
        #Layout includes selection boxes and labels for t0 and tmax. these boxes send a signal when their value is changed to the function below, which updates the values of t0 and tmax. There is also a go button which sends a signal when pressed to the pre analysis check function, which then sends a signal back to the parent listener, which then takes over the analysis.
        
        if frames is not None:

            self.frameNo = np.arange(frames.shape[0]).astype(str)

            self.tmaxlbl.addItems(self.frameNo)

            self.t0lbl.addItems(self.frameNo)





    def update_frames(self,videolength):
        '''
        if frames is not None:
            
            self.frameNo = np.arange(frames.shape[0]).astype(str)
            
            self.tmaxselector.addItems(self.frameNo)
            
            self.t0selector.addItems(self.frameNo)

        '''
        if videolength is None:
            return -1
        
        frame_indices = np.arange(videolength).astype(str)
        
        self.tmaxselector.addItems(frame_indices)
        self.t0selector.addItems(frame_indices)
        
    def update_exp_frames(self):

        try:
            self.t0 = int(self.t0selector.currentText())

            self.tmax = int(self.tmaxselector.currentText())
        except ValueError:
            if self.headless:
                print('select Valid Frame No.s')
            else:
                self.msgbox.setText('Select Valid Frame No.s')
                self.msgbox.show()


    def override_check(self):

        if self.has_been_overriden and not self.headless:
            self.override_warning.exec_()

        else:
            self.update_exp_frames()

    def pre_analysis_check(self):



        if self.t0 is None or self.tmax is None:
            self.msgbox.setText('You have not selected valid starting and ending frames for the\n experimental analysis. It may be that you have not loaded the first video to choose the end frame of the experiment.')

            self.msgbox.show()
        '''
        elif not self.multi_pressed_flag:
            self.donesig.emit()
        '''    
        
        self.donesig.emit()
        '''
        else:
            print('multidonesig sent')
            self.multidonesig.emit()
        '''    
            
    def pre_multi_check(self):

        self.multi_pressed_flag = True
        
        self.pre_analysis_check()

class MsgBox(QtWidgets.QMessageBox):
    def __init__(self):
        QtWidgets.QMessageBox.__init__(self)
                                
                                
        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.setDefaultButton(QMessageBox.Ok)

class OverrideWarningBox(MsgBox):
    def __init__(self):
        MsgBox.__init__(self)

        self.setText('You are about to override the drug arrival time which has been automatically determined. Are you sure you want to do this? Click ok to proceed')
