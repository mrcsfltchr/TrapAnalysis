from qtpy import QtGui,QtCore,QtWidgets
from matplotlib import pyplot as pyplot
from Watchbackvideos import livestream
import qimage2ndarray as qnd
import numpy as np
from PyQt5.QtCore import pyqtSignal
from SingleVesPlotter import Plotter
import os

class SingleVesViewer(QtWidgets.QWidget):
    def __init__(self,frames,traps = None,labels= None,box_dimensions = None,mode = 'standard'):

        QtWidgets.QWidget.__init__(self)

        #store frames as a dictionary
        self.frames = frames
        self.trap_positions = traps
        self.labels = labels
        self.box_dimensions = box_dimensions
        self.centres = None
        #need to set length of video
        
        self.t0 = 0
        self.tmax = 1000
        
    
        self.mythread = QtCore.QThread()
        #   initialize single vesicle video as none type
    
    
        self.vesiclelife = None
    
    
        # Add deposits for the plotting data for every labelled trap.
        
        self.ydataI = None
        self.ydataA =  None
        
        #Add deposits for comparing the data to check two different methods of extracting intensity and the area
        
        self.compare_ydataI = None
        self.compare_ydataA = None

        
        #Add dictionaries to be passed to the plot function
        
        
        self.ydata = {}
        self.xdata = {}
        self.params = {}
        
        self.compare_xdata = {}
        self.compare_ydata = {}
        self.compare_labels = {}
        #Standard message box which prompts user to accept or reject and queued operation
        
        self.interact_display = StandardDialog()
        self.proceed_to_directional_query = StandardDialog()
        
        
        #Add vesicle delete button
        
        self.delete = QtWidgets.QPushButton('Delete Vesicle')
        
        
        #Add plotting buttons
        self.plot_label_btn = QtWidgets.QPushButton('Plot Single Trap')
        
        self.plot_label_btn.clicked.connect(self.plot_now)
        
        #add button to generate heatplot
        
        self.make_heat = QtWidgets.QPushButton('Generate Heat Plot')
        
        self.make_heat.clicked.connect(self.check_then_gen_heat)
        
        
        #Add button to generate directional heat map. Unless 'directional' mode is turned on this button is not displayed to the user.
        
        self.gen_directional_heatmap_btn = QtWidgets.QPushButton('Check Exp Directionality')
        self.gen_directional_heatmap_btn.clicked.connect(self.check_ready_to_record_times)
        
        #switch control for displaying thresholded or unprocessed image inside trap
        #abstract switch
        self.threshold_on = False
        
        #actual graphic switch
        self.threshold_control = QtWidgets.QPushButton('Show Thresholded Image')
        self.threshold_control.clicked.connect(self.show_thresholded_frame)
        
        #Layout
        
        self.lyt = QtWidgets.QGridLayout()
        
        self.mode_directional_on(mode)
        # Widgets
        self.label_select_lbl = QtWidgets.QLabel('Select Trap to view')
        
        self.label_select = QtWidgets.QComboBox()
    
        if self.labels is not None:
            self.label_select.addItems(self.labels.astype(str))
    
        # video viewer
        self.one_ves_view = livestream(qnd,images = None,annotations_on = False)
        
        self.go = QtWidgets.QPushButton('Display Trap')
        
        
        self.warning_box = QtWidgets.QMessageBox()

        
        
        self.plotter_with_border = PlotBox()
        
        self.go.clicked.connect(self.thread_display_generation)
        
        self.reload_with_centres = QtWidgets.QPushButton('Display with \n Detected Centres')
        
        self.reload_with_centres.clicked.connect(self.include_centres)
        
        #include button for saving heat data
        
        self.save_heat = QtWidgets.QPushButton('Save Heat Plot Data')
        
        
        self.lyt.addWidget(self.label_select_lbl,2,0)
        self.lyt.addWidget(self.label_select,3,0)
        self.lyt.addWidget(self.one_ves_view,0,1)
        self.lyt.addWidget(self.threshold_control,1,1)
        self.lyt.addWidget(self.go,4,0)
        self.lyt.addWidget(self.reload_with_centres,2,1)
        self.lyt.addWidget(self.plotter_with_border,0,0)
        self.lyt.addWidget(self.plot_label_btn,1,0)
        self.lyt.addWidget(self.make_heat,4,1)
        self.lyt.addWidget(self.save_heat,5,1)
        
        self.lyt.addWidget(self.delete,3,1)
        
        self.setLayout(self.lyt)
    
        self.show()
    
    
    def mode_directional_on(self,mode):
    
        if mode != 'directional':
            return None
            
            
        else:


            self.lyt.addWidget(self.gen_directional_heatmap_btn,5,1)
    

    
    def raise_no_labels_warning(self):
    
        self.warning_box.setText('Incorrect Label supplied')
        self.warning_box.exec_()
    
    
    def check_then_gen_heat(self):
    
        self.interact_display.label.setText('You are about to generate a heat plot. Please make sure all spurious vesicle detections have been removed! \n Click Ok to proceed')
    
        self.interact_display.exec_()
    
    
    def check_ready_to_record_times(self):
    
        self.proceed_to_directional_query.label.setText('You are about to catalogue the time taken for each vesicle to rupture. Please ensure that spurious detections have been removed manually before proceeding.\n Click Ok to proceed or Cancel to go back')
        self.proceed_to_directional_query.exec_()
    
    
    def plot_now(self):
    
        lbl = self.label_select.currentText()
    
        self.plotter_with_border.plotter.purge_axes()
        
        # check we have the required data
        
        if self.ydataA and self.ydataI is  None:
            self.warning_box.setText('Do not have valid plotting data')

            self.warning_box.show()

        else:
            self.ydata['Area'] = self.ydataA[lbl]

            
            self.ydata['Intensity'] = self.ydataI[lbl]

            
            self.params['Area'] = ['Time since t0/s','Area within Vesicle/Pixels','Detecting Radius Method' ]
            self.params['Intensity'] = ['Time since t0/s', 'Average Intensity within Vesicle/a.u.','Average only near centre']

            self.xdata['Area'] = 0.5*np.arange(len(self.ydataA[lbl]))
            self.xdata['Intensity'] = 0.5*np.arange(len(self.ydataI[lbl]))
            
            if self.compare_ydataA is not None and self.compare_ydataI is not None:
                self.compare_xdata['Area'] = 0.5*np.arange(len(self.compare_ydataA[lbl]))
                self.compare_xdata['Intensity'] = 0.5*np.arange(len(self.compare_ydataI[lbl]))
                self.compare_ydata['Area'] = self.compare_ydataA[lbl]
                self.compare_ydata['Intensity'] = self.compare_ydataI[lbl]
                self.compare_labels['Area'] = 'Thresholding Method'
                self.compare_labels['Intensity'] = 'Detecting Radius Method'
                self.plotter_with_border.plotter.plotIAforaves(self.xdata,self.ydata,self.params,compare_xdata = self.compare_xdata,compare_ydata = self.compare_ydata,compare_labels = self.compare_labels)
            else:
                self.warning_box.setText('Alternative Method Area and Intensity data not available')
                self.warning_box.exec_()
            
                self.plotter_with_border.plotter.plotIAforaves(self.xdata,self.ydata,self.params) 
        
        
    
    
    
    
    def include_centres(self):
        
        # centres is started as null. It is arranged that when the analysis is run, the single vesicle viewer classes 'self.centres' is filled with the centres for all detected vesicles. It is a dictionary with trap label as key for the numpy array of centre positions (shape No. of frames x 2)
        label = self.label_select.currentText()
        
        print(self.centres)
        if self.centres is not None and  self.vesiclelife is not None:
            self.one_ves_view.assign_images(self.vesiclelife[self.t0:self.tmax],self.centres[label])

        else:
            self.warning_box.setText('Either the vesicle centres data has not been supplied or the video has not been assigned.\n You will need to either press "Display" to load video or ensure that the analysis has been run.')
            self.warning_box.show()

    
    def thread_display_generation(self):
    
        self.myworker = myworker(self)
    
        self.myworker.moveToThread(self.mythread)
        self.myworker.sig1.connect(self.mythread.exit)
        self.myworker.sig2.connect(self.raise_no_labels_warning)
        
        self.mythread.started.connect(self.myworker.run)
        self.mythread.start()
    
    
    
    
    
    def go_pressed(self):
    
    
        print(self.t0,self.tmax)
        print(list(self.labels.astype(str)))
        print(type(self.trap_positions))
        
        print(id(self.label_select))
        
        try:
            label = int(self.label_select.currentText())
        except:
        
            return -1
        
        self.visualise_box_contents(label)
        print(self.vesiclelife)
        self.one_ves_view.assign_images(self.vesiclelife[self.t0:self.tmax])
    
        return 0
    
    
    def set_annotations(self,traps = None,labels = None,box_dimensions = None):
    
        self.trap_positions = traps
        self.labels = labels
        self.box_dimensions = box_dimensions
    
    
        if self.labels is not None:
            self.label_select.addItems((self.labels.astype(str).tolist()))

    
    def visualise_box_contents(self,label,key='1'):
        print(label)
        trap = self.trap_positions[self.labels == label][0]
        
        print('This is the trap',trap)
        
        clip = np.zeros_like(self.frames[key][0])
        
        try:
            #here we create a binary mask of shape 512*512 (frame size of video) such that only pixels within the labelled trap have value 1 and the rest 0
            
            clip[self.rectangle(start = trap-[self.box_dimensions[0],self.box_dimensions[2]],end = trap +[self.box_dimensions[1],self.box_dimensions[3]])[0],self.rectangle(start = trap-[self.box_dimensions[0],self.box_dimensions[2]],end = trap +[self.box_dimensions[1],self.box_dimensions[3]])[1]]=1
    
    
    
    
        except:
            raise IndexError
        
        #Here exploit numpy array broadcasting. First flatten each frame in the full video into a vector so that we get a 2d array of shape, No.of frames of video requested by user  X (512*512). Then we multiply each of these vectors by the binary mask calculated just before to extract the pixels within the requested trap. Then finally we remove the non zero pixels and reshape.
        
        
        self.vesiclelife = self.frames[key].reshape(self.frames[key].shape[0],self.frames[key].shape[1]*self.frames[key].shape[2])*clip.flatten()
        
        self.vesiclelife = self.vesiclelife[self.vesiclelife !=0]
        
        self.vesiclelife = self.vesiclelife.reshape(self.frames[key].shape[0],31,31)


    def rectangle(self,start, end=None, extent=None, shape=None):
        
        if extent is not None:
            end = np.array(start) + np.array(extent)
        elif end is None:
            raise ValueError("Either `end` or `extent` must be given")
        tl = np.minimum(start, end)
        br = np.maximum(start, end)
        if extent is None:
            br += 1
        if shape is not None:
            br = np.minimum(shape, br)
            tl = np.maximum(np.zeros_like(shape), tl)
        coords = np.meshgrid(*[np.arange(st, en) for st, en in zip(tuple(tl),
                                                                   tuple(br))])
            

        return np.vstack((coords[0].flatten(),coords[1].flatten()))

    def show_thresholded_frame(self):
        
        if self.threshold_on == False:
            self.threshold_on = True
            self.one_ves_view.turn_on_threshold(self.threshold_on)
            print(self.threshold_on)
        else:
            self.threshold_on = False
            print(self.threshold_on)
            self.one_ves_view.turn_on_threshold(self.threshold_on)
            

            

                           
                           
class saveboxview(QtWidgets.QWidget):

    def __init__(self,data):
        super().__init__()
        save_array = None
        if type(data) == dict:
            
            for key in data.keys():
                if save_array is None:
                    save_array  = np.array(data[key])
                else:
                    save_array = np.vstack((save_array,data[key]))
                    
           
        else:
            self.save_data = np.array(data)
            
        #hold data for saving
        
        self.save_data = save_array
        
        #Add Widgets to view
        
        self.EnterName = QtWidgets.QLineEdit('Enter File name')
        self.save_btn = QtWidgets.QPushButton("Save")
        
        self.lyt = QtWidgets.QVBoxLayout()
        self.lyt.addWidget(self.EnterName)
        self.lyt.addWidget(self.save_btn)
        
        self.setLayout(self.lyt)
        
        
        #connect save button to the function save
        self.save_btn.clicked.connect(self.save)
        self.EnterName.returnPressed.connect(self.save)
        self.show()
        
    def save(self):
        
        np.savetxt(os.getcwd() + '/'+self.EnterName.text()+'.csv',self.save_data,delimiter = ',')
        
        #purge save_data
        self.save_data = None
        
        self.close()
        
                
        
class myworker(QtCore.QObject):
    sig1 = pyqtSignal()
    sig2 = pyqtSignal()
    def __init__(self,obj):
        QtCore.QObject.__init__(self)
        
        self.obj = obj

    def run(self):



        error_code =   self.obj.go_pressed()
            
        if error_code ==0:
            self.sig1.emit()
        else:
            self.sig2.emit()



class PlotBox(QtWidgets.QFrame):
    
    def __init__(self):
        QtWidgets.QFrame.__init__(self)
        
        self.setStyleSheet("PlotBox { border:1px solid; }, ")
        
        self.layout = QtWidgets.QVBoxLayout()
        
        
        self.plotter = Plotter()
        
        
        self.layout.addWidget(self.plotter)
        
        
        self.setLayout(self.layout)




class StandardDialog(QtWidgets.QDialog):

    def __init__(self):

        super().__init__()
        #create layout for dialog
        self.layout = QtWidgets.QVBoxLayout()
        
        #create label for displaying text
        
        self.label = QtWidgets.QLabel('Something has happened! Press accept if you want whatever it is to continue, press cancel if you want it to stop!')
        
        self.proceedbox = QtWidgets.QDialogButtonBox()
        self.proceedbox.setOrientation(QtCore.Qt.Horizontal)

        self.proceedbox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel)


        self.layout.addWidget(self.label)
        self.layout.addWidget(self.proceedbox)


        self.setLayout(self.layout)
        
        self.proceedbox.rejected.connect(self.reject)

        self.proceedbox.accepted.connect(self.accept)


