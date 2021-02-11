import pytest
import numpy as np

from automates.model_assembly.networks import GroundedFunctionNetwork


@pytest.fixture
def basic_assignment_grfn():
    """
    Modeled code:

        def function(x):
            y = x + 5
            return y


        def main():
            input = 4
            output = function(input)
    """
    return GroundedFunctionNetwork.from_json(
        "tests/data/program_analysis/grfn_execution/basic_assignment_grfn.json"
    )


@pytest.fixture
def loop_grfn():
    """
    Modeled code:

        def main():
            input = 4
            increment = 1
            while (input > 0):
                increment += 1
            result = increment
    """
    return GroundedFunctionNetwork.from_json(
        "tests/data/program_analysis/grfn_execution/loop_grfn.json"
    )


@pytest.fixture
def grfn_with_types():
    """
    Modeled code: Refer to the PID.c example code
    """
    return GroundedFunctionNetwork.from_json(
        "tests/data/program_analysis/grfn_execution/grfn_with_types.json"
    )


def test_basic_assignment_execution(basic_assignment_grfn):
    inputs = {"input": 37}
    result = basic_assignment_grfn(inputs)

    assert "output" in result
    assert result["output"] == 42


def test_loop_execution(loop_grfn):
    inputs = {"input": 5, "increment": 1}
    result = loop_grfn(inputs)

    assert "result" in result
    assert result["result"] == 5


def test_loop_execution_no_iterations(loop_grfn):
    inputs = {"input": 1, "increment": 1}
    result = loop_grfn(inputs)

    assert "result" in result
    assert result["result"] == 1


def test_loops_and_user_defined_types(grfn_with_types):
    inputs = {"count": 0}
    result = grfn_with_types(inputs)

    assert "count" in result and "pid" in result
    from deepdiff import DeepDiff

    expected_result = {
        "count": np.array([100], dtype=np.int32),
        "pid": {
            "ActualSpeed": np.array([15.26216875154356]),
            "Kd": np.array([0.2]),
            "Ki": np.array([0.015]),
            "Kp": np.array([0.2]),
            "SetSpeed": np.array([20.0]),
            "err": np.array([4.797805417884138]),
            "err_last": np.array([4.797805417884138]),
            "integral": np.array([954.3169559532655]),
            "voltage": np.array([15.26216875154356]),
        },
        "speed": np.array([15.321393223831578]),
    }
    from pprint import pprint

    pprint(DeepDiff(result, expected_result))
    assert result == expected_result
