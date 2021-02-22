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
import seaborn as sns
import scipy.optimize as sy





# Load in the data
df = pd.read_csv(
    "pronation\Python Code\Data\RESTDATA1.CSV", header=None)

# Give it a header
df.columns = ["accel", "ax", "ay", "az", "gx", "gy", "gz"]
df = df.drop(columns=['accel'])

# print(df)

# I want to take every third row starting from the second row and put it in a sigle table.
# Seperating data from each accelerometer into data frames
df0 = df.iloc[1::3, :]
df1 = df.iloc[2::3, :]
df2 = df.iloc[3::3, :]
# print(df0, df1,df2)

time = np.linspace(0, len(df['ay']), len(df['ay']))

# I want to create a best fit line for the gyro data then define
# an equation for that line. With that model I will solve the 
# I.V.P. for an eqution of positon. 
# I will then use the time values with the modol to solve for all
# position in time.  
# Taking the positions of the vertiacl and horizonal sensors 
# I will find delta change between the sensors subrtacted by 90 deg. 
#


sns.lineplot(x=time, y=df['az'], linewidth=1, color='r')
sns.lineplot(x=time, y=df['ax'], linewidth=1)
sns.lineplot(x=time, y=df['ay'], linewidth=1, color='g')


# making a best fit line to az data
def model(x, m, b):
    return m*x+b


intit_guess = [1, 1]
fit = sy.curve_fit(model, time, df['az'], p0=intit_guess, absolute_sigma=True)

# extracking out m and b
ans = fit[0]
slope_fit, y_fit = ans[0], ans[1]

plt.plot(time, model(time, slope_fit, y_fit))


# plt.show()
