#!/usr/bin/python3

### read any number of md.out files, parse for time and density, and fit exponential to check system equilibration

import sys
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def density_parse(amberout): 
    """ Parse Amber MD output file
    argument: fileobject for AMBER output file
    return: list with times and list with corrresponding densities     
    """
    time=[]
    density=[]    
    for line in amberout:
        time_match = re.search(r"TIME.+\s+(\d+\.\d+)\s+TEMP",line)
        if time_match:
            time.append(float(time_match.group(1)))
        dens_match = re.search(r"Density.+(\d+\.\d+)",line)
        if dens_match:
            density.append(float(dens_match.group(1)))
        quit_match = re.search(r"A V E R A G E",line)     
        if quit_match:
            return(time,density)

def density_fit(time,dens,di_guess=1.00,dt_guess=1.03,k_guess=0,y_start=0.98,y_end=1.04): 
    """ Fit density equilibration
    arguments: time np.array, density np.array; _guess: initial fitting parameters; y_ density window for plotting
    return: none     
    1 Fits the function di +  ((df-di) * (1-np.exp(-k * t)) to x (time) and y (density)
    with di - initial density, df - final density and k -rate 
    2 prints fitting parameters to STDOUT
    3 generates plot of data and fit
    """
# fitting
    popt, pcov = curve_fit(
        lambda t, di, df, k: di + ((df-di) * (1-np.exp(-k * t))), 
        x, y, p0=(di_guess,dt_guess,k_guess)
    )
# calculate fitted curve
    print("Initial density:\t" + str(popt[0]) + "\nFinal density:\t" + str(popt[1]) + "\nRate:\t" + str(popt[2]))
    x_fitted = np.linspace(np.min(x), np.max(x), 100)
    y_fitted = popt[0] +((popt[1]-popt[0]) * (1-np.exp(-popt[2] * x_fitted)))
# plot
    ax = plt.axes()
    ax.scatter(x, y, label='Raw data')
    ax.plot(x_fitted, y_fitted, 'k', label='Fit')
    ax.set_title(r'Density Equilibration')
    ax.set_ylabel('Density [g/cm3]')
    ax.set_ylim(y_start, y_end)
    ax.set_xlabel('Time [ps]')
    ax.legend()
    plt.show()
    plt.savefig('density.png')


### loop over all files given as command line argument, populate np.arrays, and fit and plot data 
ti=[]
dens=[]  
if len(sys.argv) > 1:
    for index in range(1,len(sys.argv)):
        fh = open(sys.argv[index], 'r')
        (temp_ti, temp_dens)=density_parse(fh)
        fh.close()
        ti= ti + temp_ti
        dens= dens + temp_dens
    x=np.array(ti)
    y=np.array(dens)
    density_fit(x,y)
    
else:
    print("\nERROR: script needs md.out file(s) as command line argument(s)\n")


