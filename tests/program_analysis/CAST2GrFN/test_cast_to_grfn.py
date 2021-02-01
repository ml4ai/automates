import pytest

from automates.program_analysis.CAST2GrFN.model.cast import (
    AstNode,
    Assignment,
    Attribute,
    BinaryOp,
    BinaryOperator,
    Call,
    ClassDef,
    Dict,
    Expr,
    FunctionDef,
    List,
    Loop,
    ModelBreak,
    ModelContinue,
    ModelIf,
    ModelReturn,
    Module,
    Name,
    Number,
    Set,
    String,
    Subscript,
    Tuple,
    UnaryOp,
    UnaryOperator,
    VarType,
    Var,
)

from automates.program_analysis.CAST2GrFN.cast import CAST
from automates.model_assembly.networks import GroundedFunctionNetwork


def get_grfn_from_json_file(file):
    return GroundedFunctionNetwork.from_json(file)


@pytest.fixture
def basic_function_def_and_assignment_grfn():
    json_filepath = "tests/data/program_analysis/CAST2GrFN/basic_function_def_and_assignment_grfn.json"
    return get_grfn_from_json_file(json_filepath)


def test_basic_function_def_and_assignment(basic_function_def_and_assignment_grfn):

    v = Var(val="exampleVar", type="float")
    n = Number(val=36.2)
    a = Assignment(left=v, right=n)
    f = FunctionDef(name="exampleFunction", func_args=[], body=[a])
    m = Module([f])

    cast = CAST([m])
    generated_grfn = cast.to_GrFN()

    assert generated_grfn == basic_function_def_and_assignment_grfn
