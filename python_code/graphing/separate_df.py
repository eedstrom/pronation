import sys
from pathlib import Path
import pandas as pd

# First arg to file is relative path to combined datafile
# Second arg to file is relative path to where to save them


def separate_files(df, save_path):
    # Separate the file using the headers
    idxs = df[df["id"] == -1].index.to_numpy()

    df_list = []

    for i in range(1, len(idxs)):
        df_list.append(df[idxs[i - 1]: idxs[i]])
    df_list.append(df[idxs[-1]:])

    # Write to csv
    for i in range(len(df_list)):
        df_list[i].to_csv(
            f'{save_path}/df{i}.csv', index=False)

def main():
    # Check for arguments passed
    if len(sys.argv) < 3:
        print('Need a df file and a path to save the new files.')
        quit()
    
    # Load in the data
    names = ["id", "t", "dt", "ax", "ay", "az",
             "gx", "gy", "gz", "mx", "my", "mz"]

    df_path = Path('.').absolute() / sys.argv[1]
    df = pd.read_csv(df_path, index_col = False, names=names)

    # Create the path to save the files
    save_path = Path('.').absolute() / sys.argv[2]
    save_path.mkdir(parents=True, exist_ok=True)
    
    # Separate Files
    separate_files(df, save_path)

    print(f'Files saved to `{save_path}`!')

if __name__ == '__main__':
    main()
