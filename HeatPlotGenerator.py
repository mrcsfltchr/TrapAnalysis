#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 11:51:28 2018

@author: MarcusF
"""

#a class which generates a heatplot
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
class HeatPlotGenerator(object):
    def __init__(self):
        self.heat_data = None
        self.xdata =None
        self.maxheat = None
        self.minheat = 0.0
        
        self.title = None
        self.ylabel = None
        self.xlabel = None
        
        self.fig = None
        self.ax = None
        self.heatbar = None
    def generate(self,xdata,heat_data,title,VesicleCount):
        
        print('Generating some serious heat!')
        self.heat_data = heat_data
        self.xdata = xdata
        self.fig,(self.ax,self.heatbar) = plt.subplots(1,2)
        


        
        '''
            
        '''
        asp = int(heat_data.shape[1]//heat_data.shape[0])

        img = self.ax.imshow(heat_data,aspect = asp,cmap = "hot",interpolation = "nearest",extent = (-0.5,heat_data.shape[1]-0.5,-0.5,heat_data.shape[0]-0.5))
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(5,prune = 'both'))

        
        xticks = self.ax.get_xticks()
        minutes = 0.5 * xticks
        
        print('Axes aspect ', self.ax.get_aspect())
    
        self.ax.set_xticklabels(minutes)
        self.ax.text(0.8,0.8,'No of Vesicles shown is: '+ str(VesicleCount),fontsize = 8,color = 'white',transform = self.ax.transAxes)
        
        '''
        locs = self.ax.xaxis.get_major_ticks()
        
        locs[0].label1.set_visible(False)
        locs[-1].label1.set_visible(False)
        
        '''
        print(img.get_extent())
        print(self.ax.transData.transform((10,self.heat_data.shape[0]-7)))
              
        '''
        self.minutes = self.xdata//6
        
        if self.minutes.shape[0]%3 == 0:
            
            coords = np.linspace(0,self.minutes.shape[0]-1,4)
            xticks = self.xdata[coords.astype(int)]
            self.ax.set_xticks(xticks)
        else:
            coords = np.linspace(0,self.minutes.shape[0]-1,6)
            xticks = self.xdata[coords.astype(int)]
            self.ax.set_xticks(xticks)
        
        print(coords)
        xtick_labels = self.minutes[coords.astype(int)]//10
        
        
        self.ax.set_xticklabels(xtick_labels)
        '''
        self.maxheat = np.max(self.heat_data)
        
        print('maxheat: ',self.maxheat)
        
        if np.min(self.heat_data) < self.minheat:
            self.minheat = np.min(self.heat_data)
        
        print('minheat: ', self.minheat)
        
        self.heatbar_data = np.linspace(self.minheat,self.maxheat,self.heat_data.shape[0])
        
        print(self.heatbar_data.shape[0])
        print(self.heatbar_data)
        self.heatbar_data = np.tile(self.heatbar_data,(5,1))
        
        self.heatbar_data = self.heatbar_data.T[::-1]
        
        self.heatbar.imshow(self.heatbar_data,cmap = "hot")

        
        
        
        loc = self.heatbar.get_yticks()
        
        nploc = np.array(loc)
        
        heat_tick_lbls = (1/self.heatbar_data.shape[0])*nploc
        

        self.heatbar.set_yticklabels(heat_tick_lbls.astype(str)[::-1])

        self.heatbar.yaxis.tick_right()
        
        self.heatbar.xaxis.set_major_locator(plt.NullLocator())
        
        self.heatbar.set_ylabel('Vesicle Intensity/arbitrary Units')
        self.ax.set_ylabel('Vesicle Number.')
        self.ax.set_xlabel('Time since drug arrival/minutes')
        self.heatbar.yaxis.set_label_position('right')
        


        plt.show()

