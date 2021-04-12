import pytest
import ast

from automates.program_analysis.PyAST2CAST import py_ast_to_cast
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
from automates.program_analysis.CAST2GrFN import cast

DATA_DIR = "tests/data/program_analysis/PyAST2CAST"


def dump_cast(C):
    print(C.to_json_str())


def test_class_1():
    prog_name = "test_class_1.py"
    folder = "class"

    v1 = Var(val=Name(name="x"), type="integer")
    v2 = Var(val=Name(name="y"), type="integer")

    a1 = Assignment(
        left=Attribute(value=Name("self"), attr=Name("x")), right=Number(1)
    )
    a2 = Assignment(
        left=Attribute(value=Name("self"), attr=Name("y")), right=Number(2)
    )

    v_self = Var(val=Name(name="self"), type="integer")

    f1 = FunctionDef(name="__init__", func_args=[v_self], body=[a1, a2])

    c1 = ClassDef(name="Foo", bases=[], funcs=[f1], fields=[v1, v2])

    v3 = Var(val=Name(name="f"), type="integer")
    a3 = Assignment(left=v3, right=Call(func=Name("Foo"), arguments=[]))

    f2 = FunctionDef(name="main", func_args=[], body=[a3])

    expr_1 = Expr(expr=Call(func=Name(name="main"), arguments=[]))
    m = Module(name=prog_name, body=[c1, f2, expr_1])

    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_class_2():
    prog_name = "test_class_2.py"
    folder = "class"

    v1 = Var(val=Name(name="x"), type="integer")
    v2 = Var(val=Name(name="y"), type="integer")
    v_self = Var(val=Name(name="self"), type="integer")

    attr1 = Attribute(value=Name("self"), attr=Name("x"))
    attr2 = Attribute(value=Name("self"), attr=Name("y"))
    a1 = Assignment(left=attr1, right=Number(1))
    a2 = Assignment(left=attr2, right=Number(2))
    f1 = FunctionDef(name="__init__", func_args=[v_self], body=[a1, a2])

    a3 = Assignment(left=attr1, right=attr2)
    ret = ModelReturn(value=attr1)
    f2 = FunctionDef(name="bar", func_args=[v_self], body=[a3, ret])

    c1 = ClassDef(name="Foo", bases=[], funcs=[f1, f2], fields=[v1, v2])

    v3 = Var(val=Name(name="f"), type="integer")
    a3 = Assignment(left=v3, right=Call(func=Name(name="Foo"), arguments=[]))

    attr3 = Attribute(value=Name("f"), attr=Name("bar"))
    expr_1 = Expr(expr=Call(func=attr3, arguments=[]))

    f3 = FunctionDef(name="main", func_args=[], body=[a3, expr_1])
    expr_2 = Expr(expr=Call(func=Name(name="main"), arguments=[]))

    m = Module(name=prog_name, body=[c1, f3, expr_2])

    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_call_1():
    prog_name = "test_call_1.py"
    folder = "expression"

    v1 = Var(val=Name("x"), type="integer")
    e1 = BinaryOp(op=BinaryOperator.MULT, left=Name("x"), right=Name("x"))
    r = ModelReturn(value=e1)
    f1 = FunctionDef(name="foo", func_args=[v1], body=[r])

    v2 = Var(val=Name("x"), type="integer")
    v3 = Var(val=Name("y"), type="integer")
    a1 = Assignment(left=v2, right=Number(2))
    call1 = Call(func=Name("foo"), arguments=[Number(2)])
    add1 = BinaryOp(op=BinaryOperator.ADD, left=Number(3), right=call1)

    a2 = Assignment(left=v3, right=add1)
    call2 = Expr(expr=Call(func=Name("print"), arguments=[Name("y")]))

    f2 = FunctionDef(name="main", func_args=[], body=[a1, a2, call2])

    m = Module(name=prog_name, body=[f1, f2])

    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_list_1():
    prog_name = "test_list_1.py"
    folder = "expression"

    v1 = Var(val=Name("x"), type="integer")
    a1 = Assignment(left=v1, right=List(values=[Number(1.0)]))

    f = FunctionDef(name="main", func_args=[], body=[a1])
    call1 = Expr(expr=(Call(func=Name(name="main"), arguments=[])))

    m = Module(name=prog_name, body=[f, call1])

    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_list_2():
    prog_name = "test_list_2.py"
    folder = "expression"

    v1 = Var(val=Name("x"), type="integer")
    a1 = Assignment(
        left=v1,
        right=List(values=[Number(1), Number(2), Number(3), Number(4)]),
    )

    s1 = Subscript(value=Name(name="x"), slice=Number(2))
    a2 = Assignment(left=s1, right=Number(10))

    add1 = BinaryOp(op=BinaryOperator.ADD, left=Number(1), right=Number(2))
    s2 = Subscript(value=Name(name="x"), slice=add1)
    a3 = Assignment(left=s2, right=Number(7))

    s3 = Subscript(value=Name(name="x"), slice=Number(0))
    s4 = Subscript(value=Name(name="x"), slice=Number(3))
    a4 = Assignment(left=s3, right=s4)

    f = FunctionDef(name="main", func_args=[], body=[a1, a2, a3, a4])
    call1 = Expr(expr=(Call(func=Name(name="main"), arguments=[])))

    m = Module(name=prog_name, body=[f, call1])

    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_add_1():
    prog_name = "test_add_1.py"
    folder = "function_def"

    add1 = Expr(
        BinaryOp(op=BinaryOperator.ADD, left=Number(1), right=Number(2))
    )
    m = Module(name=prog_name, body=[add1])

    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_add_2():
    prog_name = "test_add_2.py"
    folder = "function_def"

    v1 = Var(val=Name("y"), type="integer")
    v2 = Var(val=Name("x"), type="integer")

    a1 = Assignment(left=v1, right=Number(2))
    sub1 = BinaryOp(
        op=BinaryOperator.SUB, left=Number(1), right=Name(name="y")
    )

    a2 = Assignment(left=v2, right=sub1)
    call1 = Expr(Call(func=Name(name="main"), arguments=[]))

    f = FunctionDef(name="main", func_args=[], body=[a1, a2])
    m = Module(name=prog_name, body=[f, call1])

    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_assign_1():
    prog_name = "test_assign_1.py"
    folder = "function_def"

    v1 = Var(val=Name("x"), type="integer")
    n1 = Number(1)
    a = Assignment(left=v1, right=n1)
    f = FunctionDef(name="main", func_args=[], body=[a])
    m = Module(name=prog_name, body=[f])
    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_assign_2():
    prog_name = "test_assign_2.py"
    folder = "function_def"

    v1 = Var(val=Name("x"), type="integer")
    n1 = Number(1)
    n2 = Number(2)
    add = BinaryOp(BinaryOperator.ADD, n1, n2)
    a = Assignment(left=v1, right=add)
    f = FunctionDef(name="main", func_args=[], body=[a])
    m = Module(name=prog_name, body=[f])
    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_assign_3():
    prog_name = "test_assign_3.py"
    folder = "function_def"

    v1 = Var(val=Name("x"), type="integer")
    v2 = Var(val=Name("y"), type="integer")
    n1 = Number(1)
    n2 = Number(2)
    t1 = Tuple(values=[v1, v2])
    t2 = Tuple(values=[n1, n2])
    a = Assignment(left=t1, right=t2)
    f = FunctionDef(name="main", func_args=[], body=[a])
    m = Module(name=prog_name, body=[f])
    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_assign_4():
    prog_name = "test_assign_4.py"
    folder = "function_def"

    n1 = Number(1)
    n2 = Number(2)
    n3 = Number(3)
    n4 = Number(3.0)
    v1 = Var(val=Name("x"), type="integer")

    l1 = List(values=[n1, n2, n3])

    a1 = Assignment(left=v1, right=l1)
    a2 = Assignment(left=Subscript(slice=n1, value=Name(name="x")), right=n4)

    f = FunctionDef(name="main", func_args=[], body=[a1, a2])
    m = Module(name=prog_name, body=[f])
    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_assign_5():
    prog_name = "test_assign_5.py"
    folder = "function_def"

    v1 = Var(val=Name("x"), type="integer")
    v2 = Var(val=Name("y"), type="integer")
    name1 = Name(name="x")
    name2 = Name(name="y")

    add1 = BinaryOp(op=BinaryOperator.ADD, left=name1, right=name2)
    t1 = Tuple(values=[name1, name2, add1])
    ret = ModelReturn(t1)

    f1 = FunctionDef(name="adder", func_args=[v1, v2], body=[ret])

    v3 = Var(val=Name("a"), type="integer")
    v4 = Var(val=Name("b"), type="integer")
    v5 = Var(val=Name("c"), type="integer")

    n1 = Number(1)
    n2 = Number(2)

    t2 = Tuple(values=[v3, v4, v5])
    call1 = Call(func=Name(name="adder"), arguments=[n1, n2])

    a1 = Assignment(left=t2, right=call1)
    call2 = Call(func=Name("str"), arguments=([Name("a")]))
    add2 = BinaryOp(op=BinaryOperator.ADD, left=String("a "), right=call2)
    call3 = Expr(expr=Call(func=Name(name="print"), arguments=[add2]))

    f2 = FunctionDef(name="main", func_args=[], body=[a1, call3])

    m = Module(name=prog_name, body=[f1, f2])
    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_assign_6():
    prog_name = "test_assign_6.py"
    folder = "function_def"

    n1 = Number(100)
    v1 = Var(val=Name("x"), type="integer")
    v2 = Var(val=Name("y"), type="integer")
    v3 = Var(val=Name("z"), type="integer")
    v4 = Var(val=Name("w"), type="integer")

    a1 = Assignment(left=v4, right=n1)
    a2 = Assignment(left=v3, right=a1)
    a3 = Assignment(left=v2, right=a2)
    a4 = Assignment(left=v1, right=a3)

    f = FunctionDef(name="main", func_args=[], body=[a4])
    m = Module(name=prog_name, body=[f])
    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_function_1():
    prog_name = "test_function_1.py"
    folder = "function_def"

    f1 = FunctionDef(name="foo", func_args=[], body=[[]])
    f2 = FunctionDef(name="bar", func_args=[], body=[[]])
    call1 = Expr(Call(func=Name("foo"), arguments=[]))
    call2 = Expr(Call(func=Name("bar"), arguments=[]))

    f = FunctionDef(name="main", func_args=[], body=[call1, call2])

    m = Module(name=prog_name, body=[f1, f2, f])
    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_lambda_1():
    prog_name = "test_lambda_1.py"
    folder = "function_def"

    mult = BinaryOp(BinaryOperator.MULT, left=Name(name="y"), right=Number(2))
    v1 = Var(val=Name(name="y"), type="integer")
    v2 = Var(val=Name(name="x"), type="integer")
    l1 = FunctionDef(name="LAMBDA", func_args=[v1], body=mult)
    a1 = Assignment(left=v2, right=l1)

    f = FunctionDef(name="main", func_args=[], body=[a1])

    m = Module(name=prog_name, body=[f])
    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_if_1():
    prog_name = "test_if_1.py"
    folder = "if"

    v1 = Var(val=Name(name="x"), type="integer")
    a1 = Assignment(left=v1, right=Number(10))

    eq = BinaryOp(BinaryOperator.EQ, left=Name(name="x"), right=Number(10))

    v2 = Var(val=Name(name="y"), type="integer")
    add1 = BinaryOp(op=BinaryOperator.ADD, left=Number(2), right=Number(4))
    a2 = Assignment(left=v2, right=add1)

    if_1 = ModelIf(expr=eq, body=[a2], orelse=[])

    a3 = Assignment(left=v1, right=Number(5))

    f = FunctionDef(name="main", func_args=[], body=[a1, if_1, a3])

    m = Module(name=prog_name, body=[f])
    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_if_2():
    prog_name = "test_if_2.py"
    folder = "if"

    v1 = Var(val=Name(name="x"), type="integer")
    a1 = Assignment(left=v1, right=Number(10))

    eq = BinaryOp(op=BinaryOperator.EQ, left=Name(name="x"), right=Number(5))

    a2 = Assignment(left=v1, right=Number(1))
    a3 = Assignment(left=v1, right=Number(2))

    if_1 = ModelIf(expr=eq, body=[a2], orelse=[a3])

    a4 = Assignment(left=v1, right=Number(3))

    f = FunctionDef(name="main", func_args=[], body=[a1, if_1, a4])

    m = Module(name=prog_name, body=[f])
    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_if_3():
    prog_name = "test_if_3.py"
    folder = "if"

    v1 = Var(val=Name(name="x"), type="integer")
    a1 = Assignment(left=v1, right=Number(10))

    eq1 = BinaryOp(op=BinaryOperator.EQ, left=Name(name="x"), right=Number(5))
    eq2 = BinaryOp(op=BinaryOperator.EQ, left=Name(name="x"), right=Number(6))

    if_1 = ModelIf(expr=eq2, body=[[]], orelse=[[]])
    if_2 = ModelIf(expr=eq1, body=[[]], orelse=[if_1])

    a2 = Assignment(left=v1, right=Number(20))

    f = FunctionDef(name="main", func_args=[], body=[a1, if_2, a2])

    m = Module(name=prog_name, body=[f])
    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_for_1():
    prog_name = "test_for_1.py"
    folder = "loop"
    n1 = Number(1)
    n2 = Number(2)
    n3 = Number(3)
    n4 = Number(4)
    n5 = Number(5)
    v1 = Var(val=Name(name="y"), type="integer")
    v2 = Var(val=Name(name="x"), type="integer")
    a1 = Assignment(left=v1, right=List(values=[n1, n2, n3, n4, n5]))

    count_var = Assignment(Var(Name("i_"), "integer"), Number(0))
    loop_cond = BinaryOp(
        BinaryOperator.LT, Name("i_"), Call(Name("len"), [Name("y")])
    )
    loop_assign = Assignment(
        Var(Name("i"), "integer"), Subscript(Name("y"), Name("i_"))
    )
    loop_body = Assignment(left=v2, right=Number(1))
    loop_increment = Assignment(
        Var(Name("i_"), "integer"),
        BinaryOp(BinaryOperator.ADD, Name("i_"), Number(1)),
    )

    loop = Loop(
        expr=loop_cond, body=[loop_assign] + [loop_body] + [loop_increment]
    )

    f = FunctionDef(name="main", func_args=[], body=[a1, loop])

    m = Module(name=prog_name, body=[f])
    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_for_1():
    prog_name = "test_for_1.py"
    folder = "loop"
    n1 = Number(1)
    n2 = Number(2)
    n3 = Number(3)
    n4 = Number(4)
    n5 = Number(5)
    v1 = Var(val=Name(name="y"), type="integer")
    v2 = Var(val=Name(name="x"), type="integer")
    a1 = Assignment(left=v1, right=List(values=[n1, n2, n3, n4, n5]))

    count_var = Assignment(Var(Name("i_"), "integer"), Number(0))
    loop_cond = BinaryOp(
        BinaryOperator.LT, Name("i_"), Call(Name("len"), [Name("y")])
    )
    loop_assign = Assignment(
        Var(Name("i"), "integer"), Subscript(Name("y"), Name("i_"))
    )
    loop_body = Assignment(left=v2, right=Number(1))
    loop_increment = Assignment(
        Var(Name("i_"), "integer"),
        BinaryOp(BinaryOperator.ADD, Name("i_"), Number(1)),
    )

    loop = Loop(expr=loop_cond, body=[loop_assign, loop_body, loop_increment])

    f = FunctionDef(name="main", func_args=[], body=[a1, loop])

    m = Module(name=prog_name, body=[f])
    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])


def test_while_1():
    prog_name = "test_while_1.py"
    folder = "loop"
    n1 = Number(1)
    n2 = Number(2)
    n3 = Number(3)
    v1 = Var(val=Name(name="b"), type="integer")
    v2 = Var(val=Name(name="i"), type="integer")
    v3 = Var(val=Name(name="a"), type="integer")
    a1 = Assignment(left=v1, right=List(values=[n1, n2, n3]))
    a2 = Assignment(left=v2, right=Number(0))

    loop_cond = BinaryOp(
        BinaryOperator.LT, Name("i"), Call(Name("len"), [Name("b")])
    )
    loop_assign = Assignment(v3, Subscript(Name("b"), Name("i")))
    loop_increment = Assignment(
        v2, BinaryOp(BinaryOperator.ADD, Name("i"), Number(1))
    )

    loop = Loop(expr=loop_cond, body=[loop_assign, loop_increment])

    f = FunctionDef(name="main", func_args=[], body=[a1, a2, loop])

    m = Module(name=prog_name, body=[f])
    C = cast.CAST([m])

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
    file_contents = open(filepath).read()

    convert = py_ast_to_cast.PyASTToCAST()

    test_C = convert.visit(ast.parse(file_contents))
    test_C.name = prog_name

    assert C == cast.CAST([test_C])
