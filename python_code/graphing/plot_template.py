#! python3

# Import libraries
from matplotlib import style
import matplotlib.pyplot as plt
import pandas as pd

# # Read csv
df = pd.read_csv("School/accelkalmandata.CSV",
                 names=["bus", "t", "dt", "ax", "ay", "az",
                        "gx", "gy", "gz", "mx", "my", "mz",
                        "compx", "kalx", "compy", "kaly"])

# # Change to standard SI units
df["t"] = df["t"] / 1000
df["ax"] = df["ax"] / 1000
df["ay"] = df["ay"] / 1000
df["az"] = df["az"] / 1000
df["gx"] = df["gx"] / 10
df["gy"] = df["gy"] / 10
df["gz"] = df["gz"] / 10

# Separate by bus line
df0 = df[df["bus"] == 0]
df1 = df[df["bus"] == 1]
df2 = df[df["bus"] == 2]


def plot_gyro(df, bus_line):
    style.use("ggplot")

    fig, axs = plt.subplots(2, 1, sharex=True)

    axs[0].scatter(df["t"], df["compx"], alpha=0.3)
    axs[0].plot(df["t"], df["compx"], label="comp_x", alpha=0.3)
    axs[0].scatter(df["t"], df["kalx"], alpha=0.3)
    axs[0].plot(df["t"], df["kalx"], label="kal_x", alpha=0.3)
    axs[0].legend()

    axs[1].scatter(df["t"], df["compy"], alpha=0.3)
    axs[1].plot(df["t"], df["compy"], label="comp_y", alpha=0.3)
    axs[1].scatter(df["t"], df["kaly"], alpha=0.3)
    axs[1].plot(df["t"], df["kaly"], label="kal_y", alpha=0.3)
    axs[1].legend()

    # Customize the plot
    fig.suptitle(f"Angles with Kalman Filter for Bus {bus_line}")
    axs[0].set_xlabel("Time (s)")
    axs[1].set_xlabel("Time (s)")
    axs[0].set_ylabel("Angle (deg)")
    axs[1].set_ylabel("Angle (deg)")
    axs[0].set_title("Gyroscopic X")
    axs[1].set_title("Gyroscopic Y")

    plt.show()


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


plot_gyro(df0, 0)
