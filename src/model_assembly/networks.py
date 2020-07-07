from typing import List, Dict, Iterable, Any
from abc import ABC, abstractmethod
from functools import singledispatch
from dataclasses import dataclass
from uuid import uuid4
import datetime
import json

import networkx as nx
import numpy as np
from networkx.algorithms.simple_paths import all_simple_paths
from pygraphviz import AGraph

from .sandbox import load_lambda_function
from .structures import (
    GenericContainer,
    FuncContainer,
    CondContainer,
    LoopContainer,
    LambdaType,
    GenericStmt,
    CallStmt,
    LambdaStmt,
    GenericIdentifier,
    ContainerIdentifier,
    VariableIdentifier,
    TypeIdentifier,
    VariableDefinition,
    TypeDefinition,
    VarType,
    DataType,
)
from utils.misc import choose_font


FONT = choose_font()

dodgerblue3 = "#1874CD"
forestgreen = "#228b22"


@dataclass(repr=False, frozen=False)
class GenericNode(ABC):
    uid: str
    reference: str

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.uid

    @staticmethod
    def create_node_id() -> str:
        return str(uuid4())

    @abstractmethod
    def get_kwargs(self):
        return NotImplemented

    @abstractmethod
    def get_label(self):
        return NotImplemented


@dataclass(repr=False, frozen=False)
class VariableNode(GenericNode):
    identifier: VariableIdentifier
    value: Any
    type: VarType
    kind: DataType
    domain: str

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other) -> bool:
        return self.uid == other.uid

    @classmethod
    def from_id(cls, id: VariableIdentifier, data: VariableDefinition):
        # TODO: continue with the two functions below
        var_type = VarType.from_name(data.domain_name)
        var_kind = DataType.from_name(data.domain_name)
        return cls(
            GenericNode.create_node_id(),
            "",
            id,
            None,
            var_type,
            var_kind,
            data.domain_constraint,
        )

    def get_fullname(self):
        return f"{self.name}\n({self.index})"

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

    def get_label(self):
        return self.identifier.var_name

    @classmethod
    def from_dict(cls, data: dict):
        identifier = VariableIdentifier.from_str(data["identifier"])
        return cls(
            data["uid"],
            data["reference"],
            identifier,
            None,
            VarType.from_name(data["type"]),
            DataType.from_type_str(data["kind"]),
            data["domain"],
        )

    def to_dict(self) -> dict:
        return {
            "uid": self.uid,
            "reference": self.reference,
            "identifier": str(self.identifier),
            "type": str(self.type),
            "kind": str(self.kind),
            "domain": self.domain,
        }


@dataclass(repr=False, frozen=False)
class LambdaNode(GenericNode):
    func_type: LambdaType
    func_str: str
    function: callable

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other) -> bool:
        return self.uid == other.uid

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
            res = self.function(*values)
            if isinstance(res, tuple):
                return [np.array(item) for item in res]
            else:
                if len(values) == 0:
                    res = [np.array(res, dtype=np.float32)]
                else:
                    res = [np.array(res)]
            return res
        except Exception as e:
            print(f"Exception occured in {self.func_str}")
            raise e

    def get_kwargs(self):
        return {"shape": "rectangle", "padding": 10, "label": self.get_label()}

    def get_label(self):
        return self.func_type.shortname()

    def get_signature(self):
        return self.function.__code__.co_varnames

    @classmethod
    def from_AIR(cls, lm_id: str, lm_type: str, lm_str: str):
        lambda_fn = load_lambda_function(lm_str)
        return cls(lm_id, "", lm_type, lm_str, lambda_fn)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["uid"],
            data["reference"],
            LambdaType.from_str(data["type"]),
            data["lambda"],
            load_lambda_function(data["lambda"]),
        )

    def to_dict(self) -> dict:
        return {
            "uid": self.uid,
            "reference": self.reference,
            "type": str(self.func_type),
            "lambda": self.func_str,
        }


@dataclass
class HyperEdge:
    inputs: Iterable[VariableNode]
    lambda_fn: LambdaNode
    outputs: Iterable[VariableNode]

    def __call__(self):
        result = self.lambda_fn(*[var.value for var in self.inputs])
        for i, out_val in enumerate(result):
            self.outputs[i].value = out_val

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
    namespace: str
    scope: str
    basename: str
    occurrence_num: int
    border_color: str
    nodes: Iterable[GenericNode]

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

    @classmethod
    def from_container(cls, con: GenericContainer, occ: int):
        if isinstance(con, CondContainer):
            clr = "orange"
        elif isinstance(con, FuncContainer):
            clr = "forestgreen"
        elif isinstance(con, LoopContainer):
            clr = "navyblue"
        else:
            # TODO: perhaps use this in the future
            # clr = "lightskyblue"
            raise TypeError(f"Unrecognized container type: {type(con)}")
        id = con.identifier
        return cls(id.namespace, id.scope, id.con_name, occ, clr, [])

    @classmethod
    def from_dict(cls, data: dict, all_nodes: Dict[str, GenericNode]):
        subgraph_nodes = [all_nodes[n_id] for n_id in data["nodes"]]
        return cls(
            data["namespace"],
            data["scope"],
            data["basename"],
            data["occurrence_num"],
            data["border_color"],
            subgraph_nodes,
        )

    def to_dict(self):
        return {
            "namespace": self.namespace,
            "scope": self.scope,
            "basename": self.basename,
            "occurrence_num": self.occurrence_num,
            "border_color": self.border_color,
            "nodes": [n.uid for n in self.nodes],
        }


class GroundedFunctionNetwork(nx.DiGraph):
    def __init__(
        self,
        uid: str,
        id: ContainerIdentifier,
        timestamp: str,
        G: nx.DiGraph,
        H: List[HyperEdge],
        S: nx.DiGraph,
    ):
        super().__init__(G)
        self.hyper_edges = H
        self.subgraphs = S

        self.uid = uid
        self.date_created = timestamp
        self.namespace = id.namespace
        self.scope = id.scope
        self.name = id.con_name
        self.label = f"{self.name} ({self.namespace}.{self.scope})"

        self.variables = [n for n in self.nodes if isinstance(n, VariableNode)]
        self.lambdas = [n for n in self.nodes if isinstance(n, LambdaNode)]
        self.inputs = [
            n
            for n, d in self.in_degree()
            if d == 0 and isinstance(n, VariableNode)
        ]
        self.outputs = [
            n
            for n, d in self.out_degree()
            if d == 0 and isinstance(n, VariableNode)
        ]

        self.input_name_map = {
            var_node.identifier.var_name: var_node for var_node in self.inputs
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
        L_sz = str(len(self.lambda_nodes))
        V_sz = str(len(self.variable_nodes))
        I_sz = str(len(self.input_variables))
        O_sz = str(len(self.output_variables))
        size_str = f"< |L|: {L_sz}, |V|: {V_sz}, |I|: {I_sz}, |O|: {O_sz} >"
        return f"{self.label}\n{size_str}"

    def __call__(self, inputs: Dict[str, Any]) -> Iterable[Any]:
        """Executes the GrFN over a particular set of inputs and returns the
        result.

        Args:
            inputs: Input set where keys are the names of input nodes in the
                GrFN and each key points to a set of input values (or just one)

        Returns:
            A set of outputs from executing the GrFN, one for every set of
            inputs.
        """
        # TODO: update this function to work with new GrFN object
        full_inputs = {self.input_name_map[n]: v for n, v in inputs.items()}
        # Set input values
        for input_node in self.inputs:
            value = full_inputs[input_node]
            if isinstance(value, float):
                value = np.array([value], dtype=np.float32)
            if isinstance(value, int):
                value = np.array([value], dtype=np.int32)
            elif isinstance(value, list):
                value = np.array(value, dtype=np.float32)

            input_node.value = value

        for edge in self.hyper_edges:
            edge()

        # Return the output
        return [output.value for output in self.outputs]

    @classmethod
    def from_AIR(
        cls,
        con_id: ContainerIdentifier,
        containers: Dict[ContainerIdentifier, GenericContainer],
        variables: Dict[VariableIdentifier, VariableDefinition],
        types: Dict[TypeIdentifier, TypeDefinition],
    ):
        network = nx.DiGraph()
        hyper_edges = list()
        Occs = dict()
        subgraphs = nx.DiGraph()

        def add_variable_node(id: VariableIdentifier) -> VariableNode:
            var_data = variables[id]
            node = VariableNode.from_id(id, var_data)
            network.add_node(node, **(node.get_kwargs()))
            return node

        def add_lambda_node(
            lambda_type: LambdaType, lambda_str: str
        ) -> LambdaNode:
            lambda_id = GenericNode.create_node_id()
            node = LambdaNode.from_AIR(lambda_id, lambda_type, lambda_str)
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

            con_subgraph = GrFNSubgraph.from_container(con, Occs[con_name])
            live_variables = dict()
            if len(inputs) > 0:
                in_var_names = [n.identifier.var_name for n in inputs]
                in_var_str = ",".join(in_var_names)
                pass_func_str = f"lambda {in_var_str}:({in_var_str})"
                func = add_lambda_node(LambdaType.PASS, pass_func_str)
                out_nodes = [add_variable_node(id) for id in con.arguments]
                add_hyper_edge(inputs, func, out_nodes)
                con_subgraph.nodes.append(func)

                live_variables.update(
                    {id: node for id, node in zip(con.arguments, out_nodes)}
                )
            else:
                live_variables.update(
                    {id: add_variable_node(id) for id in con.arguments}
                )

            con_subgraph.nodes.extend(list(live_variables.values()))

            for stmt in con.statements:
                translate_stmt(stmt, live_variables, con_subgraph)

            subgraphs.add_node(con_subgraph)

            if parent is not None:
                subgraphs.add_edge(parent, con_subgraph)

            if len(inputs) > 0:
                # Do this only if this is not the starting container
                returned_vars = [live_variables[id] for id in con.returns]
                update_vars = [live_variables[id] for id in con.updated]
                output_vars = returned_vars + update_vars

                out_var_names = [n.identifier.var_name for n in output_vars]
                out_var_str = ",".join(out_var_names)
                pass_func_str = f"lambda {out_var_str}:({out_var_str})"
                func = add_lambda_node(LambdaType.PASS, pass_func_str)
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
            new_con = containers[stmt.call_id]
            if stmt.call_id not in Occs:
                Occs[stmt.call_id] = 0

            inputs = [live_variables[id] for id in stmt.inputs]
            (con_outputs, pass_func) = translate_container(
                new_con, inputs, subgraph
            )
            Occs[stmt.call_id] += 1
            out_nodes = [add_variable_node(var) for var in stmt.outputs]
            subgraph.nodes.extend(out_nodes)
            add_hyper_edge(con_outputs, pass_func, out_nodes)
            for output_node in out_nodes:
                var_id = output_node.identifier
                live_variables[var_id] = output_node

        @translate_stmt.register
        def _(
            stmt: LambdaStmt,
            live_variables: Dict[VariableIdentifier, VariableNode],
            subgraph: GrFNSubgraph,
        ) -> None:
            inputs = [live_variables[id] for id in stmt.inputs]
            out_nodes = [add_variable_node(var) for var in stmt.outputs]
            func = add_lambda_node(stmt.type, stmt.func_str)

            subgraph.nodes.append(func)
            subgraph.nodes.extend(out_nodes)

            add_hyper_edge(inputs, func, out_nodes)
            for output_node in out_nodes:
                var_id = output_node.identifier
                live_variables[var_id] = output_node

        start_container = containers[con_id]
        Occs[con_id] = 0
        translate_container(start_container, [])
        grfn_uid = str(uuid4())
        date_created = datetime.datetime.now().strftime("%Y-%m-%d")
        return cls(
            grfn_uid, con_id, date_created, network, hyper_edges, subgraphs
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
        initial_funcs = [n for n, d in self.FCG.in_degree() if d == 0]
        distances = dict()

        def find_distances(funcs, dist):
            all_successors = list()
            for func in funcs:
                distances[func] = dist
                all_successors.extend(self.FCG.successors(func))
            if len(all_successors) > 0:
                find_distances(list(set(all_successors)), dist + 1)

        find_distances(initial_funcs, 0)
        call_sets = dict()
        for func_node, call_dist in distances.items():
            if call_dist in call_sets:
                call_sets[call_dist].add(func_node)
            else:
                call_sets[call_dist] = {func_node}

        function_set_dists = sorted(
            call_sets.items(), key=lambda t: (t[0], len(t[1]))
        )
        function_sets = [func_set for _, func_set in function_set_dists]
        return function_sets

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

            for func_set in self.function_sets:
                func_set = list(func_set.intersection(set(subgraph.nodes)))
                container_subgraph.add_subgraph(func_set, rank="same")
                output_var_nodes = list()
                for func_node in func_set:
                    succs = list(self.successors(func_node))
                    output_var_nodes.extend(succs)
                output_var_nodes = set(output_var_nodes) - output_nodes
                var_nodes = output_var_nodes.intersection(subgraph.nodes)
                container_subgraph.add_subgraph(list(var_nodes), rank="same")

        root_subgraph = [n for n, d in self.subgraphs.in_degree() if d == 0][0]
        populate_subgraph(root_subgraph, A)

        return A

    def to_CAG(self):
        # TODO: finish this implementation
        """ Export to a Causal Analysis Graph (CAG) PyGraphviz AGraph object.
        The CAG shows the influence relationships between the variables and
        elides the function nodes."""

        G = nx.DiGraph()
        for grfn_node in self.nodes:
            if isinstance(grfn_node, VariableNode):
                cag_name = grfn_node.identifier.var_name
                G.add_node(cag_name, **attrs)
                for pred_fn in self.predecessors(name):
                    for pred_var in self.predecessors(pred_fn):
                        v_attrs = self.nodes[pred_var]
                        v_name = v_attrs["cag_label"]
                        G.add_node(v_name, **self.nodes[pred_var])
                        G.add_edge(v_name, cag_name)

        return G

    def CAG_to_AGraph(self):
        # TODO: finish this implementation
        """Returns a variable-only view of the GrFN in the form of an AGraph.

        Returns:
            type: A CAG constructed via variable influence in the GrFN object.

        """
        CAG = self.to_CAG()
        for name, data in CAG.nodes(data=True):
            CAG.nodes[name]["label"] = data["cag_label"]
        A = nx.nx_agraph.to_agraph(CAG)
        A.graph_attr.update(
            {"dpi": 227, "fontsize": 20, "fontname": "Menlo", "rankdir": "TB"}
        )
        A.node_attr.update(
            {
                "shape": "rectangle",
                "color": "#650021",
                "style": "rounded",
                "fontname": "Menlo",
            }
        )
        A.edge_attr.update({"color": "#650021", "arrowsize": 0.5})
        return A

    def to_FIB(self, G2):
        """ Creates a ForwardInfluenceBlanket object representing the
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
            "identifier": "::".join(
                ["@container", self.namespace, self.scope, self.name]
            ),
            "date_created": self.date_created,
            "hyper_edges": [edge.to_dict() for edge in self.hyper_edges],
            "variables": [var.to_dict() for var in self.variables],
            "functions": [func.to_dict() for func in self.lambdas],
            "subgraphs": [sgraph.to_dict() for sgraph in self.subgraphs],
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
        S = [GrFNSubgraph.from_dict(s, ALL_NODES) for s in data["subgraphs"]]
        H = [HyperEdge.from_dict(h, ALL_NODES) for h in data["hyper_edges"]]

        # Add edges to the new DiGraph using the re-created hyper-edge objects
        for edge in H:
            G.add_edges_from([(var, edge.lambda_fn) for var in edge.inputs])
            G.add_edges_from([(edge.lambda_fn, var) for var in edge.outputs])

        identifier = GenericIdentifier.from_str(data["identifier"])
        return cls(data["uid"], identifier, data["date_created"], G, H, S)
