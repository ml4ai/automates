import automates.program_analysis.CAST2GrFN.visitors.cast_function_call_visitor as call_order

from automates.program_analysis.CAST2GrFN.model.cast import (
    AstNode,
    Assignment,
    Attribute,
    BinaryOp,
    Boolean,
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
    SourceRef,
    Subscript,
    Tuple,
    UnaryOp,
    UnaryOperator,
    VarType,
    Var,
    name,
    source_ref,
    var,
)


def test_reorder_function_visitation():

    cast = Module(
        name="TestModule",
        body=[
            FunctionDef(
                name="func1",
                func_args=[],
                body=[
                    Assignment(
                        left=Name(name="a"),
                        right=Call(func=Name(name="func2"), arguments=[]),
                    )
                ],
            ),
            FunctionDef(
                name="func2", func_args=[], body=[ModelReturn(value=Number(number=1))]
            ),
        ],
    )

    order = call_order.get_function_visit_order(cast)

    assert ["func2", "func1"] == order


def test_no_reorder_needed():
    cast = Module(
        name="TestModule",
        body=[
            FunctionDef(
                name="func1", func_args=[], body=[ModelReturn(value=Number(number=1))]
            ),
            FunctionDef(
                name="func2",
                func_args=[],
                body=[
                    Assignment(
                        left=Name(name="a"),
                        right=Call(func=Name(name="func1"), arguments=[]),
                    )
                ],
            ),
        ],
    )

    order = call_order.get_function_visit_order(cast)

    assert ["func1", "func2"] == order


def test_no_calls():
    cast = Module(
        name="TestModule",
        body=[
            FunctionDef(
                name="func1", func_args=[], body=[ModelReturn(value=Number(number=1))]
            ),
            FunctionDef(
                name="func2",
                func_args=[],
                body=[
                    Assignment(
                        left=Name(name="a"),
                        right=Number(number=1),
                    )
                ],
            ),
        ],
    )
    order = call_order.get_function_visit_order(cast)

    assert ["func1", "func2"] == order
