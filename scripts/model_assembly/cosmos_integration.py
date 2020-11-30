import pandas as pd
import json
import sys

## assuming parquet file with two rows and three columns:
## foo bar baz
## 1   2   3
## 4   5   6

parquet_filepath = sys.argv[1]
print(parquet_filepath)
df = pd.read_parquet(parquet_filepath)
print(df.head())
print(df.columns)
print(df["dataset_id"][0])
print(type(df["dataset_id"][0]))
