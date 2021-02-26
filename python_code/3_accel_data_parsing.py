#!/usr/bin/env python3
# Pronation Program
# Copyright (C) 2021 Dominic Culotta, Eric Edstrom, Jae Young Lee, Teagan Mathur, Brian Petro, Wilma Rishko, Ruizhi Wang
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.optimize as sy
import scipy.interpolate as syi
import sys
import os
from pathlib import Path

df = pd.read_csv(Path(os.getcwd()) / sys.argv[1], header=None)           # Load in the data      

df.columns = ["accel", "ax", "ay", "az", "gx", "gy", "gz"]          # Give it a header
df = df.drop(columns=['accel'])
# print(df)



# I want to take every third row starting from the second row and put it in a sigle table.
df0 = df.iloc[1::3, :]          # Seperating data from each accelerometer into data frames
df1 = df.iloc[2::3, :]
df2 = df.iloc[3::3, :]
# print(df0, df1,df2)

time = np.linspace(0, len(df0['ay']), len(df0['ay']))

# I want to create a best fit line for the gyro data then define
# an equation for that line. With that model I will solve the 
# I.V.P. for an eqution of positon. 
# I will then use the time values with the modol to solve for all
# position in time.  
# Taking the positions of the vertiacl and horizonal sensors 
# I will find delta change between the sensors subrtacted by 90 deg. 

plt.plot(time, df0['az'], 'ko', markersize=3.5)         # plot accel data pts
plt.plot(time, df0['ax'], 'ro', markersize=3.5)        
plt.plot(time, df0['ay'], 'go', markersize=3.5)        

# plt.plot(time, df0['gx'], 'go', markersize=3.5)        # plot gyro data pts
# plt.plot(time, df0['gy'], 'go', markersize=3.5)        
# plt.plot(time, df0['gz'], 'go', markersize=3.5)        

# using scypi spline tools
timespline = np.linspace(0, len(df0['ay']), num=100, endpoint=True)         #adjust num=___ to change the amount of pts of spline
az_spln = syi.interp1d(time, df0['az'], kind='cubic')
plt.plot(timespline, az_spln(timespline), 'b-', label='cubic spline')



def model(x, m, b):         # making a best fit line to az data
    return m*x+b

intit_guess = [1, 1]
fit = sy.curve_fit(model, time, df0['az'], p0=intit_guess, absolute_sigma=True)

ans = fit[0]            # extracking out m and b
slope_fit, y_fit = ans[0], ans[1]

# plt.plot(time, model(time, slope_fit, y_fit))


plt.show()
