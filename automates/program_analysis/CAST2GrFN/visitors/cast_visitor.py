from automates.utils.method_dispatch import methdispatch
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


class CASTVisitor:
    def __init__(self):
        pass

    def visit_list(self, node_list: List):
        return [self.visit(n) for n in node_list]

    @methdispatch
    def visit(self, node: AstNode):
        raise NotImplementedError(f"Unimplemented AST node of type: {type(node)}")
