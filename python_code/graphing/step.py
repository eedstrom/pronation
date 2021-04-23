import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.signal import find_peaks
import sys

# Self imports
from all_together import make_df_full

def extract_steps(df_tup, df_rest_tup, p=0.25, standardize_fsr=False):
    """Plots the fsr data and extracts individual steps"""
    # Get dataframes by bus line
    *_, df3, df4, df5, df6 = df_tup
    df3 = df3.reset_index(drop=True) 
    df4 = df4.reset_index(drop=True) 
    df5 = df5.reset_index(drop=True) 
    df6 = df6.reset_index(drop=True)

    # Calculate the heights for peak analysis
    height3 = df3['val'].max() * p
    height4 = df4['val'].max() * p
    height5 = df5['val'].max() * p
    height6 = df6['val'].max() * p

    # Calculate the peaks for each dataframe
    idx3 = find_peaks(df3['val'], height=height3)[0]
    idx4 = find_peaks(df4['val'], height=height4)[0]
    idx5 = find_peaks(df5['val'], height=height5)[0]
    idx6 = find_peaks(df6['val'], height=height6)[0]
    
    # Peak dfs for plotting
    peak3 = df3[df3.index.isin(idx3)]
    peak4 = df4[df4.index.isin(idx4)]
    peak5 = df5[df5.index.isin(idx5)]
    peak6 = df6[df6.index.isin(idx6)]

    # Set up the figure
    fig, axs = plt.subplots(4, 1, sharex=True)
    
    # plot fsr data
    col = 'stand_val' if standardize_fsr else 'val'

    axs[0].scatter(peak3['t'], peak3[col], alpha=0.3, label='Peaks', c='orange')
    axs[0].plot(df3["t"], df3[col], alpha=0.3, label='Observed Values')
    axs[0].legend()
    axs[0].set_xlabel("Time (s)")
    axs[0].set_ylabel("Force (lbs)")

    axs[1].scatter(peak4['t'], peak4[col], alpha=0.3, label='Peaks', c='orange')
    axs[1].plot(df4["t"], df4[col], alpha=0.3, label='Observed Values')
    axs[1].legend()
    axs[1].set_xlabel("Time (s)")
    axs[1].set_ylabel("Force (lbs)")

    axs[2].scatter(peak5['t'], peak5[col], alpha=0.3, label='Peaks', c='orange')
    axs[2].plot(df5["t"], df5[col], alpha=0.3, label='Observed Values')
    axs[2].legend()
    axs[2].set_xlabel("Time (s)")
    axs[2].set_ylabel("Force (lbs)")

    axs[3].scatter(peak6['t'], peak6[col], alpha=0.3, label='Peaks', c='orange')
    axs[3].plot(df6["t"], df6[col], alpha=0.3, label='Observed Values')
    axs[3].legend()
    axs[3].set_xlabel("Time (s)")
    axs[3].set_ylabel("Force (lbs)")
    
    # Final customization
    fig.suptitle("FSR Readings over Time")

    # Show the figure
    plt.show()
    

def main():
    # Get system args
    if (len(sys.argv)) < 3:
        raise Exception("Path to data and path to rest data must be provided")
    
    # Define paths to the data
    WORKDIR = Path('.')
    DATAPATH = WORKDIR / sys.argv[1]
    RESTPATH = WORKDIR / sys.argv[2]
    
    # Load in the data
    rest_df = pd.read_csv(RESTPATH, header=0)
    df = pd.read_csv(DATAPATH, header=0)

    # Clean dataframes
    df_rest_tup = make_df_full(rest_df)
    df_tup = make_df_full(df)

    # Call function
    extract_steps(df_tup, df_rest_tup)


if __name__ == '__main__':
    main()
