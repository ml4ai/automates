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


@pytest.fixture
def basic_function_def_and_assignment_cast():
    v = Var(val="exampleVar", type="float")
    n = Number(number=36.2)
    a = Assignment(left=v, right=n)
    f = FunctionDef(name="exampleFunction", func_args=[], body=[a])
    m = Module(name="ExampleModule", body=[f])
    return CAST([m])


@pytest.fixture
def cast_with_all_nodes():
    class_func_arg_name = Var(val="exampleArg", type="Number")
    var = Var(val="exampleVar", type="Number")
    number = Number(number=36.2)

    class_func_assign_expr = UnaryOp(
        op=UnaryOperator.USUB,
        value=BinaryOp(op=BinaryOperator.ADD, left=class_func_arg_name, right=number),
    )
    class_func_assign = Assignment(left=var, right=class_func_assign_expr)

    class_func_str = String(string="str")
    class_func_return = ModelReturn(value=class_func_str)

    class_func_def = FunctionDef(
        name="exampleClassFunction",
        func_args=[class_func_arg_name],
        body=[class_func_assign, class_func_return],
    )

    class_field_var = Var(val="exampleClassVar", type="String")
    class_def = ClassDef(
        name="ExampleClass", bases=[], funcs=[class_func_def], fields=[class_field_var]
    )

    obj_var = Var(val="exampleObject", type="ExampleClass")
    obj_costructer_name = Name(name="ExampleClass")
    obj_constructor_call = Call(func=obj_costructer_name, arguments=[])
    obj_assign = Assignment(left=obj_var, right=obj_constructor_call)

    continue_node = ModelContinue()
    break_node = ModelBreak()
    true_expr = BinaryOp(
        op=BinaryOperator.EQ, left=Number(number=1), right=Number(number=1)
    )
    if_node = ModelIf(expr=true_expr, body=[continue_node], orelse=[break_node])

    attr = Attribute(value=obj_var, attr=Name(name="exampleClassFunction"))
    attr_expr = Expr(expr=attr)

    loop = Loop(expr=true_expr, body=[if_node, attr_expr])

    set_assign = Assignment(
        left=Var(val="exampleSet", type="Set"), right=Set(values=[])
    )
    list_assign = Assignment(
        left=Var(val="exampleList", type="List"), right=List(values=[])
    )
    dict_var = Var(val="exampleDict", type="Dict")
    dict_assign = Assignment(left=dict_var, right=Dict(values=[], keys=[]))
    dict_subscript = Expr(Subscript(value=dict_var, slice=String(string="key")))

    func_def = FunctionDef(
        name="exampleFunction",
        func_args=[],
        body=[obj_assign, loop, set_assign, list_assign, dict_assign, dict_subscript],
    )

    m = Module(name="ExampleModule", body=[class_def, func_def])

    return CAST([m])


def test_basic_function_def_and_assignment(
    basic_function_def_and_assignment_grfn, basic_function_def_and_assignment_cast
):
    generated_grfn = basic_function_def_and_assignment_cast.to_GrFN()
    assert generated_grfn == basic_function_def_and_assignment_grfn
