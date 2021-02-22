import json
import sys

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_analysis.sensitivity import SensitivityAnalyzer


def main():
    grfn_json_path = sys.argv[1]
    N = 100000

    sir_grfn = GroundedFunctionNetwork.from_json(grfn_json_path)

    bounds = {
        "s": [100000, 100001],
        "i": [1, 10],
        "r": [0, 1],
        "beta": [0, 1],
        "gamma": [0, 1],
        "dt": [1, 5],
    }
    analyzer = SensitivityAnalyzer()
    Si_list = analyzer.Si_from_Sobol(N, sir_grfn, bounds)
    for Si in Si_list:
        print(Si.to_dict())

    model_inputs = [{
        "variable_name": n.identifier.var_name,
        "variable_uid": n.uid,
        "bounds": bounds[n.identifier.var_name]
    } for n in sir_grfn.inputs]

    model_outputs = [{
        "variable_name": n.identifier.var_name,
        "variable_uid": n.uid
    } for n in sir_grfn.outputs]

    results = {
        "grfn_uid": sir_grfn.uid,
        "input_variables": model_inputs,
        "output_variables": model_outputs,
        "sensitivity_indices": [Si.to_dict() for Si in Si_list]
    }
    json.dump(results, open("SIR-Simple--SI.json", "w"))


if __name__ == "__main__":
    main()
