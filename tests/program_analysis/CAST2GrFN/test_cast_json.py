import json
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
    UnaryOp,
    UnaryOperator,
    VarType,
    Var,
)

from automates.program_analysis.CAST2GrFN.cast import CAST, CASTJsonException


def get_file_str(filepath):
    with open(filepath) as f:
        return f.read()


@pytest.fixture
def cast_with_all_nodes_json():
    return get_file_str("tests/data/program_analysis/CAST2GrFN/cast_all_nodes.json")


@pytest.fixture
def cast_with_no_node_type_exception_json():
    return get_file_str(
        "tests/data/program_analysis/CAST2GrFN/cast_with_no_node_type.json"
    )


@pytest.fixture
def cast_with_unknown_node_type_exception_json():
    return get_file_str(
        "tests/data/program_analysis/CAST2GrFN/cast_with_unknown_node_type.json"
    )


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

    return CAST([m], cast_source_language="")


def test_all_nodes_from_json(cast_with_all_nodes_json, cast_with_all_nodes):
    cast = CAST.from_json_str(cast_with_all_nodes_json)
    assert cast == cast_with_all_nodes


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_all_nodes_to_json(cast_with_all_nodes_json, cast_with_all_nodes):
    cast_json = cast_with_all_nodes.to_json_object()
    assert cast_json == json.loads(cast_with_all_nodes_json)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_all_nodes_to_json_and_from_result(
    cast_with_all_nodes_json, cast_with_all_nodes
):

    cast_json = cast_with_all_nodes.to_json_object()
    assert cast_json == json.loads(cast_with_all_nodes_json)

    cast_from_generated_json = CAST.from_json_data(cast_json)
    assert cast_with_all_nodes == cast_from_generated_json


def test_from_json_no_node_type_exception(cast_with_no_node_type_exception_json):
    with pytest.raises(CASTJsonException):
        CAST.from_json_str(cast_with_no_node_type_exception_json)


def test_from_json_unknown_cast_type_exception(
    cast_with_unknown_node_type_exception_json,
):
    with pytest.raises(CASTJsonException):
        CAST.from_json_str(cast_with_unknown_node_type_exception_json)
