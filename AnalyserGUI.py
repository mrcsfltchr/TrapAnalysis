#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 10:14:21 2018

@author: MarcusF
"""

import numpy as np
from qtpy import QtGui,QtWidgets,QtCore
from qtpy.QtWidgets import QWidget,QMainWindow, QApplication,QPushButton,QComboBox,QProgressBar,QFileDialog, QGridLayout, QLabel,QLineEdit,QMessageBox
from PyQt5.QtCore import pyqtSignal,QThread
from matplotlib import pyplot as plt

from trapanalysis import TrapGetter
from Analyser import Analyser
from AnnotatedVidViewer import TrapViewer
import sys
import os
import time


import qimage2ndarray as qnd
from QtImageViewer import QtImageViewer, handleLeftClick
from SingleVesViewer import SingleVesViewer
from AnalysisLauncher import AnalysisLauncher
import pandas as pd
from savebox import SaveBox,LoadBox as lb

from DirectionalHeatImage import DirectionalHeatMap,DirectionalHMBox
class MW(QtWidgets.QMainWindow):
    

    close_signal = pyqtSignal()
    
    def __init__(self,mode = 'standard'):
        
        #mode can be 'standard' or 'enhanced' atm.
        QtWidgets.QMainWindow.__init__(self)
        
        
        if mode == 'directional':
            self.ap = AnalyserPanel(mode = 'directional')
        
        else:
            self.ap = AnalyserPanel()
        
        
        self.setCentralWidget(self.ap)

        self.show()

    def close(self):

        self.close_signal.emit()

        super().close()

class AnalyserPanel(QWidget):
    
    trap_on_sig = pyqtSignal()
    def __init__(self,mode = 'standard'):
        QWidget.__init__(self)
        
        
        #store mode. This determines whether extra features are incorporated to GUI.
        
        self.mode = mode
        
        #loadvideo control
        
        self.loadbox = LoadBox()
        
        #debugging process convenience tool: Upload previous Analysis
        
        self.save_data_btn = QtWidgets.QPushButton('Save Data')
        self.save_data_btn.clicked.connect(self.spit_save_error)
        
        
        #Add Load historical data button, mainly for help with debugging, but also for convenience if wanting to look at data again, without having to rerun
        
        self.load_history = QPushButton('Load Analysis from File')
        
        self.load_history.clicked.connect(self.show_load)
        
        
        
        self.loadbox.choosevideo.clicked.connect(self.getfile)
        self.loadbox.pathshower.textChanged.connect(self.update_path)
        
        #analyser which contains, video loader backend, and analyser, but not TrapGetting function
        self.analyser = Analyser('')
        self.mythread = QThread()
        
        #videoviewer display. When there is no video it defaults to showing a label
        
        self.display = VideoBorder()
        self.vid_control =VideoViewerControl()
        
        #Add a button to switch to pop up videoviewer
        
        self.switch_to_popup = QtWidgets.QPushButton('Switch to Popup')
        self.switch_to_popup.clicked.connect(self.load_pop_up)
        
        #bring up single vesicle viewer window button
        
        self.svvbtn = QPushButton('View Single Trap')
        self.svvbtn.clicked.connect(self.generate_single_vesicle_viewer)
        
        
        #initialize single particle viewer as None for purpose of running code that is conditional on the single particle viewers instantiation. i.e if it is not equal to None do something
        
        self.sv = None
        
        #trapgetting control
        
        self.tc = trap_control()
        
        #Add run analysis control, which also contains choice boxes to set the beginning and end of the experiment in the video
        
        self.AControl = AnalysisLauncher()
        self.AControl.donesig.connect(self.pre_flight_check)
        
        #Add reload t0 and tmax values to override the combobox selection control
        
        self.reloadt0 = None
        self.reloadtmax = None
        
        #tells computer whether to pass the reloaded t0 and tmax "bookends" or allow the user to control the t0 and tmax using the combobox. Default is False
        
        self.combo_switch_off = True
        
        #flags
        self.trap_bool = False
        self.has_frames = False

        self.loadbox.load_video.clicked.connect(self.loadpressed)
        self.layout = QGridLayout()

        self.layout.addWidget(self.display,0,3)
        self.layout.addWidget(self.switch_to_popup,1,4)
        self.layout.addWidget(self.loadbox,2,0)
        self.layout.addWidget(self.tc,2,1)
        self.layout.addWidget(self.vid_control,2,4)
        self.layout.addWidget(self.svvbtn,0,0)
        self.layout.addWidget(self.AControl,1,1)
        self.layout.addWidget(self.save_data_btn,1,2)
        self.layout.addWidget(self.load_history,1,3)
        self.msgbox = MsgBox()
        self.msgbox.setText('')
        
        
        self.setLayout(self.layout)
        
        ''' self.show() '''
    
    
    def show_load(self):
        self.loader = lb(self)
        self.loader.show()
    
    def generate_single_vesicle_viewer(self):
    
        #first check if there are frames to view
        
        if self.analyser.frames is None:
        
            self.msgbox.setText('Load some video to watch!')
            self.msgbox.exec_()
        
            return -1
        
        if self.sv is not None:
            
            self.sv = None
        
    
        if self.mode == 'directional':
            self.sv = SingleVesViewer(self.analyser.frames,mode = 'directional')
        
    
    
        #if trap positions have been found it is safe to bring up video viewer for contents of single traps.
        if self.analyser.trapgetter.trap_positions is not None:
            
            self.sv.set_annotations(self.analyser.trapgetter.trap_positions,self.analyser.trapgetter.labels,self.analyser.trapgetter.trapdimensions)
            print(self.analyser.trapgetter.labels)
            self.sv.label_select.addItems(self.analyser.trapgetter.labels.astype(str).tolist())
        #if the analysis has been run and the intensity traces, centres_of_vesicles in each frame, areas and t0 and tmax have been defined it is safe to allow plotting function and button to show detected vesicle centres overlayed on video
        
        
            
        
        if self.analyser.bg_sub_intensity_trace is not None:
        
            #if intensity data is there assume that the active traps have been filtered correctly so update the option box for trap viewing to only the active traps
            
            self.sv.label_select.clear()
            self.sv.label_select.addItems(list(self.analyser.bg_sub_intensity_trace.keys()))
            
            # Add plotting data
            self.sv.ydataI = self.analyser.bg_sub_intensity_trace
            self.sv.ydataA = self.analyser.areatrace
            
            if self.combo_switch_off:
                self.sv.t0 = self.reloadt0
                self.sv.tmax =self.reloadtmax
            else:
                self.sv.t0 = self.AControl.t0
                self.sv.tmax = self.AControl.tmax
    
            self.sv.delete.clicked.connect(self.delete_vesicle_and)
            self.sv.interact_display.accepted.connect(self.get_heat_plot)

            self.sv.proceed_to_directional_query.accepted.connect(self.create_persisting_times)
        if self.analyser.centres is not None:
            self.sv.centres = self.analyser.centres


    def get_heat_plot(self):
    
        print('Made it to get-heat_plot')
        
        self.analyser.heat_data_generator()
        self.analyser.get_heat_plot()
    
    
    def delete_vesicle_and(self):
    
        label_as_str = self.sv.label_select.currentText()
    
        self.analyser.delete_vesicle(label_as_str)
    
        self.sv.label_select.clear()
    
        self.sv.label_select.addItems(list(self.analyser.bg_sub_intensity_trace.keys()))
    
    
    def donemessage(self):
        
        self.msgbox.Text('Done!')
        self.msgbox.show()
    
    def turn_on_traps(self):
        
        if not self.trap_bool:
            self.trap_bool = True
            self.vid_control.withtraps_switch.setText('Traps Off')
            
            #turn on annotations on video
            self.display.videoviewer.annotations_switch = True

            
            #signal the TrapViewer to update its display
        
            self.display.videoviewer.tv.videobox.update_annotations(self.analyser.trapgetter.trap_positions,self.analyser.trapgetter.labels)
            
            print(self.display.videoviewer.tv.videobox.trap_positions)
            
        
        elif self.trap_bool:
            self.trap_bool = False
            self.vid_control.withtraps_switch.setText('Traps On')
            self.display.videoviewer.annotations_switch = False
            
            self.display.videoviewer.tv.videobox.update_annotations(None,None)
            
    def loadpressed(self):
        
       
        
        if self.analyser.videopath == '':
            self.msgbox.setText('No File path has been set, Please select a compatible video file')
            self.msgbox.show()
        
        else:
            
            
            
            
            
            
            self.myworker = QAnalyser(self.analyser)
            
            self.myworker.moveToThread(self.mythread)
            print('worked')
            self.mythread.started.connect(self.myworker.run)
            self.myworker.sig1.connect(self.monitorprocess)
            self.myworker.sig1.connect(self.mythread.quit)
            self.mythread.start()
            
            
            
            
            
            ''' myevent = threading.Event()
            mymonitor = threading.Thread(target = self.monitorprocess,args = (myevent,))
            
            mythread = threading.Thread(target = self.analyser.load_frames,args = (myevent,))
        
            mythread.start()
            mymonitor.start()
            '''

    
        #self.thread = mythread(self.analyser.load_frames)
        
        #self.thread.finished.connect(self.donemessage)
        
        #self.thread.start()

    def save_data(self):
    
    
        #Save all relevant data, by creating a pop up window. In this window user is prompted to enter a Date and Time to identify files. It then proceeds to save files named "trap_positions_Date_Time.csv". "intensities_Date_Time.csv" etc.
    
    
        labelled_traps = np.hstack((self.analyser.trapgetter.labels[:,np.newaxis],self.analyser.trapgetter.trap_positions))
    
        self.sb = SaveBox(labelled_traps,self.analyser.bg_sub_intensity_trace,self.analyser.areatrace,self.analyser.centres,self.AControl.t0,self.AControl.tmax)
    
        self.sb.show()
    
    
    
    def spit_save_error(self):
        if self.analyser.bg_sub_intensity_trace is None:
            self.msgbox.setText('No data to save')
            self.msgbox.exec_()
    
    
    def update_path(self):
    
        self.analyser.videopath = self.loadbox.pathshower.text()
    
    def monitorprocess(self):
    
    
    
        print(self.mythread.isRunning())
        self.msgbox.setText('Video Successfully Loaded!')
        self.msgbox.exec_()
        print(self.analyser.frames)
        self.vid_control.showdisplay.clicked.connect(self.load_display)
        self.vid_control.withtraps_switch.clicked.connect(self.turn_on_traps)
        
    
        # wave flag to say frames have been loaded
        self.has_frames = True
        self.tc.trapgetbtn.clicked.connect(self.get_traps)
        self.tc.viewtrapkernelbtn.clicked.connect(self.view_kernel)
        # connect trap buttons to the analyser
        self.AControl.update_frames(self.analyser.frames)
    
    def pre_flight_check(self):
    
        #after we have checked in the AControl that t0 and tmax have been assigned, we also check here that the length of the video to be analysed is valid. I have presumed that a video of less than 100 frames is probably a mistake. So i warn Kareem. However, I give the user the opportunity to run analysis anyway.
        #If the length of the video is longer than this we proceed directly with the analysis.
        length = int(self.AControl.tmaxselector.currentText()) - int(self.AControl.t0selector.currentText())
        if length < 100:
            self.msgbox.setText(' Hi Kareem, are you sure you want to analyse a video of less than 100 frames? Click Ok to proceed with analysis')
                                
                                

                                
            ret = self.msgbox.exec_()
        
            self.proceed_yes_or_no(ret)
        
        else:
            self.run_analysis()
    def proceed_yes_or_no(self,ret):
        
        print(ret, "hi")
        if ret == QMessageBox.Ok:
            self.run_analysis()
        
    def run_analysis(self):
    
        # run analysis
        #when it is done call svv.set_annotations(self.analyser.trapgetter.trap_positions,self.analyser.intenstrace.keys,trap_dimensions), this should update the selection menu with only the labels of traps which have a detected vesicle inside.
        #After this we can include set svv.centres = self.analyser.centres (which is a dictionary)
        
        #set self.svv.t0 and self.svv.tmax such that detected centres match the frames in video.
        
        #check first that length of video to be analysed is not zero
        

                                
        if self.analyser.trapgetter.trap_positions is not None:
            self.analyser.sett0frame(int(self.AControl.t0selector.currentText()))
            

            self.analyser.get_clips_alt()
            self.analyser.classify_clips()
            self.analyser.analyse_frames(int(self.AControl.tmaxselector.currentText()))
            self.analyser.extract_background(int(self.AControl.tmaxselector.currentText()))
            self.analyser.subtract_background()
        
            print(list(self.analyser.bg_sub_intensity_trace.keys()))
                
            # if an instance of the Single Vesicle Viewer exists, we just want to update the allowed labels to those that have detectable vesicles. And we want to supply it with the dictionary of detected particle centres. If not we need create a new instance automatically.
            
            #Connect the save_data button so it does something when clicked now
            self.save_data_btn.clicked.connect(self.save_data)
            if self.sv is not None:
            
                self.sv = None


            
            if self.mode == 'directional':
                self.sv = SingleVesViewer(self.analyser.frames,self.analyser.trapgetter.trap_positions,self.analyser.trapgetter.labels,self.analyser.trapgetter.trapdimensions,mode = 'directional')
            else:
                self.sv = SingleVesViewer(self.analyser.frames,self.analyser.trapgetter.trap_positions,self.analyser.trapgetter.labels,self.analyser.trapgetter.trapdimensions)
            self.sv.centres = self.analyser.centres
            self.sv.label_select.clear()
            self.sv.label_select.addItems(list(self.analyser.bg_sub_intensity_trace.keys()))
            self.sv.t0 = self.AControl.t0
            self.sv.tmax = self.AControl.tmax
            
            #add plotting_data
            self.sv.ydataI = self.analyser.bg_sub_intensity_trace
            self.sv.ydataA = self.analyser.areatrace
            
            print(self.sv.ydataI)
            print(self.sv.ydataA)
            
            
            #add data for comparison, determined by a separate method.
            
            
            self.sv.compare_ydataI = self.analyser.second_bg_si_trace
            self.sv.compare_ydataA = self.analyser.secondareatrace
            

            
            
            
            #Add connections to heat plot generator from buttons in the single vesicle viewer
            self.sv.delete.clicked.connect(self.delete_vesicle_and)
            self.sv.interact_display.accepted.connect(self.get_heat_plot)
            #Add connection to directional heat_plot_gen
            
            
            self.sv.proceed_to_directional_query.accepted.connect(self.create_persisting_times)


            print(self.analyser.trapgetter.trap_positions)
        else:
            self.msgbox.setText('Make sure video has been loaded and trap positions have been found. Press "Get Traps" ')
            self.msgbox.show()

    def view_kernel(self):
    
        #Kernel Viewer, for checking trap getting process is correct
    
        self.KV = KernelViewer(self.analyser.trapgetter.kernel)
    
    
    def load_display(self):
        self.display.videoviewer.create_video_display(self.analyser.frames)

    def load_pop_up(self):
        exitval = self.display.videoviewer.create_popup_video(frames = self.analyser.frames)
        
        if exitval == -1:
            self.display.videoviewer.create_video_display(self.analyser.frames)
    def getfile(self):
        
            
        fname = QFileDialog.getOpenFileName(self,'Open File',os.getcwd(),"Video Files (*.ome.tif *.tif)")

            
        if not fname:
            self.loadbox.pathshower.setText('Select a Video')
        else:
            self.loadbox.pathshower.setText(fname[0])
            self.analyser.videopath = fname[0]

    def get_traps(self):

        if self.has_frames:
            try:
                self.analyser.get_traps()
                
                #Once traps have been successfully found, make them available for display on video view
                
                self.display.videoviewer.make_annotations_available(self.analyser.trapgetter.trap_positions,self.analyser.trapgetter.labels)
            
            
            
            except:
                self.msgbox.setText('Getting traps failed. Check Kernel, and that the visibility of the traps in the\n last frame is good')
                self.msgbox.show()


    def create_persisting_times(self):
        
        for key in self.analyser.bg_sub_intensity_trace.keys():

            intensities =self.analyser.bg_sub_intensity_trace[key] -np.min(self.analyser.bg_sub_intensity_trace[key])
            intensities = intensities/np.max(intensities)
            
            self.analyser.persisting_times[key] = len(intensities[intensities >0.5])

        
        print(self.analyser.persisting_times)

        self.create_directional_heat_map()


    
    def create_directional_heat_map(self):
            print(self.analyser.t0frameNo)
            ''' DHM = DirectionalHeatMap(self.analyser.frames[self.analyser.t0frameNo,:,:],self.analyser.mask,self.analyser.trapgetter.labels,self.analyser.persisting_times)
            DHM.colourscalegenerator()
            
            DHM.give_heat2img()
            DHM.show_image()
            
            '''

            DHM =DirectionalHMBox()

            active_trap_labels = np.array(list(self.analyser.persisting_times.keys())).astype(int)
            trap_indices = np.searchsorted(self.analyser.trapgetter.labels,active_trap_labels)
            
            print(trap_indices)
            
            traps = np.array(self.analyser.trapgetter.trap_positions)[trap_indices,:]
            
            print(traps)
            
            DHM.canvas.update_data(traps,self.analyser.persisting_times)
            DHM.canvas.colourscalegenerator()
            DHM.canvas.give_colours_to_traps()
            DHM.canvas.update_axes()


            DHM.show()

class VideoViewerControl(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.showdisplay = QPushButton('Show Video Viewer')
        self.withtraps_switch = QPushButton('Traps On')

        self.lyt = QtWidgets.QHBoxLayout()
        self.lyt.addWidget(self.showdisplay)
        self.lyt.addWidget(self.withtraps_switch)

        self.setLayout(self.lyt)


class trap_control(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.trapgetbtn = QPushButton('Get Traps')
        self.viewtrapkernelbtn = QPushButton('View Kernel')


        self.lyt = QtWidgets.QHBoxLayout()
        self.lyt.addWidget(self.trapgetbtn)
        self.lyt.addWidget(self.viewtrapkernelbtn)

        self.setLayout(self.lyt)





class QAnalyser(QtCore.QObject):
    sig1 = pyqtSignal()
    
    def __init__(self,obj):
        QtCore.QObject.__init__(self)
        self.analyser = obj

    def run(self):
        
        self.analyser.load_frames()
        self.sig1.emit()


class LoadBox(QtWidgets.QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.choosevideo = QPushButton('Choose Video')
        self.pathshower = QLineEdit('Select a Video')
            
        self.load_video = QPushButton('Load')

        self.lyt = QtWidgets.QVBoxLayout()

        self.lyt.addWidget(self.pathshower)
        self.lyt.addWidget(self.choosevideo)
        self.lyt.addWidget(self.load_video)

        self.setLayout(self.lyt)






class VideoBorder(QtWidgets.QFrame):

    def __init__(self):
        QtWidgets.QFrame.__init__(self)

        self.setStyleSheet("VideoBorder { border:1px solid; }, ")
        self.videoviewer = VideoViewingBox()

        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(self.videoviewer)
        
        self.setLayout(self.layout)

class VideoViewingBox(QWidget):
    def __init__(self):

        QWidget.__init__(self)

        self.layout = QtWidgets.QVBoxLayout()

        self.DefaultLabel = QLabel("Load Video to Display")
        
        # default flags
        
        self.annotations_switch = False
        self.annot_availables = False
        #default TrapViewer as None
        
        self.tv = None
        self.traps = None
        self.labels = None
        
        if self.traps is not None and self.labels is not None:

            self.annot_availables = True
        
        self.layout.addWidget(self.DefaultLabel)

        self.setLayout(self.layout)

        #add flag for whether popup exists
        self.popupflag = False
        #warningbox
        
        self.warningbox = QtWidgets.QMessageBox()
    
    def make_annotations_available(self,traps,labels):
        self.traps = traps
        self.labels = labels
    
        if self.traps is None and self.labels is None:
            self.warningbox.setText('invalid trap positions entered')
            self.warningbox.show()
        else:
            self.annot_availables = True
    
        
    def create_video_display(self,frames=None):
        switch = 1
        try:
            frames.shape
        except:
            switch = 0
            self.warningbox.setText('No Frames are accessible, load a video!')
            self.warningbox.show()
            
        
        if switch:
            
            self.clearLayout(self.layout)
            
            if self.annotations_switch and self.annot_availables:
                try:
                    self.tv = TrapViewer(qnd,frames,self.traps,self.labels)
                except:
                    self.warningbox.setText('Invalid Trap data or video')
                    self.warningbox.show()
                        
            else:
                self.tv = TrapViewer(qnd,frames)



            self.layout.addWidget(self.tv)


    def create_popup_video(self,frames = None):

        #if have already created the embedded videoviewer, delete it        
        if self.tv is not None:
            self.tv = None
            self.clearLayout(self.layout)

        #if this no popupwindow exists, calling this function creates it so update existence flag to true
            
        if not self.popupflag:
            self.popupflag = True

 
            
            #create new video viewer and call show to display widget in its own window
        
            self.tv = TrapViewer(qnd,frames,self.traps,self.labels)
            self.tv.show()

        #if popupflag is true a popup window should have existed, so update this to false now it has been deleted and call the function to create embedded video display
            
        else:
            self.popupflag = False
            return -1
            
    def clearLayout(self,layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()







class mythread(QtCore.QThread):
    def __init__(self,func_to_run):
        QtCore.QThread.__init__(self)
        
        self.func = func_to_run
        
    def run(self):
        print(self.currentThreadId())
        print("I'm running!")
        self.func()

class KernelViewer(QtImageViewer):
    def __init__(self,kernel):
        QtImageViewer.__init__(self)
        
        self.image = kernel

        qimg = qnd.gray2qimage(kernel,normalize = True)
        super(KernelViewer,self).setImage(qimg)
        super(KernelViewer,self).leftMouseButtonPressed.connect(handleLeftClick)
        self.show()

class MsgBox(QtWidgets.QMessageBox):
    def __init__(self):
        QtWidgets.QMessageBox.__init__(self)
                                
                                
        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.setDefaultButton(QMessageBox.Ok)
                                
        
                                


            
if __name__ == '__main__':
    
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
        
    else:
        app = QtWidgets.QApplication.instance()
    print('success')
    



    mw = MW(mode = 'directional')

    mw.close_signal.connect(app.closeAllWindows)
    app.exec_()


