from os import name
import pytest
import random

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

from automates.program_analysis.CAST2GrFN.model.cast_to_air_model import (
    C2ATypeError,
)
from automates.program_analysis.CAST2GrFN.cast import CAST
from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.utils.misc import rd


def get_grfn_from_json_file(file):
    return GroundedFunctionNetwork.from_json(file)


@pytest.fixture(autouse=True)
def run_around_tests():
    # Before each test, set the seed for generating uuids to 0 for consistency
    # between tests and expected output
    rd.seed(0)
    # Run the test function
    yield


@pytest.fixture
def basic_function_def_and_assignment_grfn():
    json_filepath = "tests/data/program_analysis/CAST2GrFN/basic_function_def_and_assignment_grfn.json"
    return get_grfn_from_json_file(json_filepath)


@pytest.fixture
def pid_c_cast_grfn():
    return None


@pytest.fixture
def cast_with_all_nodes_grfn():
    return None


@pytest.fixture
def basic_function_def_and_assignment_cast():
    v = Var(val=Name(name="exampleVar"), type="float")
    n = Number(number=36.2)
    a = Assignment(left=v, right=n)
    f = FunctionDef(name="exampleFunction", func_args=[], body=[a])
    m = Module(name="ExampleModule", body=[f])
    return CAST([m], cast_source_language="")


@pytest.fixture
def cast_with_all_nodes():
    class_func_arg_name = Var(val="exampleArg", type="Number")
    var = Var(val=Name(name="exampleVar"), type="Number")
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
        name="ExampleClass",
        bases=[],
        funcs=[class_func_def],
        fields=[class_field_var],
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
        body=[
            obj_assign,
            loop,
            set_assign,
            list_assign,
            dict_assign,
            dict_subscript,
        ],
    )

    m = Module(name="ExampleModule", body=[class_def, func_def])

    return CAST([m])


@pytest.fixture
def pid_c_cast():
    # TODO for a C struct, should we make a default init function?
    struct_pid_def = ClassDef(
        name="struct _pid",
        bases=[],
        funcs=[],
        fields=[
            Var(val=Name(name="setSpeed"), type="float"),
            Var(val=Name(name="ActualSpeed"), type="float"),
            Var(val=Name(name="err"), type="float"),
            Var(val=Name(name="err_last"), type="float"),
            Var(val=Name(name="voltage"), type="float"),
            Var(val=Name(name="integral"), type="float"),
            Var(val=Name(name="Kp"), type="float"),
            Var(val=Name(name="Ki"), type="float"),
            Var(val=Name(name="Kd"), type="float"),
        ],
    )
    global_pid_assign = Assignment(
        left=Var(val=Name(name="pid")),
        right=Call(
            func="struct_pid",
            arguments=[],
        ),
    )

    pid_assignments = [
        Assignment(
            left=Attribute(value=Name(name="pid"), attr="SetSpeed"),
            right=Number(number=0.0),
        ),
        Assignment(
            left=Attribute(value=Name(name="pid"), attr="ActualSpeed"),
            right=Number(number=0.0),
        ),
        Assignment(
            left=Attribute(value=Name(name="pid"), attr="err"),
            right=Number(number=0.0),
        ),
        Assignment(
            left=Attribute(value=Name(name="pid"), attr="err_last"),
            right=Number(number=0.0),
        ),
        Assignment(
            left=Attribute(value=Name(name="pid"), attr="voltage"),
            right=Number(number=0.0),
        ),
        Assignment(
            left=Attribute(value=Name(name="pid"), attr="integral"),
            right=Number(number=0.0),
        ),
        Assignment(
            left=Attribute(value=Name(name="pid"), attr="Kp"),
            right=Number(number=0.2),
        ),
        Assignment(
            left=Attribute(value=Name(name="pid"), attr="Ki"),
            right=Number(number=0.015),
        ),
        Assignment(
            left=Attribute(value=Name(name="pid"), attr="Kd"),
            right=Number(number=0.2),
        ),
    ]
    pid_init_func = FunctionDef(name="PID_init", body=pid_assignments)

    pid_realize_body = [
        Assignment(
            left=Attribute(value=Name(name="pid"), attr="SetSpeed"),
            right=Name(name="speed"),
        ),
        Assignment(
            left=Attribute(value=Name(name="pid"), attr="err"),
            right=BinaryOp(
                op=BinaryOperator.SUB,
                left=Attribute(value=Name(name="pid"), attr="SetSpeed"),
                right=Attribute(value=Name(name="pid"), attr="ActualSpeed"),
            ),
        ),
        Assignment(
            left=Attribute(value=Name(name="pid"), attr="integral"),
            right=BinaryOp(
                op=BinaryOperator.ADD,
                left=Attribute(value=Name(name="pid"), attr="integral"),
                right=Attribute(value=Name(name="pid"), attr="err"),
            ),
        ),
        Assignment(
            left=Attribute(value=Name(name="pid"), attr="voltage"),
            right=BinaryOp(
                op=BinaryOperator.MULT,
                left=Attribute(value=Name(name="pid"), attr="Kp"),
                right=BinaryOp(
                    op=BinaryOperator.MULT,
                    left=BinaryOp(
                        op=BinaryOperator.ADD,
                        left=Attribute(value=Name(name="pid"), attr="err"),
                        right=Attribute(value=Name(name="pid"), attr="Ki"),
                    ),
                    right=BinaryOp(
                        op=BinaryOperator.MULT,
                        left=BinaryOp(
                            op=BinaryOperator.ADD,
                            left=Attribute(value=Name(name="pid"), attr="integral"),
                            right=Attribute(value=Name(name="pid"), attr="Kd"),
                        ),
                        right=BinaryOp(
                            op=BinaryOperator.SUB,
                            left=Attribute(value=Name(name="pid"), attr="err"),
                            right=Attribute(value=Name(name="pid"), attr="err_last"),
                        ),
                    ),
                ),
            ),
        ),
        Assignment(
            left=Attribute(value=Name(name="pid"), attr="err_last"),
            right=Attribute(value=Name(name="pid"), attr="err"),
        ),
        Assignment(
            left=Attribute(value=Name(name="pid"), attr="ActualSpeed"),
            right=BinaryOp(
                op=BinaryOperator.MULT,
                left=Attribute(value=Name(name="pid"), attr="voltage"),
                right=Number(number=1.0),
            ),
        ),
        ModelReturn(value=Attribute(value=Name(name="pid"), attr="ActualSpeed")),
    ]
    pid_realize_func = FunctionDef(
        name="PID_realize",
        func_args=[Var(val=Name(name="speed"), type="float")],
        body=pid_realize_body,
    )

    main_pid_init_call = Expr(expr=Call(func=Name(name="PID_init")))
    main_count_init = Assignment(
        left=Var(val=Name(name="count"), type="int"), right=Number(number=0)
    )

    main_loop_speed_assign = Assignment(
        left=Var(val=Name(name="speed")),
        right=Call(func=Name(name="PID_init"), arguments=[Number(number=20.0)]),
    )
    main_loop_count_assign = Assignment(
        left=Var(val=Name(name="count")),
        right=BinaryOp(
            op=BinaryOperator.ADD,
            left=Var(val=Name(name="count")),
            right=Number(number=1),
        ),
    )
    main_loop = Loop(
        expr=BinaryOp(
            op=BinaryOperator.LT,
            left=Name(name="count"),
            right=Number(number=100),
        ),
        body=[main_loop_speed_assign, main_loop_count_assign],
    )
    main_return = ModelReturn(value=Number(number=0))

    main_func = FunctionDef(
        name="main",
        func_args=[],
        body=[main_pid_init_call, main_count_init, main_loop, main_return],
    )

    pid_body = [
        struct_pid_def,
        global_pid_assign,
        pid_init_func,
        pid_realize_func,
        main_func,
    ]
    pid_module = Module(name="PID", body=pid_body)
    return CAST([pid_module])


@pytest.mark.skip("Skipping due to changes in AIR")
def test_basic_function_def_and_assignment(
    basic_function_def_and_assignment_grfn,
    basic_function_def_and_assignment_cast,
):
    generated_grfn = basic_function_def_and_assignment_cast.to_GrFN()
    assert generated_grfn == basic_function_def_and_assignment_grfn


@pytest.mark.skip(reason="Need to implement test.")
def test_cast_with_all_nodes(cast_with_all_nodes_grfn, cast_with_all_nodes):
    pass
    # TODO
    # generated_grfn = cast_with_all_nodes.to_GrFN()
    # assert generated_grfn == cast_with_all_nodes_grfn


@pytest.mark.skip(reason="Need to implement test.")
def test_pid_c_cast(pid_c_cast_grfn, pid_c_cast):
    pass
    # TODO
    # generated_grfn = pid_c_cast.to_GrFN()
    # assert generated_grfn == pid_c_cast_grfn


@pytest.mark.skip(reason="Need to implement test.")
def test_function_call():
    pass


@pytest.mark.skip(reason="Need to implement test.")
def test_if_statement():
    pass


@pytest.mark.skip(reason="Need to implement test.")
def test_if_else_statement():
    pass


@pytest.mark.skip(reason="Need to implement test.")
def test_if_elif_statement():
    pass


@pytest.mark.skip(reason="Need to implement test.")
def test_if_elif_else_statement():
    pass


@pytest.mark.skip(reason="Need to implement test.")
def test_for_loop():
    pass


@pytest.mark.skip(reason="Need to implement test.")
def test_while_loop():
    pass


@pytest.mark.skip(reason="Need to implement test.")
def test_nested_loops():
    pass


@pytest.mark.skip(reason="Need to implement test.")
def test_global_variable_passing():
    pass


@pytest.mark.skip(reason="Need to implement test.")
def test_pack_and_extract():
    pass


@pytest.mark.skip(reason="Need to implement test.")
def test_only_pack():
    pass


@pytest.mark.skip(reason="Need to implement test.")
def test_only_extract():
    pass


def test_unknown_cast_node():
    c = CAST([object()], cast_source_language="")
    with pytest.raises(C2ATypeError):
        c.to_GrFN()
