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

def run_sa(file, model_args, N, compute_S2):
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
    Si_list = analyzer.Si_from_Sobol(N, grfn, bounds, inputs, outputs, calc_2nd=compute_S2)
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


def to_table(csv_table):
    old_table = np.array(csv_table)
    col_names = old_table[0, :]
    row_names = old_table[:, 0]

    new_table = old_table[1:len(row_names), 1:len(col_names)]
    col_names = np.delete(col_names, 0)
    row_names = np.delete(row_names, 0)

    return pd.DataFrame(new_table, columns=col_names, index=row_names)


def pd_tables(sa_obj, compute_S2):
    #     json_file = file

    #     sa_obj = {}
    #     with open(json_file) as f:
    #         sa_obj = json.load(f)

    outputs = []
    inputs = []

    #     for v in sa_obj["output_variables"]:
    #         outputs.append(v["variable_name"])

    for i in range(len(sa_obj["sensitivity_indices"])):
        outputs.append(f"v{i + 1}")

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
            S1_val = "--" if si['S1'][i] is None or math.isnan(si['S1'][i]) else round(si['S1'][i], 3)
            S1_conf = "--" if si['S1_conf'][i] is None or math.isnan(si['S1_conf'][i]) else round(si['S1_conf'][i], 3)

            table[idx + 1][i + 1] = f"{S1_val} +/- {S1_conf}"

    # ST Table
    st_table = [[""] * (len(inputs) + 1) for v in range(len(outputs) + 1)]

    for col in range(len(inputs)):
        st_table[0][col + 1] = inputs[col]

    for idx, _ in enumerate(outputs):
        si = sa_obj['sensitivity_indices'][idx]
        st_table[idx + 1][0] = outputs[idx]
        for i in range(len(si['ST'])):
            ST_val = "--" if si['ST'][i] is None or math.isnan(si['ST'][i]) else round(si['ST'][i], 3)
            ST_conf = "--" if si['ST_conf'][i] is None or math.isnan(si['ST_conf'][i]) else round(si['ST_conf'][i], 3)

            st_table[idx + 1][i + 1] = f"{ST_val} +/- {ST_conf}"

    # S2 Table
    if compute_S2:
        n_inputs = len(inputs)
        n_cols = math.comb(n_inputs, 2)
        s2_table = [[""] * (n_cols + 1) for v in range(len(outputs) + 1)]
        s2_columns = [""]
        for i in range(len(inputs)):
            for j in range(i + 1, n_inputs):
                s2_columns.append(f"{inputs[i]}, {inputs[j]}")
        s2_table[0] = s2_columns

        for idx, _ in enumerate(outputs):
            si = sa_obj['sensitivity_indices'][idx]
            s2_raw = si['S2']
            s2_raw_conf = si['S2_conf']
            s2_trimmed = [outputs[idx]]
            for i in range(n_inputs):
                for j in range(i + 1, n_inputs):
                    s2_val = "--" if s2_raw[i][j] is None or math.isnan(s2_raw[i][j]) else round(s2_raw[i][j], 3)
                    s2_conf = "--" if s2_raw_conf[i][j] is None or math.isnan(s2_raw_conf[i][j]) else round(
                        s2_raw_conf[i][j], 3)
                    s2_trimmed.append(f"{s2_val} +/- {s2_conf}")
            s2_table[idx + 1] = s2_trimmed
        return (to_table(table), to_table(s2_table), to_table(st_table))
    return (to_table(table), to_table(st_table))