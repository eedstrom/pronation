import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.signal import find_peaks
import sys

# Self imports
from all_together import make_df_full

def extract_steps(df_tup, df_rest_tup, standardize_fsr=False):
    """Plots the fsr data and extracts individual steps"""
    # Get dataframes by bus line
    *_, df3, df4, df5, df6 = df_tup
    df3 = df3.reset_index(drop=True) 
    df4 = df4.reset_index(drop=True) 
    df5 = df5.reset_index(drop=True) 
    df6 = df6.reset_index(drop=True) 

    # Calculate the peaks for each dataframe
    idx3 = find_peaks(df3['val'])
    idx4 = find_peaks(df4['val'])
    idx5 = find_peaks(df5['val'])
    idx6 = find_peaks(df6['val'])
    
    # Get the peaks ready to be plotted
    print(df3.head())
    # Set up the figure
    fig, axs = plt.subplots(4, 1, sharex=True)
    
    # plot fsr data
    col = 'stand_val' if standardize_fsr else 'val'

    axs[0].scatter(df3["t"], df3[col], label=0, alpha=0.3)
    axs[0].plot(df3["t"], df3[col], alpha=0.3)
    axs[0].legend()
    axs[0].set_xlabel("Time (s)")
    axs[0].set_ylabel("Force (lbs)")

    axs[1].scatter(df4["t"], df4[col], label=1, alpha=0.3)
    axs[1].plot(df4["t"], df4[col], alpha=0.3)
    axs[1].legend()
    axs[1].set_xlabel("Time (s)")
    axs[1].set_ylabel("Force (lbs)")

    axs[2].scatter(df5["t"], df5[col], label=2, alpha=0.3)
    axs[2].plot(df5["t"], df5[col], alpha=0.3)
    axs[2].legend()
    axs[2].set_xlabel("Time (s)")
    axs[2].set_ylabel("Force (lbs)")

    axs[3].scatter(df6["t"], df6[col], label=3, alpha=0.3)
    axs[3].plot(df6["t"], df6[col], alpha=0.3)
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
