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
from automates.program_analysis.GCC2GrFN.gcc_ast_to_cast_utils import (
    is_valid_operator,
    get_cast_operator,
    gcc_type_to_var_type,
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
        print(variable)
        var_type = variable["type"]
        name = variable["name"]
        cast_type = gcc_type_to_var_type(var_type)
        return Var(val=Name(name=name), type=cast_type)

    def parse_assign_statement(self, stmt):
        lhs = stmt["lhs"]
        operator = stmt["operator"]
        operands = stmt["operands"]

        # Integer assignment, so simply grab the value from the first operand
        # node.
        # Note: this would collapse an expression with only constants in it
        # (i.e. 5 + 10 into 15). If we wanted to preserve the original structure,
        # how do we avoid this collapsing?
        assign_value = None
        if operator == "integer_cst":
            assign_value = Number(number=operands[0]["value"])
        elif is_valid_operator(operator):
            cast_op = get_cast_operator(operator)
            for op in operands:
                op_code = op["code"]
                # if op_code == "integer_cst":
        assign_var = self.parse_variable(lhs)
        return Assignment(left=assign_var, right=assign_value)

    def parse_statement(self, stmt):
        stmt_type = stmt["type"]

        if stmt_type == "assign":
            return [self.parse_assign_statement(stmt)]
        elif stmt_type == "return":
            return []
        else:
            # TODO custom exception
            raise Exception(f"Error: Unknown statement type {stmt_type}")

    def parse_basic_block(self, bb):
        statements = bb["statements"]
        cast_statements = []

        for s in statements:
            cast_statements.extend(self.parse_statement(s))

        return cast_statements

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
