#!/usr/bin/env python3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#Import the data 

column_names = ["channel", "t", "dtime", "ax", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz"]    #Give header
# df = pd.read_csv(Path(os.getcwd()) / sys.argv[1], names=column_names)           # Load in the data      
df = pd.read_csv('C:/Users/Brian/OneDrive/_documents_one/_PHYS 398 DLP/Git Ripository/pronation/python_code/data/3.31_Loomis_3rd.csv',names=column_names, skiprows=1)

df0 = df[df["channel"]==0]      #Seperate the data for each LSM9DS1 accel.
df1 = df[df["channel"]==1]
df2 = df[df["channel"]==2]


# The angular displacement from angular velocity
# Using the restric pitch setting only from the arduino example
#Only calc.ing df0 for now

gyroXrate0 = df0['gx'].values.tolist()
# print(gyroXrate0)
gyroYrate0 = df0['gy'].values.tolist()
t0 = (df0['t']/1000).values.tolist()     #Put into seconds
ax0 = df0['ax'].values.tolist()
ay0 = df0['ay'].values.tolist()
az0 = df0['az'].values.tolist()

roll0s=[]
pitch0s=[]
compRoll0s=[]
compPitch0s=[]
rollInt0s=[]
pitchInt0s=[]

compRoll0=0     #Hold the to be corrected value
compPitch0=0
rollInt0=0
pitchInt0=0
# rollInt0=gyroXrate0*(t0[1]-t0[0])
# pitchInt0=gyroYrate0*(t0[1]-t0[0])


for i in range(len(t0)):
    roll0=np.degrees(np.arctan2(ax0[i],az0[i]))
    roll0s.append(roll0)    
    pitch0=np.degrees(np.arctan(-(ax0[i] / np.sqrt((ay0[i])**2 +(az0[i]**2)))))
    pitch0s.append(pitch0)

    dt0 = t0[i]-t0[i-1]       #Find time interval between measurements
    # Calculate the angle using a Complimentary filter
    compRoll0 = 0.93 * (compRoll0 + gyroXrate0[i] * dt0) + 0.07 * roll0 
    compRoll0s.append(compRoll0)
    compPitch0 = 0.93 * (compPitch0 + gyroYrate0[i] * dt0) + 0.07 * pitch0
    compPitch0s.append(compPitch0)

    #Find roll and pitch via integration
    rollInt0 += gyroXrate0[i] * dt0
    rollInt0s.append(rollInt0)
    pitchInt0 += gyroYrate0[i] * dt0
    pitchInt0s.append(pitchInt0)

    #This fixes the transition problem when the accelerometer angle jumps between -180 and 180 degrees
    if (roll0 < -90 and compRoll0 > 90) or (roll0 > 90 and compRoll0 < -90):
        compRoll0 = roll0
        rollInt0 = roll0

    if abs(compRoll0) > 90:
        gyroYrate0[i] = -(gyroYrate0[i])       #Invert rate, so it fits the restriced accelerometer reading

    #Reset the gyro angle when it has drifted too much
    if (rollInt0 < -180 or rollInt0 > 180):
        rollInt0 = compRoll0
    if (pitchInt0 < -180 or pitchInt0 > 180):
        pitchInt0 = compPitch0


# Calculate the angle using a Complimentary filter
# compAngleX0 = 0.93 * (compAngleX0 + gyroXrate0 * dt0) + 0.07 * roll0 
# compAngleY0 = 0.93 * (compAngleY0 + gyroYrate0 * dt0) + 0.07 * pitch0


plt.plot(t0, compRoll0s, label='Roll filterd by complimentary filter')
plt.plot(t0, roll0s, label='Roll unfiltered')
plt.plot(t0, rollInt0s, label='Roll calc. by integration')

plt.legend()
plt.show()
