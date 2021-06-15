import numpy as np

from automates.model_assembly.networks import GroundedFunctionNetwork

def parse_execution_inputs(inputs):
    execution_inputs = {i["variable_identifier"]: np.array(i["value"]) for i in inputs}
    return execution_inputs

def parse_execution_results(results):
    return [
        {
            "variable_name": k,
            "results": v.tolist()
        } 
        for k,v in results.items()]


def execute_grfn_json(grfn_json, input_json):
    GrFN = GroundedFunctionNetwork.from_dict(grfn_json)
    execution_inputs = parse_execution_inputs(input_json)
    results = parse_execution_results(GrFN(execution_inputs))
    from pprint import pprint
    pprint(results)
    return results