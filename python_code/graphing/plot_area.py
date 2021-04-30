#!/usr/bin/env python3
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import pandas as pd
from pathlib import Path
import sys
from all_together import make_df_full, plot_area


def main():
    if len(sys.argv) < 3:
        raise Exception('Required filenames missing, data for plotting and rest data')

    # Specify pathnames
    work_dir = Path('.').absolute()
    data_path = work_dir / sys.argv[1]
    rest_path = work_dir / sys.argv[2]

    # Load in the Loomis data
    rest_df = pd.read_csv(rest_path, header=0)
    df = pd.read_csv(data_path, header=0)

    # Set up the dataframe for analysis
    df_tup = make_df_full(df)
    df_rest_tup = make_df_full(rest_df)

    # Plot the area
    plot_area(df_tup, df_rest_tup) 

if __name__ == '__main__':
    main()
