#!/usr/bin/env python3
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import pandas as pd
from pathlib import Path
import sys

from all_together import make_df_full, comp_filter, get_initial_airplane, _get_idxs

def plot_brian(df_tup, df_rest_tup, use_filter=True, scale_fsr=False, chosen_style='default'):
    initial_airplane = get_initial_airplane(df_rest_tup)
    comp_filter(df_tup, airplane_initial=initial_airplane)

    # Split the data
    df0, df1, df2, df3, df4, df5, df6 = df_tup

    # Set up the figure
    style.use(chosen_style)
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
    axs[3].plot(df3["t"], df3[col], alpha=0.8, label="FSR 0")
    # axs[3].scatter(df3["t"], df3[col], alpha=0.3)
    axs[3].plot(df4["t"], df4[col], alpha=0.8, label="FSR 1")
    # axs[3].scatter(df4["t"], df4[col], alpha=0.3)
    axs[3].plot(df5["t"], df5[col], alpha=0.8, label="FSR 2")
    # axs[3].scatter(df5["t"], df5[col], alpha=0.3)
    axs[3].plot(df6["t"], df6[col], alpha=0.8, label="FSR 3")
    # axs[3].scatter(df6["t"], df6[col], alpha=0.3)
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
    
    # Get the step indicies
    heel_hits = _get_idxs(df_tup, df_rest_tup)

    # Reset all the indecies
    for df_iter in df_tup:
        df_iter.reset_index(drop=True, inplace=True)

    # Load in the dataframes
    df0, df1, df2, df3, df4, df5, df6 = df_tup

    # Plot a vertical line for each step
    step_times = df3[df3.index.isin(heel_hits)]['t'].to_numpy()

    # Bus 0
    axs[0].vlines(x=step_times, ymin=df0['comp_pitch'].min(), ymax=df0['comp_pitch'].max(), alpha=0.8, colors='violet', linestyles='dashed')

    # Bus 1
    axs[2].vlines(x=step_times, ymin=df1['comp_roll'].min(), ymax=df1['comp_roll'].max(), alpha=0.8, colors='violet', linestyles='dashed')

    # Bus 2
    axs[1].vlines(x=step_times, ymin=df2['comp_roll'].min(), ymax=df2['comp_roll'].max(), alpha=0.8, colors='violet', linestyles='dashed')
    
    # FSRS
    axs[3].vlines(x=step_times, ymin=0, ymax=max(df3[col].max(), df4[col].max(), df5[col].max(), df6[col].max()), alpha=0.5, colors='violet', linestyles='dashed')
    plt.show()


def main():
    # Grab the desired datafile and rest file from args
    if len(sys.argv) < 3:
        print("Data csv and Rest csv relatives paths must be specified")
        quit()
    
    WORKDIR = Path('.').absolute()
    DATAPATH = WORKDIR / sys.argv[1]
    RESTPATH = WORKDIR / sys.argv[2]

    # Load in the Loomis data
    rest_df = pd.read_csv(RESTPATH, header=0)
    df = pd.read_csv(DATAPATH, header=0)

    # Set up the dataframe for analysis
    df_tup = make_df_full(df)
    df_rest_tup = make_df_full(rest_df)
    
    plot_brian(df_tup, df_rest_tup, use_filter=True, chosen_style='seaborn-bright')


if __name__ == '__main__':
    main()
