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

df.columns = ["accel", "ax", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz"]          # Give it a header
df = df.drop(columns=['accel'])
df = np.abs(df) 
# print(df)


# I want to take every third row starting from the second row and put it in a sigle table.
df0 = df.iloc[1::3, :]          # Seperating data from each accelerometer into data frames
df1 = df.iloc[2::3, :]
df2 = df.iloc[3::3, :]
# print(df0, df1,df2)



time = np.linspace(0, len(df0['ay']), len(df0['ay']))

# My notes to help organize my thoughts
# I want to create a best fit line for the gyro data then define
# an equation for that line. With that model I will solve the 
# I.V.P. for an eqution of positon. 
# I will then use the time values with the modol to solve for all
# position in time.  
# Taking the positions of the vertiacl and horizonal sensors 
# I will find delta change between the sensors subrtacted by 90 deg. 

# plt.plot(time, df0['az'], 'k', markersize=3.5)         # plot accel data pts
# plt.plot(time, df0['ax'], 'r', markersize=3.5)        
# plt.plot(time, df0['ay'], 'g', markersize=3.5)        

# plt.plot(time, df0['gx'], 'k', markersize=3.5)        # plot gyro data pts
# plt.plot(time, df0['gy'], 'r', markersize=3.5)        
# plt.plot(time, df0['gz'], 'g', markersize=3.5)        


timespline = np.linspace(0, len(df0['ay']), num=2000, endpoint=True)         # adjust num=___ to change the amount of pts of spline
                                                                             # using scypi spline tools

az_spln_rep = syi.splrep(time, df0['az'], k=3, s=0)
az_spln_ev = syi.splev(timespline, az_spln_rep)
# plt.plot(timespline, az_spln_ev, 'b', label='cubic spline')

az_CubicSpline = syi.CubicSpline(time, df0['az'])
# plt.plot(timespline, az_CubicSpline(timespline), 'ro', label='cubic spline')

def model(x, m, b):         # using curve_fit with a 1st or poly
    return m*x+b

intit_guess = [1, 1]
fit = sy.curve_fit(model, time, df0['az'], p0=intit_guess, absolute_sigma=True)

ans = fit[0]            # extracking out m and b
slope_fit, y_fit = ans[0], ans[1]

# plt.plot(time, model(time, slope_fit, y_fit))




from scipy.signal import sosfiltfilt, butter    # running the data though a pass filter
sos = butter(4, 0.1, output='sos')
y = sosfiltfilt(sos, df0['ay'])

from scipy.signal import sosfilt, sosfilt_zi
sos8 = butter(8, 0.125, output='sos')
zi = df0['ay'][:4].mean() * sosfilt_zi(sos8)
y2, zo = sosfilt(sos8, df0['ay'], zi=zi)


# plt.plot(time, df0['ay'], 'g',alpha=0.5)
# plt.plot(time, y, label='y(t)')
# plt.plot(time, y2, label='y2(t)')
# plt.legend(framealpha=1, shadow=True)
# plt.grid(alpha=0.25)
# plt.xlabel('time')



pitch0 =np.arctan2(df0['ax'], np.sqrt(df0['ay'] * df0['ay']) + (df0['az'] * df0['az'])); #putting roll fromula in python 
roll0 = np.arctan2(df0['ay'], np.sqrt(df0['ax'] * df0['ax']) + (df0['az'] * df0['az']));
pitch0 *= 180.0 / np.pi;
roll0 *= 180.0 / np.pi;

# plt.plot(time, pitch0, 'k', markersize=3.5)         # plot roll data
plt.plot(time, roll0, 'r', markersize=3.5)  
# print(pitch0)
print(roll0)

plt.show()

# roll0.to_csv('roll_brianp_test')





