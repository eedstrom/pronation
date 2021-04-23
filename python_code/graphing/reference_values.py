#!/usr/bin/env python3
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
from pathlib import Path
from all_together import make_df_full, plot_air_and_fsr_with_comp, plot_airplane, comp_filter, get_initial_airplane


def plot_airplane_with_avg(df_tup, use_filter=None):
    # Split the data
    df0, df1, df2, *_ = df_tup

    # Set up the figure
    style.use("ggplot")
    fig, axs = plt.subplots(3, 1, sharex=True)
    
    # Get the size of each df
    n0 = df0.shape[0]
    n1 = df1.shape[0]
    n2 = df2.shape[0]
    
    # Set the column to be plotted to be non filtered
    pre = ""
    # Run the comp (or not)
    if use_filter is not None and use_filter in ('comp', 'integral'):
        # Set the initial values to be the initial values from the dataset
        initial_airplane = { "roll": [], "pitch": [], "yaw": [] }
        for df_iter in [df0, df1, df2]:
            initial_airplane["roll"].append(df_iter["roll"].iloc[0:15].mean())
            initial_airplane["pitch"].append(df_iter["pitch"].iloc[0:15].mean())
            initial_airplane["yaw"].append(df_iter["yaw"].iloc[0:15].mean())

        # Run the use_filter
        comp_filter(df_tup, airplane_initial=initial_airplane)
        pre = use_filter + "_"
    
    # roll
    roll_col = pre + 'roll'
    axs[0].scatter(df0["t"], df0[roll_col], label="Laces", alpha=0.1)
    axs[0].scatter(df1["t"], df1[roll_col], label="Heel", alpha=0.1)
    axs[0].scatter(df2["t"], df2[roll_col], label="Shin", alpha=0.1)
    axs[0].plot(df0["t"], np.repeat(df0[roll_col].mean(), n0))
    axs[0].plot(df1["t"], np.repeat(df1[roll_col].mean(), n1))
    axs[0].plot(df2["t"], np.repeat(df2[roll_col].mean(), n2))
    axs[0].legend()

    # pitch
    pitch_col = pre + 'pitch'
    axs[1].scatter(df0["t"], df0[pitch_col], label="Laces", alpha=0.3)
    axs[1].scatter(df1["t"], df1[pitch_col], label="Heel", alpha=0.3)
    axs[1].scatter(df2["t"], df2[pitch_col], label="Shin", alpha=0.3)
    axs[1].plot(df0["t"], np.repeat(df0[pitch_col].mean(), n0))
    axs[1].plot(df1["t"], np.repeat(df1[pitch_col].mean(), n1))
    axs[1].plot(df2["t"], np.repeat(df2[pitch_col].mean(), n2))
    axs[1].legend()

    # yaw
    yaw_col = pre + 'yaw'
    axs[2].scatter(df0["t"], df0[yaw_col], label="Laces", alpha=0.3)
    axs[2].scatter(df1["t"], df1[yaw_col], label="Heel", alpha=0.3)
    axs[2].scatter(df2["t"], df2[yaw_col], label="Shin", alpha=0.3)
    axs[2].plot(df0["t"], np.repeat(df0[yaw_col].mean(), n0), alpha=0.3)
    axs[2].plot(df1["t"], np.repeat(df1[yaw_col].mean(), n1), alpha=0.3)
    axs[2].plot(df2["t"], np.repeat(df2[yaw_col].mean(), n2), alpha=0.3)
    axs[2].legend()

    # Customize the plot
    fig.suptitle("Angles by Bus Line over Time")
    axs[2].set_xlabel("Time (s)")
    axs[0].set_ylabel("Angle (deg)")
    axs[1].set_ylabel("Angle (deg)")
    axs[2].set_ylabel("Angle (deg)")
    axs[0].set_title(pre + "Roll")
    axs[1].set_title(pre + "Pitch")
    axs[2].set_title(pre + "Yaw")
    plt.show()

def get_summary(df_tup, skip=0):
    df0, df1, df2, *_ = df_tup
    
    # Create a container for the averages
    avg_dict = {'roll': [], 'pitch': [], 'yaw': []}
    var_dict = {'roll': [], 'pitch': [], 'yaw': []}
    n = df0.shape[0]

    if isinstance(skip, str):
        skip = int(n * float(skip.replace("%", "").replace(".", "")) / 100)

    for df_iter in (df0, df1, df2):
        avg_dict['roll'].append(df_iter['roll'].iloc[skip : n - skip + 1].mean())
        avg_dict['pitch'].append(df_iter['pitch'].iloc[skip : n - skip + 1].mean())
        avg_dict['yaw'].append(df_iter['yaw'].iloc[skip : n - skip + 1].mean())
        var_dict['roll'].append(df_iter['roll'].iloc[skip : n - skip + 1].var())
        var_dict['pitch'].append(df_iter['pitch'].iloc[skip : n - skip + 1].var())
        var_dict['yaw'].append(df_iter['yaw'].iloc[skip : n - skip + 1].var())

    return avg_dict, var_dict

def plot_air_with_err(df_tup, pron_mean, sup_mean):
    # Split the data
    df0, df1, df2, *_ = df_tup

    # Set up the figure
    style.use("ggplot")
    fig, axs = plt.subplots(3, 3, sharex=True)
    
    # Get the size of each df
    n = df0.shape[0]
    
    # Run the comp 
    initial_airplane = {'roll': [], 'pitch': [], 'yaw': []} 
    for df_iter in (df0, df1, df2):
        initial_airplane['roll'].append(df_iter['roll'].iloc[0])
        initial_airplane['pitch'].append(df_iter['pitch'].iloc[0])
        initial_airplane['yaw'].append(df_iter['yaw'].iloc[0])

    # Run the use_filter
    comp_filter(df_tup, airplane_initial=initial_airplane)
    
    # Create the plots
    loc = ["Laces", "Heel", "Shin"]
    for col, df_iter in enumerate((df0, df1, df2)):
        for row, air in enumerate(("roll", "pitch", "yaw")):
            axs[row][col].plot(df_iter["t"], df_iter[air], alpha=0.3, label = "Observed")
            axs[row][col].plot(df_iter["t"], np.repeat(pron_mean[air][col], n), label = "Pronation Range")
            axs[row][col].plot(df_iter["t"], np.repeat(sup_mean[air][col], n), label = "Supination Range")
            axs[row][col].legend()

            if col == 0:
                axs[row][col].set_ylabel(f'{air.title()}\n(Deg)')
        axs[0][col].set_title(loc[col])
        axs[row][col].set_xlabel("Time(s)")

    # Customize the plot
    fig.suptitle("Airplane by Location")
    plt.show()

def plot_air_with_ref(df_tup, df_rest, df_pron, df_sup):
    # Split the data
    df0, df1, df2, *_ = df_tup

    # Set up the figure
    style.use("ggplot")
    fig, axs = plt.subplots(3, 3, sharex=True)
    
    # Get the size of each df
    n = df0.shape[0]
    
    initial_airplane = airplane_initial(rest_df)
    
    # Run the use_filter
    comp_filter(df_tup, airplane_initial=initial_airplane)
    
    # Create the plots
    loc = ["Laces", "Heel", "Shin"]
    for col, df_iter in enumerate((df0, df1, df2)):
        for row, air in enumerate(("roll", "pitch", "yaw")):
            axs[row][col].plot(df_iter["t"], df_iter[air], alpha=0.3, label = "Observed")
            axs[row][col].plot(df_iter["t"], df_pron, label = "Pronation Range")
            axs[row][col].plot(df_iter["t"], df_sup, label = "Supination Range")
            axs[row][col].legend()

            if col == 0:
                axs[row][col].set_ylabel(f'{air.title()}\n(Deg)')
        axs[0][col].set_title(loc[col])
        axs[row][col].set_xlabel("Time(s)")

    # Customize the plot
    fig.suptitle("Airplane by Location")
    plt.show()

    

def main():
    # # Set initial filter to None
    # uf = None

    skip = 0
    # Check for filetype arg
    if len(sys.argv) < 2:
        print('Need a file path and optionally a skip number')
        quit()
    if len(sys.argv) >= 3:
        try:
            skip = int(sys.argv[2])

        except ValueError:
            skip = sys.argv[2]

    # Load file
    filepath = Path('.').absolute() / sys.argv[1]
    sup_path = Path('python_code/data/wilma_intentional/standing_sup.csv').absolute()
    pron_path = Path('python_code/data/wilma_intentional/standing_pron.csv').absolute()

    # Read as csv
    df_sup = pd.read_csv(sup_path, index_col=False,header=0)
    df_pron = pd.read_csv(pron_path, index_col=False,header=0)
    df = pd.read_csv(filepath, index_col=False, header=0)

    # Remove info row
    # info_row = df.loc[df['id'] == -1]
    df = df.drop(index = 0)
    df = df.astype({"my": "float64", "mz": "float64"})
    df_tup = make_df_full(df)

    df_pron = df_pron.drop(index = 0)
    df_pron = df_pron.astype({"my": "float64", "mz": "float64"})
    df_pron = make_df_full(df_pron)
    
    df_sup = df_sup.drop(index = 0)
    df_sup = df_sup.astype({"my": "float64", "mz": "float64"})
    df_sup = make_df_full(df_sup)

if __name__ == '__main__':
    main()
