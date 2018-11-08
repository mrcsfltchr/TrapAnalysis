


import numpy as np

from skimage.filters import threshold_otsu
from skimage.color import gray2rgb
import os
from matplotlib import pyplot as plt





#Below is a class to take an image of vesicles which is any frame from a 
#Peptide action experiment and create a heatmap representation of the
#correlation between time taken for vesicles to burst and their positions 
# in the traps

class DirectionalHeatMap(object):
    
    def __init__(self,frame,mask,mask_labels,persisting_times):
        
        #frame: Must be a frame which shows the vesicles in the experiment.
        
        
        #active_labels: These are the labels of vesicles from which useful data has been extracted
        
        #masks: This is an 2D array of size No.of active labels x (Image Height x Image Width)
        #the mask should be binary, such that for each row, which corresponds to a single labelled box.
        #pixels in side the box have value 1 and pixels outside have value 0. These are sparse vectors, predominantly have 0 values
        
        #persisting_times: This is a dictionary with key: label, value: persistance time
        
        #Is the length in integral minutes from the being exposed to the drug, to the
        #the intensity of the dye encapsulated in the vesicle to drop to 0.5 of maximum intensity.
        
        
        
        
        self.frame = frame
        print(self.frame)
        

        
        

        

        
        self.persisting_times = []
        self.active_labels = []
        
        for key in persisting_times.keys():
            
            
            self.active_labels.append(int(key))
        
        

            self.persisting_times.append(persisting_times[key])
         
        self.active_labels = np.array(self.active_labels)
        self.persisting_times = np.array(self.persisting_times)
        
        #self.masks should also be numpy array
        
        args = np.searchsorted(mask_labels,self.active_labels)
        
        self.masks = mask[args,:]
            

        
    def find_threshold(self,clip):
        #input flattened clip of image of shape Image Height x Image Width
        # use otsu's method to find threshold. number of non zero values in clips should be  31 X 31
        
        small_clip = clip[clip >0].reshape(31,31)
        
        threshold = threshold_otsu(small_clip)
        
        return threshold
    
    def give_heat2img(self):
        
        

        
        clips = self.masks*self.frame.flatten()
        
        #want to convert the gray image representation to an rgb rep, to show heat.
        
        self.frame = (self.frame / np.max(self.frame)).astype(int)
        self.frame *= 255 
        self.rgbframe = gray2rgb(self.frame)
        
        
        for index in range(0,clips.shape[0]):
            
            clip = clips[index]
            
            threshold = self.find_threshold(clip)
            
            clip = clip.reshape(self.frame.shape)
            
            
            
            self.rgbframe[clip > threshold] = self.colours[self.times2colours == self.persisting_times[index]]
            
            
            
            
            
    def colourscalegenerator(self):
        
        
        num_colour_increments = np.unique(self.persisting_times).shape[0]

        increments = np.linspace(0,255,num_colour_increments).astype(int)
        
        #create colourspace charting from purely red to blue in  (r,g,b)
        self.colours = np.vstack((increments[::-1],np.zeros_like(increments),increments)).T
    
    
        #create a hash table for colours.
        
        
        self.times2colours = np.unique(self.persisting_times)
        

    def save_image(self):
        '''
        np.savetxt(os.getcwd() + 'directional_image.txt',self.rgbframe)
        '''


    def show_image(self):

        plt.imshow(self.rgbframe)
        plt.show()

