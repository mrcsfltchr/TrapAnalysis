# Trapped Particle Analysis sotware for microfluidic optofluorescence imaging

Written in python, using qtpy to create a GUI control panel for detecting bright objects in the field of view and extract the average intensity within a small region inside the detected object.


Brief description of functionality
Can extract Intensity values and area estimages in each frame of video for detected particles automatically.

The detection process relies on finding initial estimates for the particle positions. Attach boxes to these detected particle centre coordinates, and then in future frames only look inside these boxes for particles. The contents of the box is classified using a simple trained convolutional neural network. After classification, those boxes categorised as containing a particle are passed to a function which extracts their intensity and calculates the area.






#Functionality
============


## Views
1. Main Control Panel
   This includes control buttons for various stages of the automated particle detection. 
   As well as buttons for bringing up visualisation features

2. Whole Frame Viewing panel. 
   This includes an option to view the boxes which have been attached to the detected particle centre coordinates.

3. Single Particle Focus
   This pop up window narrows the focus onto the contents of a single detected box. The User may select which box to view by selecting from a drop down list. 
   Main features include an embedded **Plotting View** which plots results from the intensity and area of particle analysis of the inputted video. A **Video Viewer** for viewing the contents of a single box. Within this the user can select, from the buttons beneath the viewer, to overlay the video with the **detected centre coordinates**, select **threshold view** to see how the analysis algorithm has binarized the foreground particle from the backround within the box. 
    ***Selected optional functionality is specific to a drug perfusion experiment which investigates the rate at which the drug lyses the particle membrane***

4. Saving and Loading Features

    The **Intensity** of the detected particle over the course of the video, as well as the **area** of the particle, the **detected box positions** , the **detected particle centre coordinates within the boxes** and the **indices of the first and last frames of the experiment** may be saved for further analysis or for reloading later. 

    The **Intensities and Areas** are stored as csv files which are compatible with Excel. The **centres** and **initial and final frame indices** are stored as text files, as it is not anticipated that these will be used outside this program.

    It is also made possible to store data for a **heat plot** comparing the times taken for each particle to burst after exposure to the drug in the perfusion experiment this analysis was designed for.




# Acknowledgements

This developer of this software is grateful to the authors of all dependent packages. Including, but may not be limited to, *Anaconda*, *PyQt5*, *qimage2ndarray*, *tifffile.py*, *scikit-image*, *keras and tensorflow*, *numpy and scipy*


