import typing
from functools import singledispatchmethod

from automates.program_analysis.CAST2GrFN.model.cast import (
    AstNode,
)
from automates.program_analysis.CAST2GrFN.model.cast_to_air_model import (
    C2ATypeError,
)


class CASTVisitor:
    def __init__(self):
        pass

    def visit_list(self, node_list: typing.List[AstNode]):
        return [self.visit(n) for n in node_list]

    @singledispatchmethod
    def visit(self, node: AstNode):
        raise C2ATypeError(f"Unimplemented AST node of type: {type(node)}")
