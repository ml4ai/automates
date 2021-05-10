from __future__ import annotations
from typing import List, Dict, Iterable, Set, Any, Tuple, NoReturn
from abc import ABC, abstractmethod
from functools import singledispatch
from dataclasses import dataclass
from itertools import product
from copy import deepcopy

import datetime
import json
import re
import os

import networkx as nx
import numpy as np
from networkx.algorithms.simple_paths import all_simple_paths
from pygraphviz import AGraph

from .sandbox import load_lambda_function
from .air import AutoMATES_IR
from .structures import (
    GenericContainer,
    LoopContainer,
    GenericStmt,
    CallStmt,
    LambdaStmt,
    GenericIdentifier,
    ContainerIdentifier,
    VariableIdentifier,
    TypeIdentifier,
    ObjectDefinition,
    VariableDefinition,
    TypeDefinition,
    GrFNExecutionException,
)
from .metadata import (
    TypedMetadata,
    ProvenanceData,
    MeasurementType,
    LambdaType,
    DataType,
    DomainSet,
    DomainInterval,
    SuperSet,
    MetadataType,
    MetadataMethod,
    Domain,
)
from ..utils.misc import choose_font, uuid


FONT = choose_font()

dodgerblue3 = "#1874CD"
forestgreen = "#228b22"


@dataclass(repr=False, frozen=False)
class GenericNode(ABC):
    uid: str

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.uid

    @staticmethod
    def create_node_id() -> str:
        return str(uuid.uuid4())

    @abstractmethod
    def get_kwargs(self):
        return NotImplemented

    @abstractmethod
    def get_label(self):
        return NotImplemented


@dataclass(repr=False, frozen=False)
class VariableNode(GenericNode):
    identifier: VariableIdentifier
    metadata: List[TypedMetadata]
    object_ref: str = None
    value: Any = None
    input_value: Any = None

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other) -> bool:
        return self.uid == other.uid

    def __str__(self):
        return str(self.identifier)

    @classmethod
    def from_id(cls, idt: VariableIdentifier, data: VariableDefinition):
        # TODO: use domain constraint information in the future
        d_type = DataType.from_str(data.domain_name)
        m_type = MeasurementType.from_name(data.domain_name)

        def create_domain_elements():
            if MeasurementType.isa_categorical(m_type):
                set_type = SuperSet.from_data_type(d_type)
                return [
                    DomainSet(
                        d_type,
                        set_type,
                        "lambda x: SuperSet.ismember(x, set_type)",
                    )
                ]
            elif MeasurementType.isa_numerical(m_type):
                return [
                    DomainInterval(-float("inf"), float("inf"), False, False)
                ]
            else:
                return []

        dom = Domain(
            MetadataType.DOMAIN,
            ProvenanceData(
                MetadataMethod.PROGRAM_ANALYSIS_PIPELINE,
                ProvenanceData.get_dt_timestamp(),
            ),
            d_type,
            m_type,
            create_domain_elements(),
        )
        metadata = [dom] + data.metadata
        return cls(GenericNode.create_node_id(), idt, metadata)

    def get_fullname(self):
        return f"{self.name}\n({self.index})"

    def get_name(self):
        return str(self.identifier)

    def get_kwargs(self):
        is_exit = self.identifier.var_name == "EXIT"
        return {
            "color": "crimson",
            "fontcolor": "white" if is_exit else "black",
            "fillcolor": "crimson" if is_exit else "white",
            "style": "filled" if is_exit else "",
            "padding": 15,
            "label": self.get_label(),
        }

    @staticmethod
    def get_node_label(base_name):
        if "_" in base_name:
            if base_name.startswith("IF_") or base_name.startswith("COND_"):
                snake_case_tokens = [base_name]
            else:
                snake_case_tokens = base_name.split("_")
        else:
            snake_case_tokens = [base_name]

        # If the identifier is an all uppercase acronym (like `WMA`) then we
        # need to capture that. But we also the case where the first two
        # letters are capitals but the first letter does not belong with
        # the second (like `AVariable`). We also need to capture the case of
        # an acronym followed by a capital for the next word (like `AWSVars`).
        camel_case_tokens = list()
        for token in snake_case_tokens:
            if token.islower() or token.isupper():
                camel_case_tokens.append(token)
            else:
                # NOTE: special case rule for derivatives
                if re.match(r"^d[A-Z]", token) is not None:
                    camel_case_tokens.append(token)
                else:
                    camel_split = re.split(
                        r"([A-Z]+|[A-Z]?[a-z]+)(?=[A-Z]|\b)", token
                    )
                    camel_case_tokens.extend(camel_split)

        clean_tokens = [t for t in camel_case_tokens if t != ""]
        label = ""
        cur_length = 0
        for token in clean_tokens:
            tok_len = len(token)
            if cur_length == 0:
                label += token + " "
                cur_length += tok_len + 1
                continue

            if cur_length >= 8:
                label += "\n"
                cur_length = 0

            if cur_length + tok_len < 8:
                label += token + " "
                cur_length += tok_len + 1
            else:
                label += token
                cur_length += tok_len

        return label

    def get_label(self):
        node_label = self.get_node_label(self.identifier.var_name)
        return node_label

    # def get_label(self):
    #     return self.identifier.var_name

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["uid"],
            VariableIdentifier.from_str(data["identifier"]),
            data["object_ref"] if "object_ref" in data else "",
            [TypedMetadata.from_data(mdict) for mdict in data["metadata"]]
            if "metadata" in data
            else [],
        )

    def to_dict(self) -> dict:
        return {
            "uid": self.uid,
            "identifier": str(self.identifier),
            "object_ref": self.object_ref,
            "metadata": [m.to_dict() for m in self.metadata],
        }


@dataclass(repr=False, frozen=False)
class LambdaNode(GenericNode):
    func_type: LambdaType
    func_str: str
    function: callable
    metadata: List[TypedMetadata]

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other) -> bool:
        return self.uid == other.uid

    def __str__(self):
        return f"{self.get_label()}: {self.uid}"

    def __call__(self, *values) -> Iterable[np.ndarray]:
        expected_num_args = len(self.get_signature())
        input_num_args = len(values)
        if expected_num_args != input_num_args:
            raise RuntimeError(
                f"""Incorrect number of inputs
                (expected {expected_num_args} found {input_num_args})
                for lambda:\n{self.func_str}"""
            )
        try:
            if self.np_shape != (1,):
                res = self.v_function(*values)
            else:
                res = self.function(*values)
            if self.func_type == LambdaType.LITERAL:
                return [np.full(self.np_shape, res, dtype=np.float64)]
            elif isinstance(res, tuple):
                return [item for item in res]
            else:
                return [self.parse_result(values, res)]
        except Exception as e:
            print(f"Exception occured in {self.func_str}")
            raise GrFNExecutionException(e)

    def parse_result(self, values, res):
        if isinstance(res, dict):
            res = {k: self.parse_result(values, v) for k, v in res.items()}
        elif len(values) == 0:
            res = np.full(self.np_shape, res, dtype=np.float64)
        return res

    def get_kwargs(self):
        return {"shape": "rectangle", "padding": 10, "label": self.get_label()}

    def get_label(self):
        return self.func_type.shortname()

    def get_signature(self):
        return self.function.__code__.co_varnames

    @classmethod
    def from_AIR(
        cls, lm_id: str, lm_type: str, lm_str: str, mdata: List[TypedMetadata]
    ):
        lambda_fn = load_lambda_function(lm_str)
        if mdata is None:
            mdata = list()
        return cls(lm_id, lm_type, lm_str, lambda_fn, mdata)

    @classmethod
    def from_dict(cls, data: dict):
        lambda_fn = load_lambda_function(data["lambda"])
        lambda_type = LambdaType.from_str(data["type"])
        if "metadata" in data:
            metadata = [TypedMetadata.from_data(d) for d in data["metadata"]]
        else:
            metadata = []
        return cls(
            data["uid"],
            lambda_type,
            data["lambda"],
            lambda_fn,
            metadata,
        )

    def to_dict(self) -> dict:
        return {
            "uid": self.uid,
            "type": str(self.func_type),
            "lambda": self.func_str,
            "metadata": [m.to_dict() for m in self.metadata],
        }


@dataclass
class HyperEdge:
    inputs: Iterable[VariableNode]
    lambda_fn: LambdaNode
    outputs: Iterable[VariableNode]

    def __call__(self):
        result = self.lambda_fn(
            *[
                var.value if var.value is not None else var.input_value
                for var in self.inputs
            ]
        )
        # If we are in the exit decision hyper edge and in vectorized execution
        if (
            self.lambda_fn.func_type == LambdaType.DECISION
            and any([o.identifier.var_name == "EXIT" for o in self.inputs])
            and self.lambda_fn.np_shape != (1,)
        ):
            # Initialize seen exits to an array of False if it does not exist
            if not hasattr(self, "seen_exits"):
                self.seen_exits = np.full(
                    self.lambda_fn.np_shape, False, dtype=np.bool
                )

            # Gather the exit conditions for this execution
            exit_var_values = [
                o for o in self.inputs if o.identifier.var_name == "EXIT"
            ][0].value

            # For each output value, update output nodes with new value that
            # just exited, otherwise keep existing value
            for i, out_val in enumerate(result):
                # If we have seen an exit before at a given position, keep the
                # existing value, otherwise update.
                self.outputs[i].value = np.where(
                    self.seen_exits, np.copy(self.outputs[i].value), out_val
                )

            # Update seen_exits with any vectorized positions that may have
            # exited during this execution
            self.seen_exits = np.copy(self.seen_exits) | exit_var_values

        else:
            for i, out_val in enumerate(result):
                variable = self.outputs[i]
                if (
                    self.lambda_fn.func_type == LambdaType.LITERAL
                    and variable.input_value is not None
                ):
                    variable.value = variable.input_value
                else:
                    variable.value = out_val

    def __eq__(self, other) -> bool:
        return (
            self.lambda_fn == other.lambda_fn
            and all([i1 == i2 for i1, i2 in zip(self.inputs, other.inputs)])
            and all([o1 == o2 for o1, o2 in zip(self.outputs, other.outputs)])
        )

    def __hash__(self):
        return hash(
            (
                self.lambda_fn.uid,
                tuple([inp.uid for inp in self.inputs]),
                tuple([out.uid for out in self.outputs]),
            )
        )

    @classmethod
    def from_dict(cls, data: dict, all_nodes: Dict[str, GenericNode]):
        return cls(
            [all_nodes[n_id] for n_id in data["inputs"]],
            all_nodes[data["function"]],
            [all_nodes[n_id] for n_id in data["outputs"]],
        )

    def to_dict(self) -> dict:
        return {
            "inputs": [n.uid for n in self.inputs],
            "function": self.lambda_fn.uid,
            "outputs": [n.uid for n in self.outputs],
        }


@dataclass(repr=False)
class GrFNSubgraph:
    uid: str
    namespace: str
    scope: str
    basename: str
    occurrence_num: int
    parent: str
    type: str
    border_color: str
    nodes: Iterable[GenericNode]
    metadata: List[TypedMetadata]

    def __hash__(self):
        return hash(self.__str__())

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        context = f"{self.namespace}.{self.scope}"
        return f"{self.basename}::{self.occurrence_num} ({context})"

    def __eq__(self, other) -> bool:
        return (
            self.occurrence_num == other.occurrence_num
            and self.border_color == other.border_color
            and set([n.uid for n in self.nodes])
            == set([n.uid for n in other.nodes])
        )

    def __call__(
        self,
        grfn: GroundedFunctionNetwork,
        subgraphs_to_hyper_edges: Dict[GrFNSubgraph, List[HyperEdge]],
        node_to_subgraph: Dict[LambdaNode, GrFNSubgraph],
        all_nodes_visited: Set[VariableNode],
    ) -> List[GenericNode]:
        """
        Handles the execution of the lambda functions within a subgraoh of
        GrFN. We place the logic in this function versus directly in __call__
        so the logic can be shared in the loop subgraph type.

        Args:
            grfn (GroundedFucntioNetwork):
                The GrFN we are operating on. Used to find successors of nodes.
            subgraphs_to_hyper_edges (Dict[GrFNSubgraph, List[HyperEdge]]):
                A list of a subgraph to the hyper edges with nodes in the
                subgraph.
            node_to_subgraph (Dict[LambdaNode, GrFNSubgraph]):
                nodes to the subgraph they are contained in.
            all_nodes_visited (Set[VariableNode]):
                Holds the set of all variable nodes that have been visited

        Raises:
            Exception: Raised when we find multiple input interface nodes.

        Returns:
            List[GenericNode]: The final list of nodes that we update/output
            to in the parent container.
        """
        # Grab all hyper edges in this subgraph
        hyper_edges = subgraphs_to_hyper_edges[self]
        nodes_to_hyper_edge = {e.lambda_fn: e for e in hyper_edges}

        # There should be only one lambda node of type interface with outputs
        # all in the same subgraph. Identify this node as the entry point of
        # execution within this subgraph. Will be none if no input.
        input_interface_hyper_edge_node = self.get_input_interface_hyper_edge(
            hyper_edges
        )
        output_interface_hyper_edge_node = self.get_output_interface_node(
            hyper_edges
        )

        # Add nodes that must be configured via user input as they have no
        # input edge
        standalone_vars = [
            n
            for n in self.nodes
            if isinstance(n, VariableNode) and grfn.in_degree(n) == 0
        ]
        all_nodes_visited.update(standalone_vars)

        # Find the hyper edge nodes with no input to initialize the execution
        # queue and var nodes with no incoming edges
        node_execute_queue = [
            e.lambda_fn for e in hyper_edges if len(e.inputs) == 0
        ]
        node_execute_queue.extend(
            [s for n in standalone_vars for s in grfn.successors(n)]
        )

        if input_interface_hyper_edge_node:
            node_execute_queue.insert(
                0, input_interface_hyper_edge_node.lambda_fn
            )

        # Need to recurse to a different subgraph if no nodes to execute here
        if len(node_execute_queue) == 0:
            global_literal_nodes = [
                n
                for n in grfn.nodes
                if isinstance(n, LambdaNode)
                and grfn.in_degree(n) == 0
                and n.func_type == LambdaType.LITERAL
            ]
            global_output_vars = [
                n
                for n in grfn.nodes
                if isinstance(n, VariableNode) and grfn.out_degree(n) == 0
            ]

            # Choose a literal node with maximum distance to the output
            # to begin recursing.
            lit_node_to_max_dist = dict()
            for (l_node, o_node) in product(
                global_literal_nodes, global_output_vars
            ):
                max_dist = max(
                    [
                        len(path)
                        for path in all_simple_paths(grfn, l_node, o_node)
                    ]
                )
                lit_node_to_max_dist[l_node] = max_dist
            lits_by_dist = sorted(
                list(lit_node_to_max_dist.items()),
                key=lambda t: t[1],
                reverse=True,
            )
            (L_node, _) = lits_by_dist[0]
            subgraph = node_to_subgraph[L_node]
            subgraph_hyper_edges = subgraphs_to_hyper_edges[subgraph]
            subgraph_input_interface = subgraph.get_input_interface_hyper_edge(
                subgraph_hyper_edges
            )
            subgraph_outputs = subgraph(
                grfn,
                subgraphs_to_hyper_edges,
                node_to_subgraph,
                all_nodes_visited,
            )

            node_execute_queue.extend(
                set(
                    f_node
                    for o_node in subgraph_outputs
                    for f_node in grfn.successors(o_node)
                    if f_node not in all_nodes_visited
                )
            )

        while node_execute_queue:
            executed = True
            executed_visited_variables = set()
            node_to_execute = node_execute_queue.pop(0)

            # TODO remove?
            if node_to_execute in all_nodes_visited:
                continue

            if node_to_execute not in nodes_to_hyper_edge:
                # Node is not in current subgraph
                if node_to_execute.func_type == LambdaType.INTERFACE:
                    subgraph = node_to_subgraph[node_to_execute]
                    subgraph_hyper_edges = subgraphs_to_hyper_edges[subgraph]
                    subgraph_input_interface = (
                        subgraph.get_input_interface_hyper_edge(
                            subgraph_hyper_edges
                        )
                    )
                    # Either the subgraph has no input interface or all the
                    # inputs must be set.
                    if subgraph_input_interface is None or all(
                        [
                            n in all_nodes_visited
                            for n in subgraph_input_interface.inputs
                        ]
                    ):
                        # We need to recurse into a new subgraph as the
                        # next node is an interface thats not in the
                        # current subgraph

                        # subgraph execution returns the updated output nodes
                        # so we can mark them as visited here in the parent
                        # in order to continue execution
                        executed_visited_variables.update(
                            subgraph(
                                grfn,
                                subgraphs_to_hyper_edges,
                                node_to_subgraph,
                                all_nodes_visited,
                            )
                        )
                    else:
                        node_to_execute = subgraph_input_interface.lambda_fn
                        executed = False
                else:
                    raise GrFNExecutionException(
                        "Error: Attempting to execute non-interface node"
                        + f" {node_to_execute} found in another subgraph."
                    )
            elif all(
                [
                    n in all_nodes_visited
                    for n in nodes_to_hyper_edge[node_to_execute].inputs
                ]
            ):
                # All of the input nodes have been visited, so the input values
                # are initialized and we can execute. In the case of literal
                # nodes, inputs is empty and all() will default to True.
                to_execute = nodes_to_hyper_edge[node_to_execute]
                to_execute()
                executed_visited_variables.update(to_execute.outputs)
            else:
                # We still are waiting on input values to be computed, push to
                # the back of the queue
                executed = False

            if executed:
                all_nodes_visited.update(executed_visited_variables)
                all_nodes_visited.add(node_to_execute)
                node_execute_queue.extend(
                    [
                        succ
                        for var in executed_visited_variables
                        for succ in grfn.successors(var)
                        if (
                            succ in self.nodes
                            and succ not in all_nodes_visited
                        )
                        or (
                            var in self.nodes
                            and succ.func_type == LambdaType.INTERFACE
                        )
                    ]
                )
            else:
                node_execute_queue.extend(
                    [
                        lambda_pred
                        for var_pred in grfn.predecessors(node_to_execute)
                        for lambda_pred in grfn.predecessors(var_pred)
                        if (
                            lambda_pred in self.nodes
                            and lambda_pred not in all_nodes_visited
                        )
                        or lambda_pred.func_type == LambdaType.INTERFACE
                    ]
                )
                node_execute_queue.append(node_to_execute)

        return (
            {}
            if not output_interface_hyper_edge_node
            else {n for n in output_interface_hyper_edge_node.outputs}
        )

    @classmethod
    def from_container(
        cls, con: GenericContainer, occ: int, parent_subgraph: GrFNSubgraph
    ):
        id = con.identifier

        class_to_create = cls
        if isinstance(con, LoopContainer):
            class_to_create = GrFNLoopSubgraph

        return class_to_create(
            str(uuid.uuid4()),
            id.namespace,
            id.scope,
            id.con_name,
            occ,
            None if parent_subgraph is None else parent_subgraph.uid,
            con.__class__.__name__,
            cls.get_border_color(con.__class__.__name__),
            [],
            con.metadata,
        )

    def get_input_interface_hyper_edge(self, hyper_edges):
        """
        Get the interface node for input in this subgraph

        Args:
            hyper_edges (List[HyperEdge]): All hyper edges with nodes in this
                subgraph.

        Returns:
            LambdaNode: The lambda node for the input interface. None if there
                is no input for this subgraph.
        """
        input_interfaces = [
            e
            for e in hyper_edges
            if e.lambda_fn.func_type == LambdaType.INTERFACE
            and all([o in self.nodes for o in e.outputs])
        ]

        if len(input_interfaces) > 1 and self.parent:
            raise GrFNExecutionException(
                "Found multiple input interface nodes"
                + " in subgraph during execution."
                + f" Expected 1 but {len(input_interfaces)} were found."
            )
        elif len(input_interfaces) == 0:
            return None

        return input_interfaces[0]

    def get_output_interface_node(self, hyper_edges):
        """
        Get the interface node for output in this subgraph

        Args:
            hyper_edges (List[HyperEdge]): All hyper edges with nodes in this
                subgraph.

        Returns:
            LambdaNode: The lambda node for the output interface.
        """
        output_interfaces = [
            e
            for e in hyper_edges
            if e.lambda_fn.func_type == LambdaType.INTERFACE
            and all([o in self.nodes for o in e.inputs])
        ]

        if not self.parent:
            # The root subgraph has no output interface
            return None
        elif len(output_interfaces) != 1:
            raise GrFNExecutionException(
                "Found multiple output interface nodes"
                + " in subgraph during execution."
                + f" Expected 1 but {len(output_interfaces)} were found."
            )
        return output_interfaces[0]

    @staticmethod
    def get_border_color(type_str):
        if type_str == "CondContainer":
            return "orange"
        elif type_str == "FuncContainer":
            return "forestgreen"
        elif type_str == "LoopContainer":
            return "navyblue"
        else:
            raise TypeError(f"Unrecognized subgraph type: {type_str}")

    @classmethod
    def from_dict(cls, data: dict, all_nodes: Dict[str, GenericNode]):
        subgraph_nodes = [all_nodes[n_id] for n_id in data["nodes"]]
        type_str = data["type"]

        class_to_create = cls
        if type_str == "LoopContainer":
            class_to_create = GrFNLoopSubgraph

        return class_to_create(
            data["uid"],
            data["namespace"],
            data["scope"],
            data["basename"],
            data["occurrence_num"],
            data["parent"],
            type_str,
            cls.get_border_color(type_str),
            subgraph_nodes,
            [TypedMetadata.from_data(d) for d in data["metadata"]]
            if "metadata" in data
            else [],
        )

    def to_dict(self):
        return {
            "uid": self.uid,
            "namespace": self.namespace,
            "scope": self.scope,
            "basename": self.basename,
            "occurrence_num": self.occurrence_num,
            "parent": self.parent,
            "type": self.type,
            "border_color": self.border_color,
            "nodes": [n.uid for n in self.nodes],
            "metadata": [m.to_dict() for m in self.metadata],
        }


@dataclass(repr=False, eq=False)
class GrFNLoopSubgraph(GrFNSubgraph):
    def __call__(
        self,
        grfn: GroundedFunctionNetwork,
        subgraphs_to_hyper_edges: Dict[GrFNSubgraph, List[HyperEdge]],
        node_to_subgraph: Dict[LambdaNode, GrFNSubgraph],
        all_nodes_visited: Set[VariableNode],
    ):
        """
        Handle a call statement on an object of type GrFNSubgraph

        Args:
            grfn (GroundedFucntioNetwork):
                The GrFN we are operating on. Used to find successors of nodes.
            subgraphs_to_hyper_edges (Dict[GrFNSubgraph, List[HyperEdge]]):
                A list of a subgraph to the hyper edges with nodes in the
                subgraph.
            node_to_subgraph (Dict[LambdaNode, GrFNSubgraph]):
                nodes to the subgraph they are contained in.
            all_nodes_visited (Set[VariableNode]):
                Holds the set of all variable nodes that have been visited
        """

        # First, find exit node within the subgraph
        exit_var_nodes = [
            n
            for n in self.nodes
            if isinstance(n, VariableNode) and n.identifier.var_name == "EXIT"
        ]
        if len(exit_var_nodes) != 1:
            raise GrFNExecutionException(
                "Found incorrect number of exit var nodes in"
                + " loop subgraph during execution."
                + f" Expected 1 but {len(exit_var_nodes)} were found."
            )
        exit_var_node = exit_var_nodes[0]

        # Find the first decision node and mark its input variables as
        # visited so we can execute the cyclic portion of the loop
        input_interface = self.get_input_interface_hyper_edge(
            subgraphs_to_hyper_edges[self]
        )
        initial_decision = {
            n
            for v in input_interface.outputs
            for n in grfn.successors(v)
            if n.func_type == LambdaType.DECISION
        }
        first_decision_vars = {
            v
            for lm_node in initial_decision
            for v in grfn.predecessors(lm_node)
            if isinstance(v, VariableNode)
        }

        var_results = set()
        initial_visited_nodes = set()
        # Loop until the exit value becomes true
        while (
            exit_var_node.value is None
            or (
                isinstance(exit_var_node.value, bool)
                and not exit_var_node.value
            )
            or (
                isinstance(exit_var_node.value, np.ndarray)
                and not all(exit_var_node.value)
            )
        ):
            initial_visited_nodes = all_nodes_visited.copy()
            initial_visited_nodes.update(first_decision_vars)
            var_results = super().__call__(
                grfn,
                subgraphs_to_hyper_edges,
                node_to_subgraph,
                initial_visited_nodes,
            )
        all_nodes_visited = all_nodes_visited.union(initial_visited_nodes)
        return var_results


class GrFNType:
    name: str
    fields: List[Tuple[str, str]]

    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

    def get_initial_dict(self):
        d = {}
        for field in self.fields:
            d[field] = None
        return d


class GroundedFunctionNetwork(nx.DiGraph):
    def __init__(
        self,
        uid: str,
        id: ContainerIdentifier,
        timestamp: str,
        G: nx.DiGraph,
        H: List[HyperEdge],
        S: nx.DiGraph,
        T: List[TypeDefinition],
        M: List[TypedMetadata],
    ):
        super().__init__(G)
        self.hyper_edges = H
        self.subgraphs = S

        self.uid = uid
        self.timestamp = timestamp
        self.namespace = id.namespace
        self.scope = id.scope
        self.name = id.con_name
        self.label = f"{self.name} ({self.namespace}.{self.scope})"
        self.metadata = M

        self.variables = [n for n in self.nodes if isinstance(n, VariableNode)]
        self.lambdas = [n for n in self.nodes if isinstance(n, LambdaNode)]
        self.types = T

        # NOTE: removing detached variables from GrFN
        del_indices = list()
        for idx, var_node in enumerate(self.variables):
            found_var = False
            for edge in self.hyper_edges:
                if var_node in edge.inputs or var_node in edge.outputs:
                    found_var = True
                    break
            if not found_var:
                self.remove_node(var_node)
                del_indices.append(idx)
        for idx in del_indices:
            del self.variables[idx]

        root_subgraphs = [s for s in self.subgraphs if not s.parent]
        if len(root_subgraphs) != 1:
            raise Exception(
                "Error: Incorrect number of root subgraphs found in GrFN."
                + f"Should be 1 and found {len(root_subgraphs)}."
            )
        self.root_subgraph = root_subgraphs[0]

        for lambda_node in self.lambdas:
            lambda_node.v_function = np.vectorize(lambda_node.function)

        # TODO decide how we detect configurable inputs for execution
        # Configurable inputs are all variables assigned to a literal in the
        # root level subgraph AND input args to the root level subgraph
        self.inputs = [
            n
            for e in self.hyper_edges
            for n in e.outputs
            if (
                n in self.root_subgraph.nodes
                and e.lambda_fn.func_type == LambdaType.LITERAL
            )
        ]
        self.inputs.extend(
            [
                n
                for n, d in self.in_degree()
                if d == 0 and isinstance(n, VariableNode)
            ]
        )
        self.literal_vars = list()
        for var_node in self.variables:
            preds = list(self.predecessors(var_node))
            if len(preds) > 0 and preds[0].func_type == LambdaType.LITERAL:
                self.literal_vars.append(var_node)
        self.outputs = [
            n
            for n, d in self.out_degree()
            if d == 0
            and isinstance(n, VariableNode)
            and n in self.root_subgraph.nodes
        ]

        self.uid2varnode = {v.uid: v for v in self.variables}

        self.input_names = [var_node.identifier for var_node in self.inputs]

        self.output_names = [var_node.identifier for var_node in self.outputs]

        self.input_name_map = {
            var_node.identifier.var_name: var_node for var_node in self.inputs
        }
        self.input_identifier_map = {
            var_node.identifier: var_node for var_node in self.inputs
        }
        self.literal_identifier_map = {
            var_node.identifier: var_node for var_node in self.literal_vars
        }

        self.output_name_map = {
            var_node.identifier.var_name: var_node for var_node in self.outputs
        }
        self.FCG = self.to_FCG()
        self.function_sets = self.build_function_sets()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other) -> bool:
        return (
            set(self.hyper_edges) == set(other.hyper_edges)
            and set(self.subgraphs) == set(other.subgraphs)
            and set(self.inputs) == set(other.inputs)
            and set(self.outputs) == set(other.outputs)
        )

    def __str__(self):
        L_sz = str(len(self.lambdas))
        V_sz = str(len(self.variables))
        I_sz = str(len(self.inputs))
        O_sz = str(len(self.outputs))
        size_str = f"< |L|: {L_sz}, |V|: {V_sz}, |I|: {I_sz}, |O|: {O_sz} >"
        return f"{self.label}\n{size_str}"

    def __call__(
        self, inputs: Dict[str, Any], literals: Dict[str, Any] = None
    ) -> Iterable[Any]:
        """Executes the GrFN over a particular set of inputs and returns the
        result.

        Args:
            inputs: Input set where keys are the identifier strings of input
            nodes in the GrFN and each key points to a set of input values
            (or just one)
            literals: Input set where keys are the identifier strings of
            variable nodes in the GrFN that inherit directly from a literal
            node and each key points to a set of input values (or just one)

        Returns:
            A set of outputs from executing the GrFN, one for every set of
            inputs.
        """
        self.np_shape = (1,)
        # TODO: update this function to work with new GrFN object
        full_inputs = {
            self.input_identifier_map[VariableIdentifier.from_str(n)]: v
            for n, v in inputs.items()
        }
        # Set input values
        for input_node in [n for n in self.inputs if n in full_inputs]:
            value = full_inputs[input_node]
            # TODO: need to find a way to incorporate a 32/64 bit check here
            if isinstance(value, float):
                value = np.array([value], dtype=np.float64)
            if isinstance(value, int):
                value = np.array([value], dtype=np.int64)
            elif isinstance(value, list):
                value = np.array(value)
                self.np_shape = value.shape
            elif isinstance(value, np.ndarray):
                self.np_shape = value.shape

            input_node.input_value = value

        if literals is not None:
            literal_ids = set(
                [
                    VariableIdentifier.from_str(var_id)
                    for var_id in literals.keys()
                ]
            )
            lit_id2val = {
                lit_id: literals[str(lit_id)] for lit_id in literal_ids
            }
            literal_overrides = [
                (var_node, lit_id2val[identifier])
                for identifier, var_node in self.literal_identifier_map.items()
                if identifier in literal_ids
            ]
            for input_node, value in literal_overrides:
                # TODO: need to find a way to incorporate a 32/64 bit check here
                if isinstance(value, float):
                    value = np.array([value], dtype=np.float64)
                if isinstance(value, int):
                    value = np.array([value], dtype=np.int64)
                elif isinstance(value, list):
                    value = np.array(value)
                    self.np_shape = value.shape
                elif isinstance(value, np.ndarray):
                    self.np_shape = value.shape

                input_node.input_value = value

        # Configure the np array shape for all lambda nodes
        for n in self.lambdas:
            n.np_shape = self.np_shape

        subgraph_to_hyper_edges = {
            s: [h for h in self.hyper_edges if h.lambda_fn in s.nodes]
            for s in self.subgraphs
        }
        node_to_subgraph = {n: s for s in self.subgraphs for n in s.nodes}
        self.root_subgraph(
            self, subgraph_to_hyper_edges, node_to_subgraph, set()
        )
        # Return the output
        return {
            output.identifier.var_name: output.value for output in self.outputs
        }

    @classmethod
    def from_AIR(cls, air: AutoMATES_IR):
        network = nx.DiGraph()
        hyper_edges = list()
        Occs = dict()
        subgraphs = nx.DiGraph()

        def add_variable_node(
            v_id: VariableIdentifier, v_data: VariableDefinition
        ) -> VariableNode:
            node = VariableNode.from_id(v_id, v_data)
            network.add_node(node, **(node.get_kwargs()))
            return node

        variable_nodes = {
            v_id: add_variable_node(v_id, v_data)
            for v_id, v_data in air.variables.items()
        }

        def add_lambda_node(
            lambda_type: LambdaType,
            lambda_str: str,
            metadata: List[TypedMetadata] = None,
        ) -> LambdaNode:
            lambda_id = GenericNode.create_node_id()
            node = LambdaNode.from_AIR(
                lambda_id, lambda_type, lambda_str, metadata
            )
            network.add_node(node, **(node.get_kwargs()))
            return node

        def add_hyper_edge(
            inputs: Iterable[VariableNode],
            lambda_node: LambdaNode,
            outputs: Iterable[VariableNode],
        ) -> None:
            network.add_edges_from(
                [(in_node, lambda_node) for in_node in inputs]
            )
            network.add_edges_from(
                [(lambda_node, out_node) for out_node in outputs]
            )
            hyper_edges.append(HyperEdge(inputs, lambda_node, outputs))

        def translate_container(
            con: GenericContainer,
            inputs: Iterable[VariableNode],
            parent: GrFNSubgraph = None,
        ) -> Iterable[VariableNode]:
            con_name = con.identifier
            if con_name not in Occs:
                Occs[con_name] = 0

            con_subgraph = GrFNSubgraph.from_container(
                con, Occs[con_name], parent
            )
            live_variables = dict()
            if len(inputs) > 0:
                in_var_names = [n.identifier.var_name for n in inputs]
                in_var_str = ",".join(in_var_names)
                interface_func_str = f"lambda {in_var_str}:({in_var_str})"
                func = add_lambda_node(
                    LambdaType.INTERFACE, interface_func_str
                )
                out_nodes = [variable_nodes[v_id] for v_id in con.arguments]
                add_hyper_edge(inputs, func, out_nodes)
                con_subgraph.nodes.append(func)

                live_variables.update(
                    {id: node for id, node in zip(con.arguments, out_nodes)}
                )
            else:
                live_variables.update(
                    {v_id: variable_nodes[v_id] for v_id in con.arguments}
                )

            con_subgraph.nodes.extend(list(live_variables.values()))

            for stmt in con.statements:
                translate_stmt(stmt, live_variables, con_subgraph)

            subgraphs.add_node(con_subgraph)

            if parent is not None:
                subgraphs.add_edge(parent, con_subgraph)

            if len(inputs) > 0:
                # Do this only if this is not the starting container
                returned_vars = [variable_nodes[v_id] for v_id in con.returns]
                update_vars = [variable_nodes[v_id] for v_id in con.updated]
                output_vars = returned_vars + update_vars

                out_var_names = [n.identifier.var_name for n in output_vars]
                out_var_str = ",".join(out_var_names)
                interface_func_str = f"lambda {out_var_str}:({out_var_str})"
                func = add_lambda_node(
                    LambdaType.INTERFACE, interface_func_str
                )
                con_subgraph.nodes.append(func)
                return (output_vars, func)

        @singledispatch
        def translate_stmt(
            stmt: GenericStmt,
            live_variables: Dict[VariableIdentifier, VariableNode],
            parent: GrFNSubgraph,
        ) -> None:
            raise ValueError(f"Unsupported statement type: {type(stmt)}")

        @translate_stmt.register
        def _(
            stmt: CallStmt,
            live_variables: Dict[VariableIdentifier, VariableNode],
            subgraph: GrFNSubgraph,
        ) -> None:
            new_con = air.containers[stmt.call_id]
            if stmt.call_id not in Occs:
                Occs[stmt.call_id] = 0

            inputs = [variable_nodes[v_id] for v_id in stmt.inputs]
            (con_outputs, interface_func) = translate_container(
                new_con, inputs, subgraph
            )
            Occs[stmt.call_id] += 1
            out_nodes = [variable_nodes[v_id] for v_id in stmt.outputs]
            subgraph.nodes.extend(out_nodes)
            add_hyper_edge(con_outputs, interface_func, out_nodes)
            for output_node in out_nodes:
                var_id = output_node.identifier
                live_variables[var_id] = output_node

        @translate_stmt.register
        def _(
            stmt: LambdaStmt,
            live_variables: Dict[VariableIdentifier, VariableNode],
            subgraph: GrFNSubgraph,
        ) -> None:
            inputs = [variable_nodes[v_id] for v_id in stmt.inputs]
            out_nodes = [variable_nodes[v_id] for v_id in stmt.outputs]
            func = add_lambda_node(stmt.type, stmt.func_str, stmt.metadata)

            subgraph.nodes.append(func)
            subgraph.nodes.extend(out_nodes)

            add_hyper_edge(inputs, func, out_nodes)
            for output_node in out_nodes:
                var_id = output_node.identifier
                live_variables[var_id] = output_node

        start_container = air.containers[air.entrypoint]
        Occs[air.entrypoint] = 0
        translate_container(start_container, [])
        grfn_uid = str(uuid.uuid4())
        date_created = datetime.datetime.now().strftime("%Y-%m-%d")
        return cls(
            grfn_uid,
            air.entrypoint,
            date_created,
            network,
            hyper_edges,
            subgraphs,
            air.type_definitions,
            air.metadata,
        )

    def to_FCG(self):
        G = nx.DiGraph()
        func_to_func_edges = [
            (func_node, node)
            for node in self.nodes
            if isinstance(node, LambdaNode)
            for var_node in self.predecessors(node)
            for func_node in self.predecessors(var_node)
        ]
        G.add_edges_from(func_to_func_edges)
        return G

    def build_function_sets(self):
        subgraphs_to_func_sets = {s.uid: list() for s in self.subgraphs}

        initial_funcs = [n for n, d in self.FCG.in_degree() if d == 0]
        func2container = {f: s.uid for s in self.subgraphs for f in s.nodes}
        initial_funcs_to_subgraph = {
            n: func2container[n] for n in initial_funcs
        }
        containers_to_initial_funcs = {s.uid: list() for s in self.subgraphs}
        for k, v in initial_funcs_to_subgraph.items():
            containers_to_initial_funcs[v].append(k)

        def build_function_set_for_container(
            container, container_initial_funcs
        ):
            all_successors = list()
            distances = dict()
            visited_funcs = set()

            def find_distances(func, dist, path=[]):
                new_successors = list()
                func_container = func2container[func]
                if func_container == container:
                    distances[func] = (
                        max(dist, distances[func])
                        if func in distances and func not in path
                        else dist
                    )
                    if func not in visited_funcs:
                        new_successors.extend(self.FCG.successors(func))
                        visited_funcs.add(func)

                if len(new_successors) > 0:
                    all_successors.extend(new_successors)
                    for f in new_successors:
                        find_distances(f, dist + 1, path=(path + [func]))

            for f in container_initial_funcs:
                find_distances(f, 0)

            call_sets = dict()

            for func_node, call_dist in distances.items():
                if call_dist in call_sets:
                    call_sets[call_dist].add(func_node)
                else:
                    call_sets[call_dist] = {func_node}

            function_set_dists = sorted(
                call_sets.items(), key=lambda t: (t[0], len(t[1]))
            )

            subgraphs_to_func_sets[container] = [
                func_set for _, func_set in function_set_dists
            ]

        for container in self.subgraphs:
            input_interface_funcs = [
                n
                for n in container.nodes
                if isinstance(n, LambdaNode)
                and n.func_type == LambdaType.INTERFACE
                and all(
                    [
                        var_node in container.nodes
                        for var_node in self.successors(n)
                    ]
                )
            ]
            build_function_set_for_container(
                container.uid,
                input_interface_funcs
                + containers_to_initial_funcs[container.uid],
            )

        return subgraphs_to_func_sets

    def to_AGraph(self):
        """ Export to a PyGraphviz AGraph object. """
        var_nodes = [n for n in self.nodes if isinstance(n, VariableNode)]
        input_nodes = set([v for v in var_nodes if self.in_degree(v) == 0])
        output_nodes = set([v for v in var_nodes if self.out_degree(v) == 0])

        A = nx.nx_agraph.to_agraph(self)
        A.graph_attr.update(
            {"dpi": 227, "fontsize": 20, "fontname": "Menlo", "rankdir": "TB"}
        )
        A.node_attr.update({"fontname": "Menlo"})

        # A.add_subgraph(input_nodes, rank="same")
        # A.add_subgraph(output_nodes, rank="same")

        def get_subgraph_nodes(subgraph: GrFNSubgraph):
            return subgraph.nodes + [
                node
                for child_graph in self.subgraphs.successors(subgraph)
                for node in get_subgraph_nodes(child_graph)
            ]

        def populate_subgraph(subgraph: GrFNSubgraph, parent: AGraph):
            all_sub_nodes = get_subgraph_nodes(subgraph)
            container_subgraph = parent.add_subgraph(
                all_sub_nodes,
                name=f"cluster_{str(subgraph)}",
                label=subgraph.basename,
                style="bold, rounded",
                rankdir="TB",
                color=subgraph.border_color,
            )

            input_var_nodes = set(input_nodes).intersection(subgraph.nodes)
            container_subgraph.add_subgraph(list(input_var_nodes), rank="same")

            for new_subgraph in self.subgraphs.successors(subgraph):
                populate_subgraph(new_subgraph, container_subgraph)

            for _, func_sets in self.function_sets.items():
                for func_set in func_sets:
                    func_set = list(func_set.intersection(set(subgraph.nodes)))

                    container_subgraph.add_subgraph(func_set, rank="same")
                    output_var_nodes = list()
                    for func_node in func_set:
                        succs = list(self.successors(func_node))
                        output_var_nodes.extend(succs)
                    output_var_nodes = set(output_var_nodes) - output_nodes
                    var_nodes = output_var_nodes.intersection(subgraph.nodes)
                    container_subgraph.add_subgraph(
                        list(var_nodes), rank="same"
                    )

        root_subgraph = [n for n, d in self.subgraphs.in_degree() if d == 0][0]
        populate_subgraph(root_subgraph, A)

        return A

    def to_FIB(self, G2):
        """Creates a ForwardInfluenceBlanket object representing the
        intersection of this model with the other input model.

        Args:
            G1: The GrFN model to use as the basis for this FIB
            G2: The GroundedFunctionNetwork object to compare this model to.

        Returns:
            A ForwardInfluenceBlanket object to use for model comparison.
        """
        # TODO: Finish inpsection and testing of this function

        if not isinstance(G2, GroundedFunctionNetwork):
            raise TypeError(f"Expected a second GrFN but got: {type(G2)}")

        def shortname(var):
            return var[var.find("::") + 2 : var.rfind("_")]

        def shortname_vars(graph, shortname):
            return [v for v in graph.nodes() if shortname in v]

        g1_var_nodes = {
            shortname(n)
            for (n, d) in self.nodes(data=True)
            if d["type"] == "variable"
        }
        g2_var_nodes = {
            shortname(n)
            for (n, d) in G2.nodes(data=True)
            if d["type"] == "variable"
        }

        shared_nodes = {
            full_var
            for shared_var in g1_var_nodes.intersection(g2_var_nodes)
            for full_var in shortname_vars(self, shared_var)
        }

        outputs = self.outputs
        inputs = set(self.inputs).intersection(shared_nodes)

        # Get all paths from shared inputs to shared outputs
        path_inputs = shared_nodes - set(outputs)
        io_pairs = [(inp, self.output_node) for inp in path_inputs]
        paths = [
            p for (i, o) in io_pairs for p in all_simple_paths(self, i, o)
        ]

        # Get all edges needed to blanket the included nodes
        main_nodes = {node for path in paths for node in path}
        main_edges = {
            (n1, n2) for path in paths for n1, n2 in zip(path, path[1:])
        }
        blanket_nodes = set()
        add_nodes, add_edges = list(), list()

        def place_var_node(var_node):
            prev_funcs = list(self.predecessors(var_node))
            if (
                len(prev_funcs) > 0
                and self.nodes[prev_funcs[0]]["label"] == "L"
            ):
                prev_func = prev_funcs[0]
                add_nodes.extend([var_node, prev_func])
                add_edges.append((prev_func, var_node))
            else:
                blanket_nodes.add(var_node)

        for node in main_nodes:
            if self.nodes[node]["type"] == "function":
                for var_node in self.predecessors(node):
                    if var_node not in main_nodes:
                        add_edges.append((var_node, node))
                        if "::IF_" in var_node:
                            if_func = list(self.predecessors(var_node))[0]
                            add_nodes.extend([if_func, var_node])
                            add_edges.append((if_func, var_node))
                            for new_var_node in self.predecessors(if_func):
                                add_edges.append((new_var_node, if_func))
                                place_var_node(new_var_node)
                        else:
                            place_var_node(var_node)

        main_nodes |= set(add_nodes)
        main_edges |= set(add_edges)
        main_nodes = main_nodes - inputs - set(outputs)

        orig_nodes = self.nodes(data=True)

        F = nx.DiGraph()

        F.add_nodes_from([(n, d) for n, d in orig_nodes if n in inputs])
        for node in inputs:
            F.nodes[node]["color"] = dodgerblue3
            F.nodes[node]["fontcolor"] = dodgerblue3
            F.nodes[node]["penwidth"] = 3.0
            F.nodes[node]["fontname"] = FONT

        F.inputs = list(F.inputs)

        F.add_nodes_from([(n, d) for n, d in orig_nodes if n in blanket_nodes])
        for node in blanket_nodes:
            F.nodes[node]["fontname"] = FONT
            F.nodes[node]["color"] = forestgreen
            F.nodes[node]["fontcolor"] = forestgreen

        F.add_nodes_from([(n, d) for n, d in orig_nodes if n in main_nodes])
        for node in main_nodes:
            F.nodes[node]["fontname"] = FONT

        for out_var_node in outputs:
            F.add_node(out_var_node, **self.nodes[out_var_node])
            F.nodes[out_var_node]["color"] = dodgerblue3
            F.nodes[out_var_node]["fontcolor"] = dodgerblue3

        F.add_edges_from(main_edges)
        return F

    def to_json(self) -> str:
        """Outputs the contents of this GrFN to a JSON object string.

        :return: Description of returned object.
        :rtype: type
        :raises ExceptionName: Why the exception is raised.
        """
        data = {
            "uid": self.uid,
            "entry_point": "::".join(
                ["@container", self.namespace, self.scope, self.name]
            ),
            "timestamp": self.timestamp,
            "hyper_edges": [edge.to_dict() for edge in self.hyper_edges],
            "variables": [var.to_dict() for var in self.variables],
            "functions": [func.to_dict() for func in self.lambdas],
            "subgraphs": [sgraph.to_dict() for sgraph in self.subgraphs],
            "types": [t_def.to_dict() for t_def in self.types],
            "metadata": [m.to_dict() for m in self.metadata],
        }

        return json.dumps(data)

    def to_json_file(self, json_path) -> None:
        with open(json_path, "w") as outfile:
            outfile.write(self.to_json())

    @classmethod
    def from_json(cls, json_path):
        """Short summary.

        :param type cls: Description of parameter `cls`.
        :param type json_path: Description of parameter `json_path`.
        :return: Description of returned object.
        :rtype: type
        :raises ExceptionName: Why the exception is raised.

        """
        data = json.load(open(json_path, "r"))

        # Re-create variable and function nodes from their JSON descriptions
        V = {v["uid"]: VariableNode.from_dict(v) for v in data["variables"]}
        F = {f["uid"]: LambdaNode.from_dict(f) for f in data["functions"]}

        # Add all of the function and variable nodes to a new DiGraph
        G = nx.DiGraph()
        ALL_NODES = {**V, **F}
        for grfn_node in ALL_NODES.values():
            G.add_node(grfn_node, **(grfn_node.get_kwargs()))

        # Re-create the hyper-edges/subgraphs using the node lookup list
        S = nx.DiGraph()

        subgraphs = [
            GrFNSubgraph.from_dict(s, ALL_NODES) for s in data["subgraphs"]
        ]
        subgraph_dict = {s.uid: s for s in subgraphs}
        subgraph_edges = [
            (subgraph_dict[s.parent], subgraph_dict[s.uid])
            for s in subgraphs
            if s.parent is not None
        ]
        S.add_nodes_from(subgraphs)
        S.add_edges_from(subgraph_edges)

        H = [HyperEdge.from_dict(h, ALL_NODES) for h in data["hyper_edges"]]

        T = (
            [TypeDefinition.from_data(t) for t in data["types"]]
            if "types" in data
            else []
        )

        M = (
            [TypedMetadata.from_data(d) for d in data["metadata"]]
            if "metadata" in data
            else []
        )

        # Add edges to the new DiGraph using the re-created hyper-edge objects
        for edge in H:
            G.add_edges_from([(var, edge.lambda_fn) for var in edge.inputs])
            G.add_edges_from([(edge.lambda_fn, var) for var in edge.outputs])

        if "entry_point" in data:
            entry_point = data["entry_point"]
        elif "identifier" in data:
            entry_point = data["identifier"]
        else:
            entry_point = ""
        identifier = GenericIdentifier.from_str(entry_point)
        return cls(data["uid"], identifier, data["timestamp"], G, H, S, T, M)


class CausalAnalysisGraph(nx.DiGraph):
    def __init__(self, G, S, uid, date, ns, sc, nm):
        super().__init__(G)
        self.subgraphs = S
        self.uid = uid
        self.timestamp = date
        self.namespace = ns
        self.scope = sc
        self.name = nm

    @classmethod
    def from_GrFN(cls, GrFN: GroundedFunctionNetwork):
        """Export to a Causal Analysis Graph (CAG) object.
        The CAG shows the influence relationships between the variables and
        elides the function nodes."""

        G = nx.DiGraph()
        for var_node in GrFN.variables:
            G.add_node(var_node, **var_node.get_kwargs())
        for edge in GrFN.hyper_edges:
            if edge.lambda_fn.func_type == LambdaType.INTERFACE:
                G.add_edges_from(list(zip(edge.inputs, edge.outputs)))
            else:
                G.add_edges_from(list(product(edge.inputs, edge.outputs)))

        def delete_paths_at_level(nodes: list):
            orig_nodes = deepcopy(nodes)

            while len(nodes) > 0:
                updated_nodes = list()
                for node in nodes:
                    node_var_name = node.identifier.var_name
                    succs = list(G.successors(node))
                    for next_node in succs:
                        if (
                            next_node.identifier.var_name == node_var_name
                            and len(list(G.predecessors(next_node))) == 1
                        ):
                            next_succs = list(G.successors(next_node))
                            G.remove_node(next_node)
                            updated_nodes.append(node)
                            for succ_node in next_succs:
                                G.add_edge(node, succ_node)
                nodes = updated_nodes

            next_level_nodes = list()
            for node in orig_nodes:
                next_level_nodes.extend(list(G.successors(node)))
            next_level_nodes = list(set(next_level_nodes))

            if len(next_level_nodes) > 0:
                delete_paths_at_level(next_level_nodes)

        def correct_subgraph_nodes(subgraph: GrFNSubgraph):
            cag_subgraph_nodes = list(
                set(G.nodes).intersection(set(subgraph.nodes))
            )
            subgraph.nodes = cag_subgraph_nodes

            for new_subgraph in GrFN.subgraphs.successors(subgraph):
                correct_subgraph_nodes(new_subgraph)

        input_nodes = [n for n in G.nodes if G.in_degree(n) == 0]
        delete_paths_at_level(input_nodes)
        root_subgraph = [n for n, d in GrFN.subgraphs.in_degree() if d == 0][0]
        correct_subgraph_nodes(root_subgraph)
        return cls(
            G,
            GrFN.subgraphs,
            GrFN.uid,
            GrFN.timestamp,
            GrFN.namespace,
            GrFN.scope,
            GrFN.name,
        )

    def to_AGraph(self):
        """Returns a variable-only view of the GrFN in the form of an AGraph.

        Returns:
            type: A CAG constructed via variable influence in the GrFN object.

        """
        A = nx.nx_agraph.to_agraph(self)
        A.graph_attr.update(
            {
                "dpi": 227,
                "fontsize": 20,
                "fontcolor": "black",
                "fontname": "Menlo",
                "rankdir": "TB",
            }
        )
        A.node_attr.update(
            shape="rectangle",
            color="#650021",
            fontname="Menlo",
            fontcolor="black",
        )
        for node in A.iternodes():
            node.attr["fontcolor"] = "black"
            node.attr["style"] = "rounded"
        A.edge_attr.update({"color": "#650021", "arrowsize": 0.5})

        def get_subgraph_nodes(subgraph: GrFNSubgraph):
            return subgraph.nodes + [
                node
                for child_graph in self.subgraphs.successors(subgraph)
                for node in get_subgraph_nodes(child_graph)
            ]

        def populate_subgraph(subgraph: GrFNSubgraph, parent: AGraph):
            all_sub_nodes = get_subgraph_nodes(subgraph)
            container_subgraph = parent.add_subgraph(
                all_sub_nodes,
                name=f"cluster_{str(subgraph)}",
                label=subgraph.basename,
                style="bold, rounded",
                rankdir="TB",
                color=subgraph.border_color,
            )

            for new_subgraph in self.subgraphs.successors(subgraph):
                populate_subgraph(new_subgraph, container_subgraph)

        root_subgraph = [n for n, d in self.subgraphs.in_degree() if d == 0][0]
        populate_subgraph(root_subgraph, A)
        return A

    def to_igraph_gml(self, filepath: str) -> NoReturn:
        filename = os.path.join(
            filepath,
            f"{self.namespace}__{self.scope}__{self.name}--igraph.gml",
        )

        V = [str(v) for v in super().nodes]
        E = [(str(e1), str(e2)) for e1, e2 in super().edges]
        iG = nx.DiGraph()
        iG.add_nodes_from(V)
        iG.add_edges_from(E)
        nx.write_gml(iG, filename)

    def to_json(self) -> str:
        """Outputs the contents of this GrFN to a JSON object string.

        :return: Description of returned object.
        :rtype: type
        :raises ExceptionName: Why the exception is raised.
        """
        data = {
            "uid": self.uid,
            "identifier": "::".join(
                ["@container", self.namespace, self.scope, self.name]
            ),
            "timestamp": self.timestamp,
            "variables": [var.to_dict() for var in self.nodes],
            "edges": [(src.uid, dst.uid) for src, dst in self.edges],
            "subgraphs": [sgraphs.to_dict() for sgraphs in self.subgraphs],
        }
        return json.dumps(data)

    def to_json_file(self, json_path) -> None:
        with open(json_path, "w") as outfile:
            outfile.write(self.to_json())
