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

# Load in the data
df = pd.read_csv("pronation\Python Code\Data\TESTFILE.CSV", header=None)

# Give it a header
df.columns = ["ax", "ay", "az", "gx", "gy", "gz"]
time = np.linspace(0,len(df['ay']), len(df['ay']))

sns.lineplot(x=time, y=df['az'], linewidth=1, color='r')
sns.lineplot(x=time, y=df['ax'], linewidth=1)
sns.lineplot(x=time, y=df['ay'], linewidth=1, color='g')

plt.show()