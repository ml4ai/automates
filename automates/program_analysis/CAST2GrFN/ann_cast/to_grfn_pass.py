import typing
from functools import singledispatchmethod

import networkx as nx
from automates.model_assembly.metadata import LambdaType
from automates.model_assembly.networks import (
    GenericNode,
    GrFNLoopSubgraph,
    GrFNSubgraph,
    GroundedFunctionNetwork,
    HyperEdge,
    LambdaNode,
    LoopTopInterface,
)
from automates.model_assembly.sandbox import load_lambda_function
from automates.model_assembly.structures import ContainerIdentifier
from automates.program_analysis.CAST2GrFN.ann_cast.ann_cast_helpers import (
    ELSEBODY,
    IFBODY,
    MODULE_SCOPE,
    GrfnAssignment,
    call_container_name,
    con_scope_to_str,
    create_container_metadata,
    is_func_def_main,
)
from automates.program_analysis.CAST2GrFN.ann_cast.annotated_cast import *


class ToGrfnPass:
    def __init__(self, pipeline_state: PipelineState):
        self.pipeline_state = pipeline_state
        self.nodes = self.pipeline_state.nodes
        self.network = nx.DiGraph()
        self.subgraphs = nx.DiGraph()
        self.hyper_edges = []

        # populate network with variable nodes
        for grfn_var in self.pipeline_state.grfn_id_to_grfn_var.values():
            self.network.add_node(grfn_var, **grfn_var.get_kwargs())

        # the fullid of a AnnCastName node is a string which includes its 
        # variable name, numerical id, version, and scope
        for node in self.pipeline_state.nodes:
            self.visit(node, subgraph=None)

        # build GrFN
        grfn_uid = GenericNode.create_node_id()
        timestamp = "timestamp"
        type_defs = []
        metadata = []
        ns = "default-ns"
        scope = "default"
        con_name = "GrFN"
        identifier = ContainerIdentifier(ns, scope, con_name)

        # store GrFN in PipelineState
        self.pipeline_state.grfn = GroundedFunctionNetwork(grfn_uid, identifier, timestamp, 
                                        self.network, self.hyper_edges, self.subgraphs,
                                        type_defs, metadata)

    def grfn_vars_from_fullids(self, fullids: typing.Iterable):
        """
        Return the list of GrFN Variables that are associated with the fullids
        from `fullids`
        Paramters:  
            - `fullids`: an iterable of fullids
        """
        grfn_vars = []
        for fullid in fullids:
            grfn_var = self.pipeline_state.get_grfn_var(fullid)
            grfn_vars.append(grfn_var)

        return grfn_vars

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

        inputs = self.grfn_vars_from_fullids(condition_in.values())
        outputs = self.grfn_vars_from_fullids(condition_out.values())
        self.add_grfn_edges(inputs, condition_node, outputs)
            
        # add nodes to subgraph
        subgraph.nodes.extend(inputs + [condition_node] + outputs)

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

        # FUTURE: modifying the order grfn_vars are added 
        # to inputs may be necessary to perform correct execution
        # For now, we are following the pattern in `lambda_for_decision()` of
        # lambda COND, x_if, y_if, x_else, y_else: (x_if, y_if) if COND else (x_else, y_else)

        # values for decision in are two element dicts with keys IFBODY and ELSEBODY
        if_body_dict = {}
        else_body_dict = {}
        for var_id, fullid in decision_in.items():
            if_body_dict[var_id] = fullid[IFBODY]
            else_body_dict[var_id] = fullid[ELSEBODY]

        if_body_inputs = self.grfn_vars_from_fullids(if_body_dict.values())
        else_body_inputs = self.grfn_vars_from_fullids(else_body_dict.values())
        
        # concatenate if and else inputs after condition_var input to follow pattern
        inputs = [condition_var] + if_body_inputs + else_body_inputs
        outputs = self.grfn_vars_from_fullids(decision_out.values())
        self.add_grfn_edges(inputs, decision_node, outputs)
            
        # add nodes to subraph
        subgraph.nodes.extend(inputs + [decision_node] + outputs)

    def visit_grfn_assignment(self, grfn_assignment: GrfnAssignment, subgraph: GrFNSubgraph):
        assignment_node = grfn_assignment.assignment_node
        # update func_str and function for assignment node
        assignment_node.func_str = grfn_assignment.lambda_expr
        assignment_node.function = load_lambda_function(assignment_node.func_str)

        self.network.add_node(assignment_node, **assignment_node.get_kwargs())

        inputs = self.grfn_vars_from_fullids(grfn_assignment.inputs.keys())
        outputs = self.grfn_vars_from_fullids(grfn_assignment.outputs.keys())
        self.add_grfn_edges(inputs, assignment_node, outputs)

        # add subgraph nodes
        subgraph.nodes.extend(inputs + [assignment_node] + outputs)
        

    def visit(self, node: AnnCastNode, subgraph: GrFNSubgraph):
        """
        External visit that callsthe internal visit
        Useful for debugging/development.  For example,
        printing the nodes that are visited
        """
        # print current node being visited.  
        # this can be useful for debugging 
        # class_name = node.__class__.__name__
        # print(f"\nProcessing node type {class_name}")

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
        border_color = GrFNSubgraph.get_border_color(type)
        metadata = create_container_metadata(node.grfn_con_src_ref)
        nodes = []
        parent_str = parent.uid if parent is not None else None
        occs = 0
        uid = GenericNode.create_node_id()
        ns = "default-ns"
        scope = con_scope_to_str(node.func.con_scope + [call_container_name(node)])
        basename = scope
        subgraph = GrFNSubgraph(uid, ns, scope, basename,
                                occs, parent_str, type, border_color, nodes, metadata)

        self.subgraphs.add_node(subgraph)
        self.subgraphs.add_edge(parent, subgraph)

        # build top interface if needed
        if len(node.top_interface_in) > 0:
            top_interface = self.create_interface_node(node.top_interface_lambda)
            self.network.add_node(top_interface, **top_interface.get_kwargs())

            inputs = self.grfn_vars_from_fullids(node.top_interface_in.values())
            outputs = self.grfn_vars_from_fullids(node.top_interface_out.values())
            self.add_grfn_edges(inputs, top_interface, outputs)

            # container includes top_interface and top_interface outputs
            subgraph.nodes.extend([top_interface] + outputs)

        # build bot interface if needed
        if len(node.bot_interface_in) > 0:
            bot_interface = self.create_interface_node(node.bot_interface_lambda)
            self.network.add_node(bot_interface, **bot_interface.get_kwargs())

            inputs = self.grfn_vars_from_fullids(node.bot_interface_in.values())
            outputs = self.grfn_vars_from_fullids(node.bot_interface_out.values())
            self.add_grfn_edges(inputs, bot_interface, outputs)

            # container includes input and bot interface
            # the outputs need to be added to the parent subgraph
            subgraph.nodes.extend(inputs + [bot_interface])
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
        scope = con_scope_to_str(node.func.con_scope + [call_container_name(node)])
        basename = scope
        subgraph = GrFNSubgraph(uid, ns, scope, basename,
                                occs, parent_str, type, border_color, nodes, metadata)
        self.subgraphs.add_node(subgraph)
        self.subgraphs.add_edge(parent, subgraph)

        # build top interface
        if len(node.top_interface_in) > 0:
            top_interface = self.create_interface_node(node.top_interface_lambda)
            self.network.add_node(top_interface, **top_interface.get_kwargs())

            inputs = self.grfn_vars_from_fullids(node.top_interface_in.values())
            outputs = self.grfn_vars_from_fullids(node.top_interface_out.values())
            self.add_grfn_edges(inputs, top_interface, outputs)

            # container includes top_interface and top_interface outputs
            subgraph.nodes.extend([top_interface] + outputs)

        self.visit_function_def_copy(node.func_def_copy, subgraph)

        # build bot interface
        if len(node.bot_interface_in) > 0:
            bot_interface = self.create_interface_node(node.bot_interface_lambda)
            self.network.add_node(bot_interface, **bot_interface.get_kwargs())

            inputs = self.grfn_vars_from_fullids(node.bot_interface_in.values())
            outputs = self.grfn_vars_from_fullids(node.bot_interface_out.values())
            self.add_grfn_edges(inputs, bot_interface, outputs)

            # container includes input and bot interface
            # the outputs need to be added to the parent subgraph
            subgraph.nodes.extend(inputs + [bot_interface])
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
        if self.pipeline_state.GENERATE_GRFN_2_2 and not is_func_def_main(node):
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

            inputs = self.grfn_vars_from_fullids(node.top_interface_in.values())
            outputs = self.grfn_vars_from_fullids(node.top_interface_out.values())
            self.add_grfn_edges(inputs, top_interface, outputs)

            # add inputs to parent graph
            parent.nodes.extend(inputs)
            # add interface node and outputs to subraph
            subgraph.nodes.extend([top_interface] + outputs)
        
        # visit dummy assignments before body
        for dummy_assignment in node.dummy_grfn_assignments:
            self.visit_grfn_assignment(dummy_assignment, subgraph)

        # visit body
        self.visit_node_list(node.body, subgraph)

        # build bot interface if needed
        if len(node.bot_interface_in) > 0:
            bot_interface = self.create_interface_node(node.bot_interface_lambda)
            self.network.add_node(bot_interface, **bot_interface.get_kwargs())

            inputs = self.grfn_vars_from_fullids(node.bot_interface_in.values())
            outputs = self.grfn_vars_from_fullids(node.bot_interface_out.values())
            self.add_grfn_edges(inputs, bot_interface, outputs)

            # add interface node and inputs to subraph
            subgraph.nodes.extend([bot_interface] + inputs)
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
        ns = "default-ns"
        scope = con_scope_to_str(node.con_scope)
        basename = scope
        subgraph = GrFNLoopSubgraph(uid, ns, scope, basename,
                                occs, parent_str, type, border_color, nodes, metadata)
        self.subgraphs.add_node(subgraph)
        self.subgraphs.add_edge(parent, subgraph)

        # build top interface
        if len(node.top_interface_initial) > 0:
            top_interface = self.create_loop_top_interface(node.top_interface_lambda)
            self.network.add_node(top_interface, **top_interface.get_kwargs())
            # collect initial GrFN VariableNodes
            grfn_initial = self.grfn_vars_from_fullids(node.top_interface_initial.values())
            # collect updated GrFN VariableNodes 
            grfn_updated = self.grfn_vars_from_fullids(node.top_interface_updated.values())
            # combine initial and updated for inputs to loop top interface
            inputs = grfn_initial + grfn_updated
            # collect ouput GrFN VariableNodes
            outputs = self.grfn_vars_from_fullids(node.top_interface_out.values())
            self.add_grfn_edges(inputs, top_interface, outputs)

            # add interface node, updated variables, and output variables to subgraph
            subgraph.nodes.extend([top_interface] + grfn_updated + outputs)

        # visit expr, then setup condition info
        self.visit(node.expr, subgraph)
        self.create_condition_node(node.condition_in, node.condition_out, node.condition_lambda, subgraph)

        self.visit_node_list(node.body, subgraph)

        # build bot interface
        if len(node.bot_interface_in) > 0:
            bot_interface = self.create_interface_node(node.bot_interface_lambda)
            self.network.add_node(bot_interface, **bot_interface.get_kwargs())

            inputs = self.grfn_vars_from_fullids(node.bot_interface_in.values())
            outputs = self.grfn_vars_from_fullids(node.bot_interface_out.values())
            self.add_grfn_edges(inputs, bot_interface, outputs)

            # container includes input and bot interface
            # the outputs need to be added to the parent subgraph
            subgraph.nodes.extend(inputs + [bot_interface])
            parent.nodes.extend(outputs)

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

            inputs = self.grfn_vars_from_fullids(node.top_interface_in.values())
            outputs = self.grfn_vars_from_fullids(node.top_interface_out.values())
            self.add_grfn_edges(inputs, top_interface, outputs)

            # container includes top_interface and top_interface outputs
            subgraph.nodes.extend([top_interface] + outputs)

        # visit expr, then setup condition info
        self.visit(node.expr, subgraph)
        self.create_condition_node(node.condition_in, node.condition_out, node.condition_lambda, subgraph)

        self.visit_node_list(node.body, subgraph)
        self.visit_node_list(node.orelse, subgraph)
        
        condition_var = node.condition_var
        if len(node.decision_in) > 0:
            self.create_decision_node(node.decision_in, node.decision_out, 
                                  condition_var, node.decision_lambda, subgraph)

        # build bot interface
        if len(node.bot_interface_in) > 0:
            bot_interface = self.create_interface_node(node.bot_interface_lambda)
            self.network.add_node(bot_interface, **bot_interface.get_kwargs())

            inputs = self.grfn_vars_from_fullids(node.bot_interface_in.values())
            outputs = self.grfn_vars_from_fullids(node.bot_interface_out.values())
            self.add_grfn_edges(inputs, bot_interface, outputs)

            # container includes input and bot interface
            # the outputs need to be added to the parent subgraph
            subgraph.nodes.extend(inputs + [bot_interface])
            parent.nodes.extend(outputs)

    @_visit.register
    def visit_model_return(self, node: AnnCastModelReturn, subgraph: GrFNSubgraph):
        self.visit(node.value, subgraph)

        self.visit_grfn_assignment(node.grfn_assignment, subgraph)

    @_visit.register
    def visit_module(self, node: AnnCastModule, subgraph: GrFNSubgraph):
        type = "ModuleContainer"
        border_color = GrFNSubgraph.get_border_color(type)
        metadata = create_container_metadata(node.grfn_con_src_ref)
        nodes = []
        occs = 0
        parent_str = None
        uid = GenericNode.create_node_id()
        ns = "default-ns"
        scope = MODULE_SCOPE
        basename = MODULE_SCOPE
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
