import numpy as np

from automates.model_assembly.networks import GroundedFunctionNetwork, VariableNode


def parse_execution_inputs(inputs):
    execution_inputs = {i["variable_identifier"]: np.array(i["value"]) for i in inputs}
    return execution_inputs


def parse_execution_results(results):
    return [{"variable_name": k, "results": v.tolist()} for k, v in results.items()]


def gather_additional_outputs(outputs, GrFN):
    desired_output_values = {}
    for n in GrFN.variables:
        n_name = str(n.identifier)
        if n_name in set(outputs):
            desired_output_values[n.identifier] = n
    return [
        {"variable_name": k.var_name, "results": np.array(v.value).tolist()}
        for k, v in desired_output_values.items()
    ]


def execute_grfn_json(grfn_json, input_json, outputs_json):
    GrFN = GroundedFunctionNetwork.from_dict(grfn_json)
    execution_inputs = parse_execution_inputs(input_json)
    results = parse_execution_results(GrFN(execution_inputs))

    if len(outputs_json) > 0:
        results.extend(gather_additional_outputs(outputs_json, GrFN))

    return results
