import pytest

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