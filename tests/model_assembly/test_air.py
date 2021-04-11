import pytest


from automates.model_assembly.air import AutoMATES_IR
from automates.model_assembly.networks import GroundedFunctionNetwork


def test_PID_conversion():
    air_filepath = "tests/data/model_assembly/air/PID--AIR.json"
    grfn_filepath = "tests/data/model_assembly/grfn/PID--GrFN.json"
    AIR = AutoMATES_IR.from_json(air_filepath)
    GrFN = GroundedFunctionNetwork.from_AIR(AIR)
    expected_GrFN = GroundedFunctionNetwork.from_json(grfn_filepath)

    assert GrFN == expected_GrFN
