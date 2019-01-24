import numpy as np
import tifffile as tf
import scipy
from matplotlib import pyplot as plt
from skimage.filters import threshold_otsu
from skimage.restoration import richardson_lucy
from skimage.feature import canny
from skimage.filters import threshold_otsu
from skimage.filters import gaussian
from skimage.morphology import binary_dilation
from skimage.filters import sobel
from skimage.feature import peak_local_max
from scipy.ndimage import distance_transform_edt
import os
#This project


class TrapGetter(object):
    def __init__(self):
        self.trap_positions = None
        self.labels = None
        self.boxes = None
        
        self.frame = None
        
        self.kernel_path = os.getcwd() + '/initialkernel.txt'
        
        self.point_intensity_limit = 0.3
        self.low_threshold= 450
        self.high_threshold = 500
        self.topboxrel = 15
        self.bottomboxrel = 15
        self.leftboxrel = 10
        self.rightboxrel = 20
        self.duplicates = np.array([])
        
        #list the dimension of the box for export
        self.trapdimensions = [self.topboxrel,self.bottomboxrel,self.leftboxrel,self.rightboxrel]
        
        try:
            self.kernel = np.loadtxt(self.kernel_path,delimiter = ',')
        except:
            print('Kernel path is invalid')
            
            
    def set_kernel_path(self,path):
        self.kernel_path = path
    
    
    def get_vesicle_positions(self,frame,postdetection = False, threshold = None):
        self.frame = frame
        frame = gaussian(frame,2,preserve_range=True)
        if not postdetection:
            self.threshold = threshold_otsu(frame)
        
        if threshold is not None:
            self.threshold = threshold
    
        
        mask = np.zeros_like(frame)
        mask[frame > self.threshold] = 1
        
        plt.imshow(mask,cmap = 'gray')
        plt.show()
        distance_map = distance_transform_edt(mask)
        peaks = peak_local_max(distance_map,threshold_abs=3,min_distance=4)
    
        self.trap_positions = np.array(peaks)
        
        
    
    def get_trap_positions(self,frame):
        self.frame = frame
            
        
        inverted_image = np.max(frame)-frame
        
        
        edgemap = canny(inverted_image,sigma = 2.2,low_threshold = self.low_threshold,high_threshold=self.high_threshold )
            
        dilated_edges = binary_dilation(edgemap,selem = np.ones_like(frame[:3,:2]))


        edges = sobel(dilated_edges)
        
        deconvolved_image = richardson_lucy(edges,self.kernel,6,clip = False)
        
        self.trap_positions = np.array(peak_local_max(deconvolved_image,threshold_rel=self.point_intensity_limit))
        
        
    def remove_duplicates(self):
        self.duplicates = np.array([])
        self.distances = np.linalg.norm(self.trap_positions - self.trap_positions[:,np.newaxis],axis = 2)
        self.sorted_distances = np.argsort(self.distances,axis = 1)
        
        for row in np.arange(self.sorted_distances.shape[0]):
            closebyboxes = self.sorted_distances[row,:][self.distances[row,:][self.sorted_distances[row,:]] <7]
            closebyboxes = closebyboxes[1:]
            self.pairs = np.vstack((np.ones_like(closebyboxes)*row,closebyboxes)).T
            
            if self.duplicates.shape[0] == 0:
                self.duplicates = self.pairs
            else:
                self.duplicates = np.vstack((self.duplicates,self.pairs))
        
        
        self.maxdup = np.maximum(self.duplicates[:,0],self.duplicates[:,1])
        self.uniquemaxdup = np.unique(self.maxdup)
        
        self.trap_positions = np.delete(self.trap_positions,self.uniquemaxdup,axis = 0)
        
        self.labels = np.arange(1,self.trap_positions.shape[0]+1)
            
        


        return self.trap_positions,self.labels
    
    
    def get_boxes(self):
        if self.frame:
            canvas = np.zeros_like(images[0])
            for trap in self.trap_positions:
    

    
                canvas[trap[0]-self.topboxrel:trap[0]+self.bottomboxrel,trap[1]-self.leftboxrel] = 1
                canvas[trap[0]-self.topboxrel:trap[0]+self.bottomboxrel,trap[1]+self.rightboxrel]=1
                canvas[trap[0]-self.topboxrel,trap[1]-self.leftboxrel:trap[1]+self.rightboxrel]=1
                canvas[trap[0]+self.bottomboxrel,trap[1]-self.leftboxrel:trap[1]+self.rightboxrell] = 1
            



