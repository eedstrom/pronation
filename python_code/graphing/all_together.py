#! usr/bin.env python3

import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import pandas as pd
from pathlib import Path
import sys

def _clean_df_acc(df):
    """ Standardizes the units
        CALL FROM split_df NOT BY ITSELF
    """
    df["t"] = df["t"] / 1000
    df["dt"] = df["dt"] / 1000
    df["ax"] = df["ax"] / 1000
    df["ay"] = df["ay"] / 1000
    df["az"] = df["az"] / 1000
    df["gx"] = df["gx"] / 10
    df["gy"] = df["gy"] / 10
    df["gz"] = df["gz"] / 10

def _clean_df_fsr(df):
    """ Standardizes the units
        CALL FROM split_df NOT BY ITSELF
    """
    df["t"] = df["t"] / 1000
    df["dt"] = df["dt"] / 1000
    df["stand_val"] = df["val"] / df["val"].max()

def split_df(df):
    # Separate the data by bus line
    df0 = df[df["id"] == 0]
    df1 = df[df["id"] == 1]
    df2 = df[df["id"] == 2]

    # Separate the FSR data
    df3 = df[df["id"] == 3].dropna(axis=1).rename(columns={"ax": "val"})
    df4 = df[df["id"] == 4].dropna(axis=1).rename(columns={"ax": "val"})
    df5 = df[df["id"] == 5].dropna(axis=1).rename(columns={"ax": "val"})
    df6 = df[df["id"] == 6].dropna(axis=1).rename(columns={"ax": "val"})

    # Clean the acceleration data
    for df_iter in (df0, df1, df2):
        _clean_df_acc(df_iter)

    # Clean the FSR data
    for df_iter in (df3, df4, df5, df6):
        _clean_df_fsr(df_iter)

    return (df0, df1, df2, df3, df4, df5, df6)


def calc_airplane(df_tup):
    df0, df1, df2, *_ = df_tup

    # Calculate roll, pitch, and yaw for all
    for d in (df0, df1, df2):
        d["roll"] = np.arctan2(d["ay"], d["az"]) * 180 / np.pi
        d["pitch"] = np.arctan(-1 * d["ax"]/
                                np.sqrt(d["ay"] ** 2 + d["az"] ** 2)) * 180 / np.pi

        bfy = d["mz"] * np.sin(d["roll"]) - d["my"] * np.cos(d["roll"])
        bfx = d["mx"] * np.cos(d["pitch"]) + d["my"] * \
            np.sin(d["pitch"]) * np.sin(d["roll"]) + d["mz"] * \
            np.sin(d["pitch"]) * np.cos(d["roll"])
        # Convert to numpy arrays
        bfy = bfy.to_numpy()
        bfx = bfx.to_numpy()

        d['yaw'] = np.arctan(-bfy, bfx) * 180 / np.pi

def make_df_full(df):
    """Function to prepare for all plotting in later functions. This should be run
    prior to any other plotting function."""
    # Get rid of the info row
    # info_row = df.loc[df["id"] == -1]
    df = df.drop(index=0)

    # Change `my` to float
    df = df.astype({"my": "float64", "mz": "float64"})

    df["t"] = df["t"] - df["t"].min()  # Set start time to 0
    df_tup = split_df(df)              # Split the data by each bus line
    calc_airplane(df_tup)              # Calculate roll, pitch, and yaw
    return df_tup

def get_initial_airplane(df_rest_tup):
    """Function returns the initial values of roll, pitch, and yaw""" 
    # Load in the rest data and separate by bus line
    # df_rest_tup = make_df_full(rest_df)
    df0, df1, df2, *_ = df_rest_tup
    
    # Dict for storage
    airplane_initial = {
        "roll":  [],
        "pitch": [],
        "yaw":   []
    }

    # Take the average of the rest data
    for df_iter in [df0, df1, df2]:
        airplane_initial["roll"].append(df_iter["roll"].mean())
        airplane_initial["pitch"].append(df_iter["pitch"].mean())
        airplane_initial["yaw"].append(df_iter["yaw"].mean())

    return airplane_initial

def comp_filter(df_tup, beta=0.93, airplane_initial=None):
    """
    Implementation of the complimentary filter
    """
    # Get the datasets to be filtered
    df0, df1, df2, *_ = df_tup
    
    # Check if initial values were passed
    have_values = False
    if airplane_initial is not None:
        have_values = True

    # Iterate over each bus line
    for df_idx, df in enumerate([df0, df1, df2]):
        # Get the number of data points in the dataframe
        n = df.shape[0]

        # Create containers for each comp_angle
        comp_roll = np.zeros(n)
        comp_pitch = np.zeros(n)
        comp_yaw = np.zeros(n)

        # Create containers for the integration angles
        integral_roll = np.zeros(n)
        integral_pitch = np.zeros(n)
        integral_yaw = np.zeros(n)


        # Set non-zero starting values if passed
        if have_values:
            # Set initial values for the complimentary filter
            comp_roll[0] = airplane_initial["roll"][df_idx]
            comp_pitch[0] = airplane_initial["pitch"][df_idx]
            comp_yaw[0] = airplane_initial["yaw"][df_idx]

            # Set initial values for the integral method
            integral_roll[0] = airplane_initial["roll"][df_idx]
            integral_pitch[0] = airplane_initial["pitch"][df_idx]
            integral_yaw[0] = airplane_initial["yaw"][df_idx]
         
        # Change to numpy arrays for convinience
        roll = df["roll"].to_numpy()
        pitch = df["roll"].to_numpy()
        yaw = df["yaw"].to_numpy()
        gx = df["gx"].to_numpy()
        gy = df["gy"].to_numpy()
        gz = df["gz"].to_numpy()

        # Calculate the dt vector
        dt = df["t"].to_numpy() - np.roll(df["t"].to_numpy(), 1)
        dt[0] = 0

        # Iterate over each data point
        for i in range(1, n):
            # Calculate the angle from the complimentary filter
            comp_roll[i] = beta * (comp_roll[i - 1] + (gx[i] * dt[i]) ) + ( (1 - beta) * roll[i] )
            comp_pitch[i] = beta * (comp_pitch[i - 1] + (gy[i] * dt[i]) ) + ( (1 - beta) * pitch[i] )
            comp_yaw[i] =  beta * (comp_yaw[i - 1] + (gz[i] * dt[i]) ) + ( (1 - beta) * yaw[i] )

            # Calculate the angle from the integration
            integral_roll[i] = gx[i] * dt[i] + integral_roll[i - 1]
            integral_pitch[i] = gy[i] * dt[i] + integral_pitch[i - 1]
            integral_yaw[i] = gz[i] * dt[i] + integral_yaw[i - 1]

            ## Checks on the values (Make sure we are within our constraints

            # This fixes the transition problem when the accelerometer angle jumps between -180 and 180 degrees
            if (roll[i] < -90 and comp_roll[i] > 90) or (roll[i] > 90 and comp_roll[i] < -90):
                comp_roll[i] = roll[i]
                integral_roll[i] = roll[i]
            if (yaw[i] < -90 and comp_yaw[i] > 90 ) or (yaw[i] > 90 and comp_yaw[i] <-90):
                comp_yaw[i] = yaw[i]
                integral_yaw[i] = yaw[i]
            if abs(comp_roll[i]) > 90:
                gy[i] = -(gy[i])       #Invert rate, so it fits the restriced accelerometer reading

            #Reset the gyro angle when it has drifted too much
            if (integral_roll[i] < -180 or integral_roll[i] > 180):
                integral_roll[i] = comp_roll[i]
            if (integral_pitch[i] < -180 or integral_pitch[i] > 180):
                integral_pitch[i] = comp_pitch[i]
            if (integral_yaw[i] < -180 or integral_yaw[i] > 180):
                integral_yaw[i] = comp_yaw[i]

        # Add these columns to the dataframe
        df["comp_roll"] = comp_roll
        df["comp_pitch"] = comp_pitch
        df["comp_yaw"] = comp_yaw
        df["integral_roll"] = integral_roll
        df["integral_pitch"] = integral_pitch
        df["integral_yaw"] = integral_yaw

def plot_acc(df_tup):

    # Plot accelerations over time by bus line
    style.use("ggplot")
    fig, axs = plt.subplots(3, 1, sharex=True)

    # Get dataframes from tuple
    df0, df1, df2, *_ = df_tup

    # ax
    axs[0].scatter(df0["t"], df0["ax"], label="Bus 0", alpha=0.3)
    axs[0].scatter(df1["t"], df1["ax"], label="Bus 1", alpha=0.3)
    axs[0].scatter(df2["t"], df2["ax"], label="Bus 2", alpha=0.3)
    axs[0].plot(df0["t"], df0["ax"], alpha=0.3)
    axs[0].plot(df1["t"], df1["ax"], alpha=0.3)
    axs[0].plot(df2["t"], df2["ax"], alpha=0.3)
    axs[0].legend()

    # ay
    axs[1].scatter(df0["t"], df0["ay"], label="Bus 0", alpha=0.3)
    axs[1].scatter(df1["t"], df1["ay"], label="Bus 1", alpha=0.3)
    axs[1].scatter(df2["t"], df2["ay"], label="Bus 2", alpha=0.3)
    axs[1].plot(df0["t"], df0["ay"], alpha=0.3)
    axs[1].plot(df1["t"], df1["ay"], alpha=0.3)
    axs[1].plot(df2["t"], df2["ay"], alpha=0.3)
    axs[1].legend()

    # az
    axs[2].scatter(df0["t"], df0["az"], label="Bus 0", alpha=0.3)
    axs[2].scatter(df1["t"], df1["az"], label="Bus 1", alpha=0.3)
    axs[2].scatter(df2["t"], df2["az"], label="Bus 2", alpha=0.3)
    axs[2].plot(df0["t"], df0["az"], alpha=0.3)
    axs[2].plot(df1["t"], df1["az"], alpha=0.3)
    axs[2].plot(df2["t"], df2["az"], alpha=0.3)
    axs[2].legend()

    # Customize the plot
    fig.suptitle("Acceleration by Bus Line over Time")
    axs[2].set_xlabel("Time (s)")
    axs[0].set_ylabel("Acceleration (g)")
    axs[1].set_ylabel("Acceleration (g)")
    axs[2].set_ylabel("Acceleration (g)")
    axs[0].set_title("Acceleration x")
    axs[1].set_title("Acceleration y")
    axs[2].set_title("Acceleration z")
    plt.show()

def plot_airplane(df_tup):
    # Split the data
    df0, df1, df2, *_ = df_tup

    # Set up the figure
    style.use("ggplot")
    fig, axs = plt.subplots(3, 1, sharex=True)

    # roll
    axs[0].scatter(df0["t"], df0["roll"], label="Laces", alpha=0.3)
    axs[0].scatter(df1["t"], df1["roll"], label="Heel", alpha=0.3)
    axs[0].scatter(df2["t"], df2["roll"], label="Shin", alpha=0.3)
    axs[0].plot(df0["t"], df0["roll"], alpha=0.3)
    axs[0].plot(df1["t"], df1["roll"], alpha=0.3)
    axs[0].plot(df2["t"], df2["roll"], alpha=0.3)
    axs[0].legend()

    # pitch
    axs[1].scatter(df0["t"], df0["pitch"], label="Laces", alpha=0.3)
    axs[1].scatter(df1["t"], df1["pitch"], label="Heel", alpha=0.3)
    axs[1].scatter(df2["t"], df2["pitch"], label="Shin", alpha=0.3)
    axs[1].plot(df0["t"], df0["pitch"], alpha=0.3)
    axs[1].plot(df1["t"], df1["pitch"], alpha=0.3)
    axs[1].plot(df2["t"], df2["pitch"], alpha=0.3)
    axs[1].legend()

    # yaw
    axs[2].scatter(df0["t"], df0["yaw"], label="Laces", alpha=0.3)
    axs[2].scatter(df1["t"], df1["yaw"], label="Heel", alpha=0.3)
    axs[2].scatter(df2["t"], df2["yaw"], label="Shin", alpha=0.3)
    axs[2].plot(df0["t"], df0["yaw"], alpha=0.3)
    axs[2].plot(df1["t"], df1["yaw"], alpha=0.3)
    axs[2].plot(df2["t"], df2["yaw"], alpha=0.3)
    axs[2].legend()

    # Customize the plot
    fig.suptitle("Angles by Bus Line over Time")
    axs[2].set_xlabel("Time (s)")
    axs[0].set_ylabel("Angle (deg)")
    axs[1].set_ylabel("Angle (deg)")
    axs[2].set_ylabel("Angle (deg)")
    axs[0].set_title("Roll")
    axs[1].set_title("Pitch")
    axs[2].set_title("Yaw")
    plt.show()

def plot_air_and_fsr_with_comp(df_tup, beta=0.93, airplane_initial=None, scale_fsr=False):
    # Run the complimentary filter
    comp_filter(df_tup, beta=beta, airplane_initial=airplane_initial)

    # Split the data
    df0, df1, df2, df3, df4, df5, df6 = df_tup
    
    # Set up the figure
    style.use("ggplot")
    fig, axs = plt.subplots(4, 1, sharex=True)

    # complimentary roll
    axs[0].scatter(df0["t"], df0["comp_roll"], label="Laces", alpha=0.3)
    axs[0].scatter(df1["t"], df1["comp_roll"], label="Heel", alpha=0.3)
    axs[0].scatter(df2["t"], df2["comp_roll"], label="Shin", alpha=0.3)
    axs[0].plot(df0["t"], df0["comp_roll"], alpha=0.3)
    axs[0].plot(df1["t"], df1["comp_roll"], alpha=0.3)
    axs[0].plot(df2["t"], df2["comp_roll"], alpha=0.3)
    axs[0].legend()

    # complimentary pitch
    axs[1].scatter(df0["t"], df0["comp_pitch"], label="Laces", alpha=0.3)
    axs[1].scatter(df1["t"], df1["comp_pitch"], label="Heel", alpha=0.3)
    axs[1].scatter(df2["t"], df2["comp_pitch"], label="Shin", alpha=0.3)
    axs[1].plot(df0["t"], df0["comp_pitch"], alpha=0.3)
    axs[1].plot(df1["t"], df1["comp_pitch"], alpha=0.3)
    axs[1].plot(df2["t"], df2["comp_pitch"], alpha=0.3)
    axs[1].legend()

    # complimentary yaw
    axs[2].scatter(df0["t"], df0["comp_yaw"], label="Laces", alpha=0.3)
    axs[2].scatter(df1["t"], df1["comp_yaw"], label="Heel", alpha=0.3)
    axs[2].scatter(df2["t"], df2["comp_yaw"], label="Shin", alpha=0.3)
    axs[2].plot(df0["t"], df0["comp_yaw"], alpha=0.3)
    axs[2].plot(df1["t"], df1["comp_yaw"], alpha=0.3)
    axs[2].plot(df2["t"], df2["comp_yaw"], alpha=0.3)
    axs[2].legend()

    # plot fsr data
    col = 'stand_val' if scale_fsr else 'val'

    axs[3].scatter(df3["t"], df3[col], label=0, alpha=0.3)
    axs[3].scatter(df4["t"], df4[col], label=1, alpha=0.3)
    axs[3].scatter(df5["t"], df5[col], label=2, alpha=0.3)
    axs[3].scatter(df6["t"], df6[col], label=3, alpha=0.3)
    
    axs[3].plot(df3["t"], df3[col], alpha=0.3)
    axs[3].plot(df4["t"], df4[col], alpha=0.3)
    axs[3].plot(df5["t"], df5[col], alpha=0.3)
    axs[3].plot(df6["t"], df6[col], alpha=0.3)
    axs[3].legend()

    # Customize the plot
    fig.suptitle("Angles by Bus Line over Time")
    axs[3].set_xlabel("Time (s)")
    axs[0].set_ylabel("Angle (deg)")
    axs[1].set_ylabel("Angle (deg)")
    axs[2].set_ylabel("Angle (deg)")
    fsr_ylabel = "Relative Force (dimensionless)" if scale_fsr else "Force (lbs)"
    axs[3].set_ylabel(fsr_ylabel)
    axs[0].set_title("Roll")
    axs[1].set_title("Pitch")
    axs[2].set_title("Yaw")
    axs[3].set_title("FSR Force")
    plt.show()

def plot_airplane_with_integration(df_tup, beta=0.93, airplane_initial=None):
    # Run the complimentary filter
    comp_filter(df_tup, beta=beta, airplane_initial=airplane_initial)
    # Split the data
    df0, df1, df2, *_ = df_tup
    
    # Set up the figure
    style.use("ggplot")
    fig, axs = plt.subplots(3, 1, sharex=True)

    # integral roll
    axs[0].scatter(df0["t"], df0["integral_roll"], label="Laces", alpha=0.3)
    axs[0].scatter(df1["t"], df1["integral_roll"], label="Heel", alpha=0.3)
    axs[0].scatter(df2["t"], df2["integral_roll"], label="Shin", alpha=0.3)
    axs[0].plot(df0["t"], df0["integral_roll"], alpha=0.3)
    axs[0].plot(df1["t"], df1["integral_roll"], alpha=0.3)
    axs[0].plot(df2["t"], df2["integral_roll"], alpha=0.3)
    axs[0].legend()

    # integral pitch
    axs[1].scatter(df0["t"], df0["integral_pitch"], label="Laces", alpha=0.3)
    axs[1].scatter(df1["t"], df1["integral_pitch"], label="Heel", alpha=0.3)
    axs[1].scatter(df2["t"], df2["integral_pitch"], label="Shin", alpha=0.3)
    axs[1].plot(df0["t"], df0["integral_pitch"], alpha=0.3)
    axs[1].plot(df1["t"], df1["integral_pitch"], alpha=0.3)
    axs[1].plot(df2["t"], df2["integral_pitch"], alpha=0.3)
    axs[1].legend()

    # integral yaw
    axs[2].scatter(df0["t"], df0["integral_yaw"], label="Laces", alpha=0.3)
    axs[2].scatter(df1["t"], df1["integral_yaw"], label="Heel", alpha=0.3)
    axs[2].scatter(df2["t"], df2["integral_yaw"], label="Shin", alpha=0.3)
    axs[2].plot(df0["t"], df0["integral_yaw"], alpha=0.3)
    axs[2].plot(df1["t"], df1["integral_yaw"], alpha=0.3)
    axs[2].plot(df2["t"], df2["integral_yaw"], alpha=0.3)
    axs[2].legend()

    # Customize the plot
    fig.suptitle("Angles by Bus Line over Time")
    axs[2].set_xlabel("Time (s)")
    axs[0].set_ylabel("Angle (deg)")
    axs[1].set_ylabel("Angle (deg)")
    axs[2].set_ylabel("Angle (deg)")
    axs[0].set_title("Roll")
    axs[1].set_title("Pitch")
    axs[2].set_title("Yaw")
    plt.show()

def plot_ind_airplane(df_tup, df_rest_tup, air_col='roll', use_filter=True, scale_fsr=False):
    if use_filter:
        initial_airplane = get_initial_airplane(df_rest_tup)
        comp_filter(df_tup, airplane_initial=initial_airplane)
        air_col = f'comp_{air_col}'

    # Split the data
    df0, df1, df2, df3, df4, df5, df6 = df_tup

    # Set up the figure
    style.use("ggplot")
    fig, axs = plt.subplots(4, 1, sharex=True)

    # Laces
    axs[0].scatter(df0["t"], df0[air_col], alpha=0.3)
    axs[0].plot(df0["t"], df0[air_col], alpha=0.3)

    # Shin
    axs[2].scatter(df1["t"], df0[air_col], alpha=0.3)
    axs[2].plot(df1["t"], df0[air_col], alpha=0.3)

    # Heel
    axs[1].scatter(df2["t"], df0[air_col], alpha=0.3)
    axs[1].plot(df2["t"], df0[air_col], alpha=0.3)

    # plot fsr data
    col = 'stand_val' if scale_fsr else 'val'
    fsr_tit = 'Scaled FSR' if scale_fsr else 'FSR (lbs)'
    axs[3].plot(df3["t"], df3[col], alpha=0.3)
    axs[3].plot(df4["t"], df4[col], alpha=0.3)
    axs[3].plot(df5["t"], df5[col], alpha=0.3)
    axs[3].plot(df6["t"], df6[col], alpha=0.3)
    axs[3].legend()

    # Customize the plot
    fig.suptitle(f"{air_col.title()} by Location over Time")
    axs[3].set_xlabel("Time (s)")
    axs[0].set_ylabel("Angle (deg)")
    axs[1].set_ylabel("Angle (deg)")
    axs[2].set_ylabel("Angle (deg)")
    axs[3].set_ylabel(fsr_tit)
    axs[0].set_title("Laces")
    axs[1].set_title("Heel")
    axs[2].set_title("Shin")
    plt.show()


def plot_area(df_tup, df_rest_tup, sup_diff=3, pron_diff=9, use_filter=True):
    # Run the comp filter
    comp_filter(df_tup, airplane_initial=get_initial_airplane(df_rest_tup))

    # Split the data
    _, df1, df2, *_ = df_tup
    _, rest1, rest2, *_, = df_rest_tup    

    # Get the average difference in roll
    rest_diff = np.mean(rest2['roll'].to_numpy() - rest1['roll'].to_numpy())

    # Get the diff in yaw between buses 2 and 1
    roll_diff = df2["comp_roll"].to_numpy() - df1[f"comp_roll"].to_numpy()
    roll_diff = roll_diff - rest_diff

    # Set up the figure
    style.use("ggplot")
    _ , axs = plt.subplots(2, 1, sharex=True)
    
    # Plot the difference in yaw and the cutoffs
    n = df1.shape[0]
    axs[1].plot(df1["t"], roll_diff, label = "Observed Difference" )
    axs[1].plot(df1["t"], np.repeat(sup_diff, n), label="Supination Cutoff")
    axs[1].fill_between(df1['t'], roll_diff, np.repeat(sup_diff, n) ,label="Observed Supination", alpha=0.3, where = roll_diff < np.repeat(sup_diff, n), interpolate=True)
    axs[1].legend()
    axs[1].set_xlabel("Time (s)")
    axs[1].set_ylabel("Difference in Angle (deg)")
    axs[1].set_title("Regions of Supination")
    axs[1].legend()

    # Plot Pronation
    axs[0].plot(df1["t"], roll_diff, label = "Observed Difference" )
    axs[0].plot(df1["t"], np.repeat(pron_diff, n), label="Pronation Cutoff")
    axs[0].fill_between(df1['t'], roll_diff, np.repeat(pron_diff, n) ,label="Observed Pronation", alpha=0.3, where = roll_diff > np.repeat(pron_diff, n), interpolate=True)
    axs[0].legend()
    axs[0].set_xlabel("Time (s)")
    axs[0].set_ylabel("Difference in Angle (deg)")
    axs[0].set_title("Regions of Pronation")
    axs[0].legend()
    

    plt.show()


def plot_brian(df_tup, df_rest_tup, use_filter=True, scale_fsr=False):
    initial_airplane = get_initial_airplane(df_rest_tup)
    comp_filter(df_tup, airplane_initial=initial_airplane)

    # Split the data
    df0, df1, df2, df3, df4, df5, df6 = df_tup

    # Set up the figure
    style.use("ggplot")
    fig, axs = plt.subplots(4, 1, sharex=True)

    # Bus 0
    axs[0].scatter(df0["t"], df0["comp_pitch"], alpha=0.3)
    axs[0].plot(df0["t"], df0["comp_pitch"], alpha=0.3)

    # Bus 1
    axs[2].scatter(df1["t"], df1["comp_roll"], alpha=0.3)
    axs[2].plot(df1["t"], df1["comp_roll"], alpha=0.3)

    # Bus 2
    axs[1].scatter(df2["t"], df2["comp_roll"], alpha=0.3)
    axs[1].plot(df2["t"], df2["comp_roll"], alpha=0.3)

    # plot fsr data
    col = 'stand_val' if scale_fsr else 'val'
    fsr_tit = 'Scaled FSR' if scale_fsr else 'FSR (lbs)'
    axs[3].plot(df3["t"], df3[col], alpha=0.3, label="FSR 0")
    axs[3].plot(df4["t"], df4[col], alpha=0.3, label="FSR 1")
    axs[3].plot(df5["t"], df5[col], alpha=0.3, label="FSR 2")
    axs[3].plot(df6["t"], df6[col], alpha=0.3, label="FSR 3")
    axs[3].legend()

    # Customize the plot
    fig.suptitle(f"Airplane Angles and FSR Data over Time")
    # axs[3].set_xlabel("Time (s)")
    axs[0].set_ylabel("Angle (deg)")
    axs[1].set_ylabel("Angle (deg)")
    axs[2].set_ylabel("Angle (deg)")
    axs[2].set_xlabel("Time (s)")
    axs[3].set_ylabel(fsr_tit)
    axs[0].set_title("Laces - Pitch")
    axs[1].set_title("Lower Calf - Roll")
    axs[2].set_title("Heel - Roll")
    plt.show()

def main():
    # Grab the desired datafile and rest file from args
    if len(sys.argv) < 3:
        print("Data csv and Rest csv relatives paths must be specified")
        quit()
    
    work_dir = Path('.').absolute()
    data_path = work_dir / sys.argv[1]
    rest_path = work_dir / sys.argv[2]

    # if len(sys.argv) > 3:
        # air_ang = sys.argv[3]

    # Load in the Loomis data
    rest_df = pd.read_csv(rest_path, header=0)
    df = pd.read_csv(data_path, header=0)

    # Set up the dataframe for analysis
    df_tup = make_df_full(df)
    df_rest_tup = make_df_full(rest_df)

    plot_brian(df_tup, df_rest_tup, use_filter=True)

# Run main
if __name__ == "__main__":
    main()
