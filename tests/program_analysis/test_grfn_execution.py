import pytest

from automates.model_assembly.networks import GroundedFunctionNetwork


@pytest.fixture
def basic_assignment_grfn():
    return GroundedFunctionNetwork.from_json(
        "tests/data/program_analysis/grfn_execution/basic_assignment_grfn.json"
    )


def test_basic_assignment_execution(basic_assignment_grfn):
    inputs = {"input": 37}
    result = basic_assignment_grfn(inputs)

    assert "output" in result
    assert result["output"] == 42