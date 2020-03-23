#basic functions:
    #loop over input videos and determine background intensity
    #determine start of experiment
    #determine sigmoid rate parameters
    #save results in csv
    
    
import numpy as np
import pandas as pd
from BackgroundFinder import BackgroundFinder
from glob import glob
import tifffile as tf
import sys
from scipy.optimize import curve_fit
import os
from scipy.signal import find_peaks
from matplotlib import pyplot as plt


def get_video_paths(dir_path):
    
    #first change the current working directory to the path. This is not essential now but for saving we want to make
    #new subdirectories in this directory to organise the files.
    
    initial_dir = os.getcwd()
    print(initial_dir)

    try:
        print('dirpath: ' , dir_path)
        os.chdir(dir_path)
    except FileNotFoundError:
        print('Alert! File path does not exist, please try again')
        ret = -1
        return -1, None, None,None
    #next assign  video paths in the directory to a list
    
    video_filenames = os.listdir(os.getcwd())
    
    #its possible that in this list there are erroneous files (i.e there are files that are not videos)
    
    #check files end with .tif and raise warning if not.
    
    ret = 0
    delete_indices = []
    for i in range(0,len(video_filenames)):
        file = video_filenames[i]
        if file[-8:] != '.ome.tif' and  file[-10:] != '.ome-1.tif':
            delete_indices.append(i)
            ret = -2
            
    video_filenames = np.array(video_filenames)
    video_filenames = np.delete(video_filenames,delete_indices)
    video_filenames = video_filenames.tolist()
    
    if len(video_filenames) == 0:
        ret = -1
            
        
    
    os.chdir(initial_dir)
    
    return ret, video_filenames, dir_path, initial_dir


def load_frame_buffer(filename):
    print(filename)
    return tf.TiffFile(filename)

def fit_sigmoid_grad(x,a,b,A):
    return (A*np.exp(a*(x-b)))/(1+np.exp(a*(x-b)))**2


def save(dictionary, save_path, name):
    
    df = pd.DataFrame.from_dict(dictionary)
    
    
    df.to_csv(save_path+name)
    
    
    
if __name__ == '__main__':
    

    #get directory path containing Tiff Stacks, supplied by user
    #user also supplies a name for the final output file containing the sigmoid rate and half intensity point parameters
    
    
    #set optional flags to false by default
    plotmode = False
    
    
    dpath = sys.argv[1]
    name = sys.argv[2]
    
    if len(sys.argv) >3:
        if sys.argv[3] == '--plot':
            plotmode = True
            
            
    print('directory chosen is '+dpath)
    print('output filename: ' + name)
    
    #use the already created class for finding background intensity
    
    #initialise dictionary to store parameters
    flow_params = {}
    #flow_params['Rows'] = ['Rate']
    flow_params['Rows'] = ['Arrival Time']
    BF = BackgroundFinder()
    
    ret, file_list,_,_ = get_video_paths(dpath)
    
    if ret == -2:
        print('Found files which do not possess suffix "ome.tif"')
    if ret == -1:
        print('Found no valid video files')
        sys.exit()
              
              
    if plotmode:
        figg,axg = plt.subplots(1,1)
        
    firstdone = False
    flow_peak_pos = []
    for file in file_list:
        #create frame buffer variable, this is rewritten for each video.
        #video only loaded into local variable within the function, get_background.
        #the video frames are removed from memory and the median intensity for each frame taken.
            
        print(file)
              
        try:
            vid_buf = load_frame_buffer(dpath+file)
        except ValueError:
            continue
            
        BF.get_background(vid_buf)
        #BF.plot_background_intensity()
        ret = BF.get_data_gradient()
        print(BF.gradient)
        BF.smooth_gradient()
        
        if plotmode:
            
            axg.plot(BF.gradient)
            
            plt.show()
                
            
        
        '''
        
        
        ******** Deprecated sigmoid fitting. Realised the background intensity did not always increase in a sigmoidal shape ******
        
        if ret == -1:
            print('video background not found correctly')
            sys.exit()
    
        #fit the sigmoid gradient curve to the gradient of the data to find the width of the peak and the position of the half intensity point (maximum gradient)
              
        Aest = np.max(BF.background_intens)
        best = np.nonzero(BF.gradient == np.max(BF.gradient))[0][0]
              
        params = curve_fit(fit_sigmoid_grad,np.arange(BF.gradient.size),BF.gradient,p0 = [1,best,Aest])
        print('a: ',params[0][0], 'b: ', params[0][1], 'A: ',params[0][2])
        
        flow_rate = fit_sigmoid_grad(x =params[0][1],a = params[0][0],b=params[0][1],A=params[0][2])
        
        flow_params[file] = [params[0][0],params[0][1],params[0][2],flow_rate]
    
        '''    
    
        # here you have the gradient 
        
        peaks = find_peaks(BF.gradient)
        
        peak = peaks[0][0]
        
        
        
        
        max_flow_rate = BF.gradient[peak]
        flow_peak_pos.append(peak)
        
        #flow_params[file] = max_flow_rate
        
    
    print(flow_peak_pos)
    med_time_arrival = np.median(np.array(flow_peak_pos))
    label = dpath[-2:-1]
    flow_params[label]= med_time_arrival
    print(flow_params)
    save(flow_params, './'+label, name)
              
    #Takes average of the arrival times for a given chamber and records it.
          
