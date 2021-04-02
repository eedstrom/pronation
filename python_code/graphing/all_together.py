#! usr/bin.env python3

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import style
from numpy.lib.shape_base import split
import pandas as pd

# Load in all 3 datasets from Loomis
names = ["id", "t", "dt", "ax", "ay", "az",
         "gx", "gy", "gz", "mx", "my", "mz"]

# Load in the Loomis data
df = pd.read_csv("data/3.31_Loomis_Data_Ind/df1.csv")


def separate_files(df):
    # Separate the file using the headers
    idxs = df[df["id"] == -1].index.to_numpy()

    df_list = []

    for i in range(1, len(idxs)):
        df_list.append(df[idxs[i - 1]: idxs[i]])
    df_list.append(df[idxs[-1]:])

    # Write to csv
    for i in range(len(df_list)):
        df_list[i].to_csv(
            f'data/3.31_Loomis_Data_Ind/df{i}.csv', index=False, names=False)


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

    # Reset the time variable for each dataframe
    # df0["t"] = df0["t"] - df0["t"].min()
    # df1["t"] = df1["t"] - df1["t"].min()
    # df2["t"] = df2["t"] - df2["t"].min()

    return (df0, df1, df2, df3, df4, df5, df6)


def plot_acc(df_ind):
    # Clean and split the data
    df_tup = split_df(df_ind)

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


def plot_airplane(df_ind):
    # Clean and split the data
    df_tup = split_df(df_ind)

    # Plot accelerations over time by bus line
    style.use("ggplot")
    fig, axs = plt.subplots(3, 1, sharex=True)

    # Get dataframes from tuple
    df0, df1, df2, *_ = df_tup

    # Calculate roll, pitch, and yaw for all 3
    for d in [df0, df1, df2]:
        d["roll"] = np.arctan2(d["ay"], d["az"]) * 180 / np.pi
        d["pitch"] = np.arctan2(-1 * d["ax"],
                                np.sqrt(d["ay"] ** 2 + d["az"] ** 2)) * 180 / np.pi
        bfy = d["mz"] * np.sin(d["roll"]) - d["my"] * np.cos(d["roll"])
        # bfx = d["mx"] * np.cos(d["pitch"]) + d["my"] * \
        #     np.sin(d["pitch"]) * np.sin(d["roll"]) + d["mz"] * \
        #     np.sin(d["pitch"]) * np.cos(d["roll"])
        bfx = 0

        d["yaw"] = np.arctan(-bfy, bfx) * 180 / np.pi

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


plot_airplane(df)
