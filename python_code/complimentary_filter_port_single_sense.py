#!/usr/bin/env python3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#Import the data 

column_names = ["channel", "t", "dt", "ax", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz"]    #Give header
# df = pd.read_csv(Path(os.getcwd()) / sys.argv[1], names=column_names)           # Load in the data      
df = pd.read_csv('C:/Users/Brian/OneDrive/_documents_one/_PHYS 398 DLP/Git Ripository/pronation/python_code/data/3.31_Loomis_3rd.csv',names=column_names, skiprows=1)

df0 = df[df["channel"]==0]      #Seperate the data for each LSM9DS1 accel.
df1 = df[df["channel"]==1]
df2 = df[df["channel"]==2]


# The angular displacement from angular velocity
# Using the restric pitch setting only from the arduino example
#Only calc.ing df0 for now

#Correct values and set bins
gyroXrate0 = (df0['gx']/10).values.tolist()
gyroYrate0 = (df0['gy']/10).values.tolist()
gyroZrate0 = (df0['gz']/10).values.tolist()
t0 = (df0['t']/1000).values.tolist()     #Converted to seconds
ax0 = df0['ax'].values.tolist()
ay0 = df0['ay'].values.tolist()
az0 = df0['az'].values.tolist()
mx0 = df0['mx'].values. tolist()
my0 = df0['my'].values. tolist()
mz0 = df0['mz'].values. tolist()

roll0s=[]
pitch0s=[]
yaw0s=[]
compRoll0s=[]
compPitch0s=[]
compYaw0s=[]
rollInt0s=[]
pitchInt0s=[]
yawInt0s=[]

B=0.93          #Filter coefficient. See https://www.diva-portal.org/smash/get/diva2:1146723/FULLTEXT01.pdf page 10 for more detials.
compRoll0=0     #Hold the to be calc.ed values
compPitch0=0
compYaw0=0
rollInt0=0
pitchInt0=0
yawInt0=0

#Calulate estimaions for each point
for i in range(len(t0)):
    roll0=np.degrees(np.arctan2(ax0[i],az0[i]))
    roll0s.append(roll0)    
    pitch0=np.degrees(np.arctan(-(ax0[i] / np.sqrt((ay0[i])**2 +(az0[i]**2)))))
    pitch0s.append(pitch0)
    #Calc. Yaw (around the z-axis)
    Bfy0=mz0[i]*np.sin(np.radians(roll0)) - my0[i]*np.cos(np.radians(roll0))
    Bfx0=mx0[i]*np.cos(np.radians(pitch0)) + my0[i]*np.sin(np.radians(pitch0))*np.sin(np.radians(roll0)) + mz0[i]*np.sin(np.radians(pitch0))*np.cos(np.radians(roll0))
    yaw0=(-1)*np.degrees(np.arctan2(-Bfy0,Bfx0))        #Not sure if this should be inverted
    yaw0s.append(yaw0)

    if i == 0:          #First data point is instantanoues
        dt0 = 0     
    else:
        dt0 = t0[i]-t0[i-1]      #Find time interval between measurements

    # Calculate the angle using a Complimentary filter
    compRoll0 = B * (compRoll0 + (gyroXrate0[i] * dt0)) + (1-B) * roll0 
    compRoll0s.append(compRoll0)
    compPitch0 = B * (compPitch0 + gyroYrate0[i] * dt0) + (1-B) * pitch0
    compPitch0s.append(compPitch0)
    compYaw0 = B * (compYaw0 + gyroZrate0[i] * dt0) + (1-B) * yaw0
    compYaw0s.append(compYaw0)

    #Find roll, pitch, and yaw via integration
    rollInt0 += gyroXrate0[i] * dt0
    rollInt0s.append(rollInt0)
    pitchInt0 += gyroYrate0[i] * dt0
    pitchInt0s.append(pitchInt0)
    yawInt0 += gyroZrate0[i] * dt0
    yawInt0s.append(yawInt0)


    #This fixes the transition problem when the accelerometer angle jumps between -180 and 180 degrees
    if (roll0 < -90 and compRoll0 > 90) or (roll0 > 90 and compRoll0 < -90):
        compRoll0 = roll0
        rollInt0 = roll0
    if (yaw0 < -90 and compYaw0 > 90 ) or (yaw0 > 90 and compYaw0 <-90):
        compYaw0 = yaw0
        yawInt0 = yaw0
    if abs(compRoll0) > 90:
        gyroYrate0[i] = -(gyroYrate0[i])       #Invert rate, so it fits the restriced accelerometer reading

    #Reset the gyro angle when it has drifted too much
    if (rollInt0 < -180 or rollInt0 > 180):
        rollInt0 = compRoll0
    if (pitchInt0 < -180 or pitchInt0 > 180):
        pitchInt0 = compPitch0
    if (yawInt0 < -180 or yawInt0 > 180):
        yawInt0 = compYaw0




#Plot Roll 
# plt.plot(t0, compRoll0s, label='Roll filterd by complimentary filter', color='#af0000')
# plt.plot(t0, roll0s, label='Roll unfiltered', color='#5fd787')
# plt.plot(t0, rollInt0s, label='Roll calc. by integration', color='#87d7ff')

#Plot Yaw
plt.plot(t0, compYaw0s, label='Yaw filterd by complimentary filter', color='#af0000')
plt.plot(t0, yaw0s, label='Yaw unfiltered', color='#5fd787')
plt.plot(t0, yawInt0s, label='Yaw calc. by integration', color='#87d7ff')

plt.xlabel("Time (s)")
plt.ylabel("Angular Displacement (degrees)")
plt.yticks(np.arange(-180, 180, 10))

plt.legend()
plt.grid(linestyle = '--', linewidth = 0.5)

plt.show()
