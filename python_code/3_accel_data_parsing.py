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
from pykalman import KalmanFilter

column_names = ["channel", "time", "dtime", "ax", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz", "roll", "gyroXangle", "compAngleX", "kalAngleX", "pitch", "gyroYangle", "compAngleY", "kalAngleY"]          # Give it a header

df = pd.read_csv(Path(os.getcwd()) / sys.argv[1], names=column_names)           # Load in the data      

#df.columns = ["channel", "time", "dtime", "ax", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz", "roll", "gyroXangle", "compAngleX", "kalAngleX", "pitch", "gryoYangle", "compAngleY", "kalAngleY"]          # Give it a header
# print(df)
df0 = df[df["channel"]==0]
df1 = df[df["channel"]==1]
df2 = df[df["channel"]==2]

#finding mag of accel. vector
df0amag = np.sqrt((df0['ax'])**2 + (df0['ay'])**2 + (df0['az'])**2)

# Calculate roll and pitch
roll0=np.degrees(np.arctan2(df0['ay'],df0['az']))
roll1=np.degrees(np.arctan2(df1['ay'],df0['az']))
roll2=np.degrees(np.arctan2(df2['ay'],df0['az']))



# plt.plot(df0['time'], df0amag, 'bo', markersize=3, label='ax')      # plot accel data pts
# plt.plot(df0['time'], df0['ay'], 'g', markersize=3.5, label='ay')      # plot accel data pts
# plt.plot(df0['time'], df0['az'], 'k', markersize=3.5, label='az')      # plot accel data pts

print(np.std(df0['az']))
print(np.mean(df0['az']))

# Learn the Kalman transition matrix

kf=KalmanFilter(initial_state_mean=0,n_dim_obs=2)

#print(df0['ax'].values[4])
#transition=kf.em(df0['ax'].values)

# plt.plot(time, df0['gx'], 'k', markersize=3.5)          # plot gyro data pts

# Choose which filter to use

if sys.argv[2]=="0":
    plt.plot(df0['time'], df0['gyroXangle'], 'k', markersize=3, label='angular position X')        
    plt.plot(df0['time'], df0['gyroYangle'], 'g', markersize=3, label='angular position Y') 

if sys.argv[2]=="1":
    plt.plot(df0['time'], df0['kalAngleX'], 'k', markersize=3, label='angular position X')        
    plt.plot(df0['time'], df0['kalAngleY'], 'g', markersize=3, label='angular position Y') 

if sys.argv[2]=="2":
    plt.plot(df0['time'], df0['gx'], 'k', markersize=3, label='angular position X')        
    plt.plot(df0['time'], df0['gy'], 'g', markersize=3, label='angular position Y') 

tspline = np.linspace(df0['time'].iloc[0], df0['time'].iloc[-1], num=3000, endpoint=True)         # adjust num=___ to change the amount of pts of spline using scypi spline tools
az_spln_rep = syi.splrep(df0['time'], df0amag, k=3, s=0)
az_spln_ev = syi.splev(tspline, az_spln_rep)
# plt.plot(tspline, az_spln_ev, 'm', label='adjust Cubic spline')

#integrate the angular velocity 
gy_spln_rep = syi.splrep(df0['time'], df0['gy'], k=2, s=0)
gy_spln_ev = syi.splev(tspline, gy_spln_rep)



#gy_int = integ(tspline, gy_spln_rep)
# plt.plot(tspline, gy_int, '--', label='angular position')



# def model(x, m, b):         # using curve_fit with a 1st or poly
#     return m*x+b

# intit_guess = [1, 1]
# fit = sy.curve_fit(model, df0['time'], df0['az'], p0=intit_guess, absolute_sigma=True)

# ans = fit[0]            # extracking out m and b
# slope_fit, y_fit = ans[0], ans[1]

# # plt.plot(time, model(time, slope_fit, y_fit))

# pitch0 =np.arctan2(df0['ax'], np.sqrt(df0['ay'] * df0['ay']) + (df0['az'] * df0['az'])) #putting roll fromula in python 
# roll0 = np.arctan2(df0['ay'], np.sqrt(df0['ax'] * df0['ax']) + (df0['az'] * df0['az']))
# pitch0 *= 180.0 / np.pi
# roll0 *= 180.0 / np.pi

# plt.plot(time, pitch0, 'k', markersize=3.5)         # plot roll data
# plt.plot(time, roll0, 'r', markersize=3.5)  


plt.xlabel("Write time(ms)")                                        # Label the axes
# plt.ylabel("Acceleration(mg)")
plt.ylabel("Angle(deg)")
# plt.axis([0, 50000, -4000, 20000])
plt.legend()
plt.show()

# roll0.to_csv('roll_brianp_test')
