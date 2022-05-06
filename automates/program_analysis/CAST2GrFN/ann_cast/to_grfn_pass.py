import typing
from functools import singledispatchmethod
import networkx as nx
import uuid

from automates.program_analysis.CAST2GrFN.ann_cast.annotated_cast import *

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
    GrFNLoopSubgraph,
    HyperEdge,
    LambdaNode,
    LoopTopInterface,
    VariableNode
)

from automates.model_assembly.sandbox import load_lambda_function

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
        grfn_uid = GenericNode.create_node_id()
        timestamp = "timestamp"
        type_defs = []
        metadata = []
        ns = "default-ns"
        scope = "default"
        con_name = "GrFN"
        identifier = ContainerIdentifier(ns, scope, con_name)

        # store GrFN in AnnCast
        self.ann_cast.grfn = GroundedFunctionNetwork(grfn_uid, identifier, timestamp, 
                                        self.network, self.hyper_edges, self.subgraphs,
                                        type_defs, metadata)

    def create_interface_node(self, lambda_expr):
        # we should never create an interface node if we have an empty lambda expr
        assert(len(lambda_expr) > 0)
        lambda_uuid = GenericNode.create_node_id()
        lambda_str = lambda_expr
        lambda_func = load_lambda_function(lambda_str)
        # FUTURE: decide on metadata for interface nodes
        lambda_metadata = []
        lambda_type = LambdaType.INTERFACE

        interface_node = LambdaNode(lambda_uuid, lambda_type,
                                     lambda_str, lambda_func, lambda_metadata)

        # DEBUGGING
        # print(f"CREATED INTERFACE {lambda_uuid} with lambda {lambda_expr}")

        return interface_node

    def create_loop_top_interface(self, lambda_expr):
        # we should never create an interface node if we have an empty lambda expr
        assert(len(lambda_expr) > 0)
        lambda_uuid = GenericNode.create_node_id()
        lambda_str = lambda_expr
        lambda_func = load_lambda_function(lambda_str)
        # FUTURE: decide on metadata for interface nodes
        lambda_metadata = []
        lambda_type = LambdaType.LOOP_TOP_INTERFACE

        interface_node = LoopTopInterface(lambda_uuid, lambda_type,
                                     lambda_str, lambda_func, lambda_metadata)

        return interface_node

    def add_grfn_edges(self, inputs: typing.List, lambda_node, outputs: typing.List):
        """ Parameters:
              - `inputs` and `outputs` are lists of GrFN VariableNode's
              - `lambda_node` is a GrFN LambdaNode
            
            For each input in `inputs`, adds an edge from input to `lambda_node`
            For each output in `outputs`, adds an edge from `lambda_node` to output
            Adds a `HyperEdge` between `inputs`, `lambda_node`, and `outputs`
        """
        # build input edge set 
        input_edges = zip(inputs, [lambda_node] * len(inputs))
        # build output edge set 
        output_edges = zip([lambda_node] * len(outputs), outputs)
        # add edges to network
        self.network.add_edges_from(input_edges)
        self.network.add_edges_from(output_edges)
        # add HyperEdges to GrFN
        self.hyper_edges.append(HyperEdge(inputs, lambda_node, outputs))

    def create_condition_node(self, condition_in, condition_out, lambda_expr,  subgraph: GrFNSubgraph):
        lambda_uuid = GenericNode.create_node_id()
        lambda_str = lambda_expr
        lambda_func = load_lambda_function(lambda_str)
        # FUTURE: decide on metadata for condition nodes
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

    def create_decision_node(self, decision_in, decision_out, condition_var, lambda_expr, subgraph: GrFNSubgraph):
        lambda_uuid = GenericNode.create_node_id()
        lambda_str = lambda_expr
        lambda_func = load_lambda_function(lambda_str)
        # FUTURE: decide on metadata for decision nodes
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
        # update func_str and function for assignment node
        assignment_node.func_str = grfn_assignment.lambda_expr
        assignment_node.function = load_lambda_function(assignment_node.func_str)

        # TODO: simplify adding edges
        self.network.add_node(assignment_node, **assignment_node.get_kwargs())
        # accumulate created nodes to add to subgraph
        subgraph_nodes = [assignment_node]
        # accumulate inputs to assignment node
        inputs = []
        for fullid in grfn_assignment.inputs.keys():
            input = self.ann_cast.get_grfn_var(fullid)
            inputs.append(input)
            subgraph_nodes.append(input)
        # accumulate outputs from assignment node 
        outputs = []
        for fullid in grfn_assignment.outputs.keys():
            output = self.ann_cast.get_grfn_var(fullid)
            outputs.append(output)
            subgraph_nodes.append(output)

        self.add_grfn_edges(inputs, assignment_node, outputs)
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
        self.visit_grfn_assignment(node.grfn_assignment, subgraph)

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

    # TODO: Update
    @_visit.register    
    def visit_call(self, node: AnnCastCall, subgraph: GrFNSubgraph):
        if node.is_grfn_2_2:
            self.visit_call_grfn_2_2(node, subgraph)
            return 

        self.visit_node_list(node.arguments, subgraph)
        for index, assignment in node.arg_assignments.items():
            self.visit_grfn_assignment(assignment, subgraph)

        parent = subgraph
        # make a new subgraph for this If Container
        type = "CallContainer"
        border_color = "purple"
        metadata = create_container_metadata(node.grfn_con_src_ref)
        nodes = []
        parent_str = parent.uid if parent is not None else None
        occs = 0
        uid = GenericNode.create_node_id()
        ns = "default-ns"
        scope = con_scope_to_str(node.func.con_scope)
        basename = call_container_name(node)
        subgraph = GrFNSubgraph(uid, ns, scope, basename,
                                occs, parent_str, type, border_color, nodes, metadata)

        self.subgraphs.add_node(subgraph)
        self.subgraphs.add_edge(parent, subgraph)

        # build top interface if needed
        if len(node.top_interface_in) > 0:
            top_interface = self.create_interface_node(node.top_interface_lambda)
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

        # build bot interface if needed
        # TODO: decide what to do by default with bot interface
        if len(node.bot_interface_in) > 0:
            bot_interface = self.create_interface_node(node.bot_interface_lambda)
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
        
    def visit_call_grfn_2_2(self, node: AnnCastCall, subgraph: GrFNSubgraph):
        # assert isinstance(node.func, AnnCastName)
        self.visit_node_list(node.arguments, subgraph)
        for assignment in node.arg_assignments.values():
            self.visit_grfn_assignment(assignment, subgraph)

        parent = subgraph
        # make a new subgraph for this If Container
        type = "FuncContainer"
        border_color = GrFNSubgraph.get_border_color(type)
        metadata = create_container_metadata(node.func_def_copy.grfn_con_src_ref)
        nodes = []
        parent_str = parent.uid if parent is not None else None
        occs = node.invocation_index
        uid = GenericNode.create_node_id()
        ns = "default-ns"
        scope = con_scope_to_str(node.func.con_scope)
        basename = call_container_name(node)
        subgraph = GrFNSubgraph(uid, ns, scope, basename,
                                occs, parent_str, type, border_color, nodes, metadata)
        self.subgraphs.add_node(subgraph)
        self.subgraphs.add_edge(parent, subgraph)

        # build top interface
        if len(node.top_interface_in) > 0:
            top_interface = self.create_interface_node(node.top_interface_lambda)
            self.network.add_node(top_interface, **top_interface.get_kwargs())
            inputs = []
            for fullid in node.top_interface_in.values():
                grfn_id = self.ann_cast.fullid_to_grfn_id[fullid]
                grfn_var = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
                self.network.add_edge(grfn_var, top_interface)
                inputs.append(grfn_var)

            outputs = []
            for fullid in node.top_interface_out.values():
                grfn_id = self.ann_cast.fullid_to_grfn_id[fullid]
                grfn_var = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
                self.network.add_edge(top_interface, grfn_var)
                outputs.append(grfn_var)

            self.hyper_edges.append(HyperEdge(inputs, top_interface, outputs))
            # container includes top_interface and top_interface outputs
            subgraph.nodes.append(top_interface)
            subgraph.nodes.extend(outputs)

        self.visit_function_def_copy(node.func_def_copy, subgraph)

        # build bot interface
        if len(node.bot_interface_in) > 0:
            bot_interface = self.create_interface_node(node.bot_interface_lambda)
            self.network.add_node(bot_interface, **bot_interface.get_kwargs())
            inputs = []
            for fullid in node.bot_interface_in.values():
                grfn_id = self.ann_cast.fullid_to_grfn_id[fullid]
                grfn_var = self.ann_cast.grfn_id_to_grfn_var[grfn_id]
                self.network.add_edge(grfn_var, bot_interface)
                inputs.append(grfn_var)

            outputs = []
            for fullid in node.bot_interface_out.values():
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

    def visit_function_def_copy(self, node: AnnCastFunctionDef, subgraph: GrFNSubgraph):
        for dummy_assignment in node.dummy_grfn_assignments:
            self.visit_grfn_assignment(dummy_assignment, subgraph)

        self.visit_node_list(node.func_args, subgraph)
        self.visit_node_list(node.body, subgraph)

    @_visit.register
    def visit_function_def(self, node: AnnCastFunctionDef, subgraph: GrFNSubgraph):
        # for GrFN 2.2, we create function containers at call sites,
        # so we skip all functions except "main"
        if GENERATE_GRFN_2_2 and not is_func_def_main(node):
            return

        parent = subgraph
        type = "FuncContainer"
        border_color = GrFNSubgraph.get_border_color(type)
        metadata = create_container_metadata(node.grfn_con_src_ref)
        nodes = []
        parent_str = parent.uid if parent is not None else None
        occs = 0
        uid = GenericNode.create_node_id()
        ns = "default-ns"
        scope = con_scope_to_str(node.con_scope)
        basename = scope
        subgraph = GrFNSubgraph(uid, ns, scope, basename,
                                occs, parent_str, type, border_color, nodes, metadata)

        self.visit_node_list(node.func_args, subgraph)

        # build top interface if needed
        if len(node.top_interface_in) > 0:
            top_interface = self.create_interface_node(node.top_interface_lambda)
            self.network.add_node(top_interface, **top_interface.get_kwargs())
            # collect input GrFN VariableNodes
            inputs = list(map(self.ann_cast.get_grfn_var, node.top_interface_in.values()))
            # collect output GrFN VariableNodes 
            outputs = list(map(self.ann_cast.get_grfn_var, node.top_interface_out.values()))
            self.add_grfn_edges(inputs, top_interface, outputs)

            # add inputs to parent graph
            parent.nodes.extend(inputs)
            # add interface node and outputs to subraph
            subgraph.nodes.append(top_interface)
            subgraph.nodes.extend(outputs)
        
        # visit dummy assignments before body
        for dummy_assignment in node.dummy_grfn_assignments:
            self.visit_grfn_assignment(dummy_assignment, subgraph)

        # visit body
        self.visit_node_list(node.body, subgraph)

        # build bot interface if needed
        if len(node.bot_interface_in) > 0:
            bot_interface = self.create_interface_node(node.bot_interface_lambda)
            self.network.add_node(bot_interface, **bot_interface.get_kwargs())
            # collect input GrFN VariableNodes
            inputs = list(map(self.ann_cast.get_grfn_var, node.bot_interface_in.values()))
            # collect output GrFN VariableNodes 
            outputs = list(map(self.ann_cast.get_grfn_var, node.bot_interface_out.values()))
            self.add_grfn_edges(inputs, bot_interface, outputs)

            # add interface node and inputs to subraph
            subgraph.nodes.append(bot_interface)
            subgraph.nodes.extend(inputs)
            # add outputs to parent graph
            parent.nodes.extend(outputs)


        self.subgraphs.add_node(subgraph)
        self.subgraphs.add_edge(parent, subgraph)

    @_visit.register
    def visit_list(self, node: AnnCastList, subgraph: GrFNSubgraph):
        self.visit_node_list(node.values, subgraph)

    @_visit.register
    def visit_loop(self, node: AnnCastLoop, subgraph: GrFNSubgraph):
        parent = subgraph
        # make a new subgraph for this If Container
        type = "LoopContainer"
        border_color = GrFNSubgraph.get_border_color(type)
        metadata = create_container_metadata(node.grfn_con_src_ref)
        nodes = []
        parent_str = parent.uid if parent is not None else None
        occs = 0
        uid = GenericNode.create_node_id()
        # TODO: figure out naming scheme
        ns = "default-ns"
        scope = con_scope_to_str(node.con_scope)
        basename = scope
        # TODO: decide if parent needs to be a str or not
        subgraph = GrFNLoopSubgraph(uid, ns, scope, basename,
                                occs, parent_str, type, border_color, nodes, metadata)
        self.subgraphs.add_node(subgraph)
        self.subgraphs.add_edge(parent, subgraph)

        # build top interface
        if len(node.top_interface_initial) > 0:
            top_interface = self.create_loop_top_interface(node.top_interface_lambda)
            self.network.add_node(top_interface, **top_interface.get_kwargs())
            # collect initial GrFN VariableNodes
            grfn_initial = map(self.ann_cast.get_grfn_var, node.top_interface_initial.values())
            # collect updated GrFN VariableNodes 
            grfn_updated = map(self.ann_cast.get_grfn_var, node.top_interface_updated.values())
            # combine initial and updated for inputs to loop top interface
            inputs = list(grfn_initial) + list(grfn_updated)
            # collect ouput GrFN VariableNodes
            outputs = list(map(self.ann_cast.get_grfn_var, node.top_interface_out.values()))
            self.add_grfn_edges(inputs, top_interface, outputs)

            # add interface node, updated variables, and output variables to subgraph
            subgraph.nodes.append(top_interface)
            subgraph.nodes.extend(list(grfn_updated) + outputs)

        # visit expr, then setup condition info
        self.visit(node.expr, subgraph)
        self.create_condition_node(node.condition_in, node.condition_out, node.condition_lambda, subgraph)

        self.visit_node_list(node.body, subgraph)

        # build bot interface
        if len(node.bot_interface_in) > 0:
            bot_interface = self.create_interface_node(node.bot_interface_lambda)
            self.network.add_node(bot_interface, **bot_interface.get_kwargs())
            # collect input GrFN VariableNodes
            inputs = list(map(self.ann_cast.get_grfn_var, node.bot_interface_in.values()))
            # collect ouput GrFN VariableNodes
            outputs = list(map(self.ann_cast.get_grfn_var, node.bot_interface_out.values()))
            self.add_grfn_edges(inputs, bot_interface, outputs)

            # bot interface includes input and bot interface
            # the outputs need to be added to the parent subgraph
            subgraph.nodes.extend(inputs)
            subgraph.nodes.append(bot_interface)
            parent.nodes.extend(outputs)

        # DEBUGGING
        print(f"In Loop {scope}")
        print(f"\t top_interface UUID = {top_interface.uid}")
        print(f"\t bot_interface UUID = {bot_interface.uid}")


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
        metadata = create_container_metadata(node.grfn_con_src_ref)
        nodes = []
        parent_str = parent.uid if parent is not None else None
        occs = 0
        uid = GenericNode.create_node_id()
        # TODO: figure out naming scheme
        ns = "default-ns"
        scope = con_scope_to_str(node.con_scope)
        basename = scope
        subgraph = GrFNSubgraph(uid, ns, scope, basename,
                                occs, parent_str, type, border_color, nodes, metadata)
        self.subgraphs.add_node(subgraph)
        self.subgraphs.add_edge(parent, subgraph)

        # build top interface
        if len(node.top_interface_in) > 0:
            top_interface = self.create_interface_node(node.top_interface_lambda)
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
        self.create_condition_node(node.condition_in, node.condition_out, node.condition_lambda, subgraph)

        self.visit_node_list(node.body, subgraph)
        self.visit_node_list(node.orelse, subgraph)
        
        condition_var = node.condition_var
        if len(node.decision_in) > 0:
            self.create_decision_node(node.decision_in, node.decision_out, 
                                  condition_var, node.decision_lambda, subgraph)

        # self.create_interface_node(node.bot_interface_in, node.bot_interface_out, subgraph)
        # build bot interface
        if len(node.bot_interface_in) > 0:
            bot_interface = self.create_interface_node(node.bot_interface_lambda)
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
        self.visit(node.value, subgraph)

        self.visit_grfn_assignment(node.grfn_assignment, subgraph)

    @_visit.register
    def visit_module(self, node: AnnCastModule, subgraph: GrFNSubgraph):
        type = "ModuleContainer"
        border_color = "grey"
        metadata = create_container_metadata(node.grfn_con_src_ref)
        nodes = []
        occs = 0
        parent_str = None
        uid = GenericNode.create_node_id()
        ns = "default-ns"
        scope = "module"
        basename = "module"
        subgraph = GrFNSubgraph(uid, ns, scope, basename,
                                occs, parent_str, type, border_color, nodes, metadata)
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
