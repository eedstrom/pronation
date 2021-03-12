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
# df = pd.read_csv("pronation/python_code/data/running_on_treadmil.csv")


df.columns = ["time", "accel", "ax", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz"]          # Give it a header
df = df.drop(columns=['accel'])
# df = np.abs(df) 
print(df)


# I want to take every third row starting from the second row and put it in a sigle table.
df0 = df.iloc[1::3, :]          # Seperating data from each accelerometer into data frames
df1 = df.iloc[2::3, :]
df2 = df.iloc[3::3, :]
# print(df0, df1,df2)


#finding mag of accel. vector
df0amag = np.sqrt((df0['ax'])**2 + (df0['ay'])**2 + (df0['az'])**2)


# plt.plot(df0['time'], df0amag, 'bo', markersize=3, label='ax')      # plot accel data pts
# plt.plot(df0['time'], df0['ay'], 'g', markersize=3.5, label='ay')      # plot accel data pts
# plt.plot(df0['time'], df0['az'], 'k', markersize=3.5, label='az')      # plot accel data pts



print(np.std(df0['az']))
print(np.mean(df0['az']))

# plt.plot(time, df0['gx'], 'k', markersize=3.5)          # plot gyro data pts
plt.plot(df0['time'], df0['gy'], 'ro', markersize=3, label='angular velocity')        
# plt.plot(time, df0['gz'], 'g', markersize=3.5) 


tspline = np.linspace(df0['time'].iloc[0], df0['time'].iloc[-1], num=3000, endpoint=True)         # adjust num=___ to change the amount of pts of spline using scypi spline tools

az_spln_rep = syi.splrep(df0['time'], df0amag, k=3, s=0)
az_spln_ev = syi.splev(tspline, az_spln_rep)
# plt.plot(tspline, az_spln_ev, 'm', label='adjust Cubic spline')

#integrate the angular velocity 
gy_spln_rep = syi.splrep(df0['time'], df0['gy'], k=2, s=0)
gy_spln_ev = syi.splev(tspline, gy_spln_rep)

def integ(x, tck):
    x = np.atleast_1d(x)
    out = np.zeros(x.shape, dtype=x.dtype)
    for n in range(len(out)):
        out[n] = syi.splint(0, x[n], tck)
    # out += constant
    return out

gy_int = integ(tspline, gy_spln_rep)
plt.plot(tspline, gy_int, '--', label='angular position')



# az_CubicSpline = syi.CubicSpline(df0['time'], df0['az'])
# plt.plot(timespline, az_CubicSpline(timespline), 'ro', label='az0 cubic spline')




def model(x, m, b):         # using curve_fit with a 1st or poly
    return m*x+b

intit_guess = [1, 1]
fit = sy.curve_fit(model, df0['time'], df0['az'], p0=intit_guess, absolute_sigma=True)

ans = fit[0]            # extracking out m and b
slope_fit, y_fit = ans[0], ans[1]

# plt.plot(time, model(time, slope_fit, y_fit))

pitch0 =np.arctan2(df0['ax'], np.sqrt(df0['ay'] * df0['ay']) + (df0['az'] * df0['az'])) #putting roll fromula in python 
roll0 = np.arctan2(df0['ay'], np.sqrt(df0['ax'] * df0['ax']) + (df0['az'] * df0['az']))
pitch0 *= 180.0 / np.pi
roll0 *= 180.0 / np.pi

# plt.plot(time, pitch0, 'k', markersize=3.5)         # plot roll data
# plt.plot(time, roll0, 'r', markersize=3.5)  

plt.xlabel("Write time(ms)")                                        # Label the axes
# plt.ylabel("Acceleration(mg)")
plt.ylabel("Angle(deg)")
# plt.axis([0, 50000, -4000, 20000])
plt.legend()
plt.show()

# roll0.to_csv('roll_brianp_test')





