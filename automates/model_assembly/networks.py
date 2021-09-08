from __future__ import annotations
from typing import List, Dict, Iterable, Any, Tuple
from abc import ABC, abstractmethod, abstractclassmethod
from dataclasses import dataclass
from datetime import datetime
from copy import deepcopy

import inspect
import json
import ast
import re

import pygraphviz as pgv
import networkx as nx
import numpy as np
from networkx.algorithms.simple_paths import all_simple_paths
from pygraphviz import AGraph

from .sandbox import load_lambda_function
from .expression_visitor import (
    ExpressionVisitor,
    ExprAbstractNode,
    ExprOperatorNode,
    ExprDefinitionNode,
    ExprVariableNode,
    ExprValueNode,
)
from .air import (
    AutoMATES_IR,
    ContainerDef,
    CondContainerDef,
    FuncContainerDef,
    LoopContainerDef,
    StmtDef,
    CallStmtDef,
    LambdaStmtDef,
    ObjectDef,
    VariableDef,
    TypeDef,
)
from .identifiers import (
    BaseIdentifier,
    GrFNIdentifier,
    ContainerIdentifier,
    FunctionIdentifier,
    ObjectIdentifier,
    VariableIdentifier,
    TypeIdentifier,
    CAGIdentifier,
    CAGContainerIdentifier,
)
from .metadata import (
    EquationExtraction,
    TypedMetadata,
    ProvenanceData,
    MeasurementType,
    LambdaType,
    FunctionType,
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


class GrFNExecutionException(Exception):
    pass


@dataclass(repr=False, frozen=False)
class BaseNode(ABC):
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
class VariableNode(BaseNode):
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
        return f"{str(self.identifier)}::{str(self.uid)}"

    @classmethod
    def from_definition(cls, var_def: VariableDef):
        # TODO: use domain constraint information in the future
        d_type = DataType.from_str(var_def.domain_name)
        m_type = MeasurementType.from_name(var_def.domain_name)

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
        metadata = [dom] + var_def.metadata
        return cls(BaseNode.create_node_id(), var_def.identifier, metadata)

    @classmethod
    def from_identifier(cls, idt: VariableIdentifier):
        return cls(BaseNode.create_node_id(), idt, [])

    @classmethod
    def from_expr_def(cls, expr_namespace, expr_scope):
        var_id = VariableIdentifier.from_anonymous(expr_namespace, expr_scope)
        return cls(BaseNode.create_node_id(), var_id, [])

    def get_fullname(self):
        return f"{self.name}\n({self.index})"

    def get_name(self):
        return str(self.identifier)

    def get_kwargs(self):
        is_exit = self.identifier.name == "EXIT"
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
        if self.identifier.name == "@anonymous":
            return "--"
        node_label = self.get_node_label(self.identifier.name)
        return node_label

    @classmethod
    def from_dict(cls, data: dict):
        if len(data["identifier"].split("::")) == 5:
            var_id =  VariableIdentifier.from_name_str(data["identifier"])   
        else:
            var_id =  VariableIdentifier.from_str(data["identifier"])   

        return cls(
            uid=data["uid"],
            identifier=var_id,
            metadata=[TypedMetadata.from_data(mdict) for mdict in data["metadata"]]
            if "metadata" in data
            else [],
            object_ref=data["object_ref"] if "object_ref" in data else "",
        )

    def to_dict(self) -> dict:
        return {
            "uid": self.uid,
            "identifier": str(self.identifier),
            "object_ref": self.object_ref,
            "metadata": [m.to_dict() for m in self.metadata],
        }

    def add_metadata(self, metadata):
        self.metadata.append(metadata)


@dataclass(repr=False)
class BaseFuncNode(ABC):
    uid: str
    identifier: FunctionIdentifier
    type: FunctionType
    input_variables: List[VariableIdentifier]
    output_variables: List[VariableIdentifier]
    hyper_edges: List[HyperEdge]
    hyper_graph: nx.DiGraph
    metadata: List[TypedMetadata]

    def __str__(self) -> str:
        return str(self.identifier)

    def __eq__(self, other: BaseFuncNode) -> bool:
        return self.identifier == other.identifier

    def __hash__(self):
        return hash(self.identifier)

    def get_kwargs(self):
        return {"shape": "rectangle", "padding": 10, "label": self.get_label()}

    def get_label(self):
        return self.type.shortname().upper()

    @staticmethod
    def get_border_color(func_node):
        if isinstance(func_node, LoopConFuncNode):
            return "navyblue"
        elif isinstance(func_node, CondConFuncNode):
            return "orange"
        elif isinstance(func_node, BaseConFuncNode):
            return "forestgreen"
        elif isinstance(func_node, ExpressionFuncNode):
            return "pink"
        elif isinstance(func_node, OperationFuncNode):
            return "black"
        else:
            return "red"

    # @staticmethod
    # def from_container(
    #     container: ContainerDef,
    #     # CONS: Dict[ContainerIdentifier, ContainerDef],
    #     VARS: Dict[VariableIdentifier, VariableNode],
    #     # FUNCS: Dict[FunctionIdentifier, BaseFuncNode],
    # ):
    #     # NOTE: this method should only be called from FuncNodes that are
    #     # derived from container definitions in AIR JSON
    #     func_uid = str(uuid.uuid4())
    #     func_type = FunctionType.from_con(container.__class__.__name__)
    #     inputs = [
    #         VARS[var_id]
    #         if var_id in VARS
    #         else VariableNode.from_identifier(var_id)
    #         for var_id in container.arguments
    #     ]
    #     outputs = [
    #         VARS[var_id]
    #         if var_id in VARS
    #         else VariableNode.from_identifier(var_id)
    #         for var_id in container.updated + container.returns
    #     ]
    #     return (func_uid, func_type, inputs, outputs)

    @abstractclassmethod
    def from_data(
        cls,
        data: Dict[str, Any],
        FUNCS: Dict[FunctionIdentifier, BaseFuncNode],
    ):
        hyper_edges = [
            HyperEdge.from_dict(h_def, FUNCS) for h_def in data["hyper_edges"]
        ]
        hyper_graph = cls.create_hyper_graph(hyper_edges)

        return (
            data["uid"],
            data["identifier"],
            FunctionType.from_str(data["type"]),
            data["input_variables"],
            data["output_variables"],
            hyper_edges,
            hyper_graph,
            [TypedMetadata.from_data(m_def) for m_def in data["metadata"]],
        )


    @staticmethod
    def create_hyper_graph(hyper_edges: List[HyperEdge]) -> nx.DiGraph:
        output2edge = {
            out_node: h_edge
            for h_edge in hyper_edges
            for out_node in h_edge.outputs
        }

        network = nx.DiGraph()
        for h_edge in hyper_edges:
            network.add_node(h_edge)
            potential_parents = list()
            for v_node in h_edge.inputs:
                if v_node in output2edge:
                    potential_parents.append(output2edge[v_node])
            network.add_edges_from(
                [
                    (parent_func, h_edge)
                    for parent_func in set(potential_parents)
                ]
            )

        # print(network.nodes)
        return network

    @staticmethod
    def get_or_create_vars(
        ids: List[VariableIdentifier],
        AIR: AutoMATES_IR,
        VARS: Dict[VariableIdentifier, VariableNode],
    ) -> List[VariableNode]:
        def get_or_create_var(v: VariableIdentifier) -> VariableNode:
            if v not in VARS:
                VARS[v] = VariableNode.from_definition(AIR.variables[v])
            return VARS[v]

        return [get_or_create_var(v_id) for v_id in ids]

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        return {
            "uid": self.uid,
            "identifier": str(self.identifier),
            "type": str(self.type),
            "input_variables": [str(v_id) for v_id in self.input_variables],
            "output_variables": [str(v_id) for v_id in self.output_variables],
            "expression": None,
            "exit": None,
            "hyper_edges": [h.to_dict() for h in self.hyper_edges],
            "metadata": [m.to_dict() for m in self.metadata],
        }


# TODO: Some class hierarchy changes need to be made because literals shouldn't have inputs, hyper-edges, or a hypergraph and I'm not even sold on them needing to be unique. Maybe we should think about that?
@dataclass(repr=False)
class LiteralFuncNode:
    identifier: str
    type: FunctionType
    value: Any

    def __eq__(self, other: LiteralFuncNode) -> bool:
        return self.identifier == other.identifier

    def __hash__(self):
        return hash(self.identifier)

    @classmethod
    def from_value_node(cls, node: ExprValueNode):
        return cls(uuid.uuid4(), FunctionType.LITERAL, node.value)


@dataclass(repr=False)
class OperationFuncNode(BaseFuncNode):
    def __hash__(self):
        return super().__hash__()

    @classmethod
    def from_expr_def(cls, expr_def):
        operation = None
        if isinstance(expr_def, ExprDefinitionNode):
            operation = expr_def.def_type
        elif isinstance(expr_def, ExprOperatorNode):
            operation = expr_def.operator
        else:
            raise TypeError(f"Unrecognized expr node type: {type(expr_def)}")

        metadata = list()
        return cls(
            str(uuid.uuid4()),
            FunctionIdentifier.from_operator_func(
                operation, int(uuid.uuid4())
            ),
            FunctionType.OPERATOR,
            [],
            [],
            [],
            None,
            metadata,
        )

    @classmethod
    def from_data(cls, data: Dict[str, Any]):
        return cls(*(super().from_data(data)), data["identifier"])

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({"identifier": str(self.identifier)})
        return data

    def get_kwargs(self):
        return {"shape": "rectangle", "padding": 10, "label": self.get_label()}

    def get_label(self):
        return self.identifier.name


@dataclass(repr=False)
class ExpressionFuncNode(BaseFuncNode):
    expression: str
    executable: callable

    def __hash__(self):
        return super().__hash__()

    @classmethod
    def from_lambda_stmt(
        cls,
        statement: LambdaStmtDef,
        AIR: AutoMATES_IR,
        VARS: Dict[VariableIdentifier, VariableNode],
        FUNCS: Dict[FunctionIdentifier, BaseFuncNode],
    ):
        inputs = BaseFuncNode.get_or_create_vars(statement.inputs, AIR, VARS)
        outputs = BaseFuncNode.get_or_create_vars(statement.outputs, AIR, VARS)

        # add_lambda_node(stmt.type, stmt.func_str, stmt.metadata)
        func_id = FunctionIdentifier.from_lambda_stmt_id(statement.identifier)
        expr = statement.expression
        executable = load_lambda_function(expr)
        expr_type = FunctionType.get_lambda_type(
            statement.expr_type, len(inspect.signature(executable).parameters)
        )
        mdata = statement.metadata

        visitor = ExpressionVisitor()
        expr_tree = ast.parse(expr)
        visitor.visit(expr_tree)
        nodes = visitor.get_nodes()

        (
            new_vars,
            new_funcs,
            h_edges,
            # h_graph,
        ) = cls.create_expr_node_hypergraph(
            nodes, inputs, outputs, statement.identifier
        )
        h_graph = BaseFuncNode.create_hyper_graph(h_edges)

        VARS.update({v.identifier: v for v in new_vars})
        FUNCS.update({f.identifier: f for f in new_funcs})

        return cls(
            str(uuid.uuid4()),
            func_id,
            expr_type,
            [i.identifier for i in inputs],
            [o.identifier for o in outputs],
            h_edges,
            h_graph,
            mdata,
            expr,
            executable,
        )

    @staticmethod
    def create_expr_node_hypergraph(
        nodes: List[ExprAbstractNode],
        input_vars: List[VariableNode],
        output_vars: List[VariableNode],
        statement_id: LambdaStmtDef,
    ):
        expr_output_var = output_vars[0]  # assumes we have a single output
        out_id = expr_output_var.identifier
        cur_nsp = out_id.namespace
        cur_scp = f"{out_id.scope}.{'.'.join(statement_id.name.split('::'))}"

        uid2node = {n.uid: n for n in nodes}
        lambda_def = None
        for node in nodes:
            if (
                isinstance(node, ExprDefinitionNode)
                and node.def_type == "LAMBDA"
            ):
                lambda_def = node
                break

        (args_def, ret_def) = [uid2node[uid] for uid in lambda_def.children]
        arg_names = [uid2node[uid].identifier for uid in args_def.children]
        arg2var = {aname: ivar for aname, ivar in zip(arg_names, input_vars)}

        new_func_nodes = list()
        new_var_nodes = list()
        new_hyper_edges = list()
        # hyper_graph = nx.DiGraph()

        def convert_to_hyperedge(expr_node_def):
            """
            Args:
                node_def (BaseExprNode): The current node to convert to a func node and a hyperedge. Should be added to he hypergraph as a node. Needs to have edges added from all child nodes to this node.

            Raises:
                TypeError: If some children are not defined ExprNodes

            Returns:
                Tuple:
                    list of new func nodes,
                    list of new variable nodes,
                    list of new hyper edges
            """
            if isinstance(expr_node_def, ExprValueNode):
                expr_func_node = LiteralFuncNode.from_value_node(expr_node_def)
                output_var = VariableNode.from_expr_def(cur_nsp, cur_scp)
                new_hyper_edge = HyperEdge(expr_func_node, [], [output_var])
                new_var_nodes.append(output_var)
                new_func_nodes.append(expr_func_node)
                new_hyper_edges.append(new_hyper_edge)
                return
            elif isinstance(expr_node_def, ExprVariableNode):
                if expr_node_def.identifier in arg2var:
                    return arg2var[expr_node_def.identifier]
                else:
                    return VariableNode.from_expr_def(cur_nsp, cur_scp)
            child_defs = [
                uid2node[child_id] for child_id in expr_node_def.children
            ]

            input_var_nodes = list()
            for child_def in child_defs:
                if isinstance(child_def, ExprVariableNode):
                    if child_def.identifier in arg2var:
                        external_var = arg2var[child_def.identifier]
                        input_var_nodes.append(external_var)
                    else:
                        new_var = VariableNode.from_expr_def(cur_nsp, cur_scp)
                        new_var_nodes.append(new_var)
                        input_var_nodes.append(new_var)
                elif isinstance(child_def, ExprValueNode):
                    pass  # No function to create with this node type
                elif isinstance(child_def, ExprOperatorNode) or isinstance(
                    child_def, ExprDefinitionNode
                ):
                    child_out_var = convert_to_hyperedge(child_def)
                    if child_out_var is not None:
                        input_var_nodes.append(child_out_var)
                else:
                    raise TypeError(
                        f"Unexpected Expr def type: {type(child_def)}"
                    )

            expr_func_node = OperationFuncNode.from_expr_def(expr_node_def)
            output_var = VariableNode.from_expr_def(cur_nsp, cur_scp)
            new_hyper_edge = HyperEdge(
                expr_func_node, input_var_nodes, [output_var]
            )
            new_var_nodes.append(output_var)
            new_func_nodes.append(expr_func_node)
            new_hyper_edges.append(new_hyper_edge)
            # hyper_graph.add_node(new_hyper_edge)

            return output_var

        ret_child = [uid2node[uid] for uid in ret_def.children][0]
        # print(statement_id, ret_child)
        # if isinstance(ret_child, ExprVariableNode):
        #     print(
        #     ret_child.identifier,
        #     [uid2node[cid] for cid in ret_child.children],
        # )
        # else:
        #     print(
        #         ret_child.operator,
        #         [uid2node[cid] for cid in ret_child.children],
        #     )
        ret_child_inputs = [
            convert_to_hyperedge(uid2node[child_id])
            for child_id in ret_child.children
        ]
        expr_func_node = OperationFuncNode.from_expr_def(ret_child)
        new_hyper_edge = HyperEdge(
            expr_func_node, ret_child_inputs, [expr_output_var]
        )
        new_var_nodes.append(expr_output_var)
        new_func_nodes.append(expr_func_node)
        new_hyper_edges.append(new_hyper_edge)
        # convert_to_hyperedge(ret_child)
        return (
            new_var_nodes,
            new_func_nodes,
            new_hyper_edges,
        )

    @classmethod
    def from_data(cls, data: Dict[str, Any]):
        base_values = super().from_data(data)
        expr = data["expression"]
        return cls(*base_values, expr, load_lambda_function(expr))

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({"expression": self.expression})
        return data


@dataclass(repr=False, frozen=False)
class BaseConFuncNode(BaseFuncNode):
    exit: FunctionIdentifier

    def __hash__(self):
        return super().__hash__()

    @classmethod
    def from_container(
        cls,
        container: ContainerDef,
        AIR: AutoMATES_IR,
        VARS: Dict[VariableIdentifier, VariableNode],
        FUNCS: Dict[FunctionIdentifier, BaseFuncNode],
    ) -> BaseConFuncNode:
        func_id = FunctionIdentifier.from_container_id(container.identifier)
        func_type = FunctionType.from_con(container.__class__.__name__)
        inputs = BaseFuncNode.get_or_create_vars(
            container.arguments, AIR, VARS
        )
        outputs = BaseFuncNode.get_or_create_vars(
            container.updated + container.return_value, AIR, VARS
        )

        hyper_edges = list()
        for stmt in container.statements:
            if isinstance(stmt, CallStmtDef):
                # Create a new Container type function node defintion
                new_con_id = stmt.callee_container_id
                con_def = AIR.containers[new_con_id]
                if isinstance(con_def, LoopContainerDef):
                    new_func = LoopConFuncNode.from_container(
                        con_def, AIR, VARS, FUNCS
                    )
                elif isinstance(con_def, FuncContainerDef):
                    new_func = BaseConFuncNode.from_container(
                        con_def, AIR, VARS, FUNCS
                    )
                elif isinstance(con_def, CondContainerDef):
                    new_func = CondConFuncNode.from_container(
                        con_def, AIR, VARS, FUNCS
                    )
                else:
                    raise TypeError(
                        f"Unrecognized container type: {type(con_def)}"
                    )
            elif isinstance(stmt, LambdaStmtDef):
                # Create a new Expression type function node definiton
                new_func = ExpressionFuncNode.from_lambda_stmt(
                    stmt, AIR, VARS, FUNCS
                )
            else:
                raise TypeError(f"Unrecognized statement type: {type(stmt)}")
            FUNCS[new_func.identifier] = new_func
            hyper_edges.append(
                HyperEdge(
                    new_func,
                    [VARS[v_id] for v_id in new_func.input_variables],
                    [VARS[v_id] for v_id in new_func.output_variables],
                )
            )

        hyper_graph = BaseFuncNode.create_hyper_graph(hyper_edges)
        metadata = container.metadata
        exit_id = None
        for edge in hyper_edges:
            first_output = edge.outputs[0]
            if first_output.identifier.name == "EXIT":
                exit_id = first_output
        return cls(
            str(uuid.uuid4()),
            func_id,
            func_type,
            [i.identifier for i in inputs],
            [o.identifier for o in outputs],
            hyper_edges,
            hyper_graph,
            metadata,
            exit=exit_id,
        )

    @classmethod
    def from_data(cls, data: Dict[str, Any]):
        return cls(*(super().from_data(data)), data["identifier"])

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({"identifier": str(self.identifier)})
        return data


@dataclass(repr=False, frozen=False)
class CondConFuncNode(BaseConFuncNode):
    decision_node: ExpressionFuncNode

    @classmethod
    def from_container(
        cls,
        container: ContainerDef,
        AIR: AutoMATES_IR,
        VARS: Dict[VariableIdentifier, VariableNode],
        FUNCS: Dict[FunctionIdentifier, BaseFuncNode],
    ) -> CondConFuncNode:
        mock_func_node = BaseConFuncNode.from_container(
            container, AIR, VARS, FUNCS
        )
        return cls(
            uid=mock_func_node.uid,
            identifier=mock_func_node.identifier,
            type=mock_func_node.type,
            input_variables=mock_func_node.input_variables,
            output_variables=mock_func_node.output_variables,
            hyper_edges=mock_func_node.hyper_edges,
            hyper_graph=mock_func_node.hyper_graph,
            metadata=mock_func_node.metadata,
            exit=mock_func_node.exit,
            decision_node=cls.find_decision_node(mock_func_node),
        )

    @staticmethod
    def find_decision_node(base_func: BaseConFuncNode):
        for edge in base_func.hyper_edges:
            if edge.func_node.type == FunctionType.DECISION:
                return edge.func_node
        return None


@dataclass(repr=False, frozen=False)
class LoopConFuncNode(BaseConFuncNode):
    exit_condition: ExpressionFuncNode

    @classmethod
    def from_container(
        cls,
        container: ContainerDef,
        AIR: AutoMATES_IR,
        VARS: Dict[VariableIdentifier, VariableNode],
        FUNCS: Dict[FunctionIdentifier, BaseFuncNode],
    ) -> BaseConFuncNode:
        mock_func_node = BaseConFuncNode.from_container(
            container, AIR, VARS, FUNCS
        )
        return cls(
            uid=mock_func_node.uid,
            identifier=mock_func_node.identifier,
            type=mock_func_node.type,
            input_variables=mock_func_node.input_variables,
            output_variables=mock_func_node.output_variables,
            hyper_edges=mock_func_node.hyper_edges,
            hyper_graph=mock_func_node.hyper_graph,
            metadata=mock_func_node.metadata,
            exit=mock_func_node.exit,
            exit_condition=cls.find_condition_node(mock_func_node),
        )

    @staticmethod
    def find_condition_node(base_func: BaseConFuncNode):
        # NOTE: If there is more than one condition node then this will find whichever is the first in the list of hyper-edges. Extend this function once we have GrFNs that have more than a single condition node in a ConditionalContainerDef
        for h_edge in base_func.hyper_edges:
            func = h_edge.func_node
            if func.type == FunctionType.CONDITION:
                return func
        return None


# @dataclass(repr=False, frozen=False)
# class LambdaNode(BaseNode):
#     func_type: LambdaType
#     func_str: str
#     function: callable
#     metadata: List[TypedMetadata]

#     def __hash__(self):
#         return hash(self.uid)

#     def __eq__(self, other) -> bool:
#         return self.uid == other.uid

#     def __str__(self):
#         return f"{self.get_label()}: {self.uid}"

#     def __call__(self, *values) -> Iterable[np.ndarray]:
#         expected_num_args = len(self.get_signature())
#         input_num_args = len(values)
#         if expected_num_args != input_num_args:
#             raise RuntimeError(
#                 f"""Incorrect number of inputs
#                 (expected {expected_num_args} found {input_num_args})
#                 for lambda:\n{self.func_str}"""
#             )
#         try:
#             if self.np_shape != (1,):
#                 res = self.v_function(*values)
#             else:
#                 res = self.function(*values)
#             if self.func_type == LambdaType.LITERAL:
#                 return [np.full(self.np_shape, res, dtype=np.float64)]
#             elif isinstance(res, tuple):
#                 return [item for item in res]
#             else:
#                 return [self.parse_result(values, res)]
#         except Exception as e:
#             print(f"Exception occured in {self.func_str}")
#             raise GrFNExecutionException(e)

#     def parse_result(self, values, res):
#         if isinstance(res, dict):
#             res = {k: self.parse_result(values, v) for k, v in res.items()}
#         elif len(values) == 0:
#             res = np.full(self.np_shape, res, dtype=np.float64)
#         return res

#     def get_kwargs(self):
#         return {"shape": "rectangle", "padding": 10, "label": self.get_label()}

#     def get_label(self):
#         return self.func_type.shortname()

#     def get_signature(self):
#         return self.function.__code__.co_varnames

#     @classmethod
#     def from_AIR(
#         cls, lm_id: str, lm_type: str, lm_str: str, mdata: List[TypedMetadata]
#     ):
#         lambda_fn = load_lambda_function(lm_str)
#         if mdata is None:
#             mdata = list()
#         return cls(lm_id, lm_type, lm_str, lambda_fn, mdata)

#     @classmethod
#     def from_dict(cls, data: dict):
#         lambda_fn = load_lambda_function(data["lambda"])
#         lambda_type = LambdaType.from_str(data["type"])
#         if "metadata" in data:
#             metadata = [TypedMetadata.from_data(d) for d in data["metadata"]]
#         else:
#             metadata = []
#         return cls(
#             data["uid"],
#             lambda_type,
#             data["lambda"],
#             lambda_fn,
#             metadata,
#         )

#     def to_dict(self) -> dict:
#         return {
#             "uid": self.uid,
#             "type": str(self.func_type),
#             "lambda": self.func_str,
#             "metadata": [m.to_dict() for m in self.metadata],
#         }


@dataclass
class HyperEdge:
    func_node: BaseFuncNode
    inputs: List[VariableNode]
    outputs: List[VariableNode]

    def __call__(self):
        inputs = [
            var.value
            if var.value is not None
            else var.input_value
            if var.input_value is not None
            else [None]
            for var in self.inputs
        ]
        result = self.func_node(*inputs)
        # If we are in the exit decision hyper edge and in vectorized execution
        if (
            self.func_node.func_type == LambdaType.DECISION
            and any([o.identifier.name == "EXIT" for o in self.inputs])
            and self.func_node.np_shape != (1,)
        ):
            # Initialize seen exits to an array of False if it does not exist
            if not hasattr(self, "seen_exits"):
                self.seen_exits = np.full(
                    self.func_node.np_shape, False, dtype=np.bool
                )

            # Gather the exit conditions for this execution
            exit_var_values = [
                o for o in self.inputs if o.identifier.name == "EXIT"
            ][0].value

            # For each output value, update output nodes with new value that
            # just exited, otherwise keep existing value
            for res_index, out_val in enumerate(result):
                if self.outputs[res_index].value is None:
                    self.outputs[res_index].value = np.full(
                        out_val.shape, np.NaN
                    )
                # If we have seen an exit before at a given position, keep the
                # existing value, otherwise update.
                for j, _ in enumerate(self.outputs[res_index].value):
                    if self.seen_exits[j]:
                        self.outputs[res_index].value[j] = out_val[j]

            # Update seen_exits with any vectorized positions that may have
            # exited during this execution
            self.seen_exits = np.copy(self.seen_exits) | exit_var_values

        else:
            for i, out_val in enumerate(result):
                variable = self.outputs[i]
                if (
                    self.func_node.func_type == LambdaType.LITERAL
                    and variable.input_value is not None
                ):
                    variable.value = variable.input_value
                else:
                    variable.value = out_val

    def __eq__(self, other) -> bool:
        return (
            self.func_node == other.func_node
            and all([i1 == i2 for i1, i2 in zip(self.inputs, other.inputs)])
            and all([o1 == o2 for o1, o2 in zip(self.outputs, other.outputs)])
        )

    def __hash__(self):
        return hash(
            (
                self.func_node.identifier,
                tuple([inp.uid for inp in self.inputs]),
                tuple([out.uid for out in self.outputs]),
            )
        )

    @classmethod
    def from_dict(cls, data: dict, all_nodes: Dict[str, BaseNode]):
        return cls(
            all_nodes[data["function"]],
            [all_nodes[n_id] for n_id in data["inputs"]],
            [all_nodes[n_id] for n_id in data["outputs"]],
        )

    def to_dict(self) -> dict:
        return {
            "inputs": [str(n.identifier) for n in self.inputs],
            "function": str(self.func_node.identifier),
            "outputs": [str(n.identifier) for n in self.outputs],
        }


# @dataclass(repr=False)
# class GrFNSubgraph:
#     uid: str
#     namespace: str
#     scope: str
#     basename: str
#     occurrence_num: int
#     parent: str
#     type: str
#     border_color: str
#     nodes: Iterable[BaseNode]
#     metadata: List[TypedMetadata]

#     def __hash__(self):
#         return hash(self.__str__())

#     def __repr__(self):
#         return self.__str__()

#     def __str__(self):
#         context = f"{self.namespace}.{self.scope}"
#         return f"{self.basename}::{self.occurrence_num} ({context})"

#     def __eq__(self, other) -> bool:
#         return (
#             self.occurrence_num == other.occurrence_num
#             and self.border_color == other.border_color
#             and set([n.uid for n in self.nodes])
#             == set([n.uid for n in other.nodes])
#         )

#     def __call__(
#         self,
#         grfn: GroundedFunctionNetwork,
#         subgraphs_to_hyper_edges: Dict[GrFNSubgraph, List[HyperEdge]],
#         node_to_subgraph: Dict[LambdaNode, GrFNSubgraph],
#         all_nodes_visited: Set[VariableNode],
#     ) -> List[BaseNode]:
#         """
#         Handles the execution of the lambda functions within a subgraoh of
#         GrFN. We place the logic in this function versus directly in __call__
#         so the logic can be shared in the loop subgraph type.

#         Args:
#             grfn (GroundedFucntioNetwork):
#                 The GrFN we are operating on. Used to find successors of nodes.
#             subgraphs_to_hyper_edges (Dict[GrFNSubgraph, List[HyperEdge]]):
#                 A list of a subgraph to the hyper edges with nodes in the
#                 subgraph.
#             node_to_subgraph (Dict[LambdaNode, GrFNSubgraph]):
#                 nodes to the subgraph they are contained in.
#             all_nodes_visited (Set[VariableNode]):
#                 Holds the set of all variable nodes that have been visited

#         Raises:
#             Exception: Raised when we find multiple input interface nodes.

#         Returns:
#             List[BaseNode]: The final list of nodes that we update/output
#             to in the parent container.
#         """
#         # Grab all hyper edges in this subgraph
#         hyper_edges = subgraphs_to_hyper_edges[self]
#         nodes_to_hyper_edge = {e.lambda_fn: e for e in hyper_edges}

#         # There should be only one lambda node of type interface with outputs
#         # all in the same subgraph. Identify this node as the entry point of
#         # execution within this subgraph. Will be none if no input.
#         input_interface_hyper_edge_node = self.get_input_interface_hyper_edge(
#             hyper_edges
#         )
#         output_interface_hyper_edge_node = self.get_output_interface_node(
#             hyper_edges
#         )

#         # Add nodes that must be configured via user input as they have no
#         # input edge
#         standalone_vars = [
#             n
#             for n in self.nodes
#             if isinstance(n, VariableNode) and grfn.in_degree(n) == 0
#         ]
#         all_nodes_visited.update(standalone_vars)

#         # Find the hyper edge nodes with no input to initialize the execution
#         # queue and var nodes with no incoming edges
#         node_execute_queue = [
#             e.lambda_fn for e in hyper_edges if len(e.inputs) == 0
#         ]
#         node_execute_queue.extend(
#             [s for n in standalone_vars for s in grfn.successors(n)]
#         )

#         if input_interface_hyper_edge_node:
#             node_execute_queue.insert(
#                 0, input_interface_hyper_edge_node.lambda_fn
#             )

#         # Need to recurse to a different subgraph if no nodes to execute here
#         if len(node_execute_queue) == 0:
#             global_literal_nodes = [
#                 n
#                 for n in grfn.nodes
#                 if isinstance(n, LambdaNode)
#                 and grfn.in_degree(n) == 0
#                 and n.func_type == LambdaType.LITERAL
#             ]
#             global_output_vars = [
#                 n
#                 for n in grfn.nodes
#                 if isinstance(n, VariableNode) and grfn.out_degree(n) == 0
#             ]

#             # Choose a literal node with maximum distance to the output
#             # to begin recursing.
#             lit_node_to_max_dist = dict()
#             for (l_node, o_node) in product(
#                 global_literal_nodes, global_output_vars
#             ):
#                 max_dist = max(
#                     [
#                         len(path)
#                         for path in all_simple_paths(grfn, l_node, o_node)
#                     ]
#                 )
#                 lit_node_to_max_dist[l_node] = max_dist
#             lits_by_dist = sorted(
#                 list(lit_node_to_max_dist.items()),
#                 key=lambda t: t[1],
#                 reverse=True,
#             )
#             (L_node, _) = lits_by_dist[0]
#             subgraph = node_to_subgraph[L_node]
#             subgraph_hyper_edges = subgraphs_to_hyper_edges[subgraph]
#             subgraph_input_interface = subgraph.get_input_interface_hyper_edge(
#                 subgraph_hyper_edges
#             )
#             subgraph_outputs = subgraph(
#                 grfn,
#                 subgraphs_to_hyper_edges,
#                 node_to_subgraph,
#                 all_nodes_visited,
#             )

#             node_execute_queue.extend(
#                 set(
#                     f_node
#                     for o_node in subgraph_outputs
#                     for f_node in grfn.successors(o_node)
#                     if f_node not in all_nodes_visited
#                 )
#             )

#         while node_execute_queue:
#             executed = True
#             executed_visited_variables = set()
#             node_to_execute = node_execute_queue.pop(0)

#             # TODO remove?
#             if node_to_execute in all_nodes_visited:
#                 continue

#             if node_to_execute not in nodes_to_hyper_edge:
#                 # Node is not in current subgraph
#                 if node_to_execute.func_type == LambdaType.INTERFACE:
#                     subgraph = node_to_subgraph[node_to_execute]
#                     subgraph_hyper_edges = subgraphs_to_hyper_edges[subgraph]
#                     subgraph_input_interface = (
#                         subgraph.get_input_interface_hyper_edge(
#                             subgraph_hyper_edges
#                         )
#                     )
#                     # Either the subgraph has no input interface or all the
#                     # inputs must be set.
#                     if subgraph_input_interface is None or all(
#                         [
#                             n in all_nodes_visited
#                             for n in subgraph_input_interface.inputs
#                         ]
#                     ):
#                         # We need to recurse into a new subgraph as the
#                         # next node is an interface thats not in the
#                         # current subgraph

#                         # subgraph execution returns the updated output nodes
#                         # so we can mark them as visited here in the parent
#                         # in order to continue execution
#                         executed_visited_variables.update(
#                             subgraph(
#                                 grfn,
#                                 subgraphs_to_hyper_edges,
#                                 node_to_subgraph,
#                                 all_nodes_visited,
#                             )
#                         )
#                     else:
#                         node_to_execute = subgraph_input_interface.lambda_fn
#                         executed = False
#                 else:
#                     raise GrFNExecutionException(
#                         "Error: Attempting to execute non-interface node"
#                         + f" {node_to_execute} found in another subgraph."
#                     )
#             elif all(
#                 [
#                     n in all_nodes_visited
#                     for n in nodes_to_hyper_edge[node_to_execute].inputs
#                 ]
#             ):
#                 # All of the input nodes have been visited, so the input values
#                 # are initialized and we can execute. In the case of literal
#                 # nodes, inputs is empty and all() will default to True.
#                 to_execute = nodes_to_hyper_edge[node_to_execute]
#                 to_execute()
#                 executed_visited_variables.update(to_execute.outputs)
#             else:
#                 # We still are waiting on input values to be computed, push to
#                 # the back of the queue
#                 executed = False

#             if executed:
#                 all_nodes_visited.update(executed_visited_variables)
#                 all_nodes_visited.add(node_to_execute)
#                 node_execute_queue.extend(
#                     [
#                         succ
#                         for var in executed_visited_variables
#                         for succ in grfn.successors(var)
#                         if (
#                             succ in self.nodes
#                             and succ not in all_nodes_visited
#                         )
#                         or (
#                             var in self.nodes
#                             and succ.func_type == LambdaType.INTERFACE
#                         )
#                     ]
#                 )
#             else:
#                 node_execute_queue.extend(
#                     [
#                         lambda_pred
#                         for var_pred in grfn.predecessors(node_to_execute)
#                         for lambda_pred in grfn.predecessors(var_pred)
#                         if (
#                             lambda_pred in self.nodes
#                             and lambda_pred not in all_nodes_visited
#                         )
#                         or lambda_pred.func_type == LambdaType.INTERFACE
#                     ]
#                 )
#                 node_execute_queue.append(node_to_execute)

#         return (
#             {}
#             if not output_interface_hyper_edge_node
#             else {n for n in output_interface_hyper_edge_node.outputs}
#         )

#     @classmethod
#     def from_container(
#         cls, con: ContainerDef, occ: int, parent_subgraph: GrFNSubgraph
#     ):
#         id = con.identifier

#         class_to_create = cls
#         if isinstance(con, LoopContainerDef):
#             class_to_create = GrFNLoopSubgraph

#         return class_to_create(
#             str(uuid.uuid4()),
#             id.namespace,
#             id.scope,
#             id.con_name,
#             occ,
#             None if parent_subgraph is None else parent_subgraph.uid,
#             con.__class__.__name__,
#             cls.get_border_color(con.__class__.__name__),
#             [],
#             con.metadata,
#         )

#     def get_input_interface_hyper_edge(self, hyper_edges):
#         """
#         Get the interface node for input in this subgraph

#         Args:
#             hyper_edges (List[HyperEdge]): All hyper edges with nodes in this
#                 subgraph.

#         Returns:
#             LambdaNode: The lambda node for the input interface. None if there
#                 is no input for this subgraph.
#         """
#         input_interfaces = [
#             e
#             for e in hyper_edges
#             if e.lambda_fn.func_type == LambdaType.INTERFACE
#             and all([o in self.nodes for o in e.outputs])
#         ]

#         if len(input_interfaces) > 1 and self.parent:
#             raise GrFNExecutionException(
#                 "Found multiple input interface nodes"
#                 + " in subgraph during execution."
#                 + f" Expected 1 but {len(input_interfaces)} were found."
#             )
#         elif len(input_interfaces) == 0:
#             return None

#         return input_interfaces[0]

#     def get_output_interface_node(self, hyper_edges):
#         """
#         Get the interface node for output in this subgraph

#         Args:
#             hyper_edges (List[HyperEdge]): All hyper edges with nodes in this
#                 subgraph.

#         Returns:
#             LambdaNode: The lambda node for the output interface.
#         """
#         output_interfaces = [
#             e
#             for e in hyper_edges
#             if e.lambda_fn.func_type == LambdaType.INTERFACE
#             and all([o in self.nodes for o in e.inputs])
#         ]

#         if not self.parent:
#             # The root subgraph has no output interface
#             return None
#         elif len(output_interfaces) != 1:
#             raise GrFNExecutionException(
#                 "Found multiple output interface nodes"
#                 + " in subgraph during execution."
#                 + f" Expected 1 but {len(output_interfaces)} were found."
#             )
#         return output_interfaces[0]

#     @staticmethod
#     def get_border_color(type_str):
#         if type_str == "CondContainerDef":
#             return "orange"
#         elif type_str == "FuncContainerDef":
#             return "forestgreen"
#         elif type_str == "LoopContainerDef":
#             return "navyblue"
#         else:
#             raise TypeError(f"Unrecognized subgraph type: {type_str}")

#     @classmethod
#     def from_dict(cls, data: dict, all_nodes: Dict[str, BaseNode]):
#         subgraph_nodes = [all_nodes[n_id] for n_id in data["nodes"]]
#         type_str = data["type"]

#         class_to_create = cls
#         if type_str == "LoopContainerDef":
#             class_to_create = GrFNLoopSubgraph

#         return class_to_create(
#             data["uid"],
#             data["namespace"],
#             data["scope"],
#             data["basename"],
#             data["occurrence_num"],
#             data["parent"],
#             type_str,
#             cls.get_border_color(type_str),
#             subgraph_nodes,
#             [TypedMetadata.from_data(d) for d in data["metadata"]]
#             if "metadata" in data
#             else [],
#         )

#     def to_dict(self):
#         return {
#             "uid": self.uid,
#             "namespace": self.namespace,
#             "scope": self.scope,
#             "basename": self.basename,
#             "occurrence_num": self.occurrence_num,
#             "parent": self.parent,
#             "type": self.type,
#             "border_color": self.border_color,
#             "nodes": [n.uid for n in self.nodes],
#             "metadata": [m.to_dict() for m in self.metadata],
#         }


# @dataclass(repr=False, eq=False)
# class GrFNLoopSubgraph(GrFNSubgraph):
#     def __call__(
#         self,
#         grfn: GroundedFunctionNetwork,
#         subgraphs_to_hyper_edges: Dict[GrFNSubgraph, List[HyperEdge]],
#         node_to_subgraph: Dict[LambdaNode, GrFNSubgraph],
#         all_nodes_visited: Set[VariableNode],
#     ):
#         """
#         Handle a call statement on an object of type GrFNSubgraph

#         Args:
#             grfn (GroundedFucntioNetwork):
#                 The GrFN we are operating on. Used to find successors of nodes.
#             subgraphs_to_hyper_edges (Dict[GrFNSubgraph, List[HyperEdge]]):
#                 A list of a subgraph to the hyper edges with nodes in the
#                 subgraph.
#             node_to_subgraph (Dict[LambdaNode, GrFNSubgraph]):
#                 nodes to the subgraph they are contained in.
#             all_nodes_visited (Set[VariableNode]):
#                 Holds the set of all variable nodes that have been visited
#         """

#         # First, find exit node within the subgraph
#         exit_var_nodes = [
#             n
#             for n in self.nodes
#             if isinstance(n, VariableNode) and n.identifier.var_name == "EXIT"
#         ]
#         if len(exit_var_nodes) != 1:
#             raise GrFNExecutionException(
#                 "Found incorrect number of exit var nodes in"
#                 + " loop subgraph during execution."
#                 + f" Expected 1 but {len(exit_var_nodes)} were found."
#             )
#         exit_var_node = exit_var_nodes[0]

#         # Find the first decision node and mark its input variables as
#         # visited so we can execute the cyclic portion of the loop
#         input_interface = self.get_input_interface_hyper_edge(
#             subgraphs_to_hyper_edges[self]
#         )
#         initial_decision = {
#             n
#             for v in input_interface.outputs
#             for n in grfn.successors(v)
#             if n.func_type == LambdaType.DECISION
#         }
#         first_decision_vars = {
#             v
#             for lm_node in initial_decision
#             for v in grfn.predecessors(lm_node)
#             if isinstance(v, VariableNode)
#         }

#         var_results = set()
#         initial_visited_nodes = set()
#         # Loop until the exit value becomes true
#         while (
#             exit_var_node.value is None
#             or (
#                 isinstance(exit_var_node.value, bool)
#                 and not exit_var_node.value
#             )
#             or (
#                 isinstance(exit_var_node.value, np.ndarray)
#                 and not all(exit_var_node.value)
#             )
#         ):
#             initial_visited_nodes = all_nodes_visited.copy()
#             initial_visited_nodes.update(first_decision_vars)
#             var_results = super().__call__(
#                 grfn,
#                 subgraphs_to_hyper_edges,
#                 node_to_subgraph,
#                 initial_visited_nodes,
#             )
#         all_nodes_visited = all_nodes_visited.union(initial_visited_nodes)
#         return var_results


# class GrFNType:
#     name: str
#     fields: List[Tuple[str, str]]

#     def __init__(self, name, fields):
#         self.name = name
#         self.fields = fields

#     def get_initial_dict(self):
#         d = {}
#         for field in self.fields:
#             d[field] = None
#         return d


# NOTE: this is the GrFN 3.0 definition
@dataclass
class GroundedFunctionNetwork:
    uid: str
    identifier: GrFNIdentifier
    entry_point: FunctionIdentifier
    functions: Dict[FunctionIdentifier, BaseFuncNode]
    variables: Dict[VariableIdentifier, VariableNode]
    objects: Dict[ObjectIdentifier, ObjectDef]
    types: Dict[TypeIdentifier, TypeDef]
    metadata: List[TypedMetadata]

    def __post_init__(self):
        self.namespace = self.identifier.namespace
        self.scope = self.identifier.scope
        self.name = self.identifier.name
        self.label = f"{self.name} ({self.namespace}.{self.scope})"

        # NOTE: removing detached variables from GrFN
        # self.__remove_detatched_vars()

        # TODO: call expression function vectorization at some point in time on
        # load

        # TODO decide how we detect configurable inputs for execution
        # Configurable inputs are all variables assigned to a literal in the
        # root level subgraph AND input args to the root level subgraph

    def __remove_detatched_vars(self):
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

        for idx, del_idx in enumerate(del_indices):
            del self.variables[del_idx - idx]

    # def __init__(
    #     self,
    #     uid: str,
    #     id: ContainerIdentifier,
    #     timestamp: str,
    #     # G: nx.DiGraph,
    #     H: List[HyperEdge],
    #     S: nx.DiGraph,
    #     T: List[TypeDef],
    #     M: List[TypedMetadata],
    # ):
    #     # super().__init__(G)
    #     self.hyper_edges = H
    #     self.subgraphs = S

    #     self.uid = uid
    #     self.timestamp = timestamp
    #     self.namespace = id.namespace
    #     self.scope = id.scope
    #     self.name = id.name
    #     self.label = f"{self.name} ({self.namespace}.{self.scope})"
    #     self.metadata = M

    #     self.variables = [n for n in self.nodes if isinstance(n, VariableNode)]
    #     self.lambdas = [n for n in self.nodes if isinstance(n, LambdaNode)]
    #     self.types = T

    #     self.__remove_detached_vars()

    #     root_subgraphs = [s for s in self.subgraphs if not s.parent]
    #     if len(root_subgraphs) != 1:
    #         raise Exception(
    #             "Error: Incorrect number of root subgraphs found in GrFN."
    #             + f"Should be 1 and found {len(root_subgraphs)}."
    #         )
    #     self.root_subgraph = root_subgraphs[0]

    #     for lambda_node in self.lambdas:
    #         lambda_node.v_function = np.vectorize(lambda_node.function)

    #     # TODO decide how we detect configurable inputs for execution
    #     # Configurable inputs are all variables assigned to a literal in the
    #     # root level subgraph AND input args to the root level subgraph
    #     self.inputs = [
    #         n
    #         for e in self.hyper_edges
    #         for n in e.outputs
    #         if (
    #             n in self.root_subgraph.nodes
    #             and e.lambda_fn.func_type == LambdaType.LITERAL
    #         )
    #     ]
    #     self.inputs.extend(
    #         [
    #             n
    #             for n, d in self.in_degree()
    #             if d == 0 and isinstance(n, VariableNode)
    #         ]
    #     )
    #     self.literal_vars = list()
    #     for var_node in self.variables:
    #         preds = list(self.predecessors(var_node))
    #         if len(preds) > 0 and preds[0].func_type == LambdaType.LITERAL:
    #             self.literal_vars.append(var_node)
    #     self.outputs = [
    #         n
    #         for n, d in self.out_degree()
    #         if d == 0
    #         and isinstance(n, VariableNode)
    #         and n in self.root_subgraph.nodes
    #     ]

    #     self.uid2varnode = {v.uid: v for v in self.variables}

    #     self.input_names = [var_node.identifier for var_node in self.inputs]

    #     self.output_names = [var_node.identifier for var_node in self.outputs]

    #     self.input_name_map = {
    #         var_node.identifier.var_name: var_node for var_node in self.inputs
    #     }
    #     self.input_identifier_map = {
    #         var_node.identifier: var_node for var_node in self.inputs
    #     }
    #     self.literal_identifier_map = {
    #         var_node.identifier: var_node for var_node in self.literal_vars
    #     }

    #     self.output_name_map = {
    #         var_node.identifier.var_name: var_node for var_node in self.outputs
    #     }
    #     self.FCG = self.to_FCG()
    #     self.function_sets = self.build_function_sets()

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
        self,
        inputs: Dict[str, Any],
        literals: Dict[str, Any] = None,
        desired_outputs: List[str] = None,
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
            desired_outputs: A list of variable names to customize the
            desired variable nodes whose values we should output after
            execution. Will find the max version var node in the root container
            for each name given and return their values.

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

        # Check if vectorized input is given and configure the numpy shape
        for input_node in [n for n in self.inputs if n in full_inputs]:
            value = full_inputs[input_node]
            if isinstance(value, np.ndarray):
                if self.np_shape != value.shape and self.np_shape != (1,):
                    raise GrFNExecutionException(
                        f"Error: Given two vectorized inputs with different shapes: '{value.shape}' and '{self.np_shape}'"
                    )
                self.np_shape = value.shape

        # Set the values of input var nodes given in the inputs dict
        for input_node in [n for n in self.inputs if n in full_inputs]:
            value = full_inputs[input_node]
            # TODO: need to find a way to incorporate a 32/64 bit check here
            if isinstance(value, (float, np.float64)):
                value = np.full(self.np_shape, value, dtype=np.float64)
            if isinstance(value, (int, np.int64)):
                value = np.full(self.np_shape, value, dtype=np.int64)
            elif isinstance(value, (dict, list)):
                value = np.array([value] * self.np_shape[0])

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
                # TODO: need to find a way to incorporate a 32/64 bit
                # check here
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
            output.identifier.name: output.value for output in self.outputs
        }

    @classmethod
    def from_AIR(cls, AIR: AutoMATES_IR):
        FUNCS = dict()
        VARS = dict()
        OBJECTS = dict()
        TYPES = dict()
        METADATA = AIR.metadata

        root_con = AIR.containers[AIR.entrypoint]
        entry_func = BaseConFuncNode.from_container(root_con, AIR, VARS, FUNCS)
        entry_func_id = entry_func.identifier
        FUNCS[entry_func_id] = entry_func
        return cls(
            str(uuid.uuid4()),
            GrFNIdentifier.from_air_id(AIR.identifier),
            entry_func_id,
            FUNCS,
            VARS,
            OBJECTS,
            TYPES,
            METADATA,
        )

        # def add_variable_node(
        #     v_id: VariableIdentifier, v_data: VariableDef
        # ) -> VariableNode:
        #     node = VariableNode.from_id(v_id, v_data)
        #     # network.add_node(node, **(node.get_kwargs()))
        #     return node

        # variable_nodes = {
        #     v_id: add_variable_node(v_id, v_data)
        #     for v_id, v_data in air.variables.items()
        # }

        # def add_lambda_node(
        #     lambda_type: LambdaType,
        #     lambda_str: str,
        #     metadata: List[TypedMetadata] = None,
        # ) -> LambdaNode:
        #     lambda_id = BaseNode.create_node_id()
        #     node = LambdaNode.from_AIR(
        #         lambda_id, lambda_type, lambda_str, metadata
        #     )
        #     # network.add_node(node, **(node.get_kwargs()))
        #     return node

        # def add_hyper_edge(
        #     inputs: Iterable[VariableNode],
        #     lambda_node: LambdaNode,
        #     outputs: Iterable[VariableNode],
        # ) -> None:
        #     network.add_edges_from(
        #         [(in_node, lambda_node) for in_node in inputs]
        #     )
        #     network.add_edges_from(
        #         [(lambda_node, out_node) for out_node in outputs]
        #     )
        #     hyper_edges.append(HyperEdge(lambda_node, inputs, outputs))

        # def translate_container(
        #     con: ContainerDef,
        #     inputs: Iterable[VariableNode],
        #     parent: GrFNSubgraph = None,
        # ) -> Iterable[VariableNode]:
        #     con_name = con.identifier
        #     if con_name not in Occs:
        #         Occs[con_name] = 0

        #     con_subgraph = GrFNSubgraph.from_container(
        #         con, Occs[con_name], parent
        #     )
        #     live_variables = dict()
        #     if len(inputs) > 0:
        #         in_var_names = [n.identifier.var_name for n in inputs]
        #         in_var_str = ",".join(in_var_names)
        #         interface_func_str = f"lambda {in_var_str}:({in_var_str})"
        #         func = add_lambda_node(
        #             LambdaType.INTERFACE, interface_func_str
        #         )
        #         out_nodes = [variable_nodes[v_id] for v_id in con.arguments]
        #         add_hyper_edge(inputs, func, out_nodes)
        #         con_subgraph.nodes.append(func)

        #         live_variables.update(
        #             {id: node for id, node in zip(con.arguments, out_nodes)}
        #         )
        #     else:
        #         live_variables.update(
        #             {v_id: variable_nodes[v_id] for v_id in con.arguments}
        #         )

        #     con_subgraph.nodes.extend(list(live_variables.values()))

        #     for stmt in con.statements:
        #         translate_stmt(stmt, live_variables, con_subgraph)

        #     subgraphs.add_node(con_subgraph)

        #     if parent is not None:
        #         subgraphs.add_edge(parent, con_subgraph)

        #     if len(inputs) > 0:
        #         # Do this only if this is not the starting container
        #         returned_vars = [variable_nodes[v_id] for v_id in con.returns]
        #         update_vars = [variable_nodes[v_id] for v_id in con.updated]
        #         output_vars = returned_vars + update_vars

        #         out_var_names = [n.identifier.var_name for n in output_vars]
        #         out_var_str = ",".join(out_var_names)
        #         interface_func_str = f"lambda {out_var_str}:({out_var_str})"
        #         func = add_lambda_node(
        #             LambdaType.INTERFACE, interface_func_str
        #         )
        #         con_subgraph.nodes.append(func)
        #         return (output_vars, func)

        # @singledispatch
        # def translate_stmt(
        #     stmt: StmtDef,
        #     live_variables: Dict[VariableIdentifier, VariableNode],
        #     parent: GrFNSubgraph,
        # ) -> None:
        #     raise ValueError(f"Unsupported statement type: {type(stmt)}")

        # @translate_stmt.register
        # def _(
        #     stmt: CallStmtDef,
        #     live_variables: Dict[VariableIdentifier, VariableNode],
        #     subgraph: GrFNSubgraph,
        # ) -> None:
        #     new_con = air.containers[stmt.call_id]
        #     if stmt.call_id not in Occs:
        #         Occs[stmt.call_id] = 0

        #     inputs = [variable_nodes[v_id] for v_id in stmt.inputs]
        #     (con_outputs, interface_func) = translate_container(
        #         new_con, inputs, subgraph
        #     )
        #     Occs[stmt.call_id] += 1
        #     out_nodes = [variable_nodes[v_id] for v_id in stmt.outputs]
        #     subgraph.nodes.extend(out_nodes)
        #     add_hyper_edge(con_outputs, interface_func, out_nodes)
        #     for output_node in out_nodes:
        #         var_id = output_node.identifier
        #         live_variables[var_id] = output_node

        # @translate_stmt.register
        # def _(
        #     stmt: LambdaStmtDef,
        #     live_variables: Dict[VariableIdentifier, VariableNode],
        #     subgraph: GrFNSubgraph,
        # ) -> None:
        #     # inputs = [variable_nodes[v_id] for v_id in stmt.inputs]
        #     # out_nodes = [variable_nodes[v_id] for v_id in stmt.outputs]
        #     # func = add_lambda_node(stmt.type, stmt.func_str, stmt.metadata)
        #     func = ExpressionFuncNode.from_AIR(stmt)
        #     child_functions.append(func)

        #     # TODO: add func to the func_tree here. Requires pointer to
        #     # current parent function

        #     subgraph.nodes.append(func)
        #     subgraph.nodes.extend(out_nodes)

        #     add_hyper_edge(inputs, func, out_nodes)
        #     for output_node in out_nodes:
        #         var_id = output_node.identifier
        #         live_variables[var_id] = output_node

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
                if func.func_type == LambdaType.OPERATOR:
                    return
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

    def to_AGraph(self, expand_expressions=False):
        """Export to a PyGraphviz AGraph object."""
        N = pgv.AGraph(directed=True)
        # subgraphs = list()
        FUNCS = self.functions
        VARS = self.variables

        def build_network_and_subgraphs(
            func_node: BaseFuncNode,
            parent_inputs: Dict[VariableIdentifier, VariableNode],
            parent_subgraph: pgv.AGraph,
        ) -> Dict[VariableIdentifier, VariableNode]:

            out_vars = {
                v_id: VARS[v_id] for v_id in func_node.output_variables
            }

            # Can't use basenames because cond nodes will have mult vars with the same basename
            if len(parent_inputs) == 0:
                live_vars = dict()
                in_vars = dict()
            else:
                in_vars = {
                    v_id: parent_inputs[i]
                    for i, v_id in enumerate(func_node.input_variables)
                }
                live_vars = deepcopy(in_vars)
            all_sub_nodes = list()
            cur_subgraph = parent_subgraph.add_subgraph(
                [],
                name=f"cluster_{str(func_node.identifier)}",
                label=func_node.identifier.name,
                style="bold, rounded",
                rankdir="TB",
                color=BaseFuncNode.get_border_color(func_node),
            )

            def add_input_output_nodes(f_node, i_nodes, o_nodes):
                all_sub_nodes.append(f_node)
                N.add_node(f_node, **(f_node.get_kwargs()))
                for ivar_node in i_nodes:
                    if ivar_node.identifier in live_vars:
                        ivar_node = live_vars[ivar_node.identifier]
                    N.add_node(ivar_node, **(ivar_node.get_kwargs()))
                    N.add_edge(ivar_node, f_node)

                for ovar_node in o_nodes:
                    if ovar_node.identifier in live_vars:
                        ovar_node = live_vars[ovar_node.identifier]
                    N.add_node(ovar_node, **(ovar_node.get_kwargs()))
                    N.add_edge(f_node, ovar_node)

                all_sub_nodes.extend(
                    [n for n in i_nodes if n.identifier not in in_vars]
                )
                all_sub_nodes.extend(
                    [n for n in o_nodes if n.identifier not in out_vars]
                )

            for h_edge in func_node.hyper_edges:
                new_func = h_edge.func_node
                if isinstance(new_func, BaseConFuncNode):
                    sub_nodes = build_network_and_subgraphs(
                        new_func, h_edge.inputs, cur_subgraph
                    )
                    all_sub_nodes.extend(sub_nodes)
                    named_callee_outputs = {
                        var_id.name: VARS[var_id]
                        for var_id in new_func.output_variables
                    }
                    live_vars.update(
                        {
                            var.identifier: named_callee_outputs[
                                var.identifier.name
                            ]
                            for var in h_edge.outputs
                        }
                    )
                elif isinstance(new_func, ExpressionFuncNode):
                    # Set this up to expand when requested
                    if expand_expressions:
                        sub_nodes = build_network_and_subgraphs(
                            new_func, h_edge.inputs, cur_subgraph
                        )
                        all_sub_nodes.extend(sub_nodes)
                        named_callee_outputs = {
                            var_id.name: VARS[var_id]
                            for var_id in new_func.output_variables
                        }
                        live_vars.update(
                            {v.identifier: v for v in h_edge.inputs}
                        )
                        live_vars.update(
                            {
                                var.identifier: named_callee_outputs[
                                    var.identifier.name
                                ]
                                for var in h_edge.outputs
                            }
                        )
                    else:
                        add_input_output_nodes(
                            new_func, h_edge.inputs, h_edge.outputs
                        )
                elif isinstance(new_func, OperationFuncNode):
                    add_input_output_nodes(
                        new_func, h_edge.inputs, h_edge.outputs
                    )
                else:
                    raise TypeError(
                        f"Unrecognized function type during GrFN3 AGraph generation: {type(new_func)}"
                    )

            print(func_node, len(all_sub_nodes))
            if len(parent_inputs) == 0:
                all_sub_nodes += list(live_vars.values())
            # N.add_subgraph(
            #     all_sub_nodes,
            #     name=f"cluster_{str(func_node.identifier)}",
            #     label=func_node.identifier.name,
            #     style="bold, rounded",
            #     rankdir="TB",
            #     color=BaseFuncNode.get_border_color(func_node),
            # )
            cur_subgraph.add_nodes_from(all_sub_nodes)
            return all_sub_nodes

        build_network_and_subgraphs(FUNCS[self.entry_point], [], N)
        N.graph_attr.update(
            {"dpi": 227, "fontsize": 20, "fontname": "Menlo", "rankdir": "TB"}
        )
        N.node_attr.update({"fontname": "Menlo"})
        print(len(list(N.nodes())))
        return N

    def to_AGraph__old(self):
        """Export to a PyGraphviz AGraph object."""
        var_nodes = [n for n in self.nodes if isinstance(n, VariableNode)]
        input_nodes = []
        for v in var_nodes:
            if self.in_degree(v) == 0 or (
                len(list(self.predecessors(v))) == 1
                and list(self.predecessors(v))[0].func_type
                == LambdaType.LITERAL
            ):
                input_nodes.append(v)
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
            # container_subgraph.add_subgraph(list(input_var_nodes), rank="same")
            container_subgraph.add_subgraph(
                [v.uid for v in input_var_nodes], rank="same"
            )

            for new_subgraph in self.subgraphs.successors(subgraph):
                populate_subgraph(new_subgraph, container_subgraph)

            for _, func_sets in self.function_sets.items():
                for func_set in func_sets:
                    func_set = list(func_set.intersection(set(subgraph.nodes)))

                    container_subgraph.add_subgraph(
                        func_set,
                    )
                    output_var_nodes = list()
                    for func_node in func_set:
                        succs = list(self.successors(func_node))
                        output_var_nodes.extend(succs)
                    output_var_nodes = set(output_var_nodes) - output_nodes
                    var_nodes = output_var_nodes.intersection(subgraph.nodes)

                    container_subgraph.add_subgraph(
                        [v.uid for v in var_nodes],
                    )

        root_subgraph = [n for n, d in self.subgraphs.in_degree() if d == 0][0]
        populate_subgraph(root_subgraph, A)

        # TODO this code helps with the layout of the graph. However, it assumes
        # all var nodes start at -1 and are consecutive. This is currently not
        # the case, so it creates random hanging var nodes if run. Fix this.

        # unique_var_names = {
        #     "::".join(n.name.split("::")[:-1])
        #     for n in A.nodes()
        #     if len(n.name.split("::")) > 2
        # }
        # for name in unique_var_names:
        #     max_var_version = max(
        #         [
        #             int(n.name.split("::")[-1])
        #             for n in A.nodes()
        #             if n.name.startswith(name)
        #         ]
        #     )
        #     min_var_version = min(
        #         [
        #             int(n.name.split("::")[-1])
        #             for n in A.nodes()
        #             if n.name.startswith(name)
        #         ]
        #     )
        #     for i in range(min_var_version, max_var_version):
        #         e = A.add_edge(f"{name}::{i}", f"{name}::{i + 1}")
        #         e = A.get_edge(f"{name}::{i}", f"{name}::{i + 1}")
        #         e.attr["color"] = "invis"

        # for agraph_node in [
        #     a for (a, b) in product(A.nodes(), self.output_names) if a.name == str(b)
        # ]:
        #     agraph_node.attr["rank"] = "max"

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

    def to_dict(self) -> Dict:
        """Outputs the contents of this GrFN to a dict object.

        :return: Description of returned object.
        :rtype: type
        :raises ExceptionName: Why the exception is raised.
        """
        # subgraph_funcs = [sgraph.to_dict() for sgraph in self.subgraphs]
        # lambda_funcs = [func.to_dict() for func in self.lambdas]
        # visitor = ExpressionVisitor()
        # expr_node_lists = [
        #     visitor.visit(ast.parse(lm_node.func_str))
        #     for lm_node in self.lambdas
        # ]
        # operator_nodes = list()
        # for expr_nodes_obj in expr_node_lists:
        #     expr_nodes = expr_nodes_obj.nodes
        #     for expr_node in expr_nodes:
        #         if isinstance(expr_node, ExprOperatorNode):
        #             new_op_func = dict()

        # operator_func_defs = []
        data = {
            "uid": self.uid,
            "identifier": str(self.identifier),
            "entry_point": str(self.entry_point),
            "variables": [var.to_dict() for var in self.variables.values()],
            "functions": [func.to_dict() for func in self.functions.values()],
            "types": [t_def.to_dict() for t_def in self.types.values()],
            "objects": [obj.to_dict() for obj in self.objects.values()],
            "metadata": [m.to_dict() for m in self.metadata],
        }

    def to_json(self) -> str:
        """Outputs the contents of this GrFN to a JSON object string.

        :return: Description of returned object.
        :rtype: type
        :raises ExceptionName: Why the exception is raised.
        """
        data = self.to_dict()
        return json.dumps(data)

    def to_json_file(self, json_path) -> None:
        with open(json_path, "w") as outfile:
            outfile.write(self.to_json())

    @classmethod
    def from_json(cls, json_path):
        """Load a GrFN 3.0 JSON file and reconstruct the GrFN from it.
        As it stand, the function reconstruction doesn't work correctly.

        :param type cls: This instance of GrFN 3.0
        :param type json_path: Path to a GrFN 3.0 JSON file
        :return: A reconstructed GrFN 3.0 object
        :rtype: GroundedFunctionNetwork object

        """

        def extract_func_identifier(id):
            pieces = id.split("::")
            if len(pieces) > 4:
                return pieces[-4], pieces[-3], pieces[-2], pieces[-1]
            else:
                return pieces[1], pieces[2], pieces[3]

        data = json.load(open(json_path, "r"))

        F = dict()
        HE = dict() 
        for f in data["functions"]:
            namespace,scope,name,idx = extract_func_identifier(f["identifier"])
            if f["type"] == "decision":
                F[FunctionIdentifier(namespace=namespace,scope=scope,name=name,index=int(idx))] = ExpressionFuncNode.from_data(f)
            elif f["type"] == "pack":
                F[FunctionIdentifier(namespace=namespace,scope=scope,name=name,index=int(idx))] = ExpressionFuncNode.from_data(f)
            elif f["type"] == "operator":
                F[FunctionIdentifier(namespace=namespace,scope=scope,name=name,index=int(idx))] = ExpressionFuncNode.from_data(f)
            elif f["type"] == "literal":
                F[FunctionIdentifier(namespace=namespace,scope=scope,name=name,index=int(idx))] = ExpressionFuncNode.from_data(f)
            elif f["type"] == "assign":
                F[FunctionIdentifier(namespace=namespace,scope=scope,name=name,index=int(idx))] = ExpressionFuncNode.from_data(f)
            elif f["type"] == "container":
                F[FunctionIdentifier(namespace=namespace,scope=scope,name=name,index=int(idx))] = ExpressionFuncNode.from_data(f)
            elif f["type"] == "condition":
                F[FunctionIdentifier(namespace=namespace,scope=scope,name=name,index=int(idx))] = ExpressionFuncNode.from_data(f)
            elif f["type"] == "iterable":
                F[FunctionIdentifier(namespace=namespace,scope=scope,name=name,index=int(idx))] = ExpressionFuncNode.from_data(f)
            else:
                F[FunctionIdentifier(namespace=namespace,scope=scope,name=name,index=int(idx))] = BaseFuncNode.from_data(f,F)

        V = dict()
        for v in data["variables"]:
            namespace,scope,name,idx = extract_func_identifier(v["identifier"])
            V[VariableIdentifier(namespace=namespace,scope=scope,name=name,index=int(idx))] = VariableNode.from_dict(v)

        O = dict() 
        T = dict()
        M = [TypedMetadata.from_data(m) for m in data["metadata"]]

        grfn_ns,grfn_scope,grfn_name = extract_func_identifier(data["identifier"])
        fn_ns,fn_scope,fn_name,fn_idx = extract_func_identifier(data["entry_point"])

        return cls(data["uid"], 
        GrFNIdentifier(namespace=grfn_ns,scope=grfn_scope,name=grfn_name), 
        FunctionIdentifier(namespace=fn_ns,scope=fn_scope,name=fn_name,index=int(fn_idx)), 
        F, V, O, T, M)

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
        return cls.from_dict(data)


# =============================================================================
# TODO: @Tito fill in the code here for the new GrFN 2 CAG pipeline
# =============================================================================
@dataclass
class CAGContainer:
    """
    A container definition to be stored in a CausalAnalysisGraph that holds a collection of nodes that are contained under a container type FuncNode in GrFN. This class also holds a reference to a parent CAGContainer. If the parent reference is null then this is the root container of the CAG.
    """

    uid: str
    identifier: CAGContainerIdentifier
    type: str
    parent: CAGContainerIdentifier
    nodes: List[VariableIdentifier]
    metadata: List[TypedMetadata]

    @classmethod
    def from_func_node(cls, func: BaseConFuncNode, parent: FunctionIdentifier):
        """Creates a CAGContainer from a GrFN FuncNode definition and the identifier of a parent FuncNode

        Args:
            func (BaseConFuncNode): A container type FuncNode that this CAGContainer will represent at the CAG level
            parent (FunctionIdentifier): The identifier of the funcNode that contained func in the GrFN

        Returns:
            CAGContainer: a CAG container definition
        """
        con_id = CAGContainerIdentifier.from_function_id(func.identifier)
        if parent is not None:
            parent_id = CAGContainerIdentifier.from_function_id(
                parent.identifier
            )
        else:
            parent_id = None

        # FIXME: @Tito the variables captured during container creation here may have a superset of all the variables you actually want to have appear in the CAG
        variables = list()
        for edge in func.hyper_edges:
            variables.extend([v.identifier for v in edge.inputs])
            variables.extend([v.identifier for v in edge.outputs])

        return cls(
            uid=str(uuid.uuid4()),
            identifier=con_id,
            type=str(func.type),
            parent=parent_id,
            nodes=list(set(variables)),
            metadata=func.metadata,
        )

    @classmethod
    def from_dict(cls, data: dict) -> CAGContainer:
        """Reloads a CAGContainer from a dictionary that has been loaded from a JSON file

        Args:
            data (dict): the data dict from the saved CAG JSON

        Returns:
            CAGContainer: A CAGContainer with all the data from the data dict arg
        """
        return NotImplemented

    def to_dict(self) -> dict:
        """Returns this class data as a JSON serializable dictionary

        Returns:
            dict: a dictionary of serializable values
        """
        return {
            "uid": self.uid,
            "identifier": str(self.identifier),
            "type": self.type,
            "parent": str(self.parent),
            "nodes": [str(var_id) for var_id in self.nodes],
            "metadata": [m.to_dict() for m in self.metadata],
        }


@dataclass
class CausalAnalysisGraph:
    """
    A causal representation of a GrFN or GroMEt. This graph shows the following:
        (0) the variables present in a GrFN or GroMEt
        (1) the interactions between variables (in the form of edges)
        (2) the containers from the original GrFN/GroMEt
        (3) which variables were included in which container
        (4) which containers are children of other containers

    The class here captures all of that using lists of variables, edges, and containers. Along with that we capture identifier information, the date of creation, and any metadata that existed at the GrFN/GroMEt level in the appropriate location either at the level of the CAG, CAGContainer, or VariableNode.

    NOTE: We still have both identifiers and uids, but we now have a schema that *should* ensure that identifiers are unique and sufficient. Eventually we should switch to only using identifiers (since they are more human readable) but since we haven't tested uniqueness yet we are leaving uids in for now just in case we need them.
    """

    uid: str
    identifier: CAGIdentifier
    date_created: str
    nodes: List[VariableNode]
    edges: List[Tuple[VariableIdentifier, VariableIdentifier]]
    containers: List[CAGContainer]
    metadata: List[TypedMetadata]

    @classmethod
    def from_GrFN(cls, G: GroundedFunctionNetwork):
        """Builds a CausalAnalysisGraph (CAG) from a GrFN using GrFN 3.0

        Args:
            G (GroundedFunctionNetwork): A GrFN 3.0 object

        Returns:
            A CausalAnalysisGraph object
        """

        def containers_from_hyper_edges(
            func: BaseConFuncNode, parent: BaseConFuncNode = None
        ) -> List[CAGContainer]:
            """Returns a list of CAGContainers created from the hyper edges of this function node and all child function nodes that hold container functions

            Args:
                func (BaseConFuncNode): A container function node from GrFN

            Returns:
                A list of CAGContainers translated from the hyper edges
            """
            res = [CAGContainer.from_func_node(func, parent)]
            for edge in func.hyper_edges:
                child_func = edge.func_node
                if isinstance(child_func, BaseConFuncNode):
                    new_cons = containers_from_hyper_edges(child_func, func)
                    res.extend(new_cons)

            return res

        cons = containers_from_hyper_edges(G.functions[G.entry_point])

        # TODO: @Tito implement this
        return cls(
            uid=str(uuid.uuid4()),
            identifier=CAGIdentifier.from_GrFN_id(G.identifier),
            date_created=str(datetime.now()),
            nodes=[],
            edges=[],
            containers=cons,
            metadata=G.metadata,
        )

    @classmethod
    def from_json_file(cls, json_filepath: str) -> CausalAnalysisGraph:
        """Reload a CAG from a JSON file.

        Args:
            json_filepath (str): filepath to the CAG JSON file

        Returns:
            CausalAnalysisGraph: A CAG with all data from the JSON file
        """
        # TODO: @Tito implement this
        data = json.load(open(json_filepath, "r"))
        return NotImplemented

    def to_dict(self) -> dict:
        """Generates a dictionary of JSON serializable data that represents this CAG object.

        Returns:
            dict: A dictionary that can be serialized to JSON
        """
        return {
            "uid": self.uid,
            "identifier": str(self.identifier),
            "daet_created": self.date_created,
            "nodes": [var.to_dict() for var in self.nodes],
            "edges": [
                (str(src.identifier), str(dst.identifier))
                for src, dst in self.edges
            ],
            "containers": [con.to_dict() for con in self.containers],
            "metadata": [m.to_dict() for m in self.metadata],
        }

    def to_json(self) -> str:
        """Generates a JSON serialized string for this CAG object

        Returns:
            str: A JSON string with all of the data of this CAG object
        """
        return json.dumps(self.to_dict())

    def to_json_file(self, json_path) -> None:
        with open(json_path, "w") as outfile:
            outfile.write(self.to_json())


# =============================================================================


# class CausalAnalysisGraph(nx.DiGraph):
#     def __init__(self, G, S, uid, date, ns, sc, nm):
#         super().__init__(G)
#         self.subgraphs = S
#         self.uid = uid
#         self.timestamp = date
#         self.namespace = ns
#         self.scope = sc
#         self.name = nm

#     @classmethod
#     def from_GrFN(cls, GrFN: GroundedFunctionNetwork):
#         """Export to a Causal Analysis Graph (CAG) object.
#         The CAG shows the influence relationships between the variables and
#         elides the function nodes."""

#         G = nx.DiGraph()
#         for var_node in GrFN.variables:
#             G.add_node(var_node, **var_node.get_kwargs())
#         for edge in GrFN.hyper_edges:
#             if edge.lambda_fn.func_type == LambdaType.INTERFACE:
#                 G.add_edges_from(list(zip(edge.inputs, edge.outputs)))
#             else:
#                 G.add_edges_from(list(product(edge.inputs, edge.outputs)))

#         def delete_paths_at_level(nodes: list):
#             orig_nodes = deepcopy(nodes)

#             while len(nodes) > 0:
#                 updated_nodes = list()
#                 for node in nodes:
#                     node_var_name = node.identifier.var_name
#                     succs = list(G.successors(node))
#                     for next_node in succs:
#                         if (
#                             next_node.identifier.var_name == node_var_name
#                             and len(list(G.predecessors(next_node))) == 1
#                         ):
#                             next_succs = list(G.successors(next_node))
#                             G.remove_node(next_node)
#                             updated_nodes.append(node)
#                             for succ_node in next_succs:
#                                 G.add_edge(node, succ_node)
#                 nodes = updated_nodes

#             next_level_nodes = list()
#             for node in orig_nodes:
#                 next_level_nodes.extend(list(G.successors(node)))
#             next_level_nodes = list(set(next_level_nodes))

#             if len(next_level_nodes) > 0:
#                 delete_paths_at_level(next_level_nodes)

#         def correct_subgraph_nodes(subgraph: GrFNSubgraph):
#             cag_subgraph_nodes = list(
#                 set(G.nodes).intersection(set(subgraph.nodes))
#             )
#             subgraph.nodes = cag_subgraph_nodes

#             for new_subgraph in GrFN.subgraphs.successors(subgraph):
#                 correct_subgraph_nodes(new_subgraph)

#         input_nodes = [n for n in G.nodes if G.in_degree(n) == 0]
#         delete_paths_at_level(input_nodes)
#         root_subgraph = [n for n, d in GrFN.subgraphs.in_degree() if d == 0][0]
#         correct_subgraph_nodes(root_subgraph)
#         return cls(
#             G,
#             GrFN.subgraphs,
#             GrFN.uid,
#             GrFN.timestamp,
#             GrFN.namespace,
#             GrFN.scope,
#             GrFN.name,
#         )

#     def to_AGraph(self):
#         """Returns a variable-only view of the GrFN in the form of an AGraph.

#         Returns:
#             type: A CAG constructed via variable influence in the GrFN object.

#         """
#         A = nx.nx_agraph.to_agraph(self)
#         A.graph_attr.update(
#             {
#                 "dpi": 227,
#                 "fontsize": 20,
#                 "fontcolor": "black",
#                 "fontname": "Menlo",
#                 "rankdir": "TB",
#             }
#         )
#         A.node_attr.update(
#             shape="rectangle",
#             color="#650021",
#             fontname="Menlo",
#             fontcolor="black",
#         )
#         for node in A.iternodes():
#             node.attr["fontcolor"] = "black"
#             node.attr["style"] = "rounded"
#         A.edge_attr.update({"color": "#650021", "arrowsize": 0.5})

#         def get_subgraph_nodes(subgraph: GrFNSubgraph):
#             return subgraph.nodes + [
#                 node
#                 for child_graph in self.subgraphs.successors(subgraph)
#                 for node in get_subgraph_nodes(child_graph)
#             ]

#         def populate_subgraph(subgraph: GrFNSubgraph, parent: AGraph):
#             all_sub_nodes = get_subgraph_nodes(subgraph)
#             container_subgraph = parent.add_subgraph(
#                 all_sub_nodes,
#                 name=f"cluster_{str(subgraph)}",
#                 label=subgraph.basename,
#                 style="bold, rounded",
#                 rankdir="TB",
#                 color=subgraph.border_color,
#             )

#             for new_subgraph in self.subgraphs.successors(subgraph):
#                 populate_subgraph(new_subgraph, container_subgraph)

#         root_subgraph = [n for n, d in self.subgraphs.in_degree() if d == 0][0]
#         populate_subgraph(root_subgraph, A)
#         return A

#     def to_igraph_gml(self, filepath: str) -> NoReturn:
#         filename = os.path.join(
#             filepath,
#             f"{self.namespace}__{self.scope}__{self.name}--igraph.gml",
#         )

#         V = [str(v) for v in super().nodes]
#         E = [(str(e1), str(e2)) for e1, e2 in super().edges]
#         iG = nx.DiGraph()
#         iG.add_nodes_from(V)
#         iG.add_edges_from(E)
#         nx.write_gml(iG, filename)

#     def to_json(self) -> str:
#         """Outputs the contents of this GrFN to a JSON object string.

#         :return: Description of returned object.
#         :rtype: type
#         :raises ExceptionName: Why the exception is raised.
#         """
#         data = {
#             "uid": self.uid,
#             "identifier": "::".join(
#                 ["@container", self.namespace, self.scope, self.name]
#             ),
#             "timestamp": self.timestamp,
#             "variables": [var.to_dict() for var in self.nodes],
#             "edges": [(src.uid, dst.uid) for src, dst in self.edges],
#             "subgraphs": [sgraphs.to_dict() for sgraphs in self.subgraphs],
#         }
#         return json.dumps(data)

#     def to_json_file(self, json_path) -> None:
#         with open(json_path, "w") as outfile:
#             outfile.write(self.to_json())
