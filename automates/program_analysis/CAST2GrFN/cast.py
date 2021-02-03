import json
import typing

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

CAST_NODES_TYPES_LIST = [
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
]


class CASTJsonException(Exception):
    """
    Class used to represent exceptions encountered when encoding/decoding CAST json
    """

    pass


class CAST(object):
    """
    Represents the Common Abstract Syntax Tree (CAST) that will be used to generically represent
    any languages AST.
    """

    nodes: typing.List[AstNode]

    def __init__(self, nodes: typing.List[AstNode]):
        self.nodes = nodes

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

    def to_json(self):
        """
        Returns a json object string of the CAST
        """
        return json.dumps([n.to_dict() for n in self.nodes])

    @classmethod
    def from_json(cls, data):
        """
        Parses json CAST data object and returns the created CAST object
        """

        if isinstance(data, list):
            # If we see a list parse each one of its elements
            return [cls.from_json(item) for item in data]
        elif isinstance(data, str) or isinstance(data, int) or isinstance(data, float):
            # If we see a primitave type, simply return its value
            return data

        # For each CAST node type, if the json objects fields are the same as the
        # CAST nodes fields, then create that object with the values from its children nodes
        for node_type in CAST_NODES_TYPES_LIST:
            if node_type.attribute_map.keys() == data.keys():
                node_results = {k: cls.from_json(v) for k, v in data.items()}
                return node_type(**node_results)

        raise CASTJsonException(
            f"Unable to decode json CAST field with field names: {set(data.keys())}"
        )

    @classmethod
    def from_python_ast(cls):
        pass