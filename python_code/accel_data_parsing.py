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

df0 = df[df["channel"]==0]
df1 = df[df["channel"]==1]
df2 = df[df["channel"]==2]

#finding mag of accel. vector
df0amag = np.sqrt((df0['ax'])**2 + (df0['ay'])**2 + (df0['az'])**2)

# Calculate roll and pitch
roll0=np.degrees(np.arctan2(df0['ay'].values,df0['az'].values))
roll1=np.degrees(np.arctan2(df1['ay'].values,df0['az'].values))
roll2=np.degrees(np.arctan2(df2['ay'].values,df0['az'].values))

pitch0=np.degrees(np.arctan(-df0['ax'].values / np.sqrt((df0['ay'].values)**2+(df0['az'].values)**2)))
pitch1=np.degrees(np.arctan(-df1['ax'].values / np.sqrt((df1['ay'].values)**2+(df1['az'].values)**2)))
pitch2=np.degrees(np.arctan(-df2['ax'].values / np.sqrt((df2['ay'].values)**2+(df2['az'].values)**2)))

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

plt.xlabel("Write time(ms)")                                        # Label the axes
# plt.ylabel("Acceleration(mg)")
plt.ylabel("Angle(deg)")
# plt.axis([0, 50000, -4000, 20000])
plt.legend()
plt.show()
