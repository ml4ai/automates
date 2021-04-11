import sys
import json

import pandas as pd


def main():
    parquet_filename = sys.argv[1]
    json_filename = parquet_filename.replace(".parquet", ".json")
    print(json_filename)

    parquet_df = pd.read_parquet(parquet_filename)
    parquet_json = parquet_df.to_json()
    parquet_data = json.loads(parquet_json)
    print(parquet_data)
    json.dump(parquet_data, open(json_filename, "w"))


if __name__ == "__main__":
    main()
