#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 15:19:59 2019

@author: mjsf3
"""

import pandas as pd
import numpy as np
import sys
from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter1d as smooth
from scipy.optimize import curve_fit

'''def findMaxBurstingRate(data,halfIntensityPoints,window_size = 4):
    
    max_rates = []
    upperlimit = int(window_size/2)
    lowerlimit = int(window_size/2)
    
    print('upperlimit: ' + str(upperlimit),' lowerlimit: ' + str(lowerlimit))
    

    for i in range(0,halfIntensityPoints.shape[0]):
        gradient_found = False
        no_leakage = False
        section = None
        while not gradient_found or not no_leakage:
            if  halfIntensityPoints[i] < (data[:,i].shape[0] + int(window_size/2)):
                
                section = data[(halfIntensityPoints[i]-lowerlimit):(halfIntensityPoints[i]+upperlimit),i]
            elif halfIntensityPoints[i] >= (data[:,i].shape[0] + int(window_size/2)):
                no_leakage = True
                
                continue
            
            
            rate = np.gradient(section)
            print(rate)
            signs = np.sign(rate)
            
            zero_crossings = (signs[1:] - signs[:-1])== 0
            print(zero_crossings)
            
            zero_crossings = np.argwhere(zero_crossings)
            
            if zero_crossings.shape[0] == 0:
                upperlimit +=2
                lowerlimit +=2
                print('1')
                continue
            
            if zero_crossings.shape[0] ==2 and zero_crossings[1] > window_size/2:
                lowerlimit = halfIntensityPoints[i] - zero_crossings[0]
                upperlimit = zero_crossings[1] - halfIntensityPoints[i]
                gradient_found = True
                print('2')
                continue
            
            if zero_crossings[1] - zero_crossings[0] < 1:
                np.delete(zero_crossings[1])
                print('3')
                continue
            
            if zero_crossings.shape[0] == 1 and zero_crossings[0] > lowerlimit:
                lowerlimit +=3
                print('4')
            if zero_crossings.shape[0] == 1 and zero_crossings[0] < lowerlimit:
                
                upperlimit +=3
                print('5')
            if zero_crossings.shape[0] >2 and zero_crossings[1] <= lowerlimit:
                lowerlimit = halfIntensityPoints[i]- zero_crossings[1][0] +1
                
            if zero_crossings.shape[0] > 2 and zero_crossings[1] > lowerlimit:
                upperlimit = zero_crossings[1] - halfIntensityPoints[i]
                print('7')
                
          
                
            
                
            if gradient_found:    
    
                max_rate = np.max(section)
                
                max_rate = (1/30)*max_rate
                max_rates.append(max_rate)
                
        
    return max_rates
 
'''

def e(x,A,tau,C):
    exponent = (-x)/tau
    
    return A*np.exp(exponent) +C

def get_time_constant(data,start,end):
    
    if end-start < 3:
        ret = -1
        params = None
    else:
        ret = 1
        xdata = np.arange(end-start)
        ydata = data[start:end]

        print('This is max value in data,', np.nanmax(data))
        
        try:
            params = curve_fit(e,xdata,ydata,p0=[ydata[0],0.6*(end-start),ydata[-1]])
        except RuntimeError:
            #if np.log10(params[0][0]) > 1.5:
             #   ret = -1
                
            ret = -1
            params = None
        #xfit = np.linspace(0,xdata.shape[0],50)
        #yfit = e(xfit,A=params[0][0],tau=params[0][1],C=params[0][2])
        #plt.figure()
        #plt.plot(xdata,ydata)
        #plt.plot(xfit,yfit)
        #plt.title(str(params[0][0]) + ',' +str(params[0][1]) +' '+str(params[0][2]))
        #plt.show()
        print('params is ',params)
    return params, ret
    

def findMaxBurstingRate(data, halfIntensityPoints,window = 100):

    upperlimit = int(window/2)
    lowerlimit = int(window/2)


    avrates = []
    lifetimes = []
    for i in range(0,halfIntensityPoints.shape[0]):
        
        upperlimit = int(window/2)
        lowerlimit = int(window/2)
    
        plt.clf()
    
        if halfIntensityPoints[i] == 1200:
            continue
        
        if lowerlimit > halfIntensityPoints[i]:
            lowerlimit = halfIntensityPoints[i]
        if upperlimit > data[:,i].shape[0] - halfIntensityPoints[i]:
            upperlimit = data[:,i].shape[0] - halfIntensityPoints[i]
            
            
       
            

        section = data[(halfIntensityPoints[i]-lowerlimit):(halfIntensityPoints[i]+upperlimit),i]
        
        if section.shape[0] == 0:
            
            continue
        
        plt.subplot(211)
        plt.plot(section)
        
        rates = np.gradient(section)
        
        
        if np.average(rates) > 0:
            continue
        
        plt.subplot(212)
        plt.plot(rates)
        
        plt.title('Plot Number: ' + str(i))
        plt.tight_layout()
        plt.show()
        
        
        leakage_period = rates[rates < 0.1*np.min(rates)].shape[0]
        #need to check that there are no large positive increases in intensity  in between decreases. These could be vesicles appearing
        
        decreasing_indices = np.argwhere(rates < 0.1*np.min(rates))
        
        jumps = decreasing_indices[1:] - decreasing_indices[:-1]
        
        
        if jumps.shape[0] > 0:
            for jump in jumps[jumps > 20]:
                
                start = decreasing_indices[np.argwhere(jumps == jump)[0][0]][0]
                end = decreasing_indices[np.argwhere(jumps == jump)[0][0] + 1][0]
                
                if np.average(rates[start:end]) >= abs(0.5*np.min(rates)):
                    leakage_period = 0
                    
                elif rates[end:].shape[0] > rates[:start].shape[0]:
                    rates = rates[end:]
                    leakage_period = rates[rates<0.1*np.min(rates)].shape[0]
                else:
                    rates = rates[:start]
                    leakage_period = rates[rates<0.1*np.min(rates)].shape[0]
                    
                    
                    

        if leakage_period == 0:
            continue
        
        avrates.append(leakage_period)
        lifetimes.append(halfIntensityPoints[i])
        
    return avrates, lifetimes
        

def findDescendingRegion(data, halfIntensityPoints,window = 1000):    
     
    upperlimit = int(window/2)
    lowerlimit = int(window/2)

    
    avrates = []
    lifetimes = []
    
    
    for i in range(0,halfIntensityPoints.shape[0]):
        
        upperlimit = int(window/2)
        lowerlimit = int(window/2)
    
        plt.clf()
    
        if halfIntensityPoints[i] == data.shape[0]:
            continue
        
        if lowerlimit > halfIntensityPoints[i]:
            print(lowerlimit)
            lowerlimit = halfIntensityPoints[i]
        if upperlimit > data[:,i].shape[0] - halfIntensityPoints[i]:
            upperlimit = data[:,i].shape[0] - halfIntensityPoints[i]
            
            
       
            

        section = data[(halfIntensityPoints[i]-lowerlimit):(halfIntensityPoints[i]+upperlimit),i]

        if section.shape[0] == 0:
            continue
        

        
        smoothed_section = smooth(section,3)
        
        rates = np.gradient(section)
        
        
        
        if np.average(rates) > 0:
            print('This is the average gradient', np.average(rates))
            
            continue
        


        #navigate to maximum
        maximum = np.argwhere(section == np.nanmax(section))
        if maximum.shape[0] == 0:
            continue
        else:
            maximum = maximum[0][0]
        

        section = section[maximum:]
        start = np.argwhere(section < 0.95*section[0])
        if start.shape[0] == 0:
            print('went wrong at start')
            continue
        else:
            start = start[0][0]
        if start == section.shape[0]:
            
            continue

            
        end = np.argwhere(section[start:] < 0.5*section[0])
        if end.shape[0] == 0:
            end = section.shape[0]
        
        if end.shape[0] == 0:
            continue
        else:
            end = end[0][0] + start


        
        #backtrace = section[:end][::-1][section[:end][::-1] > 0.95]
        #if backtrace.shape[0] > 0:
            
          #  start = end - np.argwhere(section[:end][::-1] == backtrace[0])[0][0] -1 
        #

        #fit exponential to this region of the intensity trace and then take time constant
        
        parameters, success = get_time_constant(section,start,end)
        if success ==1:
            time_constant = parameters[0][1]
            error = parameters[1][1,1]
        else:
            time_constant = end-start
            error = 0
        avrates.append([time_constant,error])
        lifetimes.append(halfIntensityPoints[i])
                
    return avrates, lifetimes
        
    

    
if __name__ == '__main__':
    
    normalise = False
    if len(sys.argv) > 3:
        
        if sys.argv[3] == 'smooth':
            outpath = '/testinverseperiodofdyeleakage.csv'
            normalise = True
    else:
        outpath = '/inverseperiodofdyeleakage.csv'
    if len(sys.argv) > 2:
        dpath = sys.argv[1]
        fpath = sys.argv[2]
        

    else:
        print('Required input: python postProcessVesRemoval.py <directory of files > <file path>')
        
        sys.exit()
    
    df = pd.read_csv(dpath + '/'+fpath)
    
    intensity_traces = df.to_numpy()
    

    intensity_traces = intensity_traces[3:,3:]
 
    intensity_traces= intensity_traces.astype(float)
    
    
    if normalise:
        #maxes = np.nanmax(intensity_traces,axis = 0)
        
        
        #mins = np.nanmin(intensity_traces,axis = 0)
        #intensity_traces =(intensity_traces - mins)
        #intensity_traces = intensity_traces/maxes
        
        for i in range(intensity_traces.shape[1]):
            
            maxe = np.nanmax(intensity_traces[:,i])
            mine = np.nanmin(intensity_traces[:,i])
            
            intensity_traces[:,i] = intensity_traces[:,i]/maxe

        for i in range(0,intensity_traces.shape[1]):
            intensity_traces[:,i] = smooth(intensity_traces[:,i],0.3)
           
    
    lifetimes = np.nansum(intensity_traces > 0.5,axis = 0)

    
    
    av_rates, finallifetimes = findDescendingRegion(intensity_traces,lifetimes)
    
    np.savetxt(dpath + outpath,np.array(av_rates),delimiter = ',')
    
    av_rates = np.array(av_rates)
    dictionary = {}
    dictionary['rates'] = av_rates[:,0]
    dictionary['error'] = av_rates[:,1]
    
    dictionary['halfintensitypoint'] = finallifetimes
    
    df3 = pd.DataFrame.from_dict(dictionary)
    
    df3.to_csv(dpath+'lifetimesvsrates.csv')
    