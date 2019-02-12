import tifffile as tf
import numpy as np
from skimage.feature import peak_local_max
from skimage.filters import gaussian
from matplotlib import pyplot as plt







def subtract_moved_vesicles(self,frames,start_frame,trap_positions=None,labels=None):
    
    #frames: A TiffFile object from which we import frames as a numpy array
    #start_frame: The frame defining the start of the experiment.
    #the TrapGetter object which contains the list of initial vesicle positions and the corresponding labels
    
    
    frames = frames.asarray()

    subtracted_frames = frames[:-1] - frames[1:]


    interficiendum = None
    
    if subtracted_frames.shape[0] > start_frame + 1200:
        end_frame = start_frame +1200
    else:
        end_frame = subtracted_frames.shape[0]
        
    for frame_index in range(start_frame,end_frame):
        frame = subtracted_frames[frame_index]

        frame = gaussian(frame,10)
        pos_peaks = peak_local_max(frame,min_distance=40,threshold_rel=0.95)
        neg_peaks = peak_local_max(np.max(frame)-frame,min_distance=40,threshold_rel=0.95)

        pos_peaks = np.array(pos_peaks)
        neg_peaks = np.array(neg_peaks)



        peaks = np.vstack((pos_peaks,neg_peaks))


        if len(pos_peaks) >0 and len(neg_peaks) > 0:

            #if we find a positive and a negative peak in the subtracted frame, we believe that a vesicle has moved
            #remains to pair the negative peak and positive peak to make sure a vesicle moved and didnt just burst

            pair_vectors = pos_peaks[np.newaxis] - neg_peaks
            
            if pair_vectors.shape[1] ==1:
                
                if interficiendum is None:
                    interficiendum = neg_peaks

                else:
                    interficiendum = np.vstack((interficiendum,neg_peaks))

            else:
                pair = pair_vectors[np.absolute(pair_vectors[:,:,0]) < 60]


                if pair_vectors.shape[1] == 1:
                    plt.imshow(frame)
                    plt.show()

                    if interficiendum is None:
                        interficiendum = neg_peaks[pair_vectors[:,0] < 60]

                    else:
                        interficiendum = np.vstack(interficiendum,neg_peaks[pair_vectors[:,0] < 60])  

                else:
                    pair = pair_vectors[pair_vectors[:,:,1] < 0]
                    pair = pair[pair[:,0] < 60]

                    #if there is at least a pair of positive and negative peaks which are vertically less than 60 pixels away and arranged horizontally so the positive peak is on the left
                     #then we choose to bin the vesicle which in the previous frame was in the position of the nearest negative peak to a positive peak

                    if len(neg_peaks) > 1 and len(pair[0]) > 0:

                        peak = neg_peaks[[np.absolute(pair_vectors[:,:,0]) == np.min(np.absolute(pair_vectors[:,:,0]))][0][0]]

                    else:
                        peak = neg_peaks

                    if interficiendum is None:
                        interficiendum = peak
                    else:
                        interficiendum = np.vstack((interficiendum,peak))



    if trap_positions is None or labels is None:
        return -1
    
    
    trap_positions += [0,5]

    separations = trap_positions[:,:,np.newaxis] - interficiendum.T
    separations = np.linalg.norm(separations,axis = 1)



    killlabels = labels[np.sum(separations < np.sqrt(2*15**2), axis = 1) == True]
    
    print(killlabels)
    
    return killlabels





