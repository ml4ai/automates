import json
import os

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_assembly.expression_trees.expression_walker import (
    expr_trees_from_grfn,
)
from automates.model_assembly.model_dynamics import extract_model_dynamics


def extract_io_from_grfn(GrFN):
    # TODO return variable types

    optional_inputs = [
        {
            "variable_identifier": str(v.identifier),
            "variable_type": None,
            "required": False,
        }
        for v in GrFN.literal_vars
    ]

    optional_input_identifiers = {v["variable_identifier"] for v in optional_inputs}
    required_inputs = [
        {
            "variable_identifier": str(v.identifier),
            "variable_type": None,
            "required": True,
        }
        for v in GrFN.inputs
        if str(v.identifier) not in optional_input_identifiers
    ]

    optional_outputs_identifiers = dict()
    for v in GrFN.variables:
        name = (
            f"{v.identifier.namespace}::{v.identifier.scope}::{v.identifier.var_name}"
        )
        if (
            name not in optional_outputs_identifiers
            or v.identifier.index > optional_outputs_identifiers[name].index
        ):
            optional_outputs_identifiers[name] = v.identifier

    optional_outputs = [
        {
            "variable_identifier": str(v),
            "variable_type": None,
            "default": False,
        }
        for _, v in optional_outputs_identifiers.items()
    ]

    outputs = [
        {
            "variable_identifier": str(v.identifier),
            "variable_type": None,
            "default": True,
        }
        for v in GrFN.outputs
    ] + optional_outputs

    return {
        "execution_inputs": optional_inputs + required_inputs,
        "execution_outputs": outputs,
    }


def extract_expr_trees(GrFN):
    return expr_trees_from_grfn(GrFN)


def extract_model_dynamics_from_grfn(GrFN):
    potential_dynamics_grfns = extract_model_dynamics(GrFN)

    updated_grfns = list()
    for g in potential_dynamics_grfns:
        grfn_dict = g.to_dict()
        updated_grfns.append(GroundedFunctionNetwork.from_dict(grfn_dict))

    return [
        {"model": json.loads(g.to_json()), "variable_io": extract_io_from_grfn(g)}
        for g in updated_grfns
    ]


def extract_io_from_grfn_json(grfn_json):
    GrFN = GroundedFunctionNetwork.from_dict(grfn_json)
    return extract_io_from_grfn(GrFN)


def extract_expr_trees_from_grfn_json(grfn_json):
    GrFN = GroundedFunctionNetwork.from_dict(grfn_json)
    return extract_expr_trees(GrFN)


def extract_model_dynamics_from_grfn_json(grfn_json):
    GrFN = GroundedFunctionNetwork.from_dict(grfn_json)
    return extract_model_dynamics_from_grfn(GrFN)
