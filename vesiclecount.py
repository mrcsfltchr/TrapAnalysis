from matplotlib import pyplot as plt
import tifffile as tf
import numpy as np
from Analyser import Analyser



tif = tf.TiffFile('./181008_CecB-PCPG vesicles- after flushing_1_MMStack_Pos22.ome.tif/')

vesiclecount = []

A = Analyser(None)

Num_frames = tif.imagej_metadata['frames']

Num_frames = 345
print(Num_frames)

drug_start_frame = 337

for num in range(drug_start_frame,Num_frames):
    
    if not  num%200: 
        print(num)
        
    frame = tif.asarray(key = num)
    
    
    

    threshold = np.average(frame) + np.std(frame)
    print(threshold)
    vesicleNo, labels = A.get_traps(drug_start_frame,alternateframe = frame,threshold = threshold)
        
    vesiclecount.append(vesicleNo.shape[0])
    
    
plt.figure()
    
plt.plot(vesiclecount)
plt.ylabel('No. of vesicles found in each frame')
plt.xlabel('Frame No.')

plt.show()

