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


class GCC2CAST:
    def __init__(self, gcc_ast):
        self.gcc_ast = gcc_ast

    def to_cast(self):
        input_file = self.gcc_ast["mainInputFilename"]
        functions = self.gcc_ast["functions"]
        types = self.gcc_ast["recordTypes"]

        body = []

        for f in functions:
            body.append(self.parse_function(f))

        file_module = Module(name=input_file.rsplit(".")[0], body=body)
        return CAST([file_module])

    def parse_variable(self, variable):
        return

    def parse_basic_block(self, bb):
        return []

    def parse_function(self, f):
        name = f["name"]
        basic_blocks = f["basicBlocks"]
        parameters = f["parameters"] if "parameters" in f else []

        arguments = []
        for p in parameters:
            arguments.append(self.parse_variable())

        body = []
        for bb in basic_blocks:
            body.extend(self.parse_basic_block(bb))

        return FunctionDef(name=name, func_args=arguments, body=body)
