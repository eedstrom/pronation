#! usr/bin.env python3

import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd

# Load in all 3 datasets from Loomis
names=["id", "t", "dt", "ax", "ay", "az",
        "gx", "gy", "gz", "mx", "my", "mz"]

df_quiet = pd.read_csv("data/QuietStance.CSV", names=names)
df_walk = pd.read_csv("data/Walking.CSV", names=names)
df_run = pd.read_csv("data/Running.CSV", names=names)

def _clean_df_acc(df):
    """ Standardizes the units"""
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


# Clean the dataframe
df_quiet_tup = split_df(df_quiet)
df_walk_tup = split_df(df_walk)
df_run_tup = split_df(df_run)

# Plot the acceleration
plot_acc(df_quiet_tup)
plot_acc(df_walk_tup)
plot_acc(df_run_tup)
