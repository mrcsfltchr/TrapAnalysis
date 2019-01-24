from qtpy import QtWidgets
import sys
import AnnotatedVidViewer
import tifffile as tf
import qimage2ndarray as qnd
import pandas as pd


with tf.TiffFile('./181008_CecB-PCPG vesicles- after flushing_1_MMStack_Pos22.ome.tif') as tif:
    images = tif.asarray()
    
   
df = pd.read_csv('./trap_positions_181008_CecB-PCPG vesicles- after flushing_1_MMStack_Pos22.ome.tif.csv')
labelled_traps =df.as_matrix()




if __name__ == '__main__':

    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
        
    else:
        app = QtWidgets.QApplication.instance()
        
        
    Av = AnnotatedVidViewer.TrapViewer(qnd,images,labelled_traps[:,1:],labelled_traps[:,0])
    
    
    app.exec_()