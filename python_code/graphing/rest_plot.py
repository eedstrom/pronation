#!/usr/bin/env python3

# Import libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import style

# Import the rest data
df = pd.read_csv("data/rest_data.csv",
                 names=["id", "t", "dt", "ax", "ay", "az",
                        "gx", "gy", "gz", "mx", "my", "mz",
                        "compx", "kalx", "compy", "kaly"])

# # Change to standard SI units
df["t"] = df["t"] / 1000
df["dt"] = df["dt"] / 1000
df["ax"] = df["ax"] / 1000
df["ay"] = df["ay"] / 1000
df["az"] = df["az"] / 1000
df["gx"] = df["gx"] / 10
df["gy"] = df["gy"] / 10
df["gz"] = df["gz"] / 10

# Separate by id
df0 = df[df["id"] == 0]
df1 = df[df["id"] == 1]
df2 = df[df["id"] == 2]


def plot_acc():
    # Plot accelerations over time by bus line
    style.use("ggplot")
    fig, axs = plt.subplots(3, 1, sharex=True)

    # ax
    axs[0].scatter(df0["t"], df0["ax"], label="Bus 0", alpha=0.3)
    axs[0].scatter(df1["t"], df1["ax"], label="Bus 1", alpha=0.3)
    axs[0].scatter(df2["t"], df2["ax"], label="Bus 2", alpha=0.3)
    axs[0].legend()

    # ay
    axs[1].scatter(df0["t"], df0["ay"], label="Bus 0", alpha=0.3)
    axs[1].scatter(df1["t"], df1["ay"], label="Bus 1", alpha=0.3)
    axs[1].scatter(df2["t"], df2["ay"], label="Bus 2", alpha=0.3)
    axs[1].legend()

    # az
    axs[2].scatter(df0["t"], df0["az"], label="Bus 0", alpha=0.3)
    axs[2].scatter(df1["t"], df1["az"], label="Bus 1", alpha=0.3)
    axs[2].scatter(df2["t"], df2["az"], label="Bus 2", alpha=0.3)
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


def plot_gyro(df, bus_line):
    style.use("ggplot")

    fig, axs = plt.subplots(3, 1, sharex=True)

    axs[0].scatter(df["t"], df["gx"], alpha=0.3)
    axs[0].plot(df["t"], df["gx"], label="gx", alpha=0.3)

    axs[1].scatter(df["t"], df["gy"], alpha=0.3)
    axs[1].plot(df["t"], df["gy"], label="gy", alpha=0.3)

    axs[2].scatter(df["t"], df["gz"], alpha=0.3)
    axs[2].plot(df["t"], df["gz"], label="gz", alpha=0.3)

    # Customize the plot
    fig.suptitle(f"Change in angles without Kalman Filter for Bus {bus_line}")
    axs[0].set_xlabel("Time (s)")
    axs[1].set_xlabel("Time (s)")
    axs[2].set_xlabel("Time (s)")
    axs[0].set_ylabel("Angle Rate (deg/s)")
    axs[1].set_ylabel("Angle Rate (deg/s)")
    axs[2].set_ylabel("Angle Rate (deg/s)")
    axs[0].set_title("Gyroscopic X")
    axs[1].set_title("Gyroscopic Y")
    axs[2].set_title("Gyroscopic Z")

    plt.show()


def summarize(df, bus):
    summary_dict = {}
    for col in df.columns:
        if col in ("id", "t", "compx", "compy", "kalx", "kaly"):
            continue
        summary_dict[col] = [df[col].mean(), df[col].std(),
                             df[col].std() / df[col].mean()]

    # Make a pandas dataframe for easy display
    results = pd.DataFrame.from_dict(summary_dict).T
    results.columns = (f"Mean ({bus})", f"STD ({bus})", f"CV ({bus})")

    return results


def rest_summary():
    # Summarize each bus line
    df0_summary = summarize(df0, 0)
    df1_summary = summarize(df1, 1)
    df2_summary = summarize(df2, 2)

    # Merge the data back into one dataframe
    df_summary = pd.concat([df0_summary, df1_summary, df2_summary], axis=1)
    df_summary = np.round(df_summary, 3)

    # Combine the tables

    # Write the output to an html table
    with open("tables/summary_rest.html", "w") as f:
        f.write(df_summary.to_html())


plot_gyro(df2, 2)
