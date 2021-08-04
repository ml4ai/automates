import numpy as np

from automates.model_assembly.networks import GroundedFunctionNetwork, VariableNode


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
