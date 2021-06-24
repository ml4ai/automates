import json
import os
import csv
import math
import numpy as np
import pandas as pd

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_analysis.sensitivity import (
    SensitivityAnalyzer,
    SADependentVariable,
)

def run_sa(file, model_args, N):
    print("Reading soilt json file...")
    if not os.path.exists(file):
        raise Exception(f"Error: File '{file}' does not exist")
    (bounds, inputs, outputs) = model_args

    print("Parsing grfn json...")
    grfn = None
    try:
        grfn = GroundedFunctionNetwork.from_json(file)
    except Exception:
        raise Exception(f"Error: Unable to process grfn json file {file}")

    print("Running sensitivity analysis...")
    analyzer = SensitivityAnalyzer()
    Si_list = analyzer.Si_from_Sobol(N, grfn, bounds, inputs, outputs)
    model_inputs = [
        {
            "variable_name": k,
            "bounds": v,
        }
        for k, v in bounds.items()
    ]
    model_outputs = [{"variable_name": n} for n in outputs]
    results = {
        "grfn_uid": grfn.uid,
        "input_variables": model_inputs,
        "output_variables": model_outputs,
        "sensitivity_indices": [Si.to_dict() for Si in Si_list],
    }
    return results


def to_table(sa_obj):
    #     json_file = file

    #     sa_obj = {}
    #     with open(json_file) as f:
    #         sa_obj = json.load(f)

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

    for idx, _ in enumerate(outputs):
        si = sa_obj['sensitivity_indices'][idx]
        table[idx + 1][0] = outputs[idx]
        for i in range(len(si['S1'])):
            S1_val = "--" if si['S1'][i] is None or math.isnan(si['S1'][i]) else str(si['S1'][i]).split(".")[0] + "." + \
                                                                                 str(si['S1'][i]).split(".")[1][:3]
            S1_conf = "--" if si['S1_conf'][i] is None or math.isnan(si['S1_conf'][i]) else \
            str(si['S1_conf'][i]).split(".")[0] + "." + str(si['S1_conf'][i]).split(".")[1][:3]

            table[idx + 1][i + 1] = f"{S1_val} +/- {S1_conf}"
    #     return table

    #     csv_file_name = f"{json_file.rsplit('.', 1)[0]}.csv"
    #     with open(csv_file_name, "w") as csv_file:
    #         csvWriter = csv.writer(csv_file, delimiter=',')
    #         csvWriter.writerows(table)

    old_table = np.array(table)
    col_names = old_table[0, :]
    row_names = old_table[:, 0]

    new_table = old_table[1:len(row_names), 1:len(col_names)]
    col_names = np.delete(col_names, 0)
    row_names = np.delete(row_names, 0)

    return pd.DataFrame(new_table, columns=col_names, index=row_names)