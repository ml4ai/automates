from .cast_visitor import CASTVisitor

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


class CASTToJsonVisitor(CASTVisitor):
    def __init__(self):
        pass

    @methdispatch
    def visit(self, node: AstNode):
        return NotImplemented

    @visit.register
    def _(self, node: Assignment):
        return NotImplemented

    @visit.register
    def _(self, node: Attribute):
        return NotImplemented

    @visit.register
    def _(self, node: BinaryOp):
        return NotImplemented

    @visit.register
    def _(self, node: BinaryOperator):
        return NotImplemented

    @visit.register
    def _(self, node: Call):
        return NotImplemented

    @visit.register
    def _(self, node: ClassDef):
        return NotImplemented

    @visit.register
    def _(self, node: Dict):
        return NotImplemented

    @visit.register
    def _(self, node: Expr):
        return NotImplemented

    @visit.register
    def _(self, node: FunctionDef):
        return "FunctionDef:"

    @visit.register
    def _(self, node: List):
        return NotImplemented

    @visit.register
    def _(self, node: Loop):
        return NotImplemented

    @visit.register
    def _(self, node: ModelBreak):
        return NotImplemented

    @visit.register
    def _(self, node: ModelContinue):
        return NotImplemented

    @visit.register
    def _(self, node: ModelIf):
        return NotImplemented

    @visit.register
    def _(self, node: ModelReturn):
        return NotImplemented

    @visit.register
    def _(self, node: Module):
        body_res = self.visit_list(node.body)
        return "Module:" + str(body_res)

    @visit.register
    def _(self, node: Name):
        return NotImplemented

    @visit.register
    def _(self, node: Number):
        return NotImplemented

    @visit.register
    def _(self, node: Set):
        return NotImplemented

    @visit.register
    def _(self, node: String):
        return NotImplemented

    @visit.register
    def _(self, node: Subscript):
        return NotImplemented

    @visit.register
    def _(self, node: Tuple):
        return NotImplemented

    @visit.register
    def _(self, node: UnaryOp):
        return NotImplemented

    @visit.register
    def _(self, node: UnaryOperator):
        return NotImplemented

    @visit.register
    def _(self, node: VarType):
        return NotImplemented

    @visit.register
    def _(self, node: Var):
        return NotImplemented
