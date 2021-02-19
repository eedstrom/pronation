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



