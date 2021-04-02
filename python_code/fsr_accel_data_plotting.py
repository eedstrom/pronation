#!/usr/bin/env python3

import csv
import matplotlib.pyplot as plt

path = '/Users/teaganmathur/Documents/PHYS398DLP/pronation/python_code/data/'
# filenames = ['QuietStance.CSV', 'Walking.CSV', 'Running.CSV']
filenames = ['3.31_Loomis_Data.CSV']

for filename in filenames:
    # Read in data
    with open(path + filename) as csvfile:
        reader = csv.reader(csvfile)
        full_data = list(reader)
    
    # Build the data sets into a dictionary
    # e.g. {1:[[0,0,0],[0,0]], 2:[[0,0,0],[0,0]], ......}
    datasets = {}
    setnum = 0
    for row in full_data:
        if row[0] == '-1':          # Header row
            setnum = setnum + 1
            datasets[setnum] = []   # Initialize new dataset in the dictionary
        else:
            datasets[setnum].append([float(val) for val in row])

    # Loop through each data set in the dictionary
    for setnum, data in datasets.items():
        # Column information for fsr_data
        # fsr (0-3), time_taken, uncertainty_in_time, conductance in micro-mhos

        fsr0, fsr1, fsr2, fsr3 = [], [], [], []
        t0, t1, t2, t3 = [], [], [], []

        test = []

        # Formula for converting conductance (mhos) to force (lbs)
        # conductance = 6*10^(-7)*force - 1*10^(-7)
        # force = (1/6)*10^7*conductance + (1/6)

        # Separate fsr data from accel data and convert
        for row in data:
            # fsr data rows (bus lines 3-6)
            if row[0] > 2:
                bus, t, dt, cond = row
                fsr = bus - 3   # bus line 3 = fsr 0
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
                test.append(cond)
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
        plt.title("Data Set {}".format(setnum))
        plt.grid()
        plt.legend()
        plt.show()
