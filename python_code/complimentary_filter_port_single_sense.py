import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#Import the data 

column_names = ["channel", "t", "dtime", "ax", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz"]    #Give header
# df = pd.read_csv(Path(os.getcwd()) / sys.argv[1], names=column_names)           # Load in the data      
df = pd.read_csv('C:/Users/Brian/OneDrive/_documents_one/_PHYS 398 DLP/Git Ripository/pronation/python_code/data/Walking.CSV',names=column_names, skiprows=1)

df0 = df[df["channel"]==0]      #Seperate data for each LSM9DS1 accel.
df1 = df[df["channel"]==1]
df2 = df[df["channel"]==2]


# The angular displacement from angular velocity
# Using the restric pitch setting only from the arduino example
#Only calc. for df0 for now
gyroXrate0 = df0['gx']
gyroYrate0 = df0['gy']
t = df['t']

roll0s=[]
pitch0s=[]

print(df0.at['ay', 2])

for i in range(len(t)):
    dt0 = (t[i])/1000

    roll0=np.degrees(np.arctan2(df0.at[i,'ay'],df0.at[i,'az']))
    roll0s.append(roll0)
    pitch0=np.degrees(np.arctan(-(df0.at[i,'ax']) / np.sqrt((df0.at[i,'ay'])**2 +(df0.at[i,'az'])**2)))
    pitch0s.append(pitch0)

print(roll0s)


compAngleX0=roll0
compAngleY0=pitch0
# Calculate the angle using a Complimentary filter
compAngleX0 = 0.93 * (compAngleX0 + gyroXrate0 * dt0) + 0.07 * roll0 
compAngleY0 = 0.93 * (compAngleY0 + gyroYrate0 * dt0) + 0.07 * pitch0

# print(compAngleX0)
#This fixes the transition problem when the accelerometer angle jumps between -180 and 180 degrees
# for roll in roll0
#     if roll < -90 and compAngleX0 > 90 or (roll0 > 90 and compAngleX0 < -90):
#         compAngleX0 = roll0
#         gyroXangle0 = roll0

#     if abs(compAngleX0) > 90:
#         gyroYrate0 = -gyroYrate0 #Invert rate, so it fits the restriced accelerometer reading

#Calculate gyro angle without any filter
gyroXangle0 =0
gyroYangle0 =0
gyroXangle0 += gyroXrate0 * dt0
gyroYangle0 += gyroYrate0 * dt0


#Reset the gyro angle when it has drifted too much
# if (gyroXangle0 < -180 or gyroXangle0 > 180):
#     gyroXangle0 = compAngleX0
# if (gyroYangle0 < -180 or gyroYangle0 > 180):
#     gyroYangle0 = compAngleY0

# plt.plot(df0['t'], compAngleX0, label='Complintary Filter Roll0')
plt.plot(df0['t'], roll0, label='Only g vector Roll0')
# plt.plot(df0['t'], gyroXangle0, label='Only intergrating gyroX, Roll0')
plt.legend()
plt.show()
