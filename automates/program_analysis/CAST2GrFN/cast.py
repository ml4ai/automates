import json

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
from automates.program_analysis.CAST2GrFN.visitors import (
    CASTToJsonVisitor,
    CASTToAIRVisitor,
)
from automates.model_assembly.networks import GroundedFunctionNetwork


class CAST:

    nodes = list()

    def __init__(self, nodes):
        nodes = nodes

    def to_json(self):
        """
        Returns a json structure object of the CAST
        """
        pass

    def to_GrFN(self):
        c2a_visitor = CASTToAIRVisitor(self.nodes)
        air = c2a_visitor.to_air()

        from pprint import pprint

        pprint(air)

        # grfn = GroundedFunctionNetwork.from_AIR(
        #     con_id,
        #     C,
        #     V,
        #     T,
        # )
        # return grfn

    @classmethod
    def from_python_ast(cls):
        pass

    @classmethod
    def from_json(cls, data):
        """
        Parses json CAST data object and returns the created CAST object
        """
        pass