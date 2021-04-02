#!/usr/bin/env python3

import csv
import matplotlib.pyplot as plt
import os
from pathlib import Path

path = Path(os.getcwd()) / "python_code/data/"

# filenames = ['QuietStance.CSV', 'Walking.CSV', 'Running.CSV']
filenames = ['3.31_Loomis_1st.csv', '3.31_Loomis_2nd.csv', '3.31_Loomis_3rd.csv', '3.31_Loomis_4th.csv', '3.31_Loomis_5th.csv']

for filename in filenames:
    # Read in data
    with open(path / filename) as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)
        data = data[1:] # Remove the first row
        data = [[float(val) for val in row] for row in data]

    # Column information for fsr_data
    # fsr (0-3), time_taken, uncertainty_in_time, conductance in micro-mhos

    fsr0, fsr1, fsr2, fsr3 = [], [], [], []
    t0, t1, t2, t3 = [], [], [], []
    start = 0

    # Formula for converting conductance (mhos) to force (lbs)
    # conductance = 6*10^(-7)*force - 1*10^(-7)
    # force = (1/6)*10^7*conductance + (1/6)

    # Separate fsr data from accel data and convert
    for i in range(len(data)):
        row = data[i]

        if i == 0:  # find the starting time
            start = row[1] / 1000.0

        if row[0] > 2:
            bus, t, dt, cond = row
            fsr = bus - 3           # bus line 3 = fsr 0
            t = t / 1000.0 - start  # convert ms to s and set start to 0
        # accel data rows (bus lines 0-2)
        else:
            continue
        
        cond = cond * 10**(-6)   # convert micro mhos to mhos
        force = 10**7 * cond * (1.0/6.0) + (1.0/6.0) # convert conductance to force

        if fsr == 0:
            fsr0.append(force)
            t0.append(t)
        elif fsr == 1:
            fsr1.append(force)
            t1.append(t)
        elif fsr == 2:
            fsr2.append(force)
            t2.append(t)
        else:
            fsr3.append(force)
            t3.append(t)

    # Plot the fsr data
    plt.plot(t0, fsr0, label="FSR0")
    plt.plot(t1, fsr1, label="FSR1")
    plt.plot(t2, fsr2, label="FSR2")
    plt.plot(t3, fsr3, label="FSR3")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Force (lbs)")
    plt.title(filename)
    plt.grid()
    plt.legend()
    plt.show()
