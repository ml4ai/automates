from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import NoReturn, List
from queue import LifoQueue
import ast

import networkx as nx

from ..utils.misc import uuid


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
        """Converts the data stored in this node to a dictionary

        Returns:
            [type]: [description]
        """
        pass


@dataclass(repr=False, frozen=False)
class ExprVariableNode(ExprAbstractNode):
    """Class def for nodes that hold variables from a GrFN Lambda expression"""

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
class ExprValueNode(ExprAbstractNode):
    """Class def for nodes that hold values from a GrFN Lambda expression"""

    value: str

    def __hash__(self) -> hash:
        return hash(self.uid)

    def __eq__(self, other) -> bool:
        return self.uid == other.uid

    def get_label(self) -> str:
        return str(f"VALUE\n({self.value})")

    def to_dict(self) -> dict:
        return {"uid": self.uid, "type": "VALUE", "value": self.value}


class ExpressionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.nodes = list()
        self.uid_stack = LifoQueue()

    def get_nodes(self):
        return self.nodes

    def visit_Lambda(self, node: ast.Lambda) -> NoReturn:
        self.nodes = list()

        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        n1 = self.uid_stack.get()
        new_node = ExprOperatorNode(new_uid, "RETURN", [n1])
        self.nodes.append(new_node)

    def visit_Constant(self, node: ast.Constant) -> NoReturn:
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(ExprValueNode(new_uid, node.value))
        self.uid_stack.put(new_uid)

    def visit_Dict(self, node: ast.Dict) -> NoReturn:
        key_uids = list()
        for key, val in zip(node.keys, node.values):
            val_uid = ExprAbstractNode.create_node_id()
            self.nodes.append(
                ExprValueNode(
                    val_uid,
                    val.value if isinstance(val, ast.Constant) else val.id,
                )
            )

            key_uid = ExprAbstractNode.create_node_id()
            self.nodes.append(ExprVariableNode(key_uid, key.value, [val_uid]))
            key_uids.append(key_uid)

        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(ExprVariableNode(new_uid, "COMPOSITE", key_uids))
        self.uid_stack.put(new_uid)

    def visit_List(self, node: ast.List) -> NoReturn:
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(
            ExprVariableNode(
                new_uid,
                "LIST",
                list(
                    reversed(
                        [self.uid_stack.get() for _ in range(len(node.elts))]
                    )
                ),
            )
        )
        self.uid_stack.put(new_uid)

    def visit_Tuple(self, node: ast.Tuple) -> NoReturn:
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(
            ExprVariableNode(
                new_uid,
                "TUPLE",
                list(
                    reversed(
                        [self.uid_stack.get() for _ in range(len(node.elts))]
                    )
                ),
            )
        )
        self.uid_stack.put(new_uid)

    def visit_Name(self, node: ast.Name) -> NoReturn:
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(ExprVariableNode(new_uid, node.id, []))
        self.uid_stack.put(new_uid)

    def visit_Subscript(self, node: ast.Subscript) -> NoReturn:
        new_uid = ExprAbstractNode.create_node_id()
        if isinstance(node.slice.value, ast.Constant):
            node_name = f"{node.value.id}.{node.slice.value.value}"
        elif isinstance(node.slice.value, ast.Name):
            node_name = f"{node.value.id}.{node.slice.value.id}"
        else:
            raise TypeError(f"Unexpected AST type: {type(node.slice.value)}")
        self.nodes.append(ExprVariableNode(new_uid, node_name, []))
        self.uid_stack.put(new_uid)

    def visit_BinOp(self, node: ast.BinOp) -> NoReturn:
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(
            ExprOperatorNode(
                new_uid,
                node.op.__class__.__name__,
                list(reversed([self.uid_stack.get(), self.uid_stack.get()])),
            )
        )
        self.uid_stack.put(new_uid)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> NoReturn:
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
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        comp_ops_list = [op.__class__.__name__ for op in node.ops]
        comp_ops_name = " / ".join(comp_ops_list)
        self.nodes.append(
            ExprOperatorNode(
                new_uid,
                comp_ops_name,
                list(
                    reversed(
                        [
                            self.uid_stack.get()
                            for _ in range(len(node.comparators) + 1)
                        ]
                    )
                ),
            )
        )
        self.uid_stack.put(new_uid)

    def visit_BoolOp(self, node: ast.BoolOp) -> NoReturn:
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(
            ExprOperatorNode(
                new_uid,
                node.op.__class__.__name__,
                list(
                    reversed(
                        [self.uid_stack.get() for _ in range(len(node.values))]
                    )
                ),
            )
        )
        self.uid_stack.put(new_uid)

    def visit_IfExp(self, node: ast.IfExp) -> NoReturn:
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        self.nodes.append(
            ExprOperatorNode(
                new_uid,
                "IfExpr",
                list(
                    reversed(
                        [
                            self.uid_stack.get(),
                            self.uid_stack.get(),
                            self.uid_stack.get(),
                        ]
                    )
                ),
            )
        )
        self.uid_stack.put(new_uid)

    def visit_Call(self, node: ast.Call) -> NoReturn:
        self.generic_visit(node)
        new_uid = ExprAbstractNode.create_node_id()
        num_args = len(node.args) + len(node.keywords)
        self.nodes.append(
            ExprOperatorNode(
                new_uid,
                f"{node.func.id}()",
                list(
                    reversed([self.uid_stack.get() for _ in range(num_args)])
                ),
            )
        )
        self.uid_stack.get()  # Pop the func node off of the stack
        self.uid_stack.put(new_uid)


def nodes2DiGraph(nodes: List[ExprAbstractNode]) -> nx.DiGraph:
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
