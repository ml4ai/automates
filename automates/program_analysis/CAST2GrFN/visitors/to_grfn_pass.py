import typing
import re
from functools import singledispatchmethod
import networkx as nx
import uuid

from automates.program_analysis.CAST2GrFN.visitors.annotated_cast import *

from automates.model_assembly.metadata import LambdaType
from automates.model_assembly.structures import (
    CondContainer,
    ContainerIdentifier,
    GenericContainer,
    GenericIdentifier,
    LambdaStmt,
    VariableIdentifier,
)

from automates.model_assembly.networks import (
    GenericNode,
    GroundedFunctionNetwork,
    GrFNSubgraph,
    HyperEdge,
    LambdaNode,
    VariableNode
)

def grfn_subgraph(uid, namespace, scope, basename, occurences, parent, type, nodes):
    pass


class ToGrfnPass:
    def __init__(self, ann_cast: AnnCast):
        self.ann_cast = ann_cast
        self.nodes = self.ann_cast.nodes
        self.network = nx.DiGraph()
        self.subgraphs = nx.DiGraph()
        self.hyper_edges = []

        # populate network with variable nodes
        for grfn_var in self.ann_cast.grfn_id_to_grfn_var.values():
            self.network.add_node(grfn_var, **grfn_var.get_kwargs())

        # the fullid of a AnnCastName node is a string which includes its 
        # variable name, numerical id, version, and scope
        for node in self.ann_cast.nodes:
            # TODO: fix None
            self.visit(node, None)

        # build GrFN
        grfn_uid = str(uuid.uuid4())
        timestamp = "timestamp"
        type_defs = []
        metadata = []
        ns = "default-ns"
        scope = "default"
        con_name = "GrFN"
        identifier = ContainerIdentifier(ns, scope, con_name)

        grfn = GroundedFunctionNetwork(grfn_uid, identifier, timestamp, 
                                        self.network, self.hyper_edges, self.subgraphs,
                                        type_defs, metadata)
        A = grfn.to_AGraph()
        A.draw("AnnCast-to-GrFN.pdf", prog="dot")


    # def create_interface_node(self, interface_in, interface_out, subgraph: GrFNSubgraph):
    def create_interface_node(self):
        # TODO: correct values for thes
        lambda_uuid = str(uuid.uuid4())
        lambda_str = ""
        lambda_func = lambda: None
        lambda_metadata = []
        lambda_type = LambdaType.INTERFACE

        interface_node = LambdaNode(lambda_uuid, lambda_type,
                                     lambda_str, lambda_func, lambda_metadata)

        return interface_node
        # self.network.add_node(interface_node, **interface_node.get_kwargs())
        # inputs = []
        # for var_id, fullid in interface_in.items():
        #     grfn_id = self.ann_cast.fullid_to_grfn_id[fullid]
        #     grfn_var = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
        #     self.network.add_edge(grfn_var, interface_node)
        #     inputs.append(grfn_var)

        # outputs = []
        # for var_id, fullid in interface_out.items():
        #     grfn_id = self.ann_cast.fullid_to_grfn_id[fullid]
        #     grfn_var = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
        #     self.network.add_edge(interface_node, grfn_var)
        #     outputs.append(grfn_var)

        # self.hyper_edges.append(HyperEdge(inputs, interface_node, outputs))
        # # TODO: inputs should not be in subgraph for top interface
        # # and outputs should not be in subgraph for bot interface
        # subgraph.nodes.extend(inputs)
        # subgraph.nodes.append(interface_node)
        # subgraph.nodes.extend(outputs)

    def create_condition_node(self, condition_in, condition_out, subgraph: GrFNSubgraph):
        # TODO: correct values for these
        lambda_uuid = str(uuid.uuid4())
        lambda_str = ""
        lambda_func = lambda: None
        lambda_metadata = []
        lambda_type = LambdaType.CONDITION

        condition_node = LambdaNode(lambda_uuid, lambda_type,
                                     lambda_str, lambda_func, lambda_metadata)
        self.network.add_node(condition_node, **condition_node.get_kwargs())
        inputs = []
        for var_id, fullid in condition_in.items():
            grfn_id = self.ann_cast.fullid_to_grfn_id[fullid]
            grfn_var = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
            self.network.add_edge(grfn_var, condition_node)
            inputs.append(grfn_var)

        outputs = []
        for var_id, fullid in condition_out.items():
            grfn_id = self.ann_cast.fullid_to_grfn_id[fullid]
            grfn_var = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
            self.network.add_edge(condition_node, grfn_var)
            outputs.append(grfn_var)
            
        self.hyper_edges.append(HyperEdge(inputs, condition_node, outputs))
        subgraph.nodes.extend(inputs)
        subgraph.nodes.append(condition_node)
        subgraph.nodes.extend(outputs)

    def create_decision_node(self, decision_in, decision_out, condition_var, subgraph: GrFNSubgraph):
        # TODO: correct values for these
        lambda_uuid = str(uuid.uuid4())
        lambda_str = ""
        lambda_func = lambda: None
        lambda_metadata = []
        lambda_type = LambdaType.DECISION

        decision_node = LambdaNode(lambda_uuid, lambda_type,
                                     lambda_str, lambda_func, lambda_metadata)
        self.network.add_node(decision_node, **decision_node.get_kwargs())
        inputs = []

        # values for decision in are two element dicts with keys IFBODY and ELSEBODY
        for var_id, fullid in decision_in.items():
            if_grfn_id = self.ann_cast.fullid_to_grfn_id[fullid[IFBODY]]
            if_grfn_var = self.ann_cast.grfn_id_to_grfn_var[if_grfn_id]

            else_grfn_id = self.ann_cast.fullid_to_grfn_id[fullid[ELSEBODY]]
            else_grfn_var = self.ann_cast.grfn_id_to_grfn_var[else_grfn_id]

            self.network.add_edge(if_grfn_var, decision_node)
            self.network.add_edge(else_grfn_var, decision_node)
            inputs.append(if_grfn_var)
            inputs.append(else_grfn_var)

        # also need to add condition_var as input to decision node
        self.network.add_edge(condition_var, decision_node)
        inputs.append(condition_var)

        outputs = []
        for var_id, fullid in decision_out.items():
            grfn_id = self.ann_cast.fullid_to_grfn_id[fullid]
            grfn_var = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
            self.network.add_edge(decision_node, grfn_var)
            outputs.append(grfn_var)
            
        self.hyper_edges.append(HyperEdge(inputs, decision_node, outputs))
        subgraph.nodes.extend(inputs)
        subgraph.nodes.append(decision_node)
        subgraph.nodes.extend(outputs)

    def visit_grfn_assignment(self, grfn_assignment: GrfnAssignment, subgraph: GrFNSubgraph):
        assignment_node = grfn_assignment.assignment_node
        self.network.add_node(assignment_node, **assignment_node.get_kwargs())
        # accumulate created nodes to add to subgraph
        subgraph_nodes = [assignment_node]
        # accumulate inputs to assignment node
        inputs = []
        for fullid, grfn_id in grfn_assignment.inputs.items():
            input = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
            inputs.append(input)
            subgraph_nodes.append(input)
        # accumulate outputs from assignment node 
        outputs = []
        for fullid, grfn_id in grfn_assignment.outputs.items():
            output = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
            outputs.append(output)
            subgraph_nodes.append(output)

        # build input edge set 
        input_edges = zip(inputs, [assignment_node] * len(inputs))
        # build output edge set 
        output_edges = zip([assignment_node] * len(outputs), outputs)
        # add edges to network
        self.network.add_edges_from(input_edges)
        self.network.add_edges_from(output_edges)
        # add HyperEdges to GrFN
        self.hyper_edges.append(HyperEdge(inputs, assignment_node, outputs))
        # add subgraph_nodes
        subgraph.nodes.extend(subgraph_nodes)
        

    def visit(self, node: AnnCastNode, subgraph: GrFNSubgraph):
        """
        External visit that callsthe internal visit
        Useful for debugging/development.  For example,
        printing the nodes that are visited
        """
        # debug printing
        class_name = node.__class__.__name__
        print(f"\nProcessing node type {class_name}")

        # call internal visit
        return self._visit(node, subgraph)

    def visit_node_list(self, node_list: typing.List[AnnCastNode], subgraph: GrFNSubgraph):
        return [self.visit(node, subgraph) for node in node_list]

        
    @singledispatchmethod
    def _visit(self, node: AnnCastNode, subgraph: GrFNSubgraph):
        """
        Internal visit
        """
        raise NameError(f"Unrecognized node type: {type(node)}")

    @_visit.register
    def visit_assignment(self, node: AnnCastAssignment, subgraph: GrFNSubgraph):
        self.visit(node.right, subgraph)
        # add ASSIGN or LITERAL node to network
        assignment_node = node.grfn_assignment.assignment_node
        self.network.add_node(assignment_node, **assignment_node.get_kwargs())
        # accumulate created nodes to add to subgraph
        subgraph_nodes = [assignment_node]
        # accumulate inputs to assignment node
        inputs = []
        for fullid, grfn_id in node.grfn_assignment.inputs.items():
            input = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
            inputs.append(input)
            subgraph_nodes.append(input)
        # accumulate outputs from assignment node 
        outputs = []
        for fullid, grfn_id in node.grfn_assignment.outputs.items():
            output = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
            outputs.append(output)
            subgraph_nodes.append(output)

        # build input edge set 
        input_edges = zip(inputs, [assignment_node] * len(inputs))
        # build output edge set 
        output_edges = zip([assignment_node] * len(outputs), outputs)
        # add edges to network
        self.network.add_edges_from(input_edges)
        self.network.add_edges_from(output_edges)
        # add HyperEdges to GrFN
        self.hyper_edges.append(HyperEdge(inputs, assignment_node, outputs))
        # add subgraph_nodes
        subgraph.nodes.extend(subgraph_nodes)


    @_visit.register
    def visit_attribute(self, node: AnnCastAttribute, subgraph: GrFNSubgraph):
        pass

    @_visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp, subgraph: GrFNSubgraph):
        # visit LHS first
        self.visit(node.left, subgraph)

        # visit RHS second
        self.visit(node.right, subgraph)

    @_visit.register
    def visit_boolean(self, node: AnnCastBoolean, subgraph: GrFNSubgraph):
        pass

    @_visit.register
    def visit_call(self, node: AnnCastCall, subgraph: GrFNSubgraph):
        # assert isinstance(node.func, AnnCastName)
        self.visit_node_list(node.arguments, subgraph)
        for index, assignment in node.arg_assigments.items():
            self.visit_grfn_assignment(assignment, subgraph)

        parent = subgraph
        # make a new subgraph for this If Container
        type = "CondContainer"
        border_color = "purple"
        metadata = []
        nodes = []
        occs = 0
        uid = str(uuid.uuid4())
        ns = "default-ns"
        scope = con_scope_to_str(node.func.con_scope)
        basename = call_container_name(node)
        subgraph = GrFNSubgraph(uid, ns, scope, basename,
                                occs, parent, type, border_color, nodes, metadata)
        self.subgraphs.add_node(subgraph)
        self.subgraphs.add_edge(parent, subgraph)

        # build top interface
        top_interface = self.create_interface_node()
        self.network.add_node(top_interface, **top_interface.get_kwargs())
        inputs = []
        for var_id, fullid in node.top_interface_in.items():
            grfn_id = self.ann_cast.fullid_to_grfn_id[fullid]
            grfn_var = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
            self.network.add_edge(grfn_var, top_interface)
            inputs.append(grfn_var)

        outputs = []
        for var_id, fullid in node.top_interface_out.items():
            grfn_id = self.ann_cast.fullid_to_grfn_id[fullid]
            grfn_var = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
            self.network.add_edge(top_interface, grfn_var)
            outputs.append(grfn_var)

        self.hyper_edges.append(HyperEdge(inputs, top_interface, outputs))
        # container includes top_interface and top_interface outputs
        subgraph.nodes.append(top_interface)
        subgraph.nodes.extend(outputs)

        # build bot interface
        bot_interface = self.create_interface_node()
        self.network.add_node(bot_interface, **bot_interface.get_kwargs())
        inputs = []
        for var_id, fullid in node.bot_interface_in.items():
            grfn_id = self.ann_cast.fullid_to_grfn_id[fullid]
            grfn_var = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
            self.network.add_edge(grfn_var, bot_interface)
            inputs.append(grfn_var)

        outputs = []
        for var_id, fullid in node.bot_interface_out.items():
            grfn_id = self.ann_cast.fullid_to_grfn_id[fullid]
            grfn_var = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
            self.network.add_edge(bot_interface, grfn_var)
            outputs.append(grfn_var)

        self.hyper_edges.append(HyperEdge(inputs, bot_interface, outputs))
        # bot interface includes input and bot interface
        # the outputs need to be added to the parent subgraph
        subgraph.nodes.extend(inputs)
        subgraph.nodes.append(bot_interface)
        parent.nodes.extend(outputs)


    @_visit.register
    def visit_class_def(self, node: AnnCastClassDef, subgraph: GrFNSubgraph):
        pass

    @_visit.register
    def visit_dict(self, node: AnnCastDict, subgraph: GrFNSubgraph):
        pass

    @_visit.register
    def visit_expr(self, node: AnnCastExpr, subgraph: GrFNSubgraph):
        self.visit(node.expr, subgraph)

    @_visit.register
    def visit_function_def(self, node: AnnCastFunctionDef, subgraph: GrFNSubgraph):
        self.visit_node_list(node.func_args, subgraph)
        self.visit_node_list(node.body, subgraph)
        # TODO: Interfaces nodes for a Function Def

    @_visit.register
    def visit_list(self, node: AnnCastList, subgraph: GrFNSubgraph):
        self.visit_node_list(node.values, subgraph)

    @_visit.register
    def visit_loop(self, node: AnnCastLoop, subgraph: GrFNSubgraph):
        # TODO: Loop
        # visit children
        self.visit(node.expr)
        self.visit_node_list(node.body)

    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak, subgraph: GrFNSubgraph):
        pass

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue, subgraph: GrFNSubgraph):
        pass

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf, subgraph: GrFNSubgraph):
        parent = subgraph
        # make a new subgraph for this If Container
        type = "CondContainer"
        border_color = GrFNSubgraph.get_border_color(type)
        metadata = []
        nodes = []
        occs = 0
        uid = str(uuid.uuid4())
        ns = "default-ns"
        scope = con_scope_to_str(node.con_scope)
        basename = "COND"
        subgraph = GrFNSubgraph(uid, ns, scope, basename,
                                occs, parent, type, border_color, nodes, metadata)
        self.subgraphs.add_node(subgraph)
        self.subgraphs.add_edge(parent, subgraph)

        # self.create_interface_node(node.top_interface_in, node.top_interface_out, subgraph)
        # build top interface
        top_interface = self.create_interface_node()
        self.network.add_node(top_interface, **top_interface.get_kwargs())
        inputs = []
        for var_id, fullid in node.top_interface_in.items():
            grfn_id = self.ann_cast.fullid_to_grfn_id[fullid]
            grfn_var = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
            self.network.add_edge(grfn_var, top_interface)
            inputs.append(grfn_var)

        outputs = []
        for var_id, fullid in node.top_interface_out.items():
            grfn_id = self.ann_cast.fullid_to_grfn_id[fullid]
            grfn_var = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
            self.network.add_edge(top_interface, grfn_var)
            outputs.append(grfn_var)

        self.hyper_edges.append(HyperEdge(inputs, top_interface, outputs))
        # container includes top_interface and top_interface outputs
        subgraph.nodes.append(top_interface)
        subgraph.nodes.extend(outputs)

        # visit expr, then setup condition info
        self.visit(node.expr, subgraph)
        self.create_condition_node(node.condition_in, node.condition_out, subgraph)

        self.visit_node_list(node.body, subgraph)
        self.visit_node_list(node.orelse, subgraph)
        
        # TODO: Change this, we could just store the condition var in the node
        condition_fullid = list(node.condition_out.values())[0]
        condition_grfn_id = self.ann_cast.fullid_to_grfn_id[condition_fullid]
        condition_var = self.ann_cast.grfn_id_to_grfn_var[condition_grfn_id]
        self.create_decision_node(node.decision_in, node.decision_out, 
                                  condition_var, subgraph)

        # self.create_interface_node(node.bot_interface_in, node.bot_interface_out, subgraph)
        # build bot interface
        bot_interface = self.create_interface_node()
        self.network.add_node(bot_interface, **bot_interface.get_kwargs())
        inputs = []
        for var_id, fullid in node.bot_interface_in.items():
            grfn_id = self.ann_cast.fullid_to_grfn_id[fullid]
            grfn_var = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
            self.network.add_edge(grfn_var, bot_interface)
            inputs.append(grfn_var)

        outputs = []
        for var_id, fullid in node.bot_interface_out.items():
            grfn_id = self.ann_cast.fullid_to_grfn_id[fullid]
            grfn_var = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
            self.network.add_edge(bot_interface, grfn_var)
            outputs.append(grfn_var)

        self.hyper_edges.append(HyperEdge(inputs, bot_interface, outputs))
        # bot interface includes input and bot interface
        # the outputs need to be added to the parent subgraph
        subgraph.nodes.extend(inputs)
        subgraph.nodes.append(bot_interface)
        parent.nodes.extend(outputs)

    @_visit.register
    def visit_model_return(self, node: AnnCastModelReturn, subgraph: GrFNSubgraph):
        # TODO:
        self.visit(node.value, subgraph)

    @_visit.register
    def visit_module(self, node: AnnCastModule, subgraph: GrFNSubgraph):
        type = "FuncContainer"
        border_color = GrFNSubgraph.get_border_color(type)
        metadata = []
        nodes = []
        occs = 0
        parent = None
        uid = str(uuid.uuid4())
        ns = "default-ns"
        scope = "module"
        basename = "module"
        subgraph = GrFNSubgraph(uid, ns, scope, basename,
                                occs, parent, type, border_color, nodes, metadata)
        self.subgraphs.add_node(subgraph)

        self.visit_node_list(node.body, subgraph)

    @_visit.register
    def visit_name(self, node: AnnCastName, subgraph: GrFNSubgraph):
        pass

    @_visit.register
    def visit_number(self, node: AnnCastNumber, subgraph: GrFNSubgraph):
        pass

    @_visit.register
    def visit_set(self, node: AnnCastSet, subgraph: GrFNSubgraph):
        pass

    @_visit.register
    def visit_string(self, node: AnnCastString, subgraph: GrFNSubgraph):
        pass

    @_visit.register
    def visit_subscript(self, node: AnnCastSubscript, subgraph: GrFNSubgraph):
        pass

    @_visit.register
    def visit_tuple(self, node: AnnCastTuple, subgraph: GrFNSubgraph):
        pass

    @_visit.register
    def visit_unary_op(self, node: AnnCastUnaryOp, subgraph: GrFNSubgraph):
        self.visit(node.value, subgraph)

    @_visit.register
    def visit_var(self, node: AnnCastVar, subgraph: GrFNSubgraph):
        self.visit(node.val, subgraph)
