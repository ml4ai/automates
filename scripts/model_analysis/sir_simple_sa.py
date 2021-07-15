import json
import sys
import os
import math

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_analysis.sensitivity import (
    SensitivityAnalyzer,
    SADependentVariable,
)


def gather_inputs():
    bounds = {
        "SIR-simple::SIR-simple.sir::beta::-1": [0, 1],
        "SIR-simple::SIR-simple.sir::gamma::-1": [0, 1],
    }

    inputs = {
        "SIR-simple::SIR-simple.sir::S::-1": 10000,
        "SIR-simple::SIR-simple.sir::I::-1": 1000,
        "SIR-simple::SIR-simple.sir::R::-1": 10000,
        "SIR-simple::SIR-simple.sir::dt::-1": 100,
    }

    output_base_names = ["S", "I", "R"]

    return (bounds, inputs, output_base_names)


def main():

    N = 100000
    # N = 10000

    if len(sys.argv) < 2:
        raise Exception(
            "Error: Please provide a path to sir simple grfn json as an argument"
        )

    print("Reading sir simple json file...")

    file = sys.argv[1]
    if not os.path.exists(file):
        raise Exception(f"Error: File '{file}' does not exist")

    inputs = None
    bounds = None
    outputs = None

    file_name = file.split("/")[-1]
    soilt_model_name = file_name.split("--")[0]

    (bounds, inputs, outputs) = gather_inputs()

    print("Parsing grfn json...")

    grfn = None
    try:
        grfn = GroundedFunctionNetwork.from_json(file)
    except Exception:
        raise Exception(f"Error: Unable to process grfn json file {file}")

    print("Running sensitivity analysis...")

    analyzer = SensitivityAnalyzer()
    Si_list = analyzer.Si_from_Sobol(N, grfn, bounds, inputs, outputs)

    # for Si in Si_list:
    #     print(Si.to_dict())

    model_inputs = [
        {
            "variable_name": k,
            "bounds": v,
        }
        for k, v in bounds.items()
    ]

    model_outputs = [{"variable_name": n} for n in outputs]

    def fix_nans(o):
        if isinstance(o, dict):
            return {k: fix_nans(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [fix_nans(item) for item in o]
        elif isinstance(o, float) and math.isnan(o):
            return None
        return o

    sensitivity_indices_res = [fix_nans(Si.to_dict()) for Si in Si_list]
    results = {
        "grfn_uid": grfn.uid,
        "input_variables": model_inputs,
        "output_variables": model_outputs,
        "sensitivity_indices": sensitivity_indices_res,
    }

    out_file = f"{soilt_model_name}-{N}--SA.json"
    print(f"Writing results to {out_file}")
    json.dump(results, open(out_file, "w"))


if __name__ == "__main__":
    main()
