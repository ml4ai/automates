from tkinter import Pack
import typing
from functools import singledispatchmethod
from certifi import contents
import json

import networkx as nx
from numpy import insert, isin
from zmq import PROTOCOL_ERROR_ZMTP_MECHANISM_MISMATCH
from automates.model_assembly.metadata import LambdaType
from automates.model_assembly.networks import (
    GenericNode,
    GrFNLoopSubgraph,
    GrFNSubgraph,
    GroundedFunctionNetwork,
    HyperEdge,
    LambdaNode,
    LoopTopInterface,
    UnpackNode,
    PackNode,
)
#from automates.model_assembly.gromet import (
 #   GrometFN,
  #  GrometExpression,
# )
from automates.model_assembly.gromet.model import (
    function_type,
    gromet_box_conditional,
    gromet_box_function,
    gromet_box_loop,
    gromet_box,
    gromet_fn_collection,
    gromet_fn,
    gromet_port,
    gromet_wire,
    literal_value,
)

from automates.program_analysis.CAST2GrFN.ann_cast.annotated_cast import *
from automates.program_analysis.CAST2GrFN.model.cast import ( 
    ScalarType,
    ValueConstructor,
)


def del_nulls(d):
    for key,value in list(d.items()):
        #print(key, value)
        if isinstance(value, list):
            for elem in value:
                if isinstance(elem, dict):
                    del_nulls(elem)
        if value is None:
            del d[key]

    return d    

def insert_gromet_object(t: List, obj):
    """ Inserts a GroMEt object obj into a GroMEt table t
        Where obj can be 
            - A GroMEt Box
            - A GroMEt Port
            - A GroMEt Wire 
        And t can be 
            - A list of GroMEt Boxes
            - A list of GroMEt ports
            - A list of GroMEt wires
                
        If the table we're trying to insert into doesn't already exist, then we
        first create it, and then insert the value.
    """
    if t == None:
        t = []
    t.append(obj)

    return t


class ToGrometPass:
    def __init__(self, pipeline_state: PipelineState):
        self.pipeline_state = pipeline_state
        self.nodes = self.pipeline_state.nodes

        #self.network = nx.DiGraph()
        #self.subgraphs = nx.DiGraph()
        #self.hyper_edges = []

        # creating a GroMEt FN object here or a collection of GroMEt FNs
        # generally, programs are complex, so a collection of GroMEt FNs is usually created
        # visiting nodes adds FNs 
        self.gromet_collection = gromet_fn_collection.GrometFNCollection(None, [], [])

        # populate network with variable nodes
        #for grfn_var in self.pipeline_state.grfn_id_to_grfn_var.values():
        #    self.network.add_node(grfn_var, **grfn_var.get_kwargs())

        # the fullid of a AnnCastName node is a string which includes its 
        # variable name, numerical id, version, and scope
        for node in self.pipeline_state.nodes:
            self.visit(node, subgraph=None)


        with open("test_gromet.json","w") as f:
            # print(json.dumps(self.gromet_collection.to_dict()))
            gromet_collection_dict = self.gromet_collection.to_dict()
            f.write(json.dumps(del_nulls(gromet_collection_dict.copy()), indent=4))


        # build GrFN
        # grfn_uid = GenericNode.create_node_id()
        #timestamp = "timestamp"
        #type_defs = []
        #metadata = []
        #ns = "default-ns"
        #scope = "default"
        #con_name = "GrFN"
        #identifier = ContainerIdentifier(ns, scope, con_name)

        # store GrFN in PipelineState
        #self.pipeline_state.grfn = GroundedFunctionNetwork(grfn_uid, identifier, timestamp, 
        #                                self.network, self.hyper_edges, self.subgraphs,
        #                                type_defs, metadata)

    """
    def grfn_vars_from_fullids(self, fullids: typing.Iterable):
        Return the list of GrFN Variables that are associated with the fullids
        from `fullids`
        Paramters:  
            - `fullids`: an iterable of fullids
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
         Parameters:
              - `inputs` and `outputs` are lists of GrFN VariableNode's
              - `lambda_node` is a GrFN LambdaNode
            
            For each input in `inputs`, adds an edge from input to `lambda_node`
            For each output in `outputs`, adds an edge from `lambda_node` to output
            Adds a `HyperEdge` between `inputs`, `lambda_node`, and `outputs`
        
        # build input edge set 
        input_edges = zip(inputs, [lambda_node] * len(inputs))
        # build output edge set 
        output_edges = zip([lambda_node] * len(outputs), outputs)
        # add edges to network
        self.network.add_edges_from(input_edges)
        self.network.add_edges_from(output_edges)
        # add HyperEdges to GrFN
       # self.hyper_edges.append(HyperEdge(inputs, lambda_node, outputs))

    def create_condition_node(self, condition_in, condition_out, lambda_expr,  subgraph):
        # lambda_uuid = GenericNode.create_node_id()
        lambda_str = lambda_expr
        lambda_func = load_lambda_function(lambda_str)
        # FUTURE: decide on metadata for condition nodes
        lambda_metadata = []
        # lambda_type = LambdaType.CONDITION

  #      condition_node = LambdaNode(lambda_uuid, lambda_type,
   #                                  lambda_str, lambda_func, lambda_metadata)
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
        # NOTE: We can perhaps create the call to the GExpression box here

        assignment_node = grfn_assignment.assignment_node
        # update func_str and function for assignment node
        assignment_node.func_str = grfn_assignment.lambda_expr
        assignment_node.function = load_lambda_function(assignment_node.func_str)

        self.network.add_node(assignment_node, **assignment_node.get_kwargs())

        inputs = self.grfn_vars_from_fullids(grfn_assignment.inputs.keys())
        outputs = self.grfn_vars_from_fullids(grfn_assignment.outputs.keys())
        self.add_grfn_edges(inputs, assignment_node, outputs)

        # Create strings representing the inputs and outputs for pack and unpack
        if isinstance(assignment_node, (PackNode, UnpackNode)):
            assignment_node.inputs = ",".join(list(map(lambda_var_from_fullid,grfn_assignment.inputs.keys())))
            assignment_node.output = ",".join(list(map(lambda_var_from_fullid,grfn_assignment.outputs.keys())))

        # add subgraph nodes
        subgraph.nodes.extend(inputs + [assignment_node] + outputs)
        
    """
    def visit(self, node: AnnCastNode, subgraph):
        """
        External visit that callsthe internal visit
        Useful for debugging/development.  For example,
        printing the nodes that are visited
        """
        # print current node being visited.  
        # this can be useful for debugging 
        class_name = node.__class__.__name__
        print(f"\nProcessing node type {class_name}")

        # call internal visit
        return self._visit(node, subgraph)

    def visit_node_list(self, node_list: typing.List[AnnCastNode], subgraph):
        return [self.visit(node, subgraph) for node in node_list]

        
    @singledispatchmethod
    def _visit(self, node: AnnCastNode, subgraph):
        """
        Internal visit
        """
        raise NameError(f"Unrecognized node type: {type(node)}")

    @_visit.register
    def visit_assignment(self, node: AnnCastAssignment, parent_gromet_fn):
        # This first visit on the node.right should create a FN
        # where the outer box is a GExpression (GroMEt Expression)
        # The purple box on the right in examples (exp0.py)

        #new_gromet = gromet_fn.GrometFN()
        #new_gromet.B = [{"name": "", "type": function_type.FunctionType.EXPRESSION}]
        # How does this creation of a GrometBoxFunction object play into the overall construction?
        # Where does it go? 
        # new_gromet = gromet_box_function.GrometBoxFunction()

        new_gromet = gromet_fn.GrometFN()
        # new_gromet.b = [gromet_box_function.GrometBoxFunction(name="", function_type=function_type.FunctionType.EXPRESSION)]
        
        new_gromet.b = insert_gromet_object(new_gromet.b, gromet_box_function.GrometBoxFunction(name="", function_type=function_type.FunctionType.EXPRESSION))

        self.gromet_collection.function_networks.append(new_gromet)

        self.visit(node.right, new_gromet)

        # One way or another we have a hold of the GEXpression object here.
        # Whatever's returned by the RHS of the assignment, 
        # i.e. LiteralValue or primitive operator or function call.
        # Now we can look at its output port(s)

        # node.left contains info about the variable being assigned

        # At this point we identified the variable being assigned (i.e. for exp0.py: x)
        # we need to do some bookkeeping to associate the source CAST/GrFN variable with
        # the output port of the GroMEt expression call
        # NOTE: This may need to change from just indexing to something more
        new_gromet.opo = insert_gromet_object(new_gromet.opo, gromet_port.GrometPort(name=node.left.val.name, box=len(new_gromet.b) - 1))

        # NOTE: x = foo(...) <- foo returns multiple values that get packed
        # Several conditions for this 
        # - foo has multiple output ports for returning 
        #    - multiple output ports but assignment to a single variable, then we introduce a pack
        #       the result of the pack is a single introduced variable that gets wired to the single 
        #       variable
        #    - multiple output ports but assignment to multiple variables, then we wire one-to-one 
        #       in order, all the output ports of foo to each variable
        #    - else, if we dont have a one to one matching then it's an error
        # - foo has a single output port to return a value
        #    - in the case of a single target variable, then we wire directly one-to-one
        #    - otherwise if multiple target variables for a single return output port, then it's an error


        # GroMEt wiring creation
        # The creation of the wire between the output port (OP) of the top-level node 
        # of the tree rooted in node.right needs to be wired to the output port out (OPO)
        # of the GExpression of this AnnCastAssignment
        new_gromet.wfopo = insert_gromet_object(new_gromet.wfopo, gromet_wire.GrometWire(src=len(new_gromet.pof)-1, tgt=len(new_gromet.opo)-1))
        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, gromet_box_function.GrometBoxFunction(name="", function_type=function_type.FunctionType.EXPRESSION, contents=len(self.gromet_collection.function_networks)-1,value=None))
        parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, gromet_port.GrometPort(name=node.left.val.name, box=len(parent_gromet_fn.b)-1))
        
        # NOTE: A visit_grfn_assignment for GroMEt construction is likely not needed
        # The work can probably be done at this step in the Assignment visitor
        # This second visit creates the call to the GExpression that was just created 
        # in the previous visit above
        # A box that's contained within the body of a FN
        # self.visit_grfn_assignment(node.grfn_assignment, subgraph)

    @_visit.register
    def visit_attribute(self, node: AnnCastAttribute, subgraph):
        pass

    @_visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp, parent_gromet_fn):
        # visit LHS first
        self.visit(node.left, parent_gromet_fn)

        # visit RHS second
        self.visit(node.right, parent_gromet_fn)

        # NOTE/TODO Maintain a table of primitive operators that when queried give you back
        # their signatures that can be used for generating 
        ops_map = {"Add" : "+", "Sub": "-", "Mult" : "*", "Div" : "/"}

        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, gromet_box_function.GrometBoxFunction(name=ops_map[node.op], function_type=function_type.FunctionType.PRIMITIVEOP, contents=None, value=None))
        parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, gromet_port.GrometPort(name="", box=len(parent_gromet_fn.bf) - 1))
        parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, gromet_port.GrometPort(name="", box=len(parent_gromet_fn.bf) - 1))

        parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, gromet_port.GrometPort(name="", box=len(parent_gromet_fn.bf) - 1))

        if isinstance(node.left, AnnCastName):
            parent_gromet_fn.opi = insert_gromet_object(parent_gromet_fn.opi, gromet_port.GrometPort(box=len(parent_gromet_fn.b)-1 ,name=""))
            parent_gromet_fn.wfopi = insert_gromet_object(parent_gromet_fn.wfopi, gromet_wire.GrometWire(src=len(parent_gromet_fn.b)-1,tgt=len(parent_gromet_fn.pif)-2))

        if isinstance(node.right, AnnCastName):
            parent_gromet_fn.opi = insert_gromet_object(parent_gromet_fn.opi, gromet_port.GrometPort(box=len(parent_gromet_fn.b)-1 ,name=""))
            parent_gromet_fn.wfopi = insert_gromet_object(parent_gromet_fn.wfopi, gromet_wire.GrometWire(src=len(parent_gromet_fn.b)-1,tgt=len(parent_gromet_fn.pif)-1))

        if isinstance(node.left, AnnCastLiteralValue):
            parent_gromet_fn.wff = insert_gromet_object(parent_gromet_fn.wff, gromet_wire.GrometWire(src=len(parent_gromet_fn.pof)-3,tgt=len(parent_gromet_fn.pif)-2))
        
        if isinstance(node.right, AnnCastLiteralValue):
            parent_gromet_fn.wff = insert_gromet_object(parent_gromet_fn.wff, gromet_wire.GrometWire(src=len(parent_gromet_fn.pof)-2,tgt=len(parent_gromet_fn.pif)-1))



    @_visit.register
    def visit_boolean(self, node: AnnCastBoolean, subgraph):
        pass

    @_visit.register    
    def visit_call(self, node: AnnCastCall, subgraph):
        pass
        
    @_visit.register
    def visit_class_def(self, node: AnnCastClassDef, subgraph):
        pass

    @_visit.register
    def visit_dict(self, node: AnnCastDict, subgraph):
        pass

    @_visit.register
    def visit_expr(self, node: AnnCastExpr, subgraph):
        self.visit(node.expr, subgraph)

    def visit_function_def_copy(self, node: AnnCastFunctionDef, subgraph):
        pass

    @_visit.register
    def visit_function_def(self, node: AnnCastFunctionDef, parent_gromet_fn):
        new_gromet = gromet_fn.GrometFN()

        self.gromet_collection.function_networks = insert_gromet_object(self.gromet_collection.function_networks, new_gromet)        


        # metadata type for capturing the original identifier name (i.e. just foo) as it appeared in the code
        # as opposed to the PA derived name (i.e. module.foo_id0, etc..)
        # source_code_identifier_name
        # TODO: change the name so it's the full scoped name, not just the node.name
        new_gromet.b = insert_gromet_object(new_gromet.b, gromet_box_function.GrometBoxFunction(name=node.name, function_type=function_type.FunctionType.FUNCTION))
        
        for arg in node.func_args:
            # Visit the arguments
            self.visit(arg, new_gromet)
            
            # for each argument we want to have a corresponding port (PIF) here
                 
            


        for n in node.body:
            self.visit(n, new_gromet)    
            # Each node of the body here wires up some ports



        pass
    
    @_visit.register
    def visit_literal_value(self, node: AnnCastLiteralValue, parent_gromet_fn):
        # Create the GroMEt literal value (A type of Function box)
        # This will have a single outport (the little blank box)
        # What we dont determine here is the wiring to whatever variable this 
        # literal value goes to (that's up to the parent context)
        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, gromet_box_function.GrometBoxFunction(name="", function_type=function_type.FunctionType.LITERALVALUE, contents=None, value=literal_value.LiteralValue(node.value_type, node.value)))
        parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, gromet_port.GrometPort(name="", box=len(parent_gromet_fn.bf) - 1)) 

        # Perhaps we may need to return something in the future
        # an idea: the index of where this exists

    @_visit.register
    def visit_list(self, node: AnnCastList, subgraph):
        self.visit_node_list(node.values, subgraph)

    @_visit.register
    def visit_loop(self, node: AnnCastLoop, subgraph):
        pass

    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak, subgraph):
        pass

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue, subgraph):
        pass

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf, subgraph):
        pass
    @_visit.register
    def visit_model_return(self, node: AnnCastModelReturn, subgraph):
        self.visit(node.value, subgraph)

        # self.visit_grfn_assignment(node.grfn_assignment, subgraph)

    @_visit.register
    def visit_module(self, node: AnnCastModule, subgraph):
        """
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
        basename_id = -1
        """
        # We create a new GroMEt FN and add it to the GroMEt FN collection

        # Creating a new Function Network (FN) where the outer box is a module
        # i.e. a gray colored box in the drawings
        # It's like any FN but it doesn't have any outer ports, or inner/outer port boxes
        # on it (i.e. little squares on the gray box in a drawing)

        # Have a FN constructor to build the GroMEt FN
        # and pass this FN to maintain a 'nesting' approach (boxes within boxes)
        # instead of passing a GrFNSubgraph through the visitors
        new_gromet = gromet_fn.GrometFN()
        
        # Outer module box only has name 'module' and its type 'Module'
        new_gromet.b = [gromet_box_function.GrometBoxFunction(name="module", function_type=function_type.FunctionType.MODULE)]
        
        # NOTE: The pattern is to check if these (and other) boxes/ports are None
        # and if they are create a list with the appropriate element, otherwise append
        # Put this in a helper function
        new_gromet.bf = [] 
        new_gromet.pof = []

        self.gromet_collection.function_networks.append(new_gromet)
        # TODO: somewhere in this area we need to add 'new_gromet' to the
        # overall gromet FN collection, but should we do it before or after the visit?
        # self.gromet_collection.append(new_gromet)
        self.visit_node_list(node.body, new_gromet)


    @_visit.register
    def visit_name(self, node: AnnCastName, subgraph):
        pass

    @_visit.register
    def visit_number(self, node: AnnCastNumber, subgraph):
        pass

    @_visit.register
    def visit_set(self, node: AnnCastSet, subgraph):
        pass

    @_visit.register
    def visit_string(self, node: AnnCastString, subgraph):
        pass

    @_visit.register
    def visit_subscript(self, node: AnnCastSubscript, subgraph):
        pass

    @_visit.register
    def visit_tuple(self, node: AnnCastTuple, subgraph):
        self.visit_node_list(node.values, subgraph)

    @_visit.register
    def visit_unary_op(self, node: AnnCastUnaryOp, subgraph):
        self.visit(node.value, subgraph)

    @_visit.register
    def visit_var(self, node: AnnCastVar, subgraph):
        self.visit(node.val, subgraph)
