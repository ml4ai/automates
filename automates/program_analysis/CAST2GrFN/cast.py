import ast
import json
import difflib
import typing
import networkx as nx

from automates.program_analysis.CAST2GrFN.model.cast import (
    AstNode,
    Assignment,
    Attribute,
    BinaryOp,
    BinaryOperator,
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
    SourceRef,
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
    TypeDefinition,
    VariableDefinition,
)

CAST_NODES_TYPES_LIST = [
    AstNode,
    Assignment,
    Attribute,
    BinaryOp,
    BinaryOperator,
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
    SourceRef,
    Subscript,
    Tuple,
    UnaryOp,
    UnaryOperator,
    VarType,
    Var,
]


def compare_name_nodes(name1: Name, name2: Name) -> bool:
    """
    Checks if two Name nodes are equal, by only looking at
    their `name` fields.  The `__eq__` method on `Name` nodes generated
    by Swagger also checks the `id` attribute, which we do not expect
    to be consistent across CAST generations, since it is a UUID
    """
    if not (isinstance(name1, Name) and isinstance(name2, Name)):
        return False
    return name1.name == name2.name


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
    cast_source_language: str

    def __init__(self, nodes: typing.List[AstNode], cast_source_language: str):
        self.nodes = nodes
        self.cast_source_language = cast_source_language

    def __eq__(self, other):
        """
        For equality, the two CAST objects must have the same node data.
        When checking each node, we allow a custom node comparison function.
        Currently, the only case where we do a custom comparison is for Name nodes.
        For all other nodes we use their Swagger generated `__eq__` method
        """
        if len(self.nodes) != len(other.nodes):
            return False

        for i, node in enumerate(self.nodes):
            other_node = other.nodes[i]
            if isinstance(node, Name):
                comparator = compare_name_nodes
            else:
                comparator = lambda n1, n2: n1 == n2

            if not comparator(node, other_node):
                # printing diff to help locating difference
                print(f"CAST __eq__ failed:")
                self_lines = str(node).splitlines()
                other_lines = str(other_node).splitlines()
                for i, diff in enumerate(difflib.ndiff(self_lines, other_lines)):
                    if diff[0]==' ': 
                        continue
                    print(f"Line {i}: {diff}")
                return False

        return True

    def to_AGraph(self):
        G = nx.DiGraph()
        for node in self.nodes:
            print("node", node)
            print("type", type(node))
            for ast_node in ast.walk(node.body):
                for child_node in ast_node.children:
                    G.add_edge(ast_node, child_node)
        A = nx.nx_agraph.to_agraph(G)
        A.graph_attr.update(
            {"dpi": 227, "fontsize": 20, "fontname": "Menlo", "rankdir": "TB"}
        )
        A.node_attr.update({"fontname": "Menlo"})
        return A

    def to_air_dict(self):
        c2a_visitor = CASTToAIRVisitor(self.nodes, self.cast_source_language)
        air = c2a_visitor.to_air()

        main_container = [
            c["name"] for c in air["containers"] if c["name"].endswith("::main")
        ]

        called_containers = [
            s["function"]["name"]
            for c in air["containers"]
            for s in c["body"]
            if s["function"]["type"] == "container"
        ]
        root_containers = [
            c["name"] for c in air["containers"] if c["name"] not in called_containers
        ]

        container_id_to_start_from = None
        if len(main_container) > 0:
            container_id_to_start_from = main_container[0]
        elif len(root_containers) > 0:
            container_id_to_start_from = root_containers[0]
        else:
            # TODO
            raise Exception("Error: Unable to find root container to build GrFN.")

        air["entrypoint"] = container_id_to_start_from

        return air

    def to_AIR(self):
        air = self.to_air_dict()

        C, V, T, D = dict(), dict(), dict(), dict()

        # Create variable definitions
        for var_data in air["variables"]:
            new_var = VariableDefinition.from_data(var_data)
            V[new_var.identifier] = new_var

        # Create type definitions
        for type_data in air["types"]:
            new_type = TypeDefinition.from_dict(type_data)
            T[new_type.identifier] = new_type

        # Create container definitions
        for con_data in air["containers"]:
            new_container = GenericContainer.from_dict(con_data)
            for in_var in new_container.arguments:
                if in_var not in V:
                    V[in_var] = VariableDefinition.from_identifier(in_var)
            C[new_container.identifier] = new_container

        return AutoMATES_IR(
            GenericIdentifier.from_str(air["entrypoint"]), C, V, T, [], [], []
        )

    def to_GrFN(self):
        air = self.to_AIR()
        grfn = GroundedFunctionNetwork.from_AIR(air)
        return grfn

    def write_cast_object(self, cast_value):
        if isinstance(cast_value, list):
            return [self.write_cast_object(val) for val in cast_value]
        elif not isinstance(cast_value, AstNode) and not isinstance(
            cast_value, SourceRef
        ):
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
        elif isinstance(data, (float, int, str, bool)):
            # If we see a primitave type, simply return its value
            return data
        elif all(k in data for k in ("row_start", "row_end", "col_start", "col_end")):
            return SourceRef(
                row_start=data["row_start"],
                row_end=data["row_end"],
                col_start=data["col_start"],
                col_end=data["col_end"],
                source_file_name=data["source_file_name"],
            )

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
    def from_json_data(cls, json_data, cast_source_language="unknown"):
        """
        Parses json CAST data object and returns the created CAST object

        Args:
            data: JSON object with a "nodes" field containing a
            list of the top level nodes

        Returns:
            CAST: The parsed CAST object.
        """
        nodes = cls.parse_cast_json(json_data["nodes"])
        return cls(nodes, cast_source_language)

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
