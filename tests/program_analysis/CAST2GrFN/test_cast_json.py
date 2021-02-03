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


# def get_basic_function_def_cast():
#     v = Var(val="exampleVar", type="float")
#     n = Number(val=36.2)
#     a = Assignment(left=v, right=n)
#     f = FunctionDef(name="exampleFunction", func_args=[], body=[a])
#     m = Module([f])

#     return CAST([m])


def get_file_str(filepath):
    with open(filepath) as f:
        return f.readlines() 

def get_cast_with_all_nodes_expected_json_str():
    get_file_str

def get_cast_with_all_nodes():
    class_func_arg_name = Var(val="exampleArg", type=VarType.NUMBER)
    var = Var(val="exampleVar", type=VarType.NUMBER)
    number = Number(val=36.2)

    class_func_assign_expr = UnaryOp(
        op=UnaryOperator.USUB,
        value=BinaryOp(op=BinaryOperator.ADD, left=class_func_arg_name, right=number),
    )
    class_func_assign = Assignment(left=var, right=class_func_assign_expr)

    class_func_def = FunctionDef(
        name="exampleClassFunction",
        func_args=[class_func_arg_name],
        body=[class_func_assign],
    )

    class_field_var = Var(val="exampleClassVar", type=VarType.STRING)
    class_def = ClassDef(
        name="ExampleClass", bases=[], funcs=[class_func_def], fields=[class_field_var]
    )

    obj_var = Var(val="exampleObject", type="ExampleClass")
    obj_costructer_name = Name(val="ExampleClass")
    obj_constructor_call = Call(func=obj_costructer_name, arguments=[])
    obj_assign = Assignment(left=obj_var, right=obj_constructor_call)

    continue_node = ModelContinue()
    break_node = ModelBreak()
    true_expr = BinaryOp(op=BinaryOperator.EQ, left=Number(val=1), right=Number(val=1))
    if_node = ModelIf(expr=true_expr, body=[continue_node], orelse=[break_node])
    loop = Loop(expr=true_expr, body=[if_node])

    # TODO Attribute, Expr, set/list/dict, string, subscript, return

    func_def = FunctionDef(name="exampleFunction", func_args=[], body=[obj_assign, loop])

    m = Module([class_def, func_def])

    return CAST([m])


def test_all_nodes_from_json():
    cast_json = 
    cast = CAST.from_json(cast_json)
    pass


def test_all_nodes_to_json():
    cast = get_cast_with_all_nodes()
    cast_json = cast.to_json()

    # TODO read expected from file and compare
    assert cast_json == []


def test_all_nodes_to_json_and_from_result():
    cast = get_cast_with_all_nodes()
    cast_json = cast.to_json()

    # TODO read expected from file and compare
    assert cast_json == []


def test_from_json_unknown_cast_type_exception():
    cast = get_basic_function_def_cast()
    cast_json = cast.to_json()

    # TODO read expected from file and compare
    assert cast_json == []