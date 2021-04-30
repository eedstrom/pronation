#!/usr/bin/env python3

import matplotlib.pyplot as plt
import os
from pathlib import Path
import pandas as pd
import numpy as np
import time
# from PIL import Image
import cv2

def create_df(filename):
    df = pd.read_csv(Path(os.getcwd()) / "python_code/data/4.21_Loomis/" / filename, skiprows=1, header=None)      
    return df

def separate_df(df):
    # Give it a header
    df.columns = ["channel", 'time', 'dtime', "ax/cond", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz"]
    df = df.drop(columns=["dtime", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz"])
    
    df = df.drop(df.index[0])

    df['time'] = df['time'] - df['time'][1]     # Set first time to zero
    df['time'] = df['time']*(1/1000)            # Convert ms to s

    # print(df)

    # Convert conductance to force in lbs (ignore ax values)
    df["ax/cond"] = 10 * df["ax/cond"] * (1.0/6.0) + (1.0/6.0)
    df = df.rename(columns={"ax/cond": "force"})

    # Seperating data from each fsr into data frames
    df3 = df[df["channel"]==3]
    df4 = df[df["channel"]==4]
    df5 = df[df["channel"]==5]
    df6 = df[df["channel"]==6]

    return (df3, df4, df5, df6)

def plot_fsr(filename):
    df3, df4, df5, df6 = separate_df(create_df(filename))

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

time.sleep(2)

filename = 'df1.csv'
df3, df4, df5, df6 = separate_df(create_df(filename))

df3 = df3.reset_index(drop=True)
df4 = df4.reset_index(drop=True)
df5 = df5.reset_index(drop=True)
df6 = df6.reset_index(drop=True)

# CONSTANT indices for the fsr locations on foot
fsr_loc = {3:(65,13), 4:(42,20), 5:(24,24), 6:(18,6)}

# Initializing foot array
foot = np.zeros((38*2, 15*2))

# Create foot visual array
img = cv2.imread("/Users/teaganmathur/Documents/PHYS398DLP/foot_sole_outline.jpg")
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
outline = cv2.resize(img, dsize=foot.shape[::-1], interpolation=cv2.INTER_AREA)
outline[outline < 220] = 0
outline[outline != 0] = 255

for idx in range(len(df3)):
    # Set values at fsr locations
    for fsr in range(3,7):
        i,j = fsr_loc[fsr]

        if fsr == 3:
            val = df3["force"][idx]
        elif fsr == 4:
            val = df4["force"][idx]
        elif fsr == 5:
            val = df5["force"][idx]
        else:
            val = df6["force"][idx]

        foot[i, j] = val    # center of fsr
        
        foot[i+1, j] = val
        foot[i-1, j] = val
        foot[i, j+1] = val
        foot[i, j-1] = val

        foot[i+2, j] = val*0.9
        foot[i-2, j] = val*0.9
        foot[i, j+2] = val*0.9
        foot[i, j-2] = val*0.9
        foot[i+1, j+1] = val*0.9
        foot[i-1, j+1] = val*0.9
        foot[i-1, j-1] = val*0.9
        foot[i+1, j-1] = val*0.9

    # Convert foot outline array indeces to na in foot array
    foot[outline == 0] = np.nan
    
    plt.cla()
    plt.imshow(foot, cmap='jet')
    plt.title("Time: {:.2f} seconds".format(df3["time"][idx]))
    plt.draw()
    
    # Calculate how long to show this image for
    # if idx > 0:
    cb = plt.colorbar(label="Force (lbs)")
    plt.clim(0, max(df3["force"]))
    # plt.pause(df3["time"][idx]/1000 - df3["time"][idx - 1]/1000)
    plt.pause(0.005)
    cb.remove()
    # else:
        # plt.colorbar(label="Force (lbs)")
        # plt.pause(df3["time"][idx]/1000)
        # plt.pause(0.005)

