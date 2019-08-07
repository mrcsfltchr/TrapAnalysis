import pandas as pd 
import numpy as np 
import sys
import os

def background_find_and_sub(I,axis):

    bg = np.nanmin(I,axis)
    
    return I - bg[:,np.newaxis]

def normalise(I,axis):
    one = np.nanmax(I,axis)
    return I/one[:,np.newaxis]



if __name__ == '__main__':

    #expect that the list of unnormalised Intensity lists are in a single, collated, csv file. 
    #The directory containing these paths should be passed from the command line.


    if len(sys.argv) < 2:
        print(' No directory passed through CLI')
        sys.exit()

    else:
        directory = sys.argv[1]
        
    
    files = os.listdir(directory)
    files = np.array(files)
    files = files[files != 'normalised_data']
    for file in files:
        
    
        database = pd.read_csv(directory+'/'+file)

        data = database.to_numpy()
        # each row in just_data corresponds to a single vesicle intensity time series.
        just_data = data[1:,2:].T

        print(np.nanmin(just_data, axis = 1))
        just_data  = background_find_and_sub(just_data, axis = 1)
        just_data = normalise(just_data, axis =1)

        
        labelled_data = np.vstack((data[0,2:],just_data.T))
        
        labelled_data = np.hstack((data[:,0][:,np.newaxis],labelled_data))

        dfs = pd.DataFrame(labelled_data[1:,1:],columns = labelled_data[0,1:],index = labelled_data[1:,0])

        dfs.to_csv(directory+'/normalised_data/'+file[:-4]+'_normalised.csv')

        
        
