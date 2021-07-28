from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import NoReturn, List
from queue import LifoQueue
import ast

import networkx as nx

from automates.utils.misc import uuid


@dataclass(repr=False, frozen=False)
class ExprAbstractNode(ABC):
    """
    Abstract class for all Expression tree nodes that defines a node with a
    single field `uid` that is used to establish the identity of the created
    node.
    """

    uid: str

    @staticmethod
    def create_node_id() -> str:
        """Used to generate a new UUID4 object that is then stringified for
        use in an object that inherits from this class.

        Returns:
            str: the string representation of a generated UUID object
        """
        return str(uuid.uuid4())

    @abstractmethod
    def get_label(self):
        """A label that will be used to visually identify nodes when viewing
        them in a NetworkX graph.
        """
        pass

    def get_kwargs(self) -> dict:
        """The basic settings for easy viewing of a node in a NetworkX graph

        Returns:
            dict: a collection of useful visual presets
        """
        return {
            "color": "crimson",
            "fontcolor": "black",
            "fillcolor": "white",
            "padding": 15,
            "label": self.get_label(),
        }

    @abstractmethod
    def to_dict(self):
        """Converts the data stored in this node to a dictionary"""
        pass


@dataclass(repr=False, frozen=False)
class ExprVariableNode(ExprAbstractNode):
    """Class def for nodes that hold variables from a GrFN Lambda expression"""

    grfn_uid: str
    identifier: str
    children: List[ExprAbstractNode]

    def __hash__(self) -> hash:
        return hash(self.uid)

    def __eq__(self, other) -> bool:
        return self.uid == other.uid

    def get_label(self) -> str:
        return str(f"VARIABLE\n({self.identifier})")

    def to_dict(self) -> dict:
        return {
            "uid": self.uid,
            "grfn_uid": self.grfn_uid,
            "type": "VARIABLE",
            "identifier": self.identifier,
            "children": self.children,
        }


@dataclass(repr=False, frozen=False)
class ExprOperatorNode(ExprAbstractNode):
    """Class def for nodes that hold operators from a GrFN Lambda expression"""

    operator: str
    children: List[ExprAbstractNode]

    def __hash__(self) -> hash:
        return hash(self.uid)

    def __eq__(self, other) -> bool:
        return self.uid == other.uid

    def get_label(self) -> str:
        return str(f"OPERATOR\n({self.operator})")

    def to_dict(self) -> dict:
        return {
            "uid": self.uid,
            "type": "OPERATOR",
            "operator": self.operator,
            "children": self.children,
        }


@dataclass(repr=False, frozen=False)
class ExprDefinitionNode(ExprAbstractNode):
    """Class def for nodes that hold defs from a GrFN Lambda expression"""

    def_type: str
    children: List[ExprAbstractNode]

    def __hash__(self) -> hash:
        return hash(self.uid)

    def __eq__(self, other) -> bool:
        return self.uid == other.uid

    def get_label(self) -> str:
        return str(f"DEFINITION\n({self.def_type})")

    def to_dict(self) -> dict:
        return {
            "uid": self.uid,
            "type": "DEFINITION",
            "definition": self.def_type,
            "children": self.children,
        }


@dataclass(repr=False, frozen=False)
class ExprValueNode(ExprAbstractNode):
    """Class def for nodes that hold values from a GrFN Lambda expression"""

    value: str
    children: List[ExprAbstractNode]

    def __hash__(self) -> hash:
        return hash(self.uid)

    def __eq__(self, other) -> bool:
        return self.uid == other.uid

    def get_label(self) -> str:
        return str(f"VALUE\n({self.value})")

    def to_dict(self) -> dict:
        return {
            "uid": self.uid,
            "type": "VALUE",
            "value": self.value,
            "children": self.children,
        }


class ExpressionVisitor(ast.NodeVisitor):
    """Lambda expression walker that extends the Python AST NodeVisitor.

    The purpose of this class is to create a list of ExpressionNodes from a
    GrFN Lambda expression. These nodes include child references to other nodes
    in the list which allows the list of nodes to fully represent a tree for
    the lambda Expression.
    """

    def __init__(self):
        """Creates a list for the new expression nodes and stack to track UIDs
        that are used to reference child nodes when creating parent nodes.
        """
        self.nodes = list()
        self.uid_stack = LifoQueue()

    def get_nodes(self) -> List:
        """Return the list of ExpressionNodes that has been accumulated by a
        call to visit().
        """
        return self.nodes

    @staticmethod
    def reverse_uid_list(uids) -> List:
        return list(reversed(uids))

    def visit_Lambda(self, node: ast.Lambda) -> NoReturn:
        """Adds the starting position LAMBDA node for the root of an expression
        tree.

        The expected children of a lambda node are [ARUGMENTS, RETURN]. This
        function also empties the list of nodes before beginning to process a
        new lambda expression.

        Args:
            node (ast.Lambda): a Python AST Lambda node
        """
        self.nodes = list()

        self.generic_visit(node)
        return_uid = ExprAbstractNode.create_node_id()
        root_op_node = self.uid_stack.get()
        return_node = ExprOperatorNode(return_uid, "RETURN", [root_op_node])
        self.nodes.append(return_node)
        args_node = self.uid_stack.get()
        lambda_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(
            ExprDefinitionNode(lambda_uid, "LAMBDA", [args_node, return_uid])
        )

    def visit_arguments(self, node: ast.arguments) -> NoReturn:
        """Creates an ARGUMENTS node that contains an ordered list of the
        arguments to a lambda expression as its children.

        Args:
            node (ast.arguments): A Python AST arguments node
        """
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(
            ExprDefinitionNode(
                new_uid,
                "ARGUMENTS",
                self.reverse_uid_list(
                    [self.uid_stack.get() for _ in range(len(node.args))]
                ),
            )
        )
        self.uid_stack.put(new_uid)

    def visit_arg(self, node: ast.arg) -> NoReturn:
        """Creates a VariableNode for an input argument to a lambda expression.

        Args:
            node (ast.arg): A Python AST Arg node
        """
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(ExprVariableNode(new_uid, "", node.arg, []))
        self.uid_stack.put(new_uid)

    def visit_Constant(self, node: ast.Constant) -> NoReturn:
        """Adds a ValueNode as a leaf that stores some non-variable value to
        the list of nodes.

        Args:
            node (ast.Constant): a Python AST Constant node
        """
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(ExprValueNode(new_uid, node.value, []))
        self.uid_stack.put(new_uid)

    def visit_Dict(self, node: ast.Dict) -> NoReturn:
        """Adds a Variable node with the name COMPOSITE that consists of a
        collection of VariableNodes each with a single ValueNode child to
        represent all elements in the given dictionary.

        Args:
            node (ast.Dict): A Python AST dictionary node
        """
        key_uids = list()
        dict_name_uids = list()
        need_to_pack = False
        for key, val in zip(node.keys, node.values):
            self.visit(val)
            val_uid = self.uid_stack.get()
            if key is None:
                need_to_pack = True
                dict_name_uids.append(val_uid)
                continue

            key_uid = ExprAbstractNode.create_node_id()
            if isinstance(key, ast.Constant):
                self.nodes.append(ExprValueNode(key_uid, key.value, [val_uid]))
            elif isinstance(key, ast.Name):
                self.nodes.append(
                    ExprVariableNode(key_uid, "", key.id, [val_uid])
                )
            else:
                raise TypeError(f"Unrecognized key type in dict: {type(key)}")
            key_uids.append(key_uid)

        new_uid = ExprAbstractNode.create_node_id()
        if need_to_pack:
            pack_uid = ExprAbstractNode.create_node_id()
            self.nodes.append(
                ExprOperatorNode(pack_uid, "PACK", dict_name_uids)
            )
            self.nodes.append(
                ExprVariableNode(new_uid, "", "COMPOSITE", [pack_uid])
            )
        else:
            self.nodes.append(
                ExprVariableNode(new_uid, "", "COMPOSITE", key_uids)
            )
        self.uid_stack.put(new_uid)

    def visit_List(self, node: ast.List) -> NoReturn:
        """Converts a List AST node into a LIST ExpressionNode with child nodes
        for each element in the list.

        Child nodes are ordered according to their position in the list.

        Args:
            node (ast.List): a Python AST List node
        """
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(
            ExprVariableNode(
                new_uid,
                "",
                "LIST",
                self.reverse_uid_list(
                    [self.uid_stack.get() for _ in range(len(node.elts))]
                ),
            )
        )
        self.uid_stack.put(new_uid)

    def visit_Tuple(self, node: ast.Tuple) -> NoReturn:
        """Converts a Tuple AST node into a TUPLE ExpressionNode with child
        nodes for each element in the tuple.

        Child nodes are ordered according to their position in the tuple.

        Args:
            node (ast.Tuple): a Python AST Tuple node
        """
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(
            ExprVariableNode(
                new_uid,
                "",
                "TUPLE",
                self.reverse_uid_list(
                    [self.uid_stack.get() for _ in range(len(node.elts))]
                ),
            )
        )
        self.uid_stack.put(new_uid)

    def visit_Name(self, node: ast.Name) -> NoReturn:
        """Creates a new ExprVariableNode as a leaf in the nodes list.

        Args:
            node (ast.Name): a Python AST Name node
        """
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(ExprVariableNode(new_uid, "", node.id, []))
        self.uid_stack.put(new_uid)

    def visit_Subscript(self, node: ast.Subscript) -> NoReturn:
        """Creates a new ExprVariableNode as a leaf in the nodes list.

        Args:
            node (ast.Name): a Python AST Subscript node
        """
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(
            ExprOperatorNode(
                new_uid,
                "ACCESS",
                self.reverse_uid_list(
                    [self.uid_stack.get(), self.uid_stack.get()]
                ),
            )
        )
        self.uid_stack.put(new_uid)

    def visit_BinOp(self, node: ast.BinOp) -> NoReturn:
        """Creates a new ExprOperatorNode with two children for the operands
        of this operator.

        Args:
            node (ast.BinOp): a Python AST BinOp node
        """
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(
            ExprOperatorNode(
                new_uid,
                node.op.__class__.__name__,
                self.reverse_uid_list(
                    [self.uid_stack.get(), self.uid_stack.get()]
                ),
            )
        )
        self.uid_stack.put(new_uid)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> NoReturn:
        """Creates a new ExprOperatorNode with one child for the operand
        of this operator.

        Args:
            node (ast.UnaryOp): a Python AST UnaryOp node
        """
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(
            ExprOperatorNode(
                new_uid,
                node.op.__class__.__name__,
                [self.uid_stack.get()],
            )
        )
        self.uid_stack.put(new_uid)

    def visit_Compare(self, node: ast.Compare) -> NoReturn:
        """Creates a new ExprOperatorNode with n children for the n operands
        of a comparator operator.

        Args:
            node (ast.Compare): a Python AST Compare node
        """
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        comp_ops_list = [op.__class__.__name__ for op in node.ops]
        comp_ops_name = " / ".join(comp_ops_list)
        num_comp_ops = len(node.comparators) + 1
        self.nodes.append(
            ExprOperatorNode(
                new_uid,
                comp_ops_name,
                self.reverse_uid_list(
                    [self.uid_stack.get() for _ in range(num_comp_ops)]
                ),
            )
        )
        self.uid_stack.put(new_uid)

    def visit_BoolOp(self, node: ast.BoolOp) -> NoReturn:
        """Creates a new ExprOperatorNode with n children for the n operands
        of a boolean operator.

        Args:
            node (ast.BoolOp): a Python AST BoolOp node
        """
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(
            ExprOperatorNode(
                new_uid,
                node.op.__class__.__name__,
                self.reverse_uid_list(
                    [self.uid_stack.get() for _ in range(len(node.values))]
                ),
            )
        )
        self.uid_stack.put(new_uid)

    def visit_IfExp(self, node: ast.IfExp) -> NoReturn:
        """Creates a new ExprOperatorNode with 3 children ordered [condition,
        body, orelse] of a ternary if-expression operator.

        Args:
            node (ast.IfExp): a Python AST IfExp node
        """
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(
            ExprOperatorNode(
                new_uid,
                "IfExpr",
                self.reverse_uid_list(
                    [self.uid_stack.get() for _ in range(3)]
                ),
            )
        )
        self.uid_stack.put(new_uid)

    def visit_Call(self, node: ast.Call) -> NoReturn:
        """Creates a new ExprOperatorNode with a list of children for all
        arguments to the function call.

        Args:
            node (ast.Call): a Python AST Call node
        """
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        num_args = len(node.args) + len(node.keywords)
        self.nodes.append(
            ExprOperatorNode(
                new_uid,
                f"{node.func.id}()",
                self.reverse_uid_list(
                    [self.uid_stack.get() for _ in range(num_args)]
                ),
            )
        )
        self.uid_stack.get()  # Pop the func node off of the stack
        self.uid_stack.put(new_uid)


def nodes2DiGraph(nodes: List[ExprAbstractNode]) -> nx.DiGraph:
    """Creates a NetworkX DiGraph from a list of ExpressionNodes

    Args:
        nodes (List[ExprAbstractNode]): the list of nodes to be converted to
                                        a DiGraph

    Returns:
        nx.DiGraph: A DiGraph that should be a tree
    """
    uid2nodes = {n.uid: n for n in nodes}
    G = nx.DiGraph()
    G.add_nodes_from([(n, n.get_kwargs()) for n in nodes])
    G.add_edges_from(
        [
            (n, uid2nodes[child_uid])
            for n in nodes
            if hasattr(n, "children")
            for child_uid in n.children
        ]
    )
    return G
