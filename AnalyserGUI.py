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
from SingleVesViewer import saveboxview
from BackgroundFinder import BackgroundFinder
from readvidsfromdir import get_video_paths
from ifvesiclemoves import findmovedvesicles
from bigintensityjumps import findjump
import copy



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
    close_path_input_sig = pyqtSignal()
    
    def __init__(self,mode = 'standard'):
        QWidget.__init__(self)
        
        
        #add button to trigger auto run
        self.autorunstart = QtWidgets.QPushButton('Run Auto')
        self.autorunstart.clicked.connect(self.autostart_pressed)
        
        self.firstvideoflag = True
        
        #add a default value for the offset applied to the automatically found t = 0 frame.
        self.start_offset = 0
        #connect signal emitted when directorypath has been loaded into memory to function autorun
        self.close_path_input_sig.connect(self.autorun_gettraps)
        
        #add reset button
        self.purge_btn = QtWidgets.QPushButton('Reset')
        self.purge_btn.clicked.connect(self.purge)

        #store mode. This determines whether extra features are incorporated to GUI.
        
        self.mode = mode
        
        #loadvideo control
        
        self.loadbox = LoadBox()
        
        #save the video directory path to save the analysed data in. This is solely for organising the results helpfully
        self.video_directory = None
        
        #debugging process convenience tool: Upload previous Analysis
        
        self.save_data_btn = QtWidgets.QPushButton('Save Data')
        self.save_data_btn.clicked.connect(self.spit_save_error)
        
        
        #Add Load historical data button, mainly for help with debugging, but also for convenience if wanting to look at data again, without having to rerun

        
        self.load_history = QPushButton('Load Analysis from File')
        
        self.load_history.clicked.connect(self.show_load)
        

        #add an object which handles automatic finding of the drug arrival frame and frame in which to threshold to find intial vesicle positions

        self.bgf = BackgroundFinder()
        
        
        self.loadbox.choosevideo.clicked.connect(self.getfile)
        self.loadbox.pathshower.textChanged.connect(self.update_path)
        
        #add signal from loadbox "add path to list error" to the main GUI msgbox to display error message to user
        self.loadbox.loaderror.connect(self.video_path_collection_error)
        
        
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
        
        
        #This appears to the user of the auto run button is pressed
        self.autolaunch = Autorunlaunch()
        self.autolaunch.overridet0flag = False
        #initialize single particle viewer as None for purpose of running code that is conditional on the single particle viewers instantiation. i.e if it is not equal to None do something
        
        self.sv = None
        
        #trapgetting control
        
        self.tc = trap_control()
        
        #Add run analysis control, which also contains choice boxes to set the beginning and end of the experiment in the video
        
        self.AControl = AnalysisLauncher()
        self.AControl.donesig.connect(self.pre_flight_check)
        self.AControl.multidonesig.connect(self.pre_flight_check)
        
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
        self.layout.addWidget(self.autorunstart,4,0)
        self.layout.addWidget(self.switch_to_popup,1,4)
        self.layout.addWidget(self.loadbox,2,0)
        self.layout.addWidget(self.tc,2,1)
        self.layout.addWidget(self.vid_control,2,4)
        self.layout.addWidget(self.svvbtn,0,0)
        self.layout.addWidget(self.AControl,1,1)
        self.layout.addWidget(self.save_data_btn,1,2)
        self.layout.addWidget(self.load_history,1,3)
        self.layout.addWidget(self.purge_btn,3,0)
        self.msgbox = MsgBox()
        self.msgbox.setText('')
        
        
        self.setLayout(self.layout)
        
        ''' self.show() '''


    def autostart_pressed(self):
        
        
        
        self.autolaunch.enter_dir_path.returnPressed.connect(self.getfilepathandclose)
        
        self.autolaunch.start_offset.currentTextChanged.connect(self.update_start_offset)
        self.autolaunch.start_offset.setCurrentText('0')
        
        
        self.autolaunch.show()
      
    def update_start_offset(self):
        
        self.start_offset = int(self.autolaunch.start_offset.currentText())
        
        
    def getfilepathandclose(self,):
        
        self.list_dir = self.autolaunch.enter_dir_path.text()
        
        
        
        #del self.enter_dir_path
        self.close_path_input_sig.emit()
        
    def autorun_gettraps(self):
        #first disconnect the interruptions during the analysis.
        
        self.AControl.t0selector.currentTextChanged.disconnect(self.AControl.override_check)
              
        ret, self.dir_path_list, self.save_dir_path,self.network_dir = get_video_paths(self.list_dir)

        
            
        if not ret == 0:
            self.msgbox.setText('Analysis has found file names which are not .ome.tif files, do you want to continue?')
            self.msgbox.exec_()
            
        counter = 0
        
        for video_path in self.dir_path_list:
            counter +=1
            print(video_path)
            if video_path.find('Pos')+3 == '0':
                self.analyser.videopos = '9'
            else:
                
                self.analyser.videopos = video_path[video_path.find('Pos')+3]
            
            print('Why am I here?')
            if os.getcwd() != self.save_dir_path:
                os.chdir(self.save_dir_path)
            self.analyser.videopath = video_path
            if isTiff(video_path) == 0:
                try:
                    print('made it here')
                    self.analyser.frames, self.analyser.videolength = self.analyser.load_frames()
                    print('frame deposit length ',self.analyser.videolength)
                    
                    self.AControl.update_frames(self.analyser.videolength)
                    self.has_frames = True
                    
                except Exception as e:
                    '''file = open(os.getcwd() +'errorlog.txt','w')'''
                    print(e,'Hi i caught this exception')
                    '''file.write(str(e) +',')
                    '''
                    '''file.close()'''
                    continue
            else:
                continue
            
            os.chdir(self.network_dir)
            self.get_traps()
            

                        
                
            t0 = int(self.AControl.t0selector.currentText()) - self.start_offset
            self.AControl.t0selector.setCurrentText(str(t0))
            
            tmax = t0 +1200
            if tmax > self.analyser.videolength:
                self.AControl.tmaxselector.setCurrentText(str(self.analyser.videolength - 1))
            else:
                self.AControl.tmaxselector.setCurrentText(str(tmax))
                
            self.run_just_analysis()
            
            self.remove_vesicles_which_moved(self.analyser.filtered_first_intensity_trace)
            self.video_directory = self.save_dir_path + '/'

            self.auto_save_data()
                
            
       
    def remove_vesicles_which_moved(self,dictionary,threshold = -0.07,frames =None):
        
        jump_frames = []
        for key in dictionary.keys():
            
            vesintens = np.array(dictionary[key])
            large_jumps, diffs  = findjump(vesintens,threshold)
            
            if large_jumps.shape[0] > 0:
                jump_frames.append([key,large_jumps[0]+int(self.AControl.t0selector.currentText()),diffs[large_jumps[0]]])
                
        if frames is None:
            frames = self.analyser.frames
            
        tbk = []
        for frame_datum in jump_frames:
            
            images= frames.asarray(key = slice(frame_datum[1],frame_datum[1]+2))
            
            subtracted_images = images[0]-images[1]
            
    
            
            tbk.append(findmovedvesicles(subtracted_images))
           
        #copy the filtered intensity trace data and then delete the removed vesicles from it
        
        self.analyser.rffitrace = copy.deepcopy(self.analyser.filtered_first_intensity_trace)
        self.analyser.rffatrace = copy.deepcopy(self.analyser.filtered_firstareatrace)
        
        print(self.analyser.rffitrace)
        for i in range(0,len(tbk)):
            
            try: 
                tbk[i][0]
                del self.analyser.rffitrace[jump_frames[i][0]]
    
                del self.analyser.rffatrace[jump_frames[i][0]]
                print('removed vesicle')
            except TypeError:
                continue
    
    def purge(self):

        #reset analyser which contains the data. Reset thread as might contain data\
        
        os.chdir(self.network_dir)
        
        self.analyser = Analyser('')
        self.mythread = QThread()
        del self.sv
        self.display = VideoBorder()
        self.vid_control = VideoViewerControl()
        self.loadbox.videopathlist = None
        self.layout.addWidget(self.display,0,3)
        self.layout.addWidget(self.vid_control,2,4)
        del self.sb
        self.trap_bool = False
        self.has_frames = False
        
        
    
    def video_path_collection_error(self):
        
        self.msgbox.setText('Cannot add any more file paths than 4 at the moment.')
        self.msgbox.exec_()
        
    



    def show_load(self):
        self.loader = lb(self)
        self.loader.show()
    
    def generate_single_vesicle_viewer(self):
    
        #first check if there are frames to view
        
        if self.analyser.frames is None:
        
            self.msgbox.setText('Load some video to watch!')
            self.msgbox.exec_()
        
            return -1

        frames_dict = {}
        frames_dict['1'] = self.analyser.frames
        
        if self.sv is not None:
            
            self.sv = None
        
    
        if self.mode == 'directional':
            self.sv = SingleVesViewer(frames_dict,mode = 'directional')
            self.sv.show()
    
    
        #if trap positions have been found it is safe to bring up video viewer for contents of single traps.
        if self.analyser.trapgetter.trap_positions is not None:
            
            self.sv.set_annotations(traps = self.analyser.trapgetter.trap_positions,labels = self.analyser.trapgetter.labels,box_dimensions = self.analyser.trapgetter.trapdimensions)
            print(self.analyser.trapgetter.labels)
            self.sv.label_select.addItems(self.analyser.trapgetter.labels.astype(str).tolist())
        #if the analysis has been run and the intensity traces, centres_of_vesicles in each frame, areas and t0 and tmax have been defined it is safe to allow plotting function and button to show detected vesicle centres overlayed on video
        
        
            
        
        if self.analyser.bg_sub_intensity_trace != {}:
        
            #if intensity data is there assume that the active traps have been filtered correctly so update the option box for trap viewing to only the active traps
            
            self.sv.label_select.clear()
            self.sv.label_select.addItems(list(self.analyser.bg_sub_intensity_trace.keys()))
            
            # Add plotting data

            self.sv.ydataI = self.analyser.bg_sub_intensity_trace
            self.sv.ydataA = self.analyser.filtered_areatrace
            
            if self.combo_switch_off:
                self.sv.t0 = self.reloadt0
                self.sv.tmax =self.reloadtmax
            else:
                self.sv.t0 = self.AControl.t0
                self.sv.tmax = self.AControl.tmax
    
            self.sv.delete.clicked.connect(self.delete_vesicle_and)
            self.sv.interact_display.accepted.connect(self.get_heat_plot)

            self.sv.save_heat.clicked.connect(self.prepare_heat_data4save)
            
            self.sv.proceed_to_directional_query.accepted.connect(self.create_persisting_times)
        if self.analyser.centres is not None:
            self.sv.set_centres(self.analyser.centres)

    def generate_multi_vidsvv(self):

        #this function generates the single video viewer with suitable feature for viewing vesicles which are spread across multiple different video files.

        return None

    def get_heat_plot(self):
    
        print('Made it to get-heat_plot')
        
        self.analyser.heat_data_generator()
        self.analyser.get_heat_plot()
    
    
    def delete_vesicle_and(self):
    
        label_as_str = self.sv.label_select.currentText()
    
        self.analyser.delete_vesicle(label_as_str)

        #if multivideo mode need to also deleted label from analyser by vid
        '''
        if self.sv.multividflag:
            vid = self.sv.video_select.currentText()
            self.sv.activelabels_by_vid[vid] = self.sv.activelabels_by_vid[vid][self.sv.activelabels_by_vid[vid] != int(label_as_str)]
            self.activelabels_byvid[key] = self.activelabels_byvid[key][self.activelabels_byvid[key] != int(label_as_str)]
            
            self.sv.displaylabels_by_vidid()
        
        else:
            self.sv.label_select.clear()
            self.sv.label_select.addItems(list(self.analyser.bg_sub_intensity_trace.keys()))
        '''
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
        
        #first get directory

       
        
        if self.analyser.videopath == '':
            
                    

            
            
            self.msgbox.setText('No File path has been set, Please select a compatible video file')
            self.msgbox.show()
        
        else:
            
            self.video_directory = self.analyser.videopath[::-1].partition('/')[2][::-1] + '/'
            print(self.video_directory)            
            
            
            
            
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
        '''
        if not self.AControl.multi_pressed_flag:
            
            labelled_traps = np.hstack((self.analyser.trapgetter.labels[:,np.newaxis],self.analyser.trapgetter.trap_positions))
        '''
        labelled_traps = np.hstack((self.analyser.trapgetter.labels[:,np.newaxis],self.analyser.trapgetter.trap_positions))
        '''
        else:
            all_traps = None
            all_labels = None
            
            for key in self.loadbox.videopathlist.keys():
                if all_traps is None:
                    
                    all_traps = self.analyser.traps_by_vid[key]
                    all_labels = self.analyser.labels_by_vid[key]
                else:
                    all_traps = np.vstack((all_traps,self.analyser.traps_by_vid[key]))
                    all_labels = np.concatenate((all_labels,self.analyser.labels_by_vid[key]))
                    print(all_traps.shape)
                    print(all_labels.shape)
                    
            labelled_traps = np.hstack((all_labels[:,np.newaxis],all_traps))
        '''
        
        
        save_directory = self.video_directory
        self.sb = SaveBox(labelled_traps,self.analyser.bg_sub_intensity_trace,self.analyser.bg_sub_firstintensity_trace,self.analyser.filtered_intensity_trace,self.analyser.filtered_first_intensity_trace,self.analyser.areatrace,self.analyser.firstareatrace,self.analyser.filtered_areatrace,self.analyser.filtered_firstareatrace,self.analyser.centres,self.analyser.firstcentres,self.analyser.rffitrace,self.analyser.rffatrace,self.AControl.t0,self.AControl.tmax,save_directory)
    
        self.sb.show()
    
    def auto_save_data(self):
        
        labelled_traps = np.hstack((self.analyser.trapgetter.labels[:,np.newaxis],self.analyser.trapgetter.trap_positions))

        
        save_directory = self.video_directory
        self.sb = SaveBox(labelled_traps,self.analyser.bg_sub_intensity_trace,self.analyser.bg_sub_firstintensity_trace,self.analyser.filtered_intensity_trace,self.analyser.filtered_first_intensity_trace,self.analyser.areatrace,self.analyser.firstareatrace,self.analyser.filtered_areatrace,self.analyser.filtered_firstareatrace,self.analyser.centres,self.analyser.firstcentres,self.analyser.rffitrace,self.analyser.rffatrace,self.AControl.t0,self.AControl.tmax,save_directory,self.analyser.videopath)
        self.sb.autosave()
                
        self.sb = None
        self.sv = None
        
        self.clean_data_stores()
        
        

        
    
    def clean_data_stores(self):
        
        self.analyser.intensitytrace = {}
        self.analyser.firstintensitytrace = {}

        self.analyser.secondintensitytrace = {}
        self.analyser.firstsecondintensitytrace = {}

        self.analyser.bg_sub_intensity_trace = {}
        self.analyser.bg_sub_firstintensity_trace = {}

        self.analyser.filtered_intensity_trace = {}
        self.analyser.filtered_first_intensity_trace = {}

        self.analyser.second_bg_si_trace = {}
        self.analyser.second_bg_fsi_trace = {}

        self.analyser.areatrace = {}
        self.analyser.firstareatrace = {}

        self.analyser.filtered_areatrace = {}
        self.analyser.filtered_firstareatrace = {}

        self.analyser.firstsecondareatrace = {}
        self.analyser.secondareatrace = {}

        self.analyser.areaerrors = {}
        self.analyser.centres = {}
        self.analyser.firstcentres = {}
        
        self.AControl.t0selector.clear()
        self.AControl.tmaxselector.clear()
        
        
        print('cleaned')
        
        
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
        
        self.vid_control.showdisplay.clicked.connect(self.load_display)
        self.vid_control.withtraps_switch.clicked.connect(self.turn_on_traps)
        
    
        # wave flag to say frames have been loaded
        self.has_frames = True
        self.tc.trapgetbtn.clicked.connect(self.get_traps)
        self.tc.viewtrapkernelbtn.clicked.connect(self.view_kernel)
        # connect trap buttons to the analyser
        self.AControl.update_frames(self.analyser.videolength)
    

        
    def pre_flight_check(self):

        
        #after we have checked in the AControl that t0 and tmax have been assigned, we also check here that the length of the video to be analysed is valid. I have presumed that a video of less than 100 frames is probably a mistake. So i warn Kareem. However, I give the user the opportunity to run analysis anyway.
        #If the length of the video is longer than this we proceed directly with the analysis.
        length = int(self.AControl.tmaxselector.currentText()) - int(self.AControl.t0selector.currentText())
        if length < 100:
            self.msgbox.setText(' Hi Kareem, are you sure you want to analyse a video of less than 100 frames? Click Ok to proceed with analysis')
                                
                                

                                
            ret = self.msgbox.exec_()
        
            self.proceed_yes_or_no(ret)
        '''
        elif not self.AControl.multi_pressed_flag:
            self.run_analysis()
        '''
        self.run_analysis()
        '''
        else:
            print('multi run analysis function about to run')


            self.remove_empty_vid_paths()
            self.multi_run_analysis()
        ''' 
            

    def remove_empty_vid_paths(self):

        #first delete unfilled videopaths in the user created list.
        
        for key in list(self.loadbox.videopathlist.keys()):
            if self.loadbox.videopathlist[key] is None:
                self.loadbox.videopathlist.pop(key)
                    
    def proceed_yes_or_no(self,ret):
        
        print(ret, "hi")
        if ret == QMessageBox.Ok:
            '''
            if not self.AControl.multi_pressed_flag:
                self.run_analysis()
            '''
            self.run_analysis()
            '''
            else:
                self.remove_empty_vid_paths()
                self.multi_run_analysis()
            ''' 
    '''        
    def multi_run_analysis(self):
        self.activelabels_byvid = {}
         
        label_offset = 0
        for key in self.loadbox.videopathlist.keys():
            #first load the new video
            
            
            self.analyser.videopath = self.loadbox.videopathlist[key]
            
            self.analyser.multivid_frames[key]= self.analyser.load_frames(self.AControl.t0,self.AControl.tmax)
            self.analyser.mask = None
            self.analyser.frames = self.analyser.multivid_frames[key]
            self.analyser.traps_by_vid[key], self.analyser.labels_by_vid[key] = self.get_traps(multividflag = True)
            
            self.analyser.labels_by_vid[key] += label_offset
            
            #increase the offset for the next labels to be the largest label of the current set
            label_offset = self.analyser.labels_by_vid[key][-1]
            
            #now make these traps and labels the trap positions and labels which are passed to the main analysis functions 
            
            self.analyser.trapgetter.trap_positions = self.analyser.traps_by_vid[key]
            self.analyser.trapgetter.labels = self.analyser.labels_by_vid[key]
  
            #now the trap_positions and labels have been set, perform the analysis. As the intensity traces and areas are dictionaries with the labels as keys, and they are class attributes, they should 
            if self.analyser.trapgetter.trap_positions is not None:
                self.analyser.sett0frame(int(self.AControl.t0selector.currentText()))
                
    
                self.analyser.get_clips_alt()
                self.analyser.classify_clips()
                self.activelabels_byvid[key] = self.analyser.active_labels
                self.analyser.analyse_frames(int(self.AControl.tmaxselector.currentText()),multivid = True)
                self.analyser.extract_background(int(self.AControl.tmaxselector.currentText()))
                self.analyser.subtract_background()          
            print(self.analyser.labels_by_vid[key])

        self.save_data_btn.clicked.connect(self.save_data)
        print('Keys for dictionary of frames ,' , self.analyser.multivid_frames.keys())
        if self.sv is not None:

            self.sv = None
        if self.mode == 'directional':


            self.sv = SingleVesViewer(self.analyser.multivid_frames,self.analyser.traps_by_vid,self.analyser.labels_by_vid,self.activelabels_byvid,self.analyser.trapgetter.trapdimensions,self.mode)
            self.sv.show()
            
        else:
            self.sv = SingleVesViewer(self.analyser.multivid_frames,self.analyser.traps_by_vid,self.analyser.labels_by_vid,self.activelabels_byvid,self.analyser.trapgetter.trapdimensions)
            self.sv.show()
        self.sv.set_centres(self.analyser.centres)

        self.sv.t0 = self.AControl.t0
        self.sv.tmax = self.AControl.tmax
            
        #add plotting_data
        self.sv.ydataI = self.analyser.bg_sub_intensity_trace
        self.sv.ydataA = self.analyser.filtered_areatrace
        

        #add data for comparison, determined by a separate method.
            
            
        self.sv.compare_ydataI = self.analyser.second_bg_si_trace
        self.sv.compare_ydataA = self.analyser.secondareatrace
            

            
            
            
        #Add connections to heat plot generator from buttons in the single vesicle viewer
        self.sv.delete.clicked.connect(self.delete_vesicle_and)
        self.sv.interact_display.accepted.connect(self.get_heat_plot)
        self.sv.save_heat.clicked.connect(self.prepare_heat_data4save)
        #Add connection to directional heat_plot_gen
            
            
        self.sv.proceed_to_directional_query.accepted.connect(self.create_persisting_times)


        print(self.analyser.trapgetter.trap_positions)           
                
    '''     
    def run_just_analysis(self):
        

        self.analyser.sett0frame(int(self.AControl.t0selector.currentText()))
        
        print(self.analyser.t0frameNo)
        
        self.analyser.get_clips_alt()
        self.analyser.classify_clips()
        self.analyser.analyse_frames(int(self.AControl.tmaxselector.currentText()))
        self.analyser.extract_background(int(self.AControl.tmaxselector.currentText()))
        self.analyser.subtract_background()
    
        print(list(self.analyser.bg_sub_intensity_trace.keys()))
            
        # if an instance of the Single Vesicle Viewer exists, we just want to update the allowed labels to those that have detectable vesicles. And we want to supply it with the dictionary of detected particle centres. If not we need create a new instance automatically.
        
        #Connect the save_data button so it does something when clicked now
        
            
        if self.sv is not None:
        
            self.sv = None

        #create a dictionary which matches the video to the labelled position of this video in the chamber. This is done so that the single video case may be handled in the same way as the multivideo case.
            
        frames_dict = {}
        frames_dict['1'] = self.analyser.frames
        
        if self.mode == 'directional':

            
            self.sv = SingleVesViewer(frames_dict,self.analyser.trapgetter.trap_positions,self.analyser.trapgetter.labels,list(self.analyser.bg_sub_intensity_trace.keys()),self.analyser.trapgetter.trapdimensions,mode = 'directional')
            
        else:
            self.sv = SingleVesViewer(self.analyser.frames,self.analyser.trapgetter.trap_positions,self.analyser.trapgetter.labels,self.analyser.trapgetter.trapdimensions)
            
        self.sv.set_centres(self.analyser.centres)

        self.sv.t0 = self.AControl.t0
        self.sv.tmax = self.AControl.tmax
        
        #add plotting_data
        self.sv.ydataI = self.analyser.bg_sub_intensity_trace
        self.sv.ydataA = self.analyser.filtered_areatrace
        
        print(self.sv.ydataI)
        print(self.sv.ydataA)

        
        #add data for comparison, determined by a separate method.
        
        
        self.sv.compare_ydataI = self.analyser.second_bg_si_trace
        self.sv.compare_ydataA = self.analyser.secondareatrace
        

        
        
        
        #Add connections to heat plot generator from buttons in the single vesicle viewer
        self.sv.delete.clicked.connect(self.delete_vesicle_and)
        self.sv.interact_display.accepted.connect(self.get_heat_plot)
        self.sv.save_heat.clicked.connect(self.prepare_heat_data4save)
        #Add connection to directional heat_plot_gen
        
        
        self.sv.proceed_to_directional_query.accepted.connect(self.create_persisting_times)
        print('analysis Done')
        
        
        
    def run_analysis(self):
    
        # run analysis
        #when it is done call svv.set_annotations(self.analyser.trapgetter.trap_positions,self.analyser.intenstrace.keys,trap_dimensions), this should update the selection menu with only the labels of traps which have a detected vesicle inside.
        #After this we can include set svv.centres = self.analyser.centres (which is a dictionary)
        
        #set self.svv.t0 and self.svv.tmax such that detected centres match the frames in video.
        
        #check first that length of video to be analysed is not zero
        

                                
        if self.analyser.trapgetter.trap_positions is not None:
            
            self.run_just_analysis()
            
            self.remove_vesicles_which_moved(self.analyser.filtered_first_intensity_trace)
            
            self.save_data_btn.clicked.connect(self.save_data)
            
            
            self.sv.show()

        else:
            self.msgbox.setText('Make sure video has been loaded and trap positions have been found. Press "Get Traps" ')
            self.msgbox.show()


    '''def remove_vesicles_which_moved(self):
        
        print('Current start frame value , ' , self.AControl.t0selector.currentText())
        
        kill_labels = subtract_moved_vesicles(self,self.analyser.frames,int(self.AControl.t0selector.currentText()),self.analyser.trapgetter.trap_positions,self.analyser.trapgetter.labels)
        
        print(kill_labels)
        if kill_labels.shape[0] == 0:
            print('No vesicles were found to have moved')
            return
        
        
        for label in kill_labels:

            try:
                del self.analyser.intensitytrace[str(label)]
                del self.analyser.firstintensitytrace[str(label)]
                del self.analyser.secondintensitytrace[str(label)]
                del self.analyser.firstsecondintensitytrace[str(label)]
                del self.analyser.bg_sub_intensity_trace[str(label)]
                del self.analyser.bg_sub_firstintensity_trace[str(label)]
                del self.analyser.filtered_intensity_trace[str(label)]
                del self.analyser.filtered_first_intensity_trace[str(label)]
                del self.analyser.second_bg_fsi_trace[str(label)]
                del self.analyser.second_bg_si_trace[str(label)]
                del self.analyser.areatrace[str(label)]
                del self.analyser.firstareatrace[str(label)]
                del self.analyser.filtered_areatrace[str(label)]
                del self.analyser.filtered_firstareatrace[str(label)]
                del self.analyser.firstsecondareatrace[str(label)]
                del self.analyser.secondareatrace[str(label)]
            except KeyError:
                print('Did not find any data extract for vesicle with this label')
                
        self.analyser.trapgetter.labels = self.analyser.trapgetter.labels[np.searchsorted(self.analyser.trapgetter.labels,kill_labels)]
        self.analyser.trapgetter.trap_positions = self.analyser.trapgetter.trap_positions[np.searchsorted(self.analyser.trapgetter.labels,kill_labels)]
    '''    

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

    def no_manual_override(self):
        
        self.AControl.t0selector.setCurrentText(str(self.bgf.peak_max_arg))
        
    def get_traps(self,multividflag = False):


        #first use the background finder to find the frame in which to threshold intensity
        self.bgf.get_background(self.analyser.frames)
        self.bgf.get_data_gradient()
        self.bgf.find_correct_gaussian_scale()

        self.AControl.has_been_overriden = True
        
        if self.autolaunch.overridet0flag:
            t0 = int(self.autolaunch.t0selector.currentText())
            self.AControl.t0selector.setCurrentText(str(t0))
        
        else:
            t0 = self.bgf.peak_max_arg
            
            print(t0 ,'is equal to the peak max index')
            
            self.AControl.t0selector.setCurrentText(str(self.bgf.peak_max_arg))
            file = open(os.getcwd() +'/Experimentalflowrates.csv','w')

            flow_rate = np.average(self.bgf.gradient[int(self.bgf.peak_begin_frame):int(2*self.bgf.peak_max_arg - self.bgf.peak_begin_frame)])
            
            

            file.write(self.analyser.videopath + str(flow_rate)+',')
            

            file.close()
        self.AControl.update()
        self.AControl.override_warning.rejected.connect(self.no_manual_override)
        
        
        if self.has_frames:
            try:
                if multividflag:
                    traps, labels = self.analyser.get_traps(0)
                else:
                    print('made it to calling analyser get traps')
                    print('t0 is equal to ',t0)
                    traps,labels = self.analyser.get_traps(self.bgf.peak_begin_frame)
                
                #Once traps have been successfully found, make them available for display on video view
                
                self.display.videoviewer.make_annotations_available(self.analyser.trapgetter.trap_positions,self.analyser.trapgetter.labels)
            
                return traps,labels
            
            except Exception as e:
                print(e)
                
                self.msgbox.setText('Getting traps failed. Check Kernel, and that the visibility of the traps in the\n last frame is good')
                self.msgbox.show()
        return t0
            

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

    def prepare_heat_data4save(self):

        #first make sure the heat data has been calculated

        if self.analyser.heat_data.shape[0] ==0:
            self.msgbox.setText('No Heat Plot Data detected.. Make sure you have had a look at the plot')
            self.msgbox.exec_()

        else:
            
            #create data dictionary and then pass it to the savebox
            data = {}
            data['times'] = self.analyser.times
            data['heat'] = self.analyser.heat_data
            
            self.HeatSave = saveboxview(data)
            
            
            
            
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
        
        self.analyser.frames, self.analyser.videolength = self.analyser.load_frames()
        self.sig1.emit()

    def run_just_analysis(self):
        
        self.analyser.run_just_analysis()
        self.sig1.emit()

class LoadBox(QtWidgets.QWidget):
    
    loaderror = pyqtSignal()
    
    def __init__(self):
        QWidget.__init__(self)
        self.choosevideo = QPushButton('Choose Video')
        self.pathshower = QLineEdit('Select a Video')
        
        self.videopathlist = None

        self.load_video = QPushButton('Load')
        
        #Add Button to create video queue

        self.create_queue_btn= QPushButton('Create Video Queue')
        self.create_queue_btn.clicked.connect(self.create_queue)
        
        #Add button to append path to list
        self.add_path_btn = QPushButton('+')
        self.add_path_btn.clicked.connect(self.add_path)
        
        self.sublayout = QtWidgets.QHBoxLayout()

        #create a subqidget for the layout
        widg = QtWidgets.QWidget()
        
        self.sublayout.addWidget(self.create_queue_btn)
        self.sublayout.addWidget(self.add_path_btn)
        self.sublayout.addWidget(self.load_video)

        widg.setLayout(self.sublayout)
        
        self.lyt = QtWidgets.QVBoxLayout()

        self.lyt.addWidget(self.pathshower)
        self.lyt.addWidget(self.choosevideo)
        self.lyt.addWidget(widg)
        

        self.setLayout(self.lyt)




    def create_queue(self):
        #initialise dictionary to store paths of videos in
        
        self.videopathlist = {}
        for i in range(1,5):
            self.videopathlist[str(i)] = None
            
        self.num_of_videos = 0
        
    def add_path(self):
        if self.videopathlist is not None:
            #check number of paths user has attempted to add is less or equal to 4. if not send signal to owner of this class (main GUI) to raise message to user
            self.num_of_videos += 1
            if self.num_of_videos <=4:
                
                self.videopathlist[str(self.num_of_videos)] = self.pathshower.text()
                print(self.pathshower.text() + ' has been added to the queue')
            else:
                self.loaderror.emit()
        else:
            self.loaderror.emit()
            
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
        
        if frames is None:
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
                                
        
        
class Autorunlaunch(QWidget):
    
    def __init__(self):
        QWidget.__init__(self)      
        
        self.enter_dir_path = QLineEdit('Enter directory of videos to analyse')
        
        self.start_offset = QComboBox()
        self.overridet0btn = QPushButton('Override t0 frame')
        self.overridet0label = QLabel('Off')
        
        self.t0selector = QComboBox()
        items = np.arange(800).astype(str)
        self.t0selector.addItems(items)
        
        self.overridet0flag = False
        
        
        items = np.arange(40).astype(str)
        self.start_offset.addItems(items)
        self.start_offset.setCurrentText('0')
        
        
        self.overridet0btn.clicked.connect(self.pushthebutton)
        
        
        layout = QtWidgets.QHBoxLayout()
        
        
        layout.addWidget(self.enter_dir_path)
        layout.addWidget(self.start_offset)
        layout.addWidget(self.overridet0btn)
        layout.addWidget(self.overridet0label)
        layout.addWidget(self.t0selector)
        
        self.setLayout(layout)
        
    def pushthebutton(self):
        
        if self.overridet0flag:
            self.overridet0flag = False
            self.overridet0flag.setText('Off')
            
        else:
            self.overridet0flag = True
            self.overridet0label.setText('On')
            
            
        
        
        
                                
#function to determine whether file path is likely a tiff
        
def isTiff(path):
    
    ret = -1
    
    if path[-8:] == '.ome.tif' or path[-10:] == '.ome-1.tif':
        ret = 0
        
     
    return ret
        
            
if __name__ == '__main__':
    
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
        
    else:
        app = QtWidgets.QApplication.instance()
    print('success')
    



    mw = MW(mode = 'directional')

    mw.close_signal.connect(app.closeAllWindows)
    app.exec_()


