import os
import csv
import shutil


def move_sample_data(temp_dir, results_dir):

    if not os.path.exists(results_dir):
        os.makedirs(results_dir, exist_ok=True)

    samples_csv = f"{temp_dir}/validate-results.csv"
    if not os.path.exists(samples_csv):
        print(f"Error: validate-results.csv does not exist under {temp_dir}")
        return

    csv_file = open(samples_csv)
    csvreader = csv.reader(csv_file)

    for sample in csvreader:
        if sample[1] == "SUCCESS":
            shutil.move(f"{temp_dir}/results/{sample[0]}", f"{results_dir}/{sample[0]}")
