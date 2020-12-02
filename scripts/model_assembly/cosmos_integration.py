"""
Purpose: Process all parquet files in a directory into JSON data.
"""
import pandas as pd
import json
import sys
import os

from tqdm import tqdm


def main():
    parquet_file_folder = sys.argv[1]

    parquet_files = os.listdir(parquet_file_folder)

    for filename in tqdm(parquet_files, desc="Converting parquets"):
        if filename.endswith(".parquet"):
            parquet_filepath = os.path.join(parquet_file_folder, filename)
            parquet_df = pd.read_parquet(parquet_filepath)
            parquet_json = parquet_df.to_json()
            parquet_data = json.loads(parquet_json)

            parquet_data_keys = list(parquet_data.keys())
            num_data_rows = max(
                [int(k) for k in parquet_data[parquet_data_keys[0]]]
            )

            row_order_parquet_data = [dict() for i in range(num_data_rows + 1)]
            for field_key, row_data in parquet_data.items():
                for row_idx, datum in row_data.items():
                    row_idx_num = int(row_idx)
                    row_order_parquet_data[row_idx_num][field_key] = datum

            parquet_json_filepath = parquet_filepath.replace(
                ".parquet", ".json"
            )
            json.dump(row_order_parquet_data, open(parquet_json_filepath, "w"))


if __name__ == "__main__":
    main()
