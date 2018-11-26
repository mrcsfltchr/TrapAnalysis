
from qtpy import QtGui,QtCore,QtWidgets
import numpy as np
from PyQt5.QtCore import pyqtSignal

class AnalysisLauncher(QtWidgets.QWidget):

    # This signal is going to let the parent AnalyserGUI panel know that the t0 and tmax frame Nos have been set and analysis can proceed. If this signal is not received analysis will not start and a message box should appear requesting the user to set valid values.
    
    
    donesig = pyqtSignal()
    multidonesig = pyqtSignal()
    
    def __init__(self,frames = None):
        QtWidgets.QWidget.__init__(self)
        

        self.msgbox = QtWidgets.QMessageBox()

        
        self.t0 = None
        self.tmax = None
        
        self.t0lbl = QtWidgets.QLabel('Select t0')
        self.t0selector = QtWidgets.QComboBox()
        
        self.tmaxlbl = QtWidgets.QLabel('Select tmax')
        
        self.tmaxselector = QtWidgets.QComboBox()
        
        
        self.tmaxselector.currentTextChanged.connect(self.update_exp_frames)
        self.t0selector.currentTextChanged.connect(self.update_exp_frames)
        
        
        #create button to trigger analysis
        self.go_btn = QtWidgets.QPushButton('Run Analysis')
        self.go_btn.clicked.connect(self.pre_analysis_check)
        
        
        #create alternative button for multivideo analysis
        self.go_btn_list = QtWidgets.QPushButton('Run Analysis: MultiVideo')
        self.go_btn_list.clicked.connect(self.pre_multi_check)
        

        self.multi_pressed_flag = False
        
        self.layout = QtWidgets.QGridLayout()
        
        self.layout.addWidget(self.t0lbl,0,0)
        self.layout.addWidget(self.t0selector,1,0)
        
        self.layout.addWidget(self.tmaxlbl,0,1)
        self.layout.addWidget(self.tmaxselector,1,1)
        self.layout.addWidget(self.go_btn,2,0)
        self.layout.addWidget(self.go_btn_list,2,1)
        
        
        self.setLayout(self.layout)
        
        
        #Layout includes selection boxes and labels for t0 and tmax. these boxes send a signal when their value is changed to the function below, which updates the values of t0 and tmax. There is also a go button which sends a signal when pressed to the pre analysis check function, which then sends a signal back to the parent listener, which then takes over the analysis.
        
        if frames is not None:

            self.frameNo = np.arange(frames.shape[0]).astype(str)

            self.tmaxlbl.addItems(self.frameNo)

            self.t0lbl.addItems(self.frameNo)





    def update_frames(self,frames):

        if frames is not None:
            
            self.frameNo = np.arange(frames.shape[0]).astype(str)
            
            self.tmaxselector.addItems(self.frameNo)
            
            self.t0selector.addItems(self.frameNo)


    def update_exp_frames(self):

        try:
            self.t0 = int(self.t0selector.currentText())

            self.tmax = int(self.tmaxselector.currentText())
        except ValueError:
            self.msgbox.setText('Select Valid Frame No.s')
            self.msgbox.show()



    def pre_analysis_check(self):



        if self.t0 is None or self.tmax is None:
            self.msgbox.setText('You have not selected valid starting and ending frames for the\n experimental analysis')

            self.msgbox.show()

        elif not self.multi_pressed_flag:
            self.donesig.emit()


        else:
            self.multidonesig.emit()
            
            
    def pre_multi_check(self):

        self.multi_pressed_flag = True
        
        self.pre_analysis_check()
