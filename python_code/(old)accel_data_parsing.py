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
from pathlib import Path
import sys
import os

# Load in the path to the data
p = Path(os.getcwd()) / sys.argv[1]

# Load in the dat
df = pd.read_csv(p, header=None)

# Give it a header
df.columns = ["ax", "ay", "az", "gx", "gy", "gz"]
time = np.linspace(0, len(df['ay']), len(df['ay']))

sns.lineplot(x=time, y=df['az'], linewidth=1, color='r')
sns.lineplot(x=time, y=df['ax'], linewidth=1)
sns.lineplot(x=time, y=df['ay'], linewidth=1, color='g')

# making a best fit line to az data

"Hello nano world?"
def model(x, m, b):
    return m*x+b


intit_guess = [1, 1]
fit = sy.curve_fit(model, time, df['az'], p0=intit_guess, absolute_sigma=True)

# extracking out m and b
ans = fit[0]
slope_fit, y_fit = ans[0], ans[1]

plt.plot(time, model(time, slope_fit, y_fit))


plt.show()
