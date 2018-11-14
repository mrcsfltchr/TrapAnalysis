#Trap Analysis sotware for microfluidic optofluorescence imaging
written in python, using qtpy to create a GUI control panel for detecting bright objects in the field of view and extract the average intensity within a small region inside the detected object.


Brief description of functionality
Can extract Intensity values in each frame of video for detected vesicles automatically
The detection process relies on finding initial estimates for the particle positions. Attach boxes to these detected particle centre coordinates, and then in future frames only look inside these boxes for particles.
