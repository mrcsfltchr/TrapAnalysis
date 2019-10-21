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
    
    
    df.to_csv(save_path+name+'flowrates.csv')
    
    
    
if __name__ == '__main__':
    

    #get directory path containing Tiff Stacks, supplied by user
    #user also supplies a name for the final output file containing the sigmoid rate and half intensity point parameters
    
    
    dpath = sys.argv[1]
    name = sys.argv[2]
        
    print('directory chosen is '+dpath)
    print('output filename: ' + name)
    
    #use the already created class for finding background intensity
    
    #initialise dictionary to store parameters
    flow_params = {}
    flow_params['Rows'] = ['a','b','A']
    
    BF = BackgroundFinder()
    
    ret, file_list,_,_ = get_video_paths(dpath)
    
    if ret == -2:
        print('Found files which do not possess suffix "ome.tif"')
    if ret == -1:
        print('Found no valid video files')
        sys.exit()
              
              
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
        BF.smooth_gradient()
        
        if ret == -1:
            print('video background not found correctly')
            sys.exit()
    
        #fit the sigmoid gradient curve to the gradient of the data to find the width of the peak and the position of the half intensity point (maximum gradient)
              
        Aest = np.max(BF.background_intens)
        best = np.nonzero(BF.gradient == np.max(BF.gradient))[0][0]
              
        params = curve_fit(fit_sigmoid_grad,np.arange(BF.gradient.size),BF.gradient,p0 = [1,best,Aest])
        print('a: ',params[0][0], 'b: ', params[0][1], 'A: ',params[0][2])
        flow_params[file] = [params[0][0],params[0][1],params[0][2]]
        
              
    save(flow_params, dpath, name)
              
              
