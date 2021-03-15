from automates.program_analysis.CAST2GrFN.visitors.cast_to_agraph_visitor import CASTToAGraphVisitor

from automates.program_analysis.CAST2GrFN.cast import CAST
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

def basic_function_def_and_assignment_cast():
    v = Var(val=Name(name="exampleVar"), type="float")
    n = Number(number=36.2)
    a = Assignment(left=v, right=n)
    f = FunctionDef(name=Name(name="exampleFunction"), func_args=[], body=[a])
    m = Module(name="ExampleModule", body=[f])
    return CAST([m])

def basic_function_def_and_assignment_math():
    v = Var(val=Name(name="exampleVar"), type="float")
    n1 = Number(number=36.2)
    n2 = Number(number=37.8)
    op = BinaryOp(op="Add",left=n1,right=n2)
    a = Assignment(left=v, right=op)
    f = FunctionDef(name=Name(name="exampleFunction"), func_args=[], body=[a])
    m = Module(name="ExampleModule", body=[f])
    return CAST([m])

def basic_function_def_and_assignment_if():
    v1 = Var(val=Name(name="var"), type="float")
    v2 = Var(val=Name(name="var2"), type="float")
    n1 = Number(number=36.2)
    n2 = Number(number=37.8)
    a = Assignment(left=v1, right=n1)
    b = Assignment(left=v2, right=n2)
    op = BinaryOp(op="Eq",left=n1,right=n2)
    eq = ModelIf(expr=op,body=[a],orelse=b)
    f = FunctionDef(name=Name(name="exampleFunction"), func_args=[], body=[a,b,eq])
    m = Module(name="ExampleModule", body=[f])
    return CAST([m])


def main():
    #V = CASTToAGraphVisitor(basic_function_def_and_assignment_cast())
    #V = CASTToAGraphVisitor(basic_function_def_and_assignment_math())
    V = CASTToAGraphVisitor(basic_function_def_and_assignment_if())
    V.to_pdf("agraph_test")

main()
