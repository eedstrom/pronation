#!/usr/bin/env python3

import csv
import matplotlib.pyplot as plt

path = '/Users/teaganmathur/Documents/PHYS398DLP/pronation/python_code/data/FSR/'
filenames = ['QuietStanceFSR.CSV', 'WalkingFSR.CSV', 'RunningFSR.CSV']

for filename in filenames:

    # Read in fsr data
    with open(path + filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        fsr_data = list(reader)
        fsr_data = fsr_data[1:] # Remove the first row
        fsr_data = [[float(val) for val in row] for row in fsr_data]

    # Column information for fsr_data
    # fsr (0-3), time_taken, uncertainty_in_time, conductance in micro-mhos

    fsr0, fsr1, fsr2, fsr3 = [], [], [], []
    t0, t1, t2, t3 = [], [], [], []

    # Formula for converting conductance (mhos) to force (lbs)
    # conductance = 6*10^(-7)*force - 1*10^(-7)
    # force = (1/6)*10^7*conductance + (1/6)

    # Separate fsr data and convert
    for row in fsr_data:
        fsr, t, dt, cond = row

        cond = cond * 10**(-6)   # convert micro mhos to mhos
        force = (1/6) * 10**7 * cond + (1/6) # convert conductance to force

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
    plt.xlabel("Time")
    plt.ylabel("Force (lbs)")
    plt.title(filename.split('.')[0])
    plt.grid()
    plt.legend()
    plt.show()




    



