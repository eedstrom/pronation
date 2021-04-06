#!/usr/bin/env python3

import matplotlib.pyplot as plt
import os
from pathlib import Path
import pandas as pd

filenames = ['df0.csv', 'df1.csv', 'df2.csv', 'df3.csv', 'df4.csv']
for filename in filenames:

    # Load in the data
    df = pd.read_csv(Path(os.getcwd()) / "python_code/data/3.31_Loomis_Data_Ind/" / filename, skiprows=1, header=None)      

    # Give it a header
    df.columns = ["channel", 'time', 'dtime', "ax/cond", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz"]
    df = df.drop(columns=["dtime", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz"])

    df['time'] = df['time'] - df['time'][0]     # Set first time to zero
    df['time'] = df['time']*(1/1000)            # Convert ms to s

    # Convert conductance to force in lbs (ignore ax values)
    df["ax/cond"] = 10 * df["ax/cond"] * (1.0/6.0) + (1.0/6.0)
    df = df.rename(columns={"ax/cond": "force"})

    # Seperating data from each fsr into data frames
    df3 = df[df["channel"]==3]
    df4 = df[df["channel"]==4]
    df5 = df[df["channel"]==5]
    df6 = df[df["channel"]==6]

    # print(df3.head())

    # Plot the fsr data
    plt.plot(df3["time"], df3["force"], label="FSR 0")
    plt.plot(df4["time"], df4["force"], label="FSR 1")
    plt.plot(df5["time"], df5["force"], label="FSR 2")
    plt.plot(df6["time"], df6["force"], label="FSR 3")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Force (lbs)")
    plt.title(filename)
    plt.grid()
    plt.legend()
    plt.show()
