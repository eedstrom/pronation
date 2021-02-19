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


import numpy as np

accel_raw = open( 'RAWACCEL.CSV', 'r' ) #read the raw data

xaccel = []
yaccel = []
zaccel = []


for line in accel_raw.readlines():
    line = line.strip()  # remove whitespace from the line
    values = line.split(',') # split the line by commas ','

    xaccel.append(values[0])
    yaccel.append(values[1])
    zaccel.append(values[2])

print(zaccel)
