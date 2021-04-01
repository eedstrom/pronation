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

df.columns = ["channel", "time", "dtime", "ax", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz", "roll", "gyroXangle", "compAngleX", "kalAngleX", "pitch", "gyroYangle", "compAngleY", "kalAngleY"]          # Give it a header
# print(df)
df0 = df[df["channel"]==0]
df1 = df[df["channel"]==1]
df2 = df[df["channel"]==2]


# plt.plot(df0['time'], df0amag, 'bo', markersize=3, label='ax')      # plot accel data pts
# plt.plot(df0['time'], df0['ay'], 'g', markersize=3.5, label='ay')      # plot accel data pts
# plt.plot(df0['time'], df0['az'], 'k', markersize=3.5, label='az')      # plot accel data pts

tspline = np.linspace(df0['time'].iloc[0], df0['time'].iloc[-1], num=3000, endpoint=True)         # adjust num=___ to change the amount of pts of spline using scypi spline tools
az_spln_rep = syi.splrep(df0['time'], df0amag, k=3, s=0)
az_spln_ev = syi.splev(tspline, az_spln_rep)
# plt.plot(tspline, az_spln_ev, 'm', label='adjust Cubic spline')


# using curve_fit with a 1st or poly
# def model(x, m, b):      
#     return m*x+b

# intit_guess = [1, 1]
# fit = sy.curve_fit(model, df0['time'], df0['az'], p0=intit_guess, absolute_sigma=True)

# ans = fit[0]            # extracking out m and b
# slope_fit, y_fit = ans[0], ans[1]
# plt.plot(time, model(time, slope_fit, y_fit))


plt.xlabel("Time(ms)")                                        # Label the axes
# plt.ylabel("Acceleration(mg)")
plt.ylabel("Angle(deg)")
# plt.axis([0, 50000, -4000, 20000])
plt.legend()
plt.show()






