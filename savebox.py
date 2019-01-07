from qtpy import QtGui,QtWidgets,QtCore
from qtpy.QtWidgets import QWidget,QMainWindow, QApplication,QPushButton,QComboBox,QProgressBar,QFileDialog, QGridLayout, QLabel,QLineEdit
from PyQt5.QtCore import pyqtSignal,QThread
import pandas as pd
import os
from threadworker import myworker
import numpy as np
import pickle
#This class supplies a save box which pops up at the call of a save button in the parent class.
#It allows input of a Date Identifier and then handles saving the complete file names automatically.
#The aim is to save dictionaries of data so have exploited pandas dataframes to save to csv.

#Aim is to save the trap_positions, vesicle intensities, vesicle areas and vesicle centres.

#These are all saved in a csv file for convenience for the user who may not be familiar with python.

class SaveBox(QWidget):

    #pass the dictionaries to be saved

    def __init__(self,labelled_traps,intensities,firstintensities,filtered_intensities,areas,firstareas,filtered_areas,centres,firstcentres,t0,tmax,save_directory):
        
        
        QWidget.__init__(self)
        #Create thread for saving
        
        self.save_thread = QtCore.QThread()
        
        #save directory to save files to
        
        self.sd = save_directory
        #include warning box for errors
        self.warning_box = QtWidgets.QMessageBox()

        
        self.labelled_traps = labelled_traps
        self.intensities = intensities
        self.firstintensities = firstintensities
        
        self.fintensities = filtered_intensities
        self.ffintensities = first_filtered_intensities
        
        self.areas = areas
        self.firstareas = firstareas
        self.fareas = filtered_areas
        self.ffareas = first_filtered_areas
        
        self.centres = centres
        self.firstcentres = centres
        
        self.bookends = np.array([t0,tmax])
        
        self.worker = myworker(self.go_on_and_save)
        
        self.save_thread.started.connect(self.worker.run)
        
        self.worker.sig1.connect(self.save_thread.exit)
        self.worker.sig1.connect(self.close)
        
        #in order to save as csv file we must make all the numpy arrays the same length
        self.save_Date = QtWidgets.QLineEdit('Enter Date, NOT WITH "/"! ')

        self.save_Time = QtWidgets.QLineEdit('Enter Time')

        
        self.save_btn = QtWidgets.QPushButton('Save')
        
        

        self.layout = QtWidgets.QVBoxLayout()


        self.layout.addWidget(self.save_Date)

        self.layout.addWidget(self.save_Time)


        self.setLayout(self.layout)


        
        self.save_Time.returnPressed.connect(self.start_thread)

        self.save_btn.clicked.connect(self.start_thread)

    
    def start_thread(self):
    
        self.save_thread.start()
    
    

    def go_on_and_save(self):


        np.savetxt(self.sd + 'trap_positions' + '_' + self.save_Date.text()+'_'+self.save_Time.text()+ '.csv',self.labelled_traps,delimiter = ',')

        

        #Save intensity traces


        df = pd.DataFrame.from_dict(self.intensities,orient = 'index').transpose().fillna('')

        df.to_csv(self.sd + 'Intensities' + '_' + self.save_Date.text()+'_'+self.save_Time.text()+ '.csv')

        df = pd.DataFrame.from_dict(self.fintensities,orient = 'index').transpose().fillna('')

        df.to_csv(self.sd + 'filtered_Intensities' + '_' + self.save_Date.text()+'_'+self.save_Time.text()+ '.csv')

        df = pd.DataFrame.from_dict(self.firstintensities,orient = 'index').transpose().fillna('')

        df.to_csv(self.sd + 'detected_at_beginning_Intensities' + '_' + self.save_Date.text()+'_'+self.save_Time.text()+ '.csv')

        df = pd.DataFrame.from_dict(self.ffintensities,orient = 'index').transpose().fillna('')

        df.to_csv(self.sd + 'detected_at_beginning_filtered_Intensities' + '_' + self.save_Date.text()+'_'+self.save_Time.text()+ '.csv')        
        #Save Areas

        df = pd.DataFrame.from_dict(self.areas,orient = 'index').transpose().fillna('')

        df.to_csv(self.sd + 'Areas' + '_' + self.save_Date.text()+'_'+self.save_Time.text()+ '.csv')

        df = pd.DataFrame.from_dict(self.fareas,orient = 'index').transpose().fillna('')

        df.to_csv(self.sd + 'filtered_Areas' + '_' + self.save_Date.text()+'_'+self.save_Time.text()+ '.csv')



        #Save Detected Vesicle Centres. these are serialised using pickle as do not anticipate the user wanting to use the detected centre coordinates outside of python

        file = open(self.sd + 'Centres' + '_' + self.save_Date.text()+'_'+self.save_Time.text()+ '.txt','wb')
        

        pickle.dump(self.centres,file,pickle.HIGHEST_PROTOCOL)


        #save t0 and tmax

        np.savetxt(self.sd + '/bookendtimes' + '_' + self.save_Date.text()+'_'+self.save_Time.text()+ '.csv',self.bookends,delimiter = ',')








class LoadBox(QWidget):

    done_load_sig = pyqtSignal()
    def __init__(self,obj):

        QWidget.__init__(self)


        
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #Add a standard display box for error messages to user
        
        self.msgbox = QtWidgets.QMessageBox()
        
        self.data_deposit = obj
        
        self.layout = QtWidgets.QVBoxLayout()

        #add load button and connect
        
        self.load_button = QPushButton('Load')
        self.load_button.clicked.connect(self.load_regular)
        
        
        self.overide_load_fmt = QPushButton('Load files with different name convention')
        
        self.done_load_sig.connect(self.close)

        self.directorypathchoose = QLineEdit('Input directory path in format "C:/..." without final "/"')
        self.datechoose = QLineEdit('Choose Date in format: "DD-MM-YY"')
        self.timechoose = QLineEdit('Choose Time in format: "HH:MM"')
        
        #add ability to load upon pressing Enter only for time input, on presumption that people will fill date first and then the time..
        
        self.timechoose.returnPressed.connect(self.load_regular)
        
        
        self.layout.addWidget(self.directorypathchoose)
        
        self.layout.addWidget(self.datechoose)

        self.layout.addWidget(self.timechoose)

        self.layout.addWidget(self.load_button)
        
        self.layout.addWidget(self.overide_load_fmt)
        
        
        self.setLayout(self.layout)

    
        #When error occurs an error messagebox will be shown. When the user accepts this the loadbox should close to be reopenned again
        
        self.msgbox.buttonClicked.connect(self.close)
        

    def load_regular(self):

        
        self.directorypath = self.directorypathchoose.text()
        if self.directorypath[len(self.directorypath)-1]=='/':
            self.directorypath=self.directorypath[:len(self.directorypath)-1]
            

        try:
            #load intensities
            intensity_df = pd.read_csv(self.directorypath + '/Intensities' + '_' + self.datechoose.text()+'_'+self.timechoose.text()+ '.csv')
        except:
            self.msgbox.setText('Loading Intensity data failed, check the Date and Time have been written in the same way as\n when you saved the files')
            self.msgbox.exec_()
        
            return
        
        
        uncleaned_intensity_dict = intensity_df.to_dict(orient= 'list')
        
        
        self.data_deposit.analyser.bg_sub_intensity_trace = self.strip_dict_of_nan(uncleaned_intensity_dict)
        
        for key in self.data_deposit.analyser.bg_sub_intensity_trace.keys():
            print(type(self.data_deposit.analyser.bg_sub_intensity_trace[key]))

        #load areas
        
        try:
            area_df = pd.read_csv(self.directorypath + '/Areas' + '_' + self.datechoose.text()+'_'+self.timechoose.text()+ '.csv')

        except:
            self.msgbox.setText('Loading Intensity data failed, check the Date and Time have been written in the same way as\n when you saved the files')
            self.msgbox.exec_()
        
        uncleaned_area_dict = area_df.to_dict(orient = 'list')

        self.data_deposit.analyser.areatrace = self.strip_dict_of_nan(uncleaned_area_dict)
        

        
        #load trap_positions
        self.labelled_traps = np.loadtxt(self.directorypath + '/trap_positions' + '_' + self.datechoose.text()+'_'+self.timechoose.text()+ '.csv',delimiter = ',')

        labels_traps_split = np.hsplit(self.labelled_traps,[1,3])
        
        
        self.data_deposit.analyser.trapgetter.trap_positions = labels_traps_split[1].astype(int)
        
        self.data_deposit.analyser.trapgetter.labels = labels_traps_split[0].reshape((labels_traps_split[0].shape[0],)).astype(int)
        
        #load detected vesicle centres

        

        file = open(self.directorypath+ '/Centres' + '_' + self.datechoose.text()+'_'+self.timechoose.text()+ '.txt','rb')

        self.data_deposit.analyser.centres = pickle.load(file)
    

        #load bookend times for experiment length
        
        t0_tmax = np.loadtxt(self.directorypath + '/bookendtimes' + '_' + self.datechoose.text()+'_'+self.timechoose.text()+ '.csv',delimiter = ',')
        
        
        
        self.data_deposit.reloadt0 = int(t0_tmax[0])
        self.data_deposit.reloadtmax = int(t0_tmax[1])
    
        self.done_load_sig.emit()
    
      


    def strip_dict_of_nan(self,dict):

        del dict[np.array(list(dict.keys()))[0]]
        
        for key in np.array(list(dict.keys())):

            dict[key] = np.array(dict[key])

            
            dict[key] = dict[key][np.isnan(dict[key]) == False ]
            
            dict[key] = dict[key].astype(int)
        
        
        
        return dict
