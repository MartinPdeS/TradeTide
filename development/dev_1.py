import pandas as pd

filename = "/Users/martinpdes/Desktop/GitProject/TradeTide/TradeTide/data/jpy_usd/2023/data.csv"

import pandas as pd

# Step 1: Read the file and find the line where the actual data starts
input_file = filename
with open(input_file, "r") as f:
    lines = f.readlines()

# Identify where the data starts (after '#DATA')
data_start_index = next(i for i, line in enumerate(lines) if line.strip() == "#DATA") + 1

# Step 2: Load only the data into pandas
from io import StringIO
data_str = ''.join(lines[data_start_index:])
df = pd.read_csv(StringIO(data_str))

# Step 3: Add a new column (example: average price)
df["spread"] = 0

# Step 4: Save back the file, optionally including the metadata
output_file = filename
with open(output_file, "w") as f:
    # Write original metadata lines
    f.writelines(lines[:data_start_index])
    # Write modified DataFrame
    df.to_csv(f, index=False)
