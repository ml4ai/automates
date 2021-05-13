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
from automates.model_assembly.air import AutoMATES_IR
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

    def __eq__(self, other):
        return len(self.nodes) == len(other.nodes) and all(
            [
                self_node == other_node
                for self_node, other_node in zip(self.nodes, other.nodes)
            ]
        )

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

        # TODO: fix this to send objects and metadata
        #       (and documentation as a form of metadata)
        air = AutoMATES_IR(
            GenericIdentifier.from_str(
                "@container::initial::@global::exampleFunction"
            ),
            C,
            V,
            T,
            [],
            [],
            [],
        )
        grfn = GroundedFunctionNetwork.from_AIR(air)
        return grfn

    def write_cast_object(self, cast_value):
        if isinstance(cast_value, list):
            return [self.write_cast_object(val) for val in cast_value]
        elif not isinstance(cast_value, AstNode):
            return cast_value

        return dict(
            {
                attr: self.write_cast_object(getattr(cast_value, attr))
                for attr in cast_value.attribute_map.keys()
            },
            **{"node_type": type(cast_value).__name__},
        )

    def to_json_object(self):
        """
        Returns a json object of the CAST
        """
        return {"nodes": [self.write_cast_object(n) for n in self.nodes]}

    def to_json_str(self):
        """
        Returns a json string of the CAST
        """
        return json.dumps(
            self.to_json_object(),
            sort_keys=True,
            indent=4,
        )

    @classmethod
    def parse_cast_json(cls, data):
        if isinstance(data, list):
            # If we see a list parse each one of its elements
            return [cls.parse_cast_json(item) for item in data]
        elif data is None:
            return None
        elif isinstance(data, (float, int, str)):
            # If we see a primitave type, simply return its value
            return data

        if "node_type" in data:
            # Create the object specified by "node_type" object with the values
            # from its children nodes
            for node_type in CAST_NODES_TYPES_LIST:

                if node_type.__name__ == data["node_type"]:
                    node_results = {
                        k: cls.parse_cast_json(v)
                        for k, v in data.items()
                        if k != "node_type"
                    }
                    return node_type(**node_results)

        raise CASTJsonException(
            f"Unable to decode json CAST field with field names: {set(data.keys())}"
        )

    @classmethod
    def from_json_data(cls, json_data):
        """
        Parses json CAST data object and returns the created CAST object

        Args:
            data: JSON object with a "nodes" field containing a
            list of the top level nodes

        Returns:
            CAST: The parsed CAST object.
        """
        nodes = cls.parse_cast_json(json_data["nodes"])
        return cls(nodes)

    @classmethod
    def from_json_file(cls, json_filepath):
        """
        Loads json CAST data from a file and returns the created CAST object

        Args:
            json_filepath: string of a full filepath to a JSON file
                           representing a CAST with a `nodes` field

        Returns:
            CAST: The parsed CAST object.
        """
        return cls.from_json_data(json.load(open(json_filepath, "r")))

    @classmethod
    def from_json_str(cls, json_str):
        """
        Parses json CAST string and returns the created CAST object

        Args:
            json_str: JSON string representing a CAST with a "nodes" field
            containing a list of the top level nodes

        Raises:
            CASTJsonException: If we encounter an unknown CAST node

        Returns:
            CAST: The parsed CAST object.
        """
        return cls.from_json_data(json.loads(json_str))

    @classmethod
    def from_python_ast(cls):
        pass