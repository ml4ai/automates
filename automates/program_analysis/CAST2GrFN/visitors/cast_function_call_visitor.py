import typing
from functools import singledispatchmethod

from automates.program_analysis.CAST2GrFN.visitors.cast_visitor import CASTVisitor

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
    Subscript,
    Tuple,
    UnaryOp,
    Var,
)


def flatten(l):
    for el in l:
        if isinstance(el, typing.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el


def get_function_visit_order(cast):
    visitor = CASTFunctionCallVisitor()
    calls = visitor.visit(cast)

    roots = list()
    for k in calls.keys():
        found = False
        for v in calls.values():
            if k in v:
                found = True
                break
        if not found:
            roots.append(k)

    order = list()

    def get_order(name, calls_list):
        if name not in calls_list:
            return
        for call in calls_list[name]:
            get_order(call, calls_list)
        order.append(name)

    for root in roots:
        get_order(root, calls)

    return order


class CASTTypeError(TypeError):
    """Used to create errors in the CASTToAGraphVisitor, in particular
    when the visitor encounters some value that it wasn't expecting.

    Args:
        Exception: An exception that occurred during execution.
    """

    pass


class CASTFunctionCallVisitor(CASTVisitor):
    @singledispatchmethod
    def visit(self, node: AstNode):
        """Generic visitor for unimplemented/unexpected nodes"""
        raise CASTTypeError(f"Unrecognized node type: {type(node)}")

    @visit.register
    def _(self, node: list):
        return self.visit_list(node)

    @visit.register
    def _(self, node: Assignment):
        return self.visit(node.left) + self.visit(node.right)

    @visit.register
    def _(self, node: Attribute):
        return self.visit(node.value) + self.visit(node.attr)

    @visit.register
    def _(self, node: BinaryOp):
        return self.visit(node.left) + self.visit(node.right)

    @visit.register
    def _(self, node: Boolean):
        return []

    @visit.register
    def _(self, node: Call):
        return [node.func.name] + self.visit(node.arguments)

    @visit.register
    def _(self, node: ClassDef):
        # Fields should not have function calles
        return self.visit(node.funcs)

    @visit.register
    def _(self, node: Dict):
        return self.visit(node.keys) + self.visit(node.values)

    @visit.register
    def _(self, node: Expr):
        return self.visit(node.expr)

    @visit.register
    def _(self, node: FunctionDef):
        return (node.name, set(flatten(self.visit(node.body))))

    @visit.register
    def _(self, node: List):
        return self.visit(node.values)

    @visit.register
    def _(self, node: Loop):
        return self.visit(node.expr) + self.visit(node.body)

    @visit.register
    def _(self, node: ModelBreak):
        return []

    @visit.register
    def _(self, node: ModelContinue):
        return []

    @visit.register
    def _(self, node: ModelIf):
        return self.visit(node.expr) + self.visit(node.body) + self.visit(node.orelse)

    @visit.register
    def _(self, node: ModelReturn):
        return self.visit(node.value)

    @visit.register
    def _(self, node: Module):
        return {item[0]: item[1] for item in self.visit(node.body) if len(item) == 2}

    @visit.register
    def _(self, node: Name):
        return []

    @visit.register
    def _(self, node: Number):
        return []

    @visit.register
    def _(self, node: Set):
        return self.visit(node.values)

    @visit.register
    def _(self, node: String):
        return []

    @visit.register
    def _(self, node: Subscript):
        return self.visit(node.value) + self.visit(node.slice)

    @visit.register
    def _(self, node: Tuple):
        return self.visit(node.values)

    @visit.register
    def _(self, node: UnaryOp):
        return self.visit(node.value)

    @visit.register
    def _(self, node: Var):
        return []
