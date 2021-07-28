import json
import sys
import csv
import math

def main():
    json_file = sys.argv[1]

    sa_obj = {}
    with open(json_file) as f:
        sa_obj = json.load(f)

    outputs = []
    inputs = []

    for v in sa_obj["output_variables"]:
        outputs.append(v["variable_name"])

    for v in sa_obj["input_variables"]:
        identifier = v["variable_name"]
        name = identifier.split("::")[-2]
        inputs.append(name)

    table = [[""] * (len(inputs) + 1) for v in range(len(outputs) + 1)]

    for col in range(len(inputs)):
        table[0][col + 1] = inputs[col]

    for idx,_ in enumerate(outputs):
        si = sa_obj['sensitivity_indices'][idx]
        table[idx + 1][0] = outputs[idx]
        for i in range(len(si['S1'])):
            S1_val = "--" if si['S1'][i] is None or math.isnan(si['S1'][i]) else str(si['S1'][i]).split(".")[0] + "." + str(si['S1'][i]).split(".")[1][:3]
            S1_conf = "--" if si['S1_conf'][i] is None or math.isnan(si['S1_conf'][i]) else str(si['S1_conf'][i]).split(".")[0] + "." + str(si['S1_conf'][i]).split(".")[1][:3]

            table[idx + 1][i + 1] = f"{S1_val} +/- {S1_conf}"

    csv_file_name = f"{json_file.rsplit('.', 1)[0]}.csv"
    with open(csv_file_name, "w") as csv_file:
        csvWriter = csv.writer(csv_file, delimiter=',')
        csvWriter.writerows(table)

if __name__ == "__main__":
    main()
