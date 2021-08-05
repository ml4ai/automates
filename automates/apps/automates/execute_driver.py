import numpy as np
import json

from automates.model_assembly.networks import GroundedFunctionNetwork, VariableNode
import automates.apps.automates.model_code.chime_sir as chime
import automates.apps.automates.model_code.sir_simple as sir_simple


def parse_execution_inputs(inputs):
    execution_inputs = {i["variable_identifier"]: np.array(i["value"]) for i in inputs}
    return execution_inputs


def parse_execution_results(results):
    return [{"variable_name": k, "results": v.tolist()} for k, v in results.items()]


def gather_additional_outputs(outputs, GrFN):
    desired_output_values = {}
    # FIXME hange this code from doing a linear time loop through all the
    # variables in the GrFN to instead loop through all of the variable
    # identifiers in outputs. Assert that each identifier presented in outputs
    #  appears in an identifier variable index stored in GrFN (we may need to
    #  create this structure) and have that assertion wrapped in a try/catch in
    # case it fails to return an error message that certain desired output
    # identifiers were not found in the GrFN.
    for n in GrFN.variables:
        n_name = str(n.identifier)
        if n_name in set(outputs):
            desired_output_values[n.identifier] = n
    return [
        {"variable_name": k.var_name, "results": np.array(v.value).tolist()}
        for k, v in desired_output_values.items()
    ]


def execute_grfn_json(grfn_json, input_json, outputs_json):
    # TODO Before execution happens, verify all required inputs are given
    GrFN = GroundedFunctionNetwork.from_dict(grfn_json)
    execution_inputs = parse_execution_inputs(input_json)
    results = parse_execution_results(GrFN(execution_inputs))

    if len(outputs_json) > 0:
        results.extend(gather_additional_outputs(outputs_json, GrFN))

    return results


def collect_unknown_experiment_inputs(expected, given):
    found_unknown_keys = list()
    for input in expected:
        if input not in given:
            found_unknown_keys.append(input)
    return found_unknown_keys


def run_model_experiment(
    name, start, end, step, expected_parameters, parameters, drive_fn
):
    found_unknown_keys = collect_unknown_experiment_inputs(
        expected_parameters, parameters
    )
    if len(found_unknown_keys) > 0:
        return {
            "code": 400,
            "error": f"Did not find expected parameters {found_unknown_keys} for model {name}.",
        }

    return drive_fn(start, end, step, parameters)


def execute_gromet_experiment_json(experiment_json):
    """
    Expected input object:

    {
        "command": "simulate-gsl",
        "definition": {
            "type": "easel",
            "source": "{ \"model\": \" GroMEt Model String \" }"
        },
        "start": 0,
        "end": 120.0,
        "step": 30.0,
        "domain_parameter": "",
        "parameters": {
            "beta": 0.9
        },
        "outputs": [
            "s",
            "i",
            "r"
        ]
    }

    Args:
        experiment_json (Dict): A python object reflecting the model above

    Returns: results of gromet experiment execution
    """

    expected_keys = [
        "definition",
        "start",
        "end",
        "step",
        "domain_parameter",
        "parameters",
        "outputs",
    ]
    not_found_keys = []
    for key in expected_keys:
        if key not in experiment_json:
            not_found_keys.append(key)

    if len(not_found_keys) > 0:
        return {"code": 400, "message": f"Expected key(s) {not_found_keys} not found."}

    start = None
    end = None
    step = None
    try:
        start = int(experiment_json["start"])
        end = int(experiment_json["end"])
        step = int(experiment_json["step"])
    except:
        return {
            "code": 400,
            "message": f'Unable to parse integer value provided for one of "start", "end", or "step".',
        }

    domain_parameter = experiment_json["domain_parameter"]
    parameters = experiment_json["parameters"]
    outputs = experiment_json["outputs"]
    gromet_source_json_str = experiment_json["definition"]["source"]["model"]
    gromet_obj = json.loads(gromet_source_json_str)
    model_name = gromet_obj["name"]

    results = {}
    if model_name == "SIR-simple":
        expected_sir_simple_inputs = [
            "SIR-simple::SIR-simple::sir::0::--::s::0",
            "SIR-simple::SIR-simple::sir::0::--::i::0",
            "SIR-simple::SIR-simple::sir::0::--::r::0",
            "SIR-simple::SIR-simple::sir::0::--::beta::0",
            "SIR-simple::SIR-simple::sir::0::--::gamma::0",
        ]
        try:
            results = run_model_experiment(
                model_name,
                start,
                end,
                step,
                expected_sir_simple_inputs,
                parameters,
                sir_simple.drive,
            )
        except:
            return {
                "status": 500,
                "message": f'Error: Encountered issue while executing experiment "{model_name}".',
            }

    elif model_name == "CHIME-SIR":
        expected_sir_simple_inputs = []
        try:
            results = run_model_experiment(
                model_name,
                start,
                end,
                step,
                expected_sir_simple_inputs,
                parameters,
                chime.drive,
            )
        except:
            return {
                "status": 500,
                "message": f'Error: Encountered issue while executing experiment "{model_name}".',
            }
    else:
        return {
            "code": 400,
            "message": f'Unable to run model experiment for "{model_name}".',
        }

    return {
        "status": 200,
        "body": {
            "values": {k: v for k, v in results.items() if k in outputs},
            "domain_parameter": results[domain_parameter],
        },
    }
