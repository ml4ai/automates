import json
import sys

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_analysis.sensitivity import (
    SensitivityAnalyzer,
    SADependentVariable,
)


def main():
    bounds = {
        "SIR-simple.py::SIR-simple.py.sir::S::-1::f728b4fa-4248-5e3a-0a5d-2f346baa9455": [
            100000,
            100001,
        ],
        "SIR-simple.py::SIR-simple.py.sir::I::-1::eb1167b3-67a9-c378-7c65-c1e582e2e662": [
            1,
            10,
        ],
        "SIR-simple.py::SIR-simple.py.sir::R::-1::f7c1bd87-4da5-e709-d471-3d60c8a70639": [
            0,
            1,
        ],
    }

    inputs = {
        "SIR-simple.py::SIR-simple.py.sir::beta::-1::e443df78-9558-867f-5ba9-1faf7a024204": 1,
        "SIR-simple.py::SIR-simple.py.sir::gamma::-1::23a7711a-8133-2876-37eb-dcd9e87a1613": SADependentVariable(
            "SIR-simple.py::SIR-simple.py.sir::gamma::-1::23a7711a-8133-2876-37eb-dcd9e87a1613",
            [
                "SIR-simple.py::SIR-simple.py.sir::R::-1::f7c1bd87-4da5-e709-d471-3d60c8a70639",
                "SIR-simple.py::SIR-simple.py.sir::I::-1::eb1167b3-67a9-c378-7c65-c1e582e2e662",
            ],
            lambda a, b: a + b,
        ),
        "SIR-simple.py::SIR-simple.py.sir::dt::-1::1846d424-c17c-6279-23c6-612f48268673": SADependentVariable(
            "SIR-simple.py::SIR-simple.py.sir::dt::-1::1846d424-c17c-6279-23c6-612f48268673",
            [
                "SIR-simple.py::SIR-simple.py.sir::gamma::-1::23a7711a-8133-2876-37eb-dcd9e87a1613",
            ],
            lambda a: a * 2,
        ),
    }

    grfn = GroundedFunctionNetwork.from_json(sys.argv[1])

    # exec = SensitivityAnalyzer.build_execution(grfn, bounds, inputs)

    # res = exec([100000, 5, 0.5])
    a = SensitivityAnalyzer()
    N = 100
    Si_list = a.Si_from_Sobol(N, grfn, bounds, inputs)

    from pprint import pprint

    # pprint(Si_list)
    for Si in Si_list:
        pprint(Si.to_dict())


# grfn_json_path = sys.argv[1]
# N = 100000

# sir_grfn = GroundedFunctionNetwork.from_json(grfn_json_path)

# bounds = {
#     "s": [100000, 100001],
#     "i": [1, 10],
#     "r": [0, 1],
#     "beta": [0, 1],
#     "gamma": [0, 1],
#     "dt": [1, 5],
# }
# analyzer = SensitivityAnalyzer()
# Si_list = analyzer.Si_from_Sobol(N, sir_grfn, bounds)
# for Si in Si_list:
#     print(Si.to_dict())

# model_inputs = [
#     {
#         "variable_name": n.identifier.var_name,
#         "variable_uid": n.uid,
#         "bounds": bounds[n.identifier.var_name],
#     }
#     for n in sir_grfn.inputs
# ]

# model_outputs = [
#     {"variable_name": n.identifier.var_name, "variable_uid": n.uid}
#     for n in sir_grfn.outputs
# ]

# results = {
#     "grfn_uid": sir_grfn.uid,
#     "input_variables": model_inputs,
#     "output_variables": model_outputs,
#     "sensitivity_indices": [Si.to_dict() for Si in Si_list],
# }
# json.dump(results, open("SIR-Simple--SI.json", "w"))


if __name__ == "__main__":
    main()
