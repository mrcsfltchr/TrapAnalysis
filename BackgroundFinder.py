import numpy as np
from matplotlib import pyplot as plt

from scipy.optimize import curve_fit
from scipy.ndimage.filters import gaussian_filter1d as gaussian
import time

class BackgroundFinder(object):
    
    def __init__(self):
        
        self.background_intens = None

        self.popt = None
        self.pcov = None
        
    def get_data_gradient(self):
        
        if self.background_intens is None:
            return -1
        
        normalised_gradient = self.background_intens/np.max(self.background_intens[:-20])
        
        self.gradient = np.gradient(normalised_gradient)
        
        return 0
    
    def plot_gradient(self):
        
        plt.plot(self.gradient)
        plt.title('Gradient of background intensity over time')
        plt.ylabel('Gradient/a.u.')
        plt.xlabel('Frame No.')
        plt.show()
    def find_correct_gaussian_scale(self):
        
        #function convolves several gaussians with different sigma across the gradient line. 
        #find sigma which fits gaussian best. This should give the largest peak in the convolution. 
        #the peak value of this largest peak is taken as the time at which the concentration of the drug is half of its final concentration
        
        
        self.peak_max_val = -1
        self.peak_max_arg = 0
        self.peak_begin_frame = 0
        for i in range(5,30,5):
            tic = time.time()
            gradient = gaussian(self.gradient[:-100],i)
            #clipped the gradient away from the last few frames as sometimes the intensity increases significantly at the end and the start of the experiment will not be this close to the end of the video anyway
            
            new_peak_val = np.max(gradient)
            
            new_peak_arg = np.argmax(gradient)
            
            if new_peak_val > self.peak_max_val:
                self.peak_max_val = new_peak_val
                self.peak_max_arg = new_peak_arg
                self.width = i
            toc = time.time()
           
            print('This has taken  %.4f' % (toc - tic))
        self.gradient = gaussian(self.gradient,self.width)
        #find minimum just before maximum, to find the frame at which we should look for vesicles
        
        
        delta = 0
        grad_peak2firstval = self.gradient[:self.peak_max_arg][::-1]
        
        for num in range(grad_peak2firstval.shape[0]-1):
            newdelta = grad_peak2firstval[num+1]-grad_peak2firstval[num]

            print(newdelta)
            
            if abs(newdelta) < 0.01:
                
                firstmin = num

                self.peak_begin_frame = self.peak_max_arg - firstmin
                
                
                return 

                #firstmin is distance from bottom of peak to the maximum value of peak along array
        

        
        
    def smooth_gradient(self,sigma = 40):
        
        #most fluctuations in gradient are of a frequency of 1 or two array elements. Want to smooth out these.
        
        #therefore we want a width of the array element space gaussian of much larger than this, but which is less than or equal to the width of peak we want to see
        
        self.gradient = gaussian(self.gradient,sigma)
        
        
    def get_background(self,frames_buffer):

        #frames_buffer is a tifffile object 
        
        #frames must be an array of shape, (Number of frames,Image Height, Image Width)

        
        frames = frames_buffer.asarray()
        
        self.background_intens = np.median(frames,axis = (1,2))
        

    def plot_background_intensity(self):

        if self.background_intens is  None:
            return -1

        plt.plot(self.background_intens)

        #plt.xticks([10,self.background_intens.shape[0]//2,self.background_intens.shape[0]-10],labels = [5,0.5*(self.background_intens.shape[0]//2),0.5*(self.background_intens.shape[0]-10)])

        
        plt.title('Backround Intensity as drug enters the chamber')

        plt.ylabel('Intensity/arbitrary units')
        plt.xlabel('Time/mins')
        plt.show()

    def normalize_data(self):
        
        max_data = np.max(self.background_intens[:-100])
        self.background_intens /= max_data
        min_data = np.min(self.background_intens)
        
        self.background_intens -= min_data
        
        
    def fit_sigmoid(self):

        self.xdata = np.arange(self.background_intens.shape[0])
        self.ydata = self.background_intens

        self.popt, self.pcov = curve_fit(self.sigmoid, self.xdata, self.ydata, maxfev = 1000)

        
    def sigmoid(self,x, a, b):
         y = 1 / (1 + np.exp(-b*(x-a)))
         return y



    def plot_fit(self):

        if self.popt is None or self.pcov is None:

            return -1


        x = np.arange(-10,self.background_intens.shape[0]+100)
        y = self.sigmoid(x, *self.popt)
        plt.plot(self.xdata, self.ydata, 'o', label='data')
        plt.plot(x,y, label='fit')

        plt.legend(loc='best')
        plt.show()


 



        
