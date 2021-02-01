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
from automates.model_assembly.structures import (
    GenericContainer,
    GenericStmt,
    GenericIdentifier,
    GenericDefinition,
    VariableDefinition,
)


class CAST:

    nodes = list()

    def __init__(self, nodes):
        self.nodes = nodes

    def to_json(self):
        """
        Returns a json structure object of the CAST
        """
        pass

    def to_GrFN(self):
        c2a_visitor = CASTToAIRVisitor(self.nodes)
        air = c2a_visitor.to_air()

        C, V, T, D = dict(), dict(), dict(), dict()

        # Create variable definitions
        for var_data in air["variables"]:
            new_var = GenericDefinition.from_dict(var_data)
            V[new_var.identifier] = new_var

        # Create type definitions
        for type_data in air["types"]:
            new_type = GenericDefinition.from_dict(type_data)
            T[new_type.identifier] = new_type

        # Create container definitions
        for con_data in air["containers"]:
            new_container = GenericContainer.from_dict(con_data)
            for in_var in new_container.arguments:
                if in_var not in V:
                    V[in_var] = VariableDefinition.from_identifier(in_var)
            C[new_container.identifier] = new_container

        grfn = GroundedFunctionNetwork.from_AIR(
            GenericIdentifier.from_str("@container::initial::@global::exampleFunction"),
            C,
            V,
            T,
        )
        return grfn

    @classmethod
    def from_python_ast(cls):
        pass

    @classmethod
    def from_json(cls, data):
        """
        Parses json CAST data object and returns the created CAST object
        """
        pass