import typing

from .cast_visitor import CASTVisitor

from automates.utils.method_dispatch import methdispatch
from automates.program_analysis.CAST2GrFN.model.cast_to_air_model import (
    C2AState,
    C2AExpression,
    C2AVariable,
    C2AFunction,
    C2ATypeDef,
    CASTToAIRException,
)
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


class CASTToAIRVisitor(CASTVisitor):
    cast: typing.List[AstNode]
    state: C2AState

    def __init__(self, cast):
        self.cast = cast
        self.state = C2AState()

    def to_air(self):
        # TODO create a function visitor to grab function definitions
        self.visit_list(self.cast)
        return self.state.to_AIR()

    @methdispatch
    def visit(self, node: AstNode):
        return NotImplemented

    @visit.register
    def _(self, node: Assignment):

        left_res = self.visit(node.left)
        right_res = self.visit(node.right)

        if isinstance(node.left, Var):
            # If we are assigning to strictly a var, create
            # the new version of the var
            assigned_var_name = left_res.variables[0].name
            new_ver = self.state.find_next_var_version(assigned_var_name)
            version = self.state.find_next_var_version()
            new_var = C2AVariable(
                version,
            )
        else:
            raise CASTToAIRException(
                f"Unable to handle left hand of assignment of type {type(node.left)}"
            )

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
        self.state.push_scope(node.name)
        self.visit_list(node.args)
        self.visit_list(node.body)
        return

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
        # TODO module cast node should be updated with name
        body_res = self.visit_list(node.body)

    @visit.register
    def _(self, node: Name):
        return node.val

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
        name = node.val.val
        var_obj = self.state.find_highest_version_var(name)
        if var_obj is None:
            var_obj = C2AVariable(
                -1,
                name,
                self.state.scope_stack,
                self.state.current_module,
                node.type,
            )

        return C2AExpression([var_obj], name)
