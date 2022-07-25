import typing
from functools import singledispatchmethod
from attr import attr

import networkx as nx
from numpy import insert
from automates.model_assembly.gromet.model import (
    FunctionType,    
    GrometBoxConditional,
    GrometBoxFunction,
    GrometBoxLoop,
    GrometBox,
    GrometFNModule,
    GrometFN,
    GrometPort,
    GrometWire,
    LiteralValue,
)
from automates.model_assembly.gromet.model.gromet_type import GrometType
from automates.model_assembly.gromet.model.typed_value import TypedValue

from automates.program_analysis.CAST2GrFN.ann_cast.annotated_cast import *
from automates.program_analysis.CAST2GrFN.model.cast import ( 
    ScalarType,
    ValueConstructor,
)

PRIMITIVES = {"Add" : "+", "Sub": "-", "Mult" : "*", "Div" : "/", "Lt": "<", "Gt": ">", "Eq": "==", "Pow": "**",
             "_list_get" : "", "_list_set" : "", "_array_get" : "", "_array_set" : "", "_tuple_get" : "", "_tuple_set" : "",
             "_iter" : "", "_next": "", "_member": "", "_add": "", "_delete": ""}

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

# TODO:
# - Port id algorithm
# - Fixing the loop wiring
# - Integrating function arguments/function defs with all the current constructs
#    - Wiring arguments to where they're being used as variables, etc
# - Clean up/refactor some of the logic 


class ToGrometPass:
    def __init__(self, pipeline_state: PipelineState):
        self.pipeline_state = pipeline_state
        self.nodes = self.pipeline_state.nodes

        self.var_environment = {}
        self.cast_node_stack = []

        #self.network = nx.DiGraph()
        #self.subgraphs = nx.DiGraph()
        #self.hyper_edges = []

        # creating a GroMEt FN object here or a collection of GroMEt FNs
        # generally, programs are complex, so a collection of GroMEt FNs is usually created
        # visiting nodes adds FNs 
        self.gromet_module = GrometFNModule("", None, [], [])

        # populate network with variable nodes
        #for grfn_var in self.pipeline_state.grfn_id_to_grfn_var.values():
        #    self.network.add_node(grfn_var, **grfn_var.get_kwargs())

        # the fullid of a AnnCastName node is a string which includes its 
        # variable name, numerical id, version, and scope
        for node in self.pipeline_state.nodes:
            self.visit(node, parent_gromet_fn=None, parent_cast_node=None)

        pipeline_state.gromet_collection = self.gromet_module

    def set_index(self):
        """ Called after a Gromet FN is added to the whole collection
            Properly sets the index of the Gromet FN that was just added
        """
        idx = len(self.gromet_module.attributes)
        self.gromet_module._attributes[-1].index = idx

    def is_primitive(self, func_name):
        return func_name in PRIMITIVES.keys()

    def handle_primitive_function(self, node: AnnCastCall, parent_gromet_fn, parent_cast_node):
        """ Creates an Expression GroMEt FN for the primitive function stored in node.
            Then it gets wired up to its parent_gromet_fn appropriately 
        """
        # Create the Expression FN and its box function 
        primitive_fn = GrometFN()
        primitive_fn.b = insert_gromet_object(primitive_fn.b, GrometBoxFunction(function_type=FunctionType.EXPRESSION))
        
        # Create FN's opi and and opo
        for arg in node.arguments:
            primitive_fn.opi = insert_gromet_object(primitive_fn.opi, GrometPort(box=len(primitive_fn.b)))

        primitive_fn.opo = insert_gromet_object(primitive_fn.opo, GrometPort(box=len(primitive_fn.b)))

        # Insert it into the overall Gromet FN collection
        self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN, value=primitive_fn))
        self.set_index()

        # Create the primitive expression bf
        primitive_func_bf = GrometBoxFunction(name=node.func.name,function_type=FunctionType.PRIMITIVE)
        primitive_fn.bf = insert_gromet_object(primitive_fn.bf, primitive_func_bf)
        
        # Create its pifs and wire them to the opis 
        for i,arg in enumerate(node.arguments,1):
            primitive_fn.pif = insert_gromet_object(primitive_fn.pif, GrometPort(box=len(primitive_fn.bf)))
            primitive_fn.wfopi = insert_gromet_object(primitive_fn.wfopi, GrometWire(src=i, tgt=i))

        # Write its pof and wire it to its opo
        primitive_fn.pof = insert_gromet_object(primitive_fn.pof, GrometPort(box=len(primitive_fn.bf)))
        primitive_fn.wfopo = insert_gromet_object(primitive_fn.wfopo, GrometWire(src=len(primitive_fn.opo), tgt=len(primitive_fn.pof)))

        # Creates the 'call' to this primitive expression which then gets inserted into the parent's Gromet FN
        parent_primitive_call_bf = GrometBoxFunction(function_type=FunctionType.EXPRESSION, contents=len(self.gromet_module.attributes))            
        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, parent_primitive_call_bf)
        for arg in node.arguments:
            parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf)))
        parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(box=len(parent_gromet_fn.bf)))


    def find_gromet(self, func_name):
        """ Attempts to find func_name in self.gromet_module.attributes
            and will return the index of where it is if it finds it.
            It checks if the attribute is a GroMEt FN.
            It will also return a boolean stating whether or not it found it. 
            If it doesn't find it, the func_idx then represents the index at 
            the end of the self.gromet_module.attributes collection.
        """
        func_idx = 0
        found_func = False
        for attribute in self.gromet_module.attributes:
            if attribute.type == GrometType.FN:
                gromet_fn = attribute.value
                if gromet_fn.b != None:
                    gromet_fn_b = gromet_fn.b[0]
                    if gromet_fn_b.name == func_name:
                        found_func = True
                        break 
                    
            func_idx += 1

        return func_idx+1, found_func

    def visit(self, node: AnnCastNode, parent_gromet_fn, parent_cast_node):
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
        return self._visit(node, parent_gromet_fn, parent_cast_node)

    def visit_node_list(self, node_list: typing.List[AnnCastNode], parent_gromet_fn, parent_cast_node):
        return [self.visit(node, parent_gromet_fn, parent_cast_node) for node in node_list]

    @singledispatchmethod
    def _visit(self, node: AnnCastNode, parent_gromet_fn, parent_cast_node):
        """
        Internal visit
        """
        raise NameError(f"Unrecognized node type: {type(node)}")

    # This that create 'expression' GroMEt FNs (i.e. new big standalone colored boxes in the diagram)
    # - The expression on the right hand side of an assignment
    #     - This could be as simple as a LiteralValue (like the number 2)
    #     - It could be a binary expression (like 2 + 3)
    #     - It could be a function call (foo(2))

    @_visit.register
    def visit_assignment(self, node: AnnCastAssignment, parent_gromet_fn, parent_cast_node):
        # How does this creation of a GrometBoxFunction object play into the overall construction?
        # Where does it go? 

        # This first visit on the node.right should create a FN
        # where the outer box is a GExpression (GroMEt Expression)
        # The purple box on the right in examples (exp0.py)
        # Because we don't know exactly what node.right holds at this time
        # we create the Gromet FN for the GExpression here

        # A function call creates a GroMEt FN at the scope of the 
        # outer GroMEt FN box. In other words it's incorrect
        # to scope it to this assignment's Gromet FN
        if isinstance(node.right, AnnCastCall):
            # Assignment for 
            # x = foo(...)
            
            self.visit(node.right, parent_gromet_fn, node)
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

            # We've made the call box function, which made its argument box functions and wired them appropriately.
            # Now, we have to make the output(s) to this call's box function and have them be assigned appropriately.
            if isinstance(node.left, AnnCastTuple):
                for i, elem in enumerate(node.left.values, 1):
                    parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(name=elem.val.name, box=len(parent_gromet_fn.bf), id=i))
            else:
                parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(name=node.left.val.name, box=len(parent_gromet_fn.bf), id=1))
        elif isinstance(node.right, AnnCastName):
            # Assignment for 
            # x = y 

            # Create a passthrough GroMEt
            new_gromet = GrometFN()
            new_gromet.b = insert_gromet_object(new_gromet.b, GrometBoxFunction(function_type=FunctionType.EXPRESSION))
            new_gromet.opi = insert_gromet_object(new_gromet.opi, GrometPort(box=len(new_gromet.b), id=1)) 
            new_gromet.opo = insert_gromet_object(new_gromet.opo, GrometPort(box=len(new_gromet.b), id=1))
            new_gromet.wopio = insert_gromet_object(new_gromet.wopio, GrometWire(src=len(new_gromet.opo),tgt=len(new_gromet.opi)))

            # Add it to the GroMEt collection
            self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN ,value=new_gromet))
            self.set_index()

            # Make it's 'call' expression in the parent gromet
            parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, GrometBoxFunction(function_type=FunctionType.EXPRESSION,contents=len(self.gromet_module.attributes)))
            
            parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf), id=1))
            if isinstance(parent_gromet_fn.b[0], GrometBoxFunction) and (parent_gromet_fn.b[0].function_type == FunctionType.EXPRESSION or parent_gromet_fn.b[0].function_type == FunctionType.PREDICATE):
                parent_gromet_fn.opi = insert_gromet_object(parent_gromet_fn.opi, GrometPort(box=len(parent_gromet_fn.b) ,name=node.right.name, id=1))

            if node.right.name in self.var_environment:
                entry = self.var_environment[node.right.name]
                parent_gromet_fn.wfopi = insert_gromet_object(parent_gromet_fn.wfopi, GrometWire(src=len(parent_gromet_fn.pif), tgt=entry[2]+1)) 
            # parent_gromet_fn.wfopi = insert_gromet_object(parent_gromet_fn.wfopi, GrometWire(src=len(parent_gromet_fn.pif),tgt=len(parent_gromet_fn.b))) 
            parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(name=node.left.val.name, box=len(parent_gromet_fn.bf), id=1))
        elif isinstance(node.right, AnnCastLiteralValue):
            # Assignment for 
            # LiteralValue (i.e. 3)
            
            # Make Expression GrometFN
            new_gromet = GrometFN()
            new_gromet.b = insert_gromet_object(new_gromet.b, GrometBoxFunction(function_type=FunctionType.EXPRESSION))
            
            # Visit the literal value, which makes a bf for a literal and puts a pof to it
            self.visit(node.right, new_gromet, node)

            # Create the opo for the Gromet Expression holding the literal and then wire its opo to the literal's pof
            new_gromet.opo = insert_gromet_object(new_gromet.opo, GrometPort(box=len(new_gromet.b)))
            new_gromet.wfopo = insert_gromet_object(new_gromet.wfopo, GrometWire(src=len(new_gromet.opo), tgt=len(new_gromet.pof)))

            # Append this Gromet Expression holding the literal to the overall gromet FN collection
            self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN,value=new_gromet))
            self.set_index()

            # Make the 'call' box function that connects the expression to the parent and creates its output port
            parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, GrometBoxFunction(function_type=FunctionType.EXPRESSION, contents=len(self.gromet_module.attributes)))
            parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(name=node.left.val.name, box=len(parent_gromet_fn.bf)))

        else: 
            # General Case
            # Assignment for
            # Expression (x + y + ...), etc
            
            # Create an expression FN 
            new_gromet = GrometFN()
            new_gromet.b = insert_gromet_object(new_gromet.b, GrometBoxFunction(function_type=FunctionType.EXPRESSION))
            self.visit(node.right, new_gromet, node)
            # At this point we identified the variable being assigned (i.e. for exp0.py: x)
            # we need to do some bookkeeping to associate the source CAST/GrFN variable with
            # the output port of the GroMEt expression call
            # NOTE: This may need to change from just indexing to something more
            new_gromet.opo = insert_gromet_object(new_gromet.opo, GrometPort(box=len(new_gromet.b)))

            # GroMEt wiring creation
            # The creation of the wire between the output port (pof) of the top-level node 
            # of the tree rooted in node.right needs to be wired to the output port out (OPO)
            # of the GExpression of this AnnCastAssignment
            new_gromet.wfopo = insert_gromet_object(new_gromet.wfopo, GrometWire(src=len(new_gromet.opo), tgt=len(new_gromet.pof)))

            self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN,value=new_gromet))
            self.set_index()

            # An assignment in a conditional or loop's body doesn't add bf, pif, or pof to the parent gromet FN
            # So we check if this assignment is not in either of those and add accordingly
            # NOTE: The above is no longer true because now Ifs/Loops create an additional 'Function' GroMEt FN for
            #       their respective parts, so we do need to add this Expression GroMEt FN to the parent bf
            parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, GrometBoxFunction(function_type=FunctionType.EXPRESSION, contents=len(self.gromet_module.attributes)))
            
            # LiteralValues don't have inputs any inputs, so we don't add a pif 
            for opi in new_gromet.opi:
                parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf)))
                if opi.name in self.var_environment:
                    entry = self.var_environment[opi.name]
                    parent_gromet_fn.wfopi = insert_gromet_object(parent_gromet_fn.wfopi, GrometWire(src=len(parent_gromet_fn.pif), tgt=entry[2]+1)) 

                opi.name = None
                        


            parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(name=node.left.val.name, box=len(parent_gromet_fn.bf)))

        # One way or another we have a hold of the GEXpression object here.
        # Whatever's returned by the RHS of the assignment, 
        # i.e. LiteralValue or primitive operator or function call.
        # Now we can look at its output port(s)

        # node.left contains info about the variable being assigned

        # new_gromet.wfopo = insert_gromet_object(new_gromet.wfopo, gromet_wire.GrometWire(src=len(new_gromet.pof)-1, tgt=len(new_gromet.opo)-1))
        # parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, gromet_box_function.GrometBoxFunction(name="", function_type=function_type.FunctionType.EXPRESSION, contents=len(self.gromet_collection.function_networks)-1,value=None))
        # parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, gromet_port.GrometPort(name=node.left.val.name, box=len(parent_gromet_fn.b)-1))

    @_visit.register
    def visit_attribute(self, node: AnnCastAttribute, parent_gromet_fn, parent_cast_node):
        pass

    @_visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp, parent_gromet_fn, parent_cast_node):
        # visit LHS first
        self.visit(node.left, parent_gromet_fn, node)

        # visit RHS second
        self.visit(node.right, parent_gromet_fn, node)

        # NOTE/TODO Maintain a table of primitive operators that when queried give you back
        # their signatures that can be used for generating 
        ops_map = {"Add" : "+", "Sub": "-", "Mult" : "*", "Div" : "/", "Lt": "<", "Gt": ">", "Eq": "==", "Pow": "**"}

        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, GrometBoxFunction(name=ops_map[node.op], function_type=FunctionType.PRIMITIVE))
        parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf), id=1))
        parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf), id=2))

        parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(box=len(parent_gromet_fn.bf), id=1))

        if isinstance(node.left, AnnCastName):
            if isinstance(parent_gromet_fn.b[0], GrometBoxFunction) and (parent_gromet_fn.b[0].function_type == FunctionType.EXPRESSION or parent_gromet_fn.b[0].function_type == FunctionType.PREDICATE):
                parent_gromet_fn.opi = insert_gromet_object(parent_gromet_fn.opi, GrometPort(name=node.left.name,box=len(parent_gromet_fn.b)))
                # parent_gromet_fn.opi[-1].id = len(parent_gromet_fn.opi) # Neccessary in case this is the first opi we are adding
            parent_gromet_fn.wfopi = insert_gromet_object(parent_gromet_fn.wfopi, GrometWire(src=len(parent_gromet_fn.pif)-1,tgt=len(parent_gromet_fn.b))) 
        if isinstance(node.right, AnnCastName):
            if isinstance(parent_gromet_fn.b[0], GrometBoxFunction) and (parent_gromet_fn.b[0].function_type == FunctionType.EXPRESSION or parent_gromet_fn.b[0].function_type == FunctionType.PREDICATE):
                parent_gromet_fn.opi = insert_gromet_object(parent_gromet_fn.opi, GrometPort(name=node.right.name,box=len(parent_gromet_fn.b)))
                # parent_gromet_fn.opi[-1].id = len(parent_gromet_fn.opi)
            parent_gromet_fn.wfopi = insert_gromet_object(parent_gromet_fn.wfopi, GrometWire(src=len(parent_gromet_fn.pif),tgt=len(parent_gromet_fn.b))) 

        if isinstance(node.left, AnnCastLiteralValue):
            parent_gromet_fn.wff = insert_gromet_object(parent_gromet_fn.wff, GrometWire(src=len(parent_gromet_fn.pif),tgt=len(parent_gromet_fn.pof)-1)) 
        
        if isinstance(node.right, AnnCastLiteralValue):
            parent_gromet_fn.wff = insert_gromet_object(parent_gromet_fn.wff, GrometWire(src=len(parent_gromet_fn.pif),tgt=len(parent_gromet_fn.pof)-1)) 


    @_visit.register
    def visit_boolean(self, node: AnnCastBoolean, parent_gromet_fn, parent_cast_node):
        pass

    @_visit.register    
    def visit_call(self, node: AnnCastCall, parent_gromet_fn, parent_cast_node):

        # Certain functions (special functions that PA has designated as primitive)
        # Are considered 'primitive' operations, in other words calls to them aren't 
        # considered function calls but rather they're considered expressions, so we 
        # call a special handler to handle these
        if self.is_primitive(node.func.name):
            self.handle_primitive_function(node, parent_gromet_fn, parent_cast_node)
            return         

        # The CAST generation step has the potential to rearrange
        # the order in which FunctionDefs appear in the code 
        # so that a Call comes before its definition. This means
        # that a GroMEt FN isn't guaranteed to exist before a Call 
        # to it is made. So we either find the GroMEt in the collection of
        # FNs or we create a 'temporary' one that will be filled out later
        identified_func_name = f"{'.'.join(node.func.con_scope)}.{node.func.name}_id{node.func.id}"
        func_name = node.func.name

        idx, found = self.find_gromet(func_name)        


        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, GrometBoxFunction(name=identified_func_name, function_type=FunctionType.FUNCTION, contents=idx))
        for arg in node.arguments:
            # Could add wfopi as needed here I think
            if isinstance(arg, AnnCastName):
                parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf)))
                print("----"+arg.name)
                if arg.name in self.var_environment:
                    entry = self.var_environment[arg.name]
                    parent_gromet_fn.wfopi = insert_gromet_object(parent_gromet_fn.wfopi, GrometWire(src=len(parent_gromet_fn.pif) ,tgt=entry[2]))
                else:   
                    parent_gromet_fn.wff = insert_gromet_object(parent_gromet_fn.wff, GrometWire(src=len(parent_gromet_fn.pif),tgt=len(parent_gromet_fn.pof)))
            else:
                self.visit(arg, parent_gromet_fn, node)



        # print(f"Function {func_name} found: {found} at index: {idx}")
        # print(parent_gromet_fn)

        # Make a placeholder for this function since we haven't visited its FunctionDef at the end
        # of the list of the Gromet FNs
        if not found:
            temp_gromet_fn = GrometFN()
            temp_gromet_fn.b = insert_gromet_object(temp_gromet_fn.b, GrometBoxFunction(name=func_name, function_type=FunctionType.FUNCTION))
            self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN,value=temp_gromet_fn))
            self.set_index()
            # assert idx == len(self.gromet_module.attributes) - 1
        
    @_visit.register
    def visit_class_def(self, node: AnnCastClassDef, parent_gromet_fn, parent_cast_node):
        pass

    @_visit.register
    def visit_dict(self, node: AnnCastDict, parent_gromet_fn, parent_cast_node):
        pass

    @_visit.register
    def visit_expr(self, node: AnnCastExpr, parent_gromet_fn, parent_cast_node):
        self.visit(node.expr, parent_gromet_fn, parent_cast_node)

    def visit_function_def_copy(self, node: AnnCastFunctionDef, parent_gromet_fn, parent_cast_node):
        pass

    @_visit.register
    def visit_function_def(self, node: AnnCastFunctionDef, parent_gromet_fn, parent_cast_node):
        # print(f"-----{node.name.name}------")
        func_name = node.name.name
        identified_func_name = ".".join(node.con_scope)
        idx,found = self.find_gromet(func_name)

        if not found:
            new_gromet = GrometFN()
            self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN, value=new_gromet))
            self.set_index()
            new_gromet.b = insert_gromet_object(new_gromet.b, GrometBoxFunction(name=func_name, function_type=FunctionType.FUNCTION))
        else:
            new_gromet = self.gromet_module.attributes[idx-1].value

        # metadata type for capturing the original identifier name (i.e. just foo) as it appeared in the code
        # as opposed to the PA derived name (i.e. module.foo_id0, etc..)
        # source_code_identifier_name
        # TODO: where does this OPO really belong?
        # NOTE: The following opo below was moved into a different visitor
        #       with the logic being that the return statement takes care of building the opos which correspond to return values 
        #       in a function def
        #       new_gromet.opo = insert_gromet_object(new_gromet.opo, GrometPort(box=len(new_gromet.b), id=1))
        
        for i, arg in enumerate(node.func_args, 1):
            # Visit the arguments
            self.visit(arg, new_gromet, node)
            
            # for each argument we want to have a corresponding port (OPI) here
            new_gromet.opi = insert_gromet_object(new_gromet.opi, GrometPort(box=len(new_gromet.b),name=arg.val.name, id=i))
            # Store each argument, its opi, and where it is in the opi table
            # For use when creating wfopi wires
            # Have to add 1 to the third value if we want to use it as an index reference
            self.var_environment[arg.val.name] = (arg, new_gromet.opi[-1], len(new_gromet.opi)-1)
            
        # new_gromet.wfopi = []
        for n in node.body:
            self.visit(n, new_gromet, node)   

        # Create wfopo/wlopo/wcopo to wire the final computations to the output port 
        # TODO: What about the case where there's multiple return values
        # also TODO: We need some kind of logic check to determine when we make a wopio for the case that an argument just passes through without
        # being used 
        if new_gromet.bc != None:
            new_gromet.wcopo = insert_gromet_object(new_gromet.wcopo, GrometWire(src=len(new_gromet.opo), tgt=len(new_gromet.poc))) 
        elif new_gromet.bl != None:
            new_gromet.wlopo = insert_gromet_object(new_gromet.wlopo, GrometWire(src=len(new_gromet.opo), tgt=len(new_gromet.pol))) 
        elif new_gromet.bf != None:
            new_gromet.wfopo = insert_gromet_object(new_gromet.wfopo, GrometWire(src=len(new_gromet.opo), tgt=len(new_gromet.pof))) 

        self.var_environment = {}

        # main is a special function, in that program executions start 
        # I think here we must add a bf to properly reflect this execution
        # main's input/output ports are its arguments/return value if it has any
        # not quite sure how to go about this yet (TODO)
        if func_name == "main":
            parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, GrometBoxFunction(name=identified_func_name,function_type=FunctionType.FUNCTION,contents=idx))


    @_visit.register
    def visit_literal_value(self, node: AnnCastLiteralValue, parent_gromet_fn, parent_cast_node):
        # Create the GroMEt literal value (A type of Function box)
        # This will have a single outport (the little blank box)
        # What we dont determine here is the wiring to whatever variable this 
        # literal value goes to (that's up to the parent context)
        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, GrometBoxFunction(function_type=FunctionType.LITERAL, value=LiteralValue(node.value_type, node.value)))
        parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(box=len(parent_gromet_fn.bf), id=1)) 

        # Perhaps we may need to return something in the future
        # an idea: the index of where this exists

    @_visit.register
    def visit_list(self, node: AnnCastList, parent_gromet_fn, parent_cast_node):
        self.visit_node_list(node.values, parent_gromet_fn, parent_cast_node)

    @_visit.register
    def visit_loop(self, node: AnnCastLoop, parent_gromet_fn, parent_cast_node):

        print(node.top_interface_vars.values())

        # Create empty gromet box loop that gets filled out before
        # being added to the parent gromet_fn
        gromet_bl = GrometBoxLoop()

        # Finally, insert the gromet box loop into the parent gromet
        parent_gromet_fn.bl = insert_gromet_object(parent_gromet_fn.bl, gromet_bl)

        # Create the pil and pol ports that the gromet box loop uses
        for i, (_,val) in enumerate(node.used_vars.items(), 1):
            # TODO: Connect the ports using the ID system clay introduced
            parent_gromet_fn.pil = insert_gromet_object(parent_gromet_fn.pil, GrometPort(box=len(parent_gromet_fn.bl), id=i))
            parent_gromet_fn.pol = insert_gromet_object(parent_gromet_fn.pol, GrometPort(name=val,box=len(parent_gromet_fn.bl), id=i))

        ######### Loop Condition

        # This creates a predicate Gromet FN
        gromet_predicate_fn = GrometFN()
        self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN, value=gromet_predicate_fn))
        self.set_index()

        # The predicate then gets visited
        gromet_predicate_fn.b = insert_gromet_object(gromet_predicate_fn.b, GrometBoxFunction(function_type=FunctionType.PREDICATE))
        self.visit(node.expr, gromet_predicate_fn, node) # visit condition

        # Create the predicate's opo and wire it appropriately
        gromet_predicate_fn.opo = insert_gromet_object(gromet_predicate_fn.opo, GrometPort(box=len(gromet_predicate_fn.b), id=1))
        gromet_predicate_fn.wfopo = insert_gromet_object(gromet_predicate_fn.wfopo, GrometWire(src=len(gromet_predicate_fn.opo),tgt=len(gromet_predicate_fn.pof)))
        
        # Insert the predicate as the condition field of this loop's Gromet box loop
        gromet_bl_bf = GrometBoxFunction(function_type=FunctionType.PREDICATE, contents=len(self.gromet_module.attributes))
        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, gromet_bl_bf)
        gromet_bl.condition = gromet_bl_bf.contents # NOTE: gromet_bl and gromet_bc store numbers in their fields, not lists or bfs, the numbers point to bfs

        for i, opi in enumerate(gromet_predicate_fn.opi, 1):
            parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(id=i, box=len(parent_gromet_fn.bf)))
        
        for i, opo in enumerate(gromet_predicate_fn.opo, 1):
            parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(id=i, box=len(parent_gromet_fn.bf)))

        ######### Loop Body

        # The body section of the loop is itself a Gromet FN, so we create one and add it to our global list of FNs for this overall module
        gromet_body_fn = GrometFN()
        gromet_body_fn.b = insert_gromet_object(gromet_body_fn.b, GrometBoxFunction(function_type=FunctionType.FUNCTION))
        self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN, value=gromet_body_fn))
        self.set_index()

        # Then, we need the body's 'call' bf in the parent GroMEt FN this loop exists in, so we add it here
        gromet_body_bf = GrometBoxFunction(function_type=FunctionType.FUNCTION, contents=len(self.gromet_module.attributes))
        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, gromet_body_bf)
        
        # The Gromet FN for the loop body needs to have its opis and opos generated here, since it isn't an actual FunctionDef here to make it with
        for i, (_,val) in enumerate(node.used_vars.items(), 1):
            gromet_body_fn.opi = insert_gromet_object(gromet_body_fn.opi, GrometPort(box=len(gromet_body_fn.b), id=i))
            gromet_body_fn.opo = insert_gromet_object(gromet_body_fn.opo, GrometPort(name=val, box=len(gromet_body_fn.b), id=i))

        # The 'call' bf for the body FN needs to have its pifs and pofs generated here as well
        for i, (_,val) in enumerate(node.used_vars.items(), 1):
            parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(name="AAA", box=len(parent_gromet_fn.bf), id=i))
            parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(name=val, box=len(parent_gromet_fn.bf), id=i))

        # Go through all the statements in the loop's body and have the visitors appropriately fill out the loop body's FN
        for n in node.body:
            self.visit(n, gromet_body_fn, node)

        gromet_bl.body = gromet_body_bf.contents

        # print(node.bot_interface_out)
        


    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak, parent_gromet_fn, parent_cast_node):
        pass

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue, parent_gromet_fn, parent_cast_node):
        pass

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf, parent_gromet_fn, parent_cast_node):
        gromet_bc = GrometBoxConditional()        

        print(node.vars_accessed_before_mod)
        print(node.modified_vars)
        print(node.used_vars)


        print()
        print(node.expr_highest_var_vers)
        print(node.ifbody_highest_var_vers)
        print(node.elsebody_highest_var_vers)

        print(node.top_interface_vars.items())

        # This creates a predicate Gromet FN NOTE: The location of this predicate creation might change later 
        gromet_predicate_fn = GrometFN()
        self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN, value=gromet_predicate_fn))
        self.set_index()

        parent_gromet_fn.bc = insert_gromet_object(parent_gromet_fn.bc, gromet_bc)


        for i, (_,val) in enumerate(node.top_interface_vars.items(), 1):
            # TODO: Connect the ports using the ID system clay introduced
            parent_gromet_fn.pic = insert_gromet_object(parent_gromet_fn.pic, GrometPort(box=len(parent_gromet_fn.bc), id=i))
        
        for i, (_,val) in enumerate(node.bot_interface_vars.items(), 1):
            # TODO: Connect the ports using the ID system clay introduced
            parent_gromet_fn.poc = insert_gromet_object(parent_gromet_fn.poc, GrometPort(name=val,box=len(parent_gromet_fn.bc), id=i))

        # TODO: We also need to put this around a loop
        # And in particular we only want to make wires to variables that are used in the conditional
        # Check type of parent_cast_node to determine which wire to create
        # TODO: Previously, we were always generating a wfc wire for variables coming into a conditional
        # However, we can also have variables coming in from other sources such as an opi.
        # This is a temporary fix for the specific case in the CHIME model, but will need to be revisited
        if isinstance(parent_cast_node, AnnCastFunctionDef):
            parent_gromet_fn.wcopi = insert_gromet_object(parent_gromet_fn.wcopi, GrometWire(src=len(parent_gromet_fn.pic), tgt=len(parent_gromet_fn.opi)))
        else:
            parent_gromet_fn.wfc = insert_gromet_object(parent_gromet_fn.wfc, GrometWire(src=len(parent_gromet_fn.pic),tgt=len(parent_gromet_fn.pof)))
        
        # Visit the predicate afterwards
        gromet_predicate_fn.b = insert_gromet_object(gromet_predicate_fn.b, GrometBoxFunction(function_type=FunctionType.PREDICATE))
        self.visit(node.expr, gromet_predicate_fn, node)

        # Create the predicate's opo and wire it appropriately
        gromet_predicate_fn.opo = insert_gromet_object(gromet_predicate_fn.opo, GrometPort(box=len(gromet_predicate_fn.b), id=1))
        gromet_predicate_fn.wfopo = insert_gromet_object(gromet_predicate_fn.wfopo, GrometWire(src=len(gromet_predicate_fn.opo),tgt=len(gromet_predicate_fn.pof)))

        # Assign the predicate
        predicate_bf = GrometBoxFunction(function_type=FunctionType.FUNCTION, contents=len(self.gromet_module.attributes))
        gromet_bc.condition = predicate_bf.contents # NOTE: this is an index into the bf array of the Gromet FN that this if statement is in
        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, predicate_bf)
        parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf), id=1))
        parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(box=len(parent_gromet_fn.bf), id=1))

              # TODO: put this in a loop to handle more than one argument
        parent_gromet_fn.wl_cargs = insert_gromet_object(parent_gromet_fn.wl_cargs, GrometWire(src=len(parent_gromet_fn.pif),
                                                                                                tgt=len(parent_gromet_fn.pic)))
        
        # Visit the body (if cond true part) of the gromet fn
        body_if_fn = GrometFN()
        body_if_fn.b = insert_gromet_object(body_if_fn.b, GrometBoxFunction(function_type=FunctionType.FUNCTION))
        self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN, value=body_if_fn))
        self.set_index()

        self.visit(node.body[0], body_if_fn, node)
        body_if_bf = GrometBoxFunction(function_type=FunctionType.FUNCTION, contents=len(self.gromet_module.attributes))
        gromet_bc.body_if = body_if_bf.contents # NOTE: this is an index into the bf array of the Gromet FN this if statement is in
        # body_if_fn.bf = insert_gromet_object(body_if_fn.bf, )

        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, body_if_bf)
        parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf), id=1))
        parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(box=len(parent_gromet_fn.bf), id=1))

        # Visit the else (if cond false part) of the gromet fn
        self.visit(node.orelse[0], parent_gromet_fn, node)
        body_else_bf = GrometBoxFunction(function_type=FunctionType.FUNCTION, contents=len(self.gromet_module._attributes))
        gromet_bc.body_else = body_else_bf.contents # NOTE: this is an index to the bf array of the Gromet FN this if statement is in
        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, body_else_bf)
        parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf), id=1))
        parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(box=len(parent_gromet_fn.bf), id=1))


    @_visit.register
    def visit_model_return(self, node: AnnCastModelReturn, parent_gromet_fn, parent_cast_node):
        self.visit(node.value, parent_gromet_fn, node)

        # self.visit_grfn_assignment(node.grfn_assignment, subgraph)

    @_visit.register
    def visit_module(self, node: AnnCastModule, parent_gromet_fn, parent_cast_node):
        # We create a new GroMEt FN and add it to the GroMEt FN collection

        # Creating a new Function Network (FN) where the outer box is a module
        # i.e. a gray colored box in the drawings
        # It's like any FN but it doesn't have any outer ports, or inner/outer port boxes
        # on it (i.e. little squares on the gray box in a drawing)

        # Have a FN constructor to build the GroMEt FN
        # and pass this FN to maintain a 'nesting' approach (boxes within boxes)
        # instead of passing a GrFNSubgraph through the visitors
        new_gromet = GrometFN()
        
        # Outer module box only has name 'module' and its type 'Module'
        new_gromet.b = insert_gromet_object(new_gromet.b, GrometBoxFunction(name="module", function_type=FunctionType.MODULE))

        # Module level GroMEt FN sits in its own special field dicating the module node
        self.gromet_module.fn = new_gromet

        # Set the name of the outer Gromet module to be the source file name
        self.gromet_module.name = node.source_refs[0].source_file_name.replace(".py", "")
        
        self.visit_node_list(node.body, new_gromet, node)


    @_visit.register
    def visit_name(self, node: AnnCastName, parent_gromet_fn, parent_cast_node):
        # NOTE: Maybe make wfopi between the function input and where it's being used 
        
        # Currently making opos for return values of functions
        if isinstance(parent_cast_node, AnnCastModelReturn):
            parent_gromet_fn.opo = insert_gromet_object(parent_gromet_fn.opo, GrometPort(box=len(parent_gromet_fn.b)))

    @_visit.register
    def visit_number(self, node: AnnCastNumber, parent_gromet_fn, parent_cast_node):
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
    def visit_tuple(self, node: AnnCastTuple, parent_gromet_fn, parent_cast_node):
        self.visit_node_list(node.values, parent_gromet_fn, parent_cast_node)

    @_visit.register
    def visit_unary_op(self, node: AnnCastUnaryOp, parent_gromet_fn, parent_cast_node):
        self.visit(node.value, parent_gromet_fn, node)

    @_visit.register
    def visit_var(self, node: AnnCastVar, parent_gromet_fn, parent_cast_node):
        self.visit(node.val, parent_gromet_fn, parent_cast_node)
