import json
import sys
import os

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_analysis.sensitivity import (
    SensitivityAnalyzer,
    SADependentVariable,
)


def gather_stemp_soilt_inputs():
    bounds = {
        "stemp_soilt::stemp_soilt.soilt::srad::-1": [0.5, 30],
        "stemp_soilt::stemp_soilt.soilt::tmax::-1": [0, 40],
        # "stemp_soilt::stemp_soilt.soilt::nlayr::-1": [1, 20],
    }

    inputs = {
        # "stemp_soilt::stemp_soilt.soilt::nlayr::-1": SADependentVariable(
        #     "stemp_soilt::stemp_soilt.soilt::nlayr::-1",
        #     ["stemp_soilt::stemp_soilt.soilt::nlayr::-1"],
        #     lambda nlayr: int(nlayr),
        # ),
        "stemp_soilt::stemp_soilt.soilt::nlayr::-1": 10,
        "stemp_soilt::stemp_soilt.soilt::atot::-1": 0,
        "stemp_soilt::stemp_soilt.soilt::tma::-1": [0, 0, 0, 0, 0],
        "stemp_soilt::stemp_soilt.soilt::ww::-1": 1,
        "stemp_soilt::stemp_soilt.soilt::albedo::-1": 0,
        "stemp_soilt::stemp_soilt.soilt::b::-1": 0,
        "stemp_soilt::stemp_soilt.soilt::cumdpt::-1": 1,
        "stemp_soilt::stemp_soilt.soilt::doy::-1": 0,
        "stemp_soilt::stemp_soilt.soilt::dp::-1": 1,
        "stemp_soilt::stemp_soilt.soilt::hday::-1": 0,
        "stemp_soilt::stemp_soilt.soilt::pesw::-1": 1,
        "stemp_soilt::stemp_soilt.soilt::tamp::-1": 0,
        "stemp_soilt::stemp_soilt.soilt::tav::-1": SADependentVariable(
            "stemp_soilt::stemp_soilt.soilt::tav::-1",
            ["stemp_soilt::stemp_soilt.soilt::tmax::-1"],
            lambda tmax: tmax - 5,
        ),
        "stemp_soilt::stemp_soilt.soilt::tavg::-1": SADependentVariable(
            "stemp_soilt::stemp_soilt.soilt::tavg::-1",
            [
                "stemp_soilt::stemp_soilt.soilt::tmax::-1",
                "stemp_soilt::stemp_soilt.soilt::tav::-1",
            ],
            lambda tmax, tav: (tmax + tav) / 2,
        ),
        "stemp_soilt::stemp_soilt.soilt::dsmid::-1": SADependentVariable(
            "stemp_soilt::stemp_soilt.soilt::dsmid::-1",
            ["stemp_soilt::stemp_soilt.soilt::nlayr::-1"],
            lambda nlayr: [0] * nlayr,
        ),
        "stemp_soilt::stemp_soilt.soilt::st::-1": SADependentVariable(
            "stemp_soilt::stemp_soilt.soilt::st::-1",
            ["stemp_soilt::stemp_soilt.soilt::nlayr::-1"],
            lambda nlayr: [0] * nlayr,
        ),
    }

    output_base_names = ["atot", "tma", "srftemp", "st"]
    # output_base_names = ["tma"]

    return (bounds, inputs, output_base_names)


def gather_stemp_epic_soilt_inputs():
    bounds = {
        # "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::srad::-1": [0.5, 30],
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::tmax::-1": [0, 40],
        # "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::nlayr::-1": [1, 20],
    }

    inputs = {
        # "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::nlayr::-1": SADependentVariable(
        #     "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::nlayr::-1",
        #     ["stemp_epic_soilt::stemp_epic_soilt.soilt_epic::nlayr::-1"],
        #     lambda nlayr: int(nlayr),
        # ),
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::b::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::bcv::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::nlayr::-1": 10,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::tma::-1": [0, 0, 0, 0, 0],
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::ww::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::cumdpt::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::dp::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::pesw::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::wetday::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::wft::-1": 20,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::tav::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::tmin::-1": SADependentVariable(
            "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::tmin::-1",
            ["stemp_epic_soilt::stemp_epic_soilt.soilt_epic::tmax::-1"],
            lambda tmax: tmax - 5,
        ),
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::tavg::-1": SADependentVariable(
            "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::tavg::-1",
            [
                "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::tmax::-1",
                "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::tav::-1",
            ],
            lambda tmax, tav: (tmax + tav) / 2,
        ),
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::dsmid::-1": SADependentVariable(
            "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::dsmid::-1",
            ["stemp_epic_soilt::stemp_epic_soilt.soilt_epic::nlayr::-1"],
            lambda nlayr: [0] * nlayr,
        ),
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::st::-1": SADependentVariable(
            "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::st::-1",
            ["stemp_epic_soilt::stemp_epic_soilt.soilt_epic::nlayr::-1"],
            lambda nlayr: [0] * nlayr,
        ),
    }

    output_base_names = ["tma", "srftemp", "st", "x2_avg"]

    return (bounds, inputs, output_base_names)


def main():

    # N = 100000
    # N = 10000
    N = 10

    if len(sys.argv) < 2:
        raise Exception(
            "Error: Please provide a path to soilt grfn json as an argument"
        )

    print("Reading soilt json file...")

    file = sys.argv[1]
    if not os.path.exists(file):
        raise Exception(f"Error: File '{file}' does not exist")

    inputs = None
    bounds = None
    outputs = None

    file_name = file.split("/")[-1]
    soilt_model_name = file_name.split("--")[0]

    if soilt_model_name == "stemp_soilt":
        (bounds, inputs, outputs) = gather_stemp_soilt_inputs()
    elif soilt_model_name == "stemp_epic_soilt":
        (bounds, inputs, outputs) = gather_stemp_epic_soilt_inputs()
    else:
        raise Exception(f"Error: Unknown soilt model {soilt_model_name}")

    print("Parsing grfn json...")

    grfn = None
    try:
        grfn = GroundedFunctionNetwork.from_json(file)
    except Exception:
        raise Exception(f"Error: Unable to process grfn json file {file}")

    print("Running sensitivity analysis...")

    analyzer = SensitivityAnalyzer()
    Si_list = analyzer.Si_from_Sobol(N, grfn, bounds, inputs, outputs, calc_2nd=True)

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

    results = {
        "grfn_uid": grfn.uid,
        "input_variables": model_inputs,
        "output_variables": model_outputs,
        "sensitivity_indices": [Si.to_dict() for Si in Si_list],
    }

    out_file = f"{soilt_model_name}-{N}--SA.json"
    print(f"Writing results to {out_file}")
    json.dump(results, open(out_file, "w"))


if __name__ == "__main__":
    main()
