#!/usr/bin/python3

import csv
import matplotlib.pyplot as plt

path = '/Volumes/NO NAME/FSR.CSV'

# Read in fsr data
with open(path, newline='') as csvfile:
    reader = csv.reader(csvfile)
    fsr_data = list(reader)
    fsr_data = fsr_data[1:] # Remove the first row
    fsr_data = [[float(val) for val in row] for row in fsr_data]

# Column information for fsr_data
# fsr (0-3), time_taken, uncertainty_in_time, conductance in micro-mhos

fsr0, fsr1, fsr2, fsr3 = [], [], [], []
t0, t1, t2, t3 = [], [], [], []

# Separate fsr data
for row in fsr_data:
    fsr, t, dt, cond = row

    if fsr == 0:
        fsr0.append(cond)
        t0.append(t)
    elif fsr == 1:
        fsr1.append(cond)
        t1.append(t)
    elif fsr == 2:
        fsr2.append(cond)
        t2.append(t)
    else:
        fsr3.append(cond)
        t3.append(t)

# Plot the fsr data
plt.plot(t0, fsr0, label="FSR0")
plt.plot(t1, fsr1, label="FSR1")
plt.plot(t2, fsr2, label="FSR2")
plt.plot(t3, fsr3, label="FSR3")
plt.xlabel("Time")
plt.ylabel("Conductance (micro-mhos)")
plt.grid()
plt.legend()
plt.show()




    



