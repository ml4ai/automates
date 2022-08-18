from copy import deepcopy
import typing
import sys

from automates.utils.misc import uuid

from functools import singledispatchmethod
from automates.model_assembly.gromet.metadata.provenance import Provenance
from datetime import datetime
from time import time

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

from automates.model_assembly.gromet.metadata.source_code_data_type import SourceCodeDataType
from automates.model_assembly.gromet.metadata.source_code_reference import SourceCodeReference
from automates.model_assembly.gromet.metadata.source_code_collection import SourceCodeCollection
from automates.model_assembly.gromet.metadata.code_file_reference import CodeFileReference
from automates.model_assembly.gromet.metadata.gromet_creation import GrometCreation

from automates.program_analysis.CAST2GrFN.ann_cast.annotated_cast import *
from automates.program_analysis.CAST2GrFN.model.cast import ( 
    ScalarType,
    ValueConstructor,
)

cons = "num"

PRIMITIVES = {"Add" : "+", "Sub": "-", "Mult" : "*", "Div" : "/", "Lt": "<", "Gt": ">", "Eq": "==", "Pow": "**", "NotEq": "!=",
             "_List_get" : "", "_List_set" : "", "_Array_get" : "", "_Array_set" : "", "_Tuple_get" : "", "_Tuple_set" : "",
             "_iter" : "", "_next": "", "_member": "", "_add": "", "_delete": "", "print": "", 
             "_List": "", "_List_"+cons: "", "_Array": "", "_Array_"+cons: "", "_Tuple": "", "_Tuple_"+cons: "", "_Set": ""}

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

    # Logic for generating port ids
    if isinstance(obj, GrometPort):
        if t == None:
            obj.id = 1
        else:
            current_box = obj.box 
            current_box_ports = [port for port in t if port.box == current_box]
            obj.id = len(current_box_ports)+1
    
    if t == None:
        t = []
    t.append(obj)

    return t

def generate_provenance():
    timestamp = str(datetime.fromtimestamp(time()))
    method_name = "skema_code2fn_program_analysis"
    return Provenance(method=method_name, timestamp=timestamp)

def comp_name_nodes(n1, n2):
    if not isinstance(n1, AnnCastName) and not isinstance(n1, AnnCastUnaryOp):
        return False
    if not isinstance(n2, AnnCastName) and not isinstance(n2, AnnCastUnaryOp):
        return False
    if isinstance(n1, AnnCastUnaryOp):
        n1_name = n1.value.name    
        n1_id = n1.value.id
    else:
        n1_name = n1.name
        n1_id = n1.id
    if isinstance(n2, AnnCastUnaryOp):
        n2_name = n2.value.name    
        n2_id = n2.value.id
    else:
        n2_name = n2.name
        n2_id = n2.id

    return n1_name == n2_name and n1_id == n2_id     

def find_existing_opi(gromet_fn, opi_name):
    idx = 1
    if gromet_fn.opi == None:
        return False,idx

    for opi in gromet_fn.opi:
        if opi_name == opi.name:
            return True,idx
        idx += 1
    return False,idx

def find_existing_pil(gromet_fn, opi_name):
    if gromet_fn.pil == None:
        return -1

    idx = 1
    for pil in gromet_fn.pil:
        if opi_name == pil.name:
            return idx
        idx += 1
    return -1

# TODO:
# - Fixing the loop wiring
# - Integrating function arguments/function defs with all the current constructs
#    - Wiring arguments to where they're being used as variables, etc
# - Clean up/refactor some of the logic 


class ToGrometPass:
    def __init__(self, pipeline_state: PipelineState):
        self.pipeline_state = pipeline_state
        self.nodes = self.pipeline_state.nodes

        self.var_environment = {"global": None, "args": None, "local": None}
        self.cast_node_stack = []

        # creating a GroMEt FN object here or a collection of GroMEt FNs
        # generally, programs are complex, so a collection of GroMEt FNs is usually created
        # visiting nodes adds FNs 
        self.gromet_module = GrometFNModule("", None, [], [])

        # the fullid of a AnnCastName node is a string which includes its 
        # variable name, numerical id, version, and scope
        for node in self.pipeline_state.nodes:
            self.visit(node, parent_gromet_fn=None, parent_cast_node=None)

        pipeline_state.gromet_collection = self.gromet_module
                    
    def wire_from_var_env(self, name, gromet_fn):
        if name in self.var_environment["global"]:
            global_env = self.var_environment["global"]
            entry = global_env[name]
            gromet_fn.wff = insert_gromet_object(gromet_fn.wff, GrometWire(src=len(gromet_fn.pif), tgt=entry[2]+1)) 
        elif name in self.var_environment["local"]:
            local_env = self.var_environment["local"]
            entry = local_env[name]
            if isinstance(entry[0], AnnCastLoop):
                gromet_fn.wlf = insert_gromet_object(gromet_fn.wlf, GrometWire(src=len(gromet_fn.pif),tgt=entry[2]+1))
            else:
                gromet_fn.wff = insert_gromet_object(gromet_fn.wff, GrometWire(src=len(gromet_fn.pif),tgt=entry[2]+1))
        elif name in self.var_environment["args"]:
            args_env = self.var_environment["args"]
            entry = args_env[name]
            gromet_fn.wfopi = insert_gromet_object(gromet_fn.wfopi, GrometWire(src=len(gromet_fn.pif),tgt=entry[2]+1))

    def create_source_code_reference(self, ref_info):
        # return None # comment this when we want metadata
        if ref_info == None:
            return None

        line_begin = ref_info.row_start
        line_end = ref_info.row_end
        col_begin = ref_info.col_start
        col_end = ref_info.col_end

        file_uid = str(self.gromet_module.metadata[-1].files[0].uid)
        return SourceCodeReference(provenance=generate_provenance(), code_file_reference_uid=file_uid, line_begin=line_begin, line_end=line_end, col_begin=col_begin, col_end=col_end)

    def set_index(self):
        """ Called after a Gromet FN is added to the whole collection
            Properly sets the index of the Gromet FN that was just added
        """
        return
        idx = len(self.gromet_module.attributes)
        self.gromet_module._attributes[-1].index = idx

    def is_primitive(self, func_name):
        return func_name in PRIMITIVES.keys()

    def handle_primitive_function(self, node: AnnCastCall, parent_gromet_fn, parent_cast_node):
        """ Creates an Expression GroMEt FN for the primitive function stored in node.
            Then it gets wired up to its parent_gromet_fn appropriately 
        """
        ref = node.source_refs[0]
        metadata = [self.create_source_code_reference(ref)]
        # Create the Expression FN and its box function 
        primitive_fn = GrometFN()
        primitive_fn.b = insert_gromet_object(primitive_fn.b, GrometBoxFunction(function_type=FunctionType.EXPRESSION, metadata=metadata))

        # Create the primitive expression bf
        primitive_func_bf = GrometBoxFunction(name=node.func.name,function_type=FunctionType.PRIMITIVE)
        primitive_fn.bf = insert_gromet_object(primitive_fn.bf, primitive_func_bf)
        primitive_bf_loc = len(primitive_fn.bf)

        primitive_fn.opo = insert_gromet_object(primitive_fn.opo, GrometPort(box=len(primitive_fn.b)))

        # Write its pof and wire it to its opo
        primitive_fn.pof = insert_gromet_object(primitive_fn.pof, GrometPort(box=len(primitive_fn.bf)))
        primitive_fn.wfopo = insert_gromet_object(primitive_fn.wfopo, GrometWire(src=len(primitive_fn.opo), tgt=len(primitive_fn.pof)))

        # Create FN's opi and and opo
        for arg in node.arguments:
            # print(type(arg))
            if isinstance(arg, AnnCastBinaryOp) or isinstance(arg, AnnCastLiteralValue):
                self.visit(arg, primitive_fn, parent_cast_node)
                primitive_fn.pif = insert_gromet_object(primitive_fn.pif, GrometPort(box=primitive_bf_loc))
                primitive_fn.wff = insert_gromet_object(primitive_fn.wff, GrometWire(src=len(primitive_fn.pif), tgt=(len(primitive_fn.pof))))
            #elif isinstance(arg, AnnCastCall):
             #   if self.is_primitive(arg.func.name):
              #      self.handle_primitive_function(arg, primitive_fn, node)
               #     primitive_fn.pif = insert_gromet_object(primitive_fn.pif, GrometPort(box=primitive_bf_loc))
                #    primitive_fn.wff = insert_gromet_object(primitive_fn.wff, GrometWire(src=len(primitive_fn.pif), tgt=(len(primitive_fn.pof))))
            else:
                primitive_fn.opi = insert_gromet_object(primitive_fn.opi, GrometPort(box=len(primitive_fn.b)))
                primitive_fn.pif = insert_gromet_object(primitive_fn.pif, GrometPort(box=primitive_bf_loc))
                primitive_fn.wfopi = insert_gromet_object(primitive_fn.wfopi, GrometWire(src=len(primitive_fn.pif), tgt=len(primitive_fn.opi)))

        # Insert it into the overall Gromet FN collection
        self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN, value=primitive_fn))
        self.set_index()

        ref = node.source_refs[0]
        metadata = self.create_source_code_reference(ref)
        # Creates the 'call' to this primitive expression which then gets inserted into the parent's Gromet FN
        parent_primitive_call_bf = GrometBoxFunction(function_type=FunctionType.EXPRESSION, contents=len(self.gromet_module.attributes), metadata=[metadata])            

        # We create the arguments of the primitive expression call here and then
        # We must wire the arguments of this primitive expression appropriately
        # We have an extra check to see if the local came from a Loop, in which
        # case we use a wlf wire to wire the pol to the pif

        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, parent_primitive_call_bf)

    def add_var_to_env(self, var_name, var_cast, var_pof, var_pof_idx, parent_cast_node):
        """ Adds a variable with name var_name, CAST node var_cast, Gromet pof var_pof
            and pof index var_pof_idx to the overall variable environment.
            This addition to the environment happens in these conditions
                - An assignment at the global (module) level
                - An assignment at the local (function def) level
                - When visiting a function argument (This is done at the function def visitor)
            This environment is used when a reference to a variable and its pof is 
            needed in Gromet, this is mostly used when creating wires between outputs
            and inputs
            parent_cast_node allows us to determine if this variable exists within 
        """
        
        if isinstance(parent_cast_node, AnnCastModule):
            global_env = self.var_environment["global"] 
            global_env[var_name] = (var_cast, var_pof, var_pof_idx)
        elif isinstance(parent_cast_node, AnnCastFunctionDef) or isinstance(parent_cast_node, AnnCastModelIf) or isinstance(parent_cast_node, AnnCastLoop):
            local_env = self.var_environment["local"] 
            local_env[var_name] = (parent_cast_node, var_pof, var_pof_idx)
        else:
            print(f"error: add_var_to_env: we came from{type(parent_cast_node)}")
            sys.exit()


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
        # class_name = node.__class__.__name__
        # print(f"\nProcessing node type {class_name}")

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

    # This creates 'expression' GroMEt FNs (i.e. new big standalone colored boxes in the diagram)
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
            # x,y,z = foo(...)
            
            func_bf_idx = self.visit(node.right, parent_gromet_fn, node)
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
            # We also add any variables that have been assigned in this AnnCastAssignment to the variable environment
            if isinstance(node.left, AnnCastTuple):
                for elem in node.left.values:
                    ref = elem.source_refs[0]
                    metadata = self.create_source_code_reference(ref)
                    parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(name=elem.val.name, box=len(parent_gromet_fn.bf), metadata=[metadata]))
                    self.add_var_to_env(elem.val.name, elem, parent_gromet_fn.pof[-1], len(parent_gromet_fn.pof)-1, parent_cast_node)
            else:
                ref = node.left.source_refs[0]
                metadata = self.create_source_code_reference(ref)
                #func_name = node.right.func.name
                #idx, found = self.find_gromet(func_name)        
                #print(found)
                if func_bf_idx == None:
                    func_bf_idx = len(parent_gromet_fn.bf)
                parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(name=node.left.val.name, box=func_bf_idx, metadata=[metadata]))
                self.add_var_to_env(node.left.val.name, node.left, parent_gromet_fn.pof[-1], len(parent_gromet_fn.pof)-1, parent_cast_node)
        elif isinstance(node.right, AnnCastName):
            # Assignment for 
            # x = y 

            # Create a passthrough GroMEt
            new_gromet = GrometFN()
            new_gromet.b = insert_gromet_object(new_gromet.b, GrometBoxFunction(function_type=FunctionType.EXPRESSION))
            new_gromet.opi = insert_gromet_object(new_gromet.opi, GrometPort(box=len(new_gromet.b))) 
            new_gromet.opo = insert_gromet_object(new_gromet.opo, GrometPort(box=len(new_gromet.b)))
            new_gromet.wopio = insert_gromet_object(new_gromet.wopio, GrometWire(src=len(new_gromet.opo),tgt=len(new_gromet.opi)))

            # Add it to the GroMEt collection
            self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN ,value=new_gromet))
            self.set_index()

            # Make it's 'call' expression in the parent gromet
            parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, GrometBoxFunction(function_type=FunctionType.EXPRESSION,contents=len(self.gromet_module.attributes)))
            
            parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf)))
            if isinstance(parent_gromet_fn.b[0], GrometBoxFunction) and (parent_gromet_fn.b[0].function_type == FunctionType.EXPRESSION or parent_gromet_fn.b[0].function_type == FunctionType.PREDICATE):
                parent_gromet_fn.opi = insert_gromet_object(parent_gromet_fn.opi, GrometPort(box=len(parent_gromet_fn.b) ,name=node.right.name))
            
            self.wire_from_var_env(node.right.name, parent_gromet_fn)

            parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(name=node.left.val.name, box=len(parent_gromet_fn.bf)))
           
            # Store the new variable we created into the var environment
            self.add_var_to_env(node.left.val.name, node.left, parent_gromet_fn.pof[-1], len(parent_gromet_fn.pof)-1, parent_cast_node)
        elif isinstance(node.right, AnnCastLiteralValue):
            # Assignment for 
            # LiteralValue (i.e. 3)
            ref = node.source_refs[0]
            metadata = self.create_source_code_reference(ref)
            
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
            parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, GrometBoxFunction(function_type=FunctionType.EXPRESSION, contents=len(self.gromet_module.attributes), metadata=[metadata]))
            parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(name=node.left.val.name, box=len(parent_gromet_fn.bf)))

            # TODO: expand on this later with loops
            if isinstance(parent_cast_node, AnnCastModelIf):
                parent_gromet_fn.opi = insert_gromet_object(parent_gromet_fn.opi, GrometPort(box=len(parent_gromet_fn.b)))
                parent_gromet_fn.opo = insert_gromet_object(parent_gromet_fn.opo, GrometPort(box=len(parent_gromet_fn.b)))
                parent_gromet_fn.wfopo = insert_gromet_object(parent_gromet_fn.wfopo, GrometWire(src=len(parent_gromet_fn.opo), tgt=len(parent_gromet_fn.pof)))

            # Store the new variable we created into the variable environment
            self.add_var_to_env(node.left.val.name, node.left, parent_gromet_fn.pof[-1], len(parent_gromet_fn.pof)-1, parent_cast_node)
        else: 
            # General Case
            # Assignment for
            #   - Expression consisting of binary ops (x + y + ...), etc
            #   - Other cases we haven't thought about
            ref = node.source_refs[0]
            metadata = self.create_source_code_reference(ref)
            
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
            parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, GrometBoxFunction(function_type=FunctionType.EXPRESSION, contents=len(self.gromet_module.attributes), metadata=[metadata]))


            # There's no guarantee that our expression GroMEt used any inputs
            # Therefore we check if we have any inputs before checking them
            # For each opi the Expression GroMEt may have, we add a corresponding pif
            # to it, and then we see if we need to wire the pif to anything
            if new_gromet.opi != None:
                # print(new_gromet.opi)
                for opi in new_gromet.opi:
                    parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf)))
                    self.wire_from_var_env(opi.name, parent_gromet_fn)

                    # This is kind of a hack, so the opis are labeled by the GroMEt expression creation, but then we have to unlabel them
                    opi.name = None


            # Put the final pof in the GroMEt expression call, and add its respective variable to the variable environment
            parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(name=node.left.val.name, box=len(parent_gromet_fn.bf)))

            # TODO: expand on this later
            if isinstance(parent_cast_node, AnnCastModelIf):
                parent_gromet_fn.opi = insert_gromet_object(parent_gromet_fn.opi, GrometPort(box=len(parent_gromet_fn.b)))
                parent_gromet_fn.opo = insert_gromet_object(parent_gromet_fn.opo, GrometPort(box=len(parent_gromet_fn.b)))
                parent_gromet_fn.wfopo = insert_gromet_object(parent_gromet_fn.wfopo, GrometWire(src=len(parent_gromet_fn.opo), tgt=len(parent_gromet_fn.pof)))

            self.add_var_to_env(node.left.val.name, node.left, parent_gromet_fn.pof[-1], len(parent_gromet_fn.pof)-1, parent_cast_node)

        # One way or another we have a hold of the GEXpression object here.
        # Whatever's returned by the RHS of the assignment, 
        # i.e. LiteralValue or primitive operator or function call.
        # Now we can look at its output port(s)

    @_visit.register
    def visit_attribute(self, node: AnnCastAttribute, parent_gromet_fn, parent_cast_node):
        pass

    @_visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp, parent_gromet_fn, parent_cast_node):
        # What constitutes the two pieces of a BinaryOp?
        # Each piece can either be
        # - A literal value (i.e. 2)
        # - A function call that returns a value (i.e. foo())
        # - A BinaryOp itself        
        # - A variable reference (i.e. x), this is the only one that doesnt plug a pof 
        #   - This generally causes us to create an opi and a wfopi to connect this to a pif
        # - Other
        #   - A list access (i.e. x[2]) translates to a function call (_list_set), same for other sequential types

        # visit LHS first
        self.visit(node.left, parent_gromet_fn, node)
        
        # Collect where the location of the left pof is 
        # If the left node is an AnnCastName then it
        # automatically doesn't have a pof
        # (This create an opi later)
        left_pof = -1
        if parent_gromet_fn.pof != None:
            left_pof = len(parent_gromet_fn.pof)
        if isinstance(node.left, AnnCastName) or isinstance(node.left, AnnCastUnaryOp):
            left_pof = -1

        # visit RHS second
        self.visit(node.right, parent_gromet_fn, node)
        
        # Collect where the location of the right pof is 
        # If the right node is an AnnCastName then it
        # automatically doesn't have a pof
        # (This create an opi later)
        right_pof = -1
        if parent_gromet_fn.pof != None:
            right_pof = len(parent_gromet_fn.pof)
        if isinstance(node.right, AnnCastName) or isinstance(node.right, AnnCastUnaryOp): 
            right_pof = -1

        ref = node.source_refs[0]
        metadata = self.create_source_code_reference(ref)

        # NOTE/TODO Maintain a table of primitive operators that when queried give you back
        # their signatures that can be used for generating 
        # A global mapping is maintained but it isnt being used for their signatures yet
        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, GrometBoxFunction(name=PRIMITIVES[node.op], function_type=FunctionType.PRIMITIVE, metadata=[metadata]))

        # After we visit the left and right they (in all scenarios but one) append a POF 
        # The one case where it doesnt happen is when the left or right are variables in the expression
        # In this case then they need an opi and the appropriate wiring for it 
        parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf)))
        if isinstance(node.left, AnnCastName) and left_pof == -1:
            if parent_gromet_fn.b[0].function_type != FunctionType.FUNCTION:
                # This check is used for when the binary operation is part of a Function and not an Expression
                # In which case the Function Def handles creating opis
                found_opi, opi_idx = find_existing_opi(parent_gromet_fn, node.left.name)

                if not comp_name_nodes(node.left, node.right) and not found_opi:
                    parent_gromet_fn.opi = insert_gromet_object(parent_gromet_fn.opi, GrometPort(name=node.left.name,box=len(parent_gromet_fn.b)))
                    parent_gromet_fn.wfopi = insert_gromet_object(parent_gromet_fn.wfopi, GrometWire(src=len(parent_gromet_fn.pif),tgt=len(parent_gromet_fn.opi)))
                else: 
                    parent_gromet_fn.wfopi = insert_gromet_object(parent_gromet_fn.wfopi, GrometWire(src=len(parent_gromet_fn.pif),tgt=len(parent_gromet_fn.opi)))
                #parent_gromet_fn.opi = insert_gromet_object(parent_gromet_fn.opi, GrometPort(name=node.left.name,box=len(parent_gromet_fn.b)))
                #parent_gromet_fn.wfopi = insert_gromet_object(parent_gromet_fn.wfopi, GrometWire(src=len(parent_gromet_fn.pif),tgt=len(parent_gromet_fn.opi)))
            else:
                # If we are in a function def then we retrieve where the variable is 
                # Whether it's in the local or the args environment
                
                self.wire_from_var_env(node.left.name, parent_gromet_fn)
        else:
            # In this case, the left node gave us a pof, so we can wire it to the pif here
            parent_gromet_fn.wff = insert_gromet_object(parent_gromet_fn.wff, GrometWire(src=len(parent_gromet_fn.pif), tgt=left_pof))            
        
        
        # Repeat the above but for the right node this time
        # NOTE: In the case that the left and the right node both refer to the same function argument we only
        # want one opi created and so we dont create one here
        parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf)))
        if isinstance(node.right, AnnCastName) and right_pof == -1:
            # This check is used for when the binary operation is part of a Function and not an Expression
            # In which case the Function Def handles creating opis
            if parent_gromet_fn.b[0].function_type != FunctionType.FUNCTION:
                found_opi, opi_idx = find_existing_opi(parent_gromet_fn, node.right.name)

                if not comp_name_nodes(node.left, node.right) and not found_opi:
                    parent_gromet_fn.opi = insert_gromet_object(parent_gromet_fn.opi, GrometPort(name=node.right.name,box=len(parent_gromet_fn.b)))
                    parent_gromet_fn.wfopi = insert_gromet_object(parent_gromet_fn.wfopi, GrometWire(src=len(parent_gromet_fn.pif),tgt=len(parent_gromet_fn.opi)))
                else: 
                    parent_gromet_fn.wfopi = insert_gromet_object(parent_gromet_fn.wfopi, GrometWire(src=len(parent_gromet_fn.pif),tgt=opi_idx))
            else:
                # If we are in a function def then we retrieve where the variable is 
                # Whether it's in the local or the args environment
                self.wire_from_var_env(node.right.name, parent_gromet_fn)
        else:
            # In this case, the right node gave us a pof, so we can wire it to the pif here
            parent_gromet_fn.wff = insert_gromet_object(parent_gromet_fn.wff, GrometWire(src=len(parent_gromet_fn.pif), tgt=right_pof))            

        # Add the pof that serves as the output of this binary operation
        parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(box=len(parent_gromet_fn.bf)))

    @_visit.register
    def visit_boolean(self, node: AnnCastBoolean, parent_gromet_fn, parent_cast_node):
        pass

    def wire_binary_op_args(self, node, parent_gromet_fn):
        if isinstance(node, AnnCastName):
            parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf)))
            if node.name in self.var_environment["local"]:
                local_env = self.var_environment["local"]
                entry = local_env[node.name]
                if isinstance(entry[0], AnnCastLoop):
                    parent_gromet_fn.wlf = insert_gromet_object(parent_gromet_fn.wlf, GrometWire(src=len(parent_gromet_fn.pif),tgt=entry[2]+1))
                else:
                    parent_gromet_fn.wff = insert_gromet_object(parent_gromet_fn.wff, GrometWire(src=len(parent_gromet_fn.pif),tgt=entry[2]+1))
            elif node.name in self.var_environment["args"]:
                args_env = self.var_environment["args"]
                entry = args_env[node.name]
                parent_gromet_fn.wfopi = insert_gromet_object(parent_gromet_fn.wfopi, GrometWire(src=len(parent_gromet_fn.pif),tgt=entry[2]+1))
            return
        if isinstance(node, AnnCastBinaryOp):
            self.wire_binary_op_args(node.left, parent_gromet_fn)
            self.wire_binary_op_args(node.right, parent_gromet_fn)
            return

    @_visit.register    
    def visit_call(self, node: AnnCastCall, parent_gromet_fn, parent_cast_node):

        # Certain functions (special functions that PA has designated as primitive)
        # Are considered 'primitive' operations, in other words calls to them aren't 
        # considered function calls but rather they're considered expressions, so we 
        # call a special handler to handle these
        if self.is_primitive(node.func.name):
            self.handle_primitive_function(node, parent_gromet_fn, parent_cast_node)

            # Handle the primitive's arguments that don't involve expressions of more than 1 variable
            for arg in node.arguments:
                #NOTE: do we need a global check? if arg.name in self.var_environment["global"]:
                # print(f"+++++++++++++++++++++{type(arg)}")

                if isinstance(arg, AnnCastName):
                    parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf)))
                    if arg.name in self.var_environment["local"]:
                        local_env = self.var_environment["local"]
                        entry = local_env[arg.name]
                        if isinstance(entry[0], AnnCastLoop):
                            parent_gromet_fn.wlf = insert_gromet_object(parent_gromet_fn.wlf, GrometWire(src=len(parent_gromet_fn.pif),tgt=entry[2]+1))
                        else:
                            parent_gromet_fn.wff = insert_gromet_object(parent_gromet_fn.wff, GrometWire(src=len(parent_gromet_fn.pif),tgt=entry[2]+1))
                    elif arg.name in self.var_environment["args"]:
                        args_env = self.var_environment["args"]
                        entry = args_env[arg.name]
                        parent_gromet_fn.wfopi = insert_gromet_object(parent_gromet_fn.wfopi, GrometWire(src=len(parent_gromet_fn.pif),tgt=entry[2]+1))
                elif isinstance(arg, AnnCastBinaryOp):
                    self.wire_binary_op_args(arg, parent_gromet_fn)

            primitive_fn_opi = self.gromet_module.attributes[-1].value.opi
            for i,opi in enumerate(primitive_fn_opi,1):
                opi.name = None
            return         
        ref = node.source_refs[0]
        metadata = self.create_source_code_reference(ref)

        arg_fn_pofs = []
        for arg in node.arguments:
            # Go through the arguments and for all of them, create any necessary GroMEt FNs (in the case the argument is something more than a name)
            if isinstance(arg, AnnCastCall):
                self.visit(arg, parent_gromet_fn, node)
                parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(box=len(parent_gromet_fn.bf)))
                arg_fn_pofs.append(len(parent_gromet_fn.pof)) # Store the pof index so we can use it later in wiring
            elif not isinstance(arg, AnnCastName):
                self.visit(arg, parent_gromet_fn, node)
                arg_fn_pofs.append(len(parent_gromet_fn.pof)) # Store the pof index so we can use it later in wiring
            else:
                arg_fn_pofs.append(None)
        # print(arg_fn_pofs)

        # The CAST generation step has the potential to rearrange
        # the order in which FunctionDefs appear in the code 
        # so that a Call comes before its definition. This means
        # that a GroMEt FN isn't guaranteed to exist before a Call 
        # to it is made. So we either find the GroMEt in the collection of
        # FNs or we create a 'temporary' one that will be filled out later
        qualified_func_name = f"{'.'.join(node.func.con_scope)}.{node.func.name}_{node.invocation_index}"
        func_name = node.func.name

        # Make a placeholder for this function if we haven't visited its FunctionDef at the end
        # of the list of the Gromet FNs
        idx, found = self.find_gromet(func_name)        
        if not found:
            temp_gromet_fn = GrometFN()
            temp_gromet_fn.b = insert_gromet_object(temp_gromet_fn.b, GrometBoxFunction(name=func_name, function_type=FunctionType.FUNCTION))
            self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN,value=temp_gromet_fn))
            self.set_index()

        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, GrometBoxFunction(name=qualified_func_name, function_type=FunctionType.FUNCTION, contents=idx, metadata=[metadata]))
        func_call_idx = len(parent_gromet_fn.bf)

        # For each argument we determine if it's a variable being used
        # If it is then
        #  - Determine if it's a local variable or function def argument
        #  - Then wire appropriately
        # Need to handle the case for FunctionCall and BinaryOp still
        for idx,arg in enumerate(node.arguments):
            pof = arg_fn_pofs[idx]
            parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=func_call_idx))
            if isinstance(arg, AnnCastName):
                # print("----"+arg.name)
                self.wire_from_var_env(arg.name, parent_gromet_fn)
                if arg.name not in self.var_environment["global"] and arg.name not in self.var_environment["local"] and arg.name not in self.var_environment["args"]:   
                    parent_gromet_fn.wff = insert_gromet_object(parent_gromet_fn.wff, GrometWire(src=len(parent_gromet_fn.pif),tgt=len(parent_gromet_fn.pof)))
            else:
                parent_gromet_fn.wff = insert_gromet_object(parent_gromet_fn.wff, GrometWire(src=len(parent_gromet_fn.pif),tgt=pof))
        
        return func_call_idx

        
    @_visit.register
    def visit_class_def(self, node: AnnCastClassDef, parent_gromet_fn, parent_cast_node):
        pass

    @_visit.register
    def visit_dict(self, node: AnnCastDict, parent_gromet_fn, parent_cast_node):
        pass

    @_visit.register
    def visit_expr(self, node: AnnCastExpr, parent_gromet_fn, parent_cast_node):
        self.visit(node.expr, parent_gromet_fn, parent_cast_node)

    def handle_function_def(self, node: AnnCastFunctionDef, new_gromet_fn, func_body):
        """ Handles the logic of making a function, whether the function itself is a real
            function definition (that is, it comes from an AnnCastFunctionDef) or it's 
            'artifically generated' (that is, a set of statements coming from a loop or an if statement)
        """        

        self.var_environment["local"] = {}
        for n in func_body: 
            self.visit(n, new_gromet_fn, node)   

        # Create wfopo/wlopo/wcopo to wire the final computations to the output port 
        # TODO: What about the case where there's multiple return values
        # also TODO: We need some kind of logic check to determine when we make a wopio for the case that an argument just passes through without
        # being used 
            
        # If the last node in  the FunctionDef is a return node we must do some final wiring
        if isinstance(n, AnnCastModelReturn):
            if isinstance(n.value, AnnCastTuple):
                ret_vals = list(n.value.values)
            else:
                ret_vals = [n.value]

            for (i,val) in enumerate(ret_vals,1):
                if val.name in self.var_environment["local"]:
                    # If it's in the local env, then 
                    # either it comes from a loop (wlopo), a conditional (wcopo), or just another
                    # function (wfopo), then we check where it comes from and wire appropriately
                    local_env = self.var_environment["local"]
                    entry = local_env[val.name]
                    if isinstance(entry[0], AnnCastLoop):
                        new_gromet_fn.wlopo = insert_gromet_object(new_gromet_fn.wlopo, GrometWire(src=i,tgt=entry[2]+1))
                    elif isinstance(entry[0], AnnCastModelIf):
                        new_gromet_fn.wcopo = insert_gromet_object(new_gromet_fn.wcopo, GrometWire(src=i,tgt=entry[2]+1))
                    else:
                        new_gromet_fn.wfopo = insert_gromet_object(new_gromet_fn.wfopo, GrometWire(src=i,tgt=entry[2]+1))
                elif val.name in self.var_environment["args"]:
                    # If it comes from arguments, then that means the variable
                    # Didn't get changed in the function at all and thus it's just
                    # A pass through (wopio)
                    args_env = self.var_environment["args"]
                    entry = args_env[val.name]
                    new_gromet_fn.wopio = insert_gromet_object(new_gromet_fn.wopio, GrometWire(src=i,tgt=entry[2]+1))
        elif new_gromet_fn.opo != None: # This is in the case of a loop or conditional adding opos
            for (i,opo) in enumerate(new_gromet_fn.opo,1):
                # print(opo, end="--")
                if opo.name in self.var_environment["local"]:
                    # print("wfopo")
                    local_env = self.var_environment["local"]
                    entry = local_env[opo.name]
                    if isinstance(entry[0], AnnCastLoop):
                        new_gromet_fn.wlopo = insert_gromet_object(new_gromet_fn.wlopo, GrometWire(src=i,tgt=entry[2]+1))
                    #elif isinstance(entry[0], AnnCastModelIf):
                    #    new_gromet_fn.wcopo = insert_gromet_object(new_gromet_fn.wcopo, GrometWire(src=i,tgt=entry[2]+1))
                    else:
                        new_gromet_fn.wfopo = insert_gromet_object(new_gromet_fn.wfopo, GrometWire(src=i,tgt=entry[2]+1))
                elif opo.name in self.var_environment["args"]:
                    # print("wopio")
                    args_env = self.var_environment["args"]
                    entry = args_env[opo.name]
                    new_gromet_fn.wopio = insert_gromet_object(new_gromet_fn.wopio, GrometWire(src=i,tgt=entry[2]+1))


        # We're out of the function definition here, so we 
        # can clear the local  variable environment
        self.var_environment["local"] = {}

    @_visit.register
    def visit_function_def(self, node: AnnCastFunctionDef, parent_gromet_fn, parent_cast_node):
        # print(f"-----{node.name.name}------")
        func_name = node.name.name
        identified_func_name = ".".join(node.con_scope)
        idx,found = self.find_gromet(func_name)

        ref = node.source_refs[0]

        if not found:
            new_gromet = GrometFN()
            self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN, value=new_gromet))
            self.set_index()
            new_gromet.b = insert_gromet_object(new_gromet.b, GrometBoxFunction(name=func_name, function_type=FunctionType.FUNCTION))
        else:
            new_gromet = self.gromet_module.attributes[idx-1].value
            
        metadata = self.create_source_code_reference(ref)

        new_gromet.b[0].metadata = [metadata]

        # metadata type for capturing the original identifier name (i.e. just foo) as it appeared in the code
        # as opposed to the PA derived name (i.e. module.foo_id0, etc..)
        # source_code_identifier_name
        
        # Initialize the function argument variable environment and populate it as we 
        # visit the function arguments
        self.var_environment["args"] = {}
        arg_env = self.var_environment["args"]
        
        for arg in node.func_args: 
            #print("VISITING ARG ----")
            # Visit the arguments
            self.visit(arg, new_gromet, node)
            
            # for each argument we want to have a corresponding port (OPI) here
            arg_ref = arg.source_refs[0]
            new_gromet.opi = insert_gromet_object(new_gromet.opi, GrometPort(box=len(new_gromet.b),name=arg.val.name,metadata=[self.create_source_code_reference(arg_ref)]))
            
            # Store each argument, its opi, and where it is in the opi table
            # For use when creating wfopi wires
            # Have to add 1 to the third value if we want to use it as an index reference
            arg_env[arg.val.name] = (arg, new_gromet.opi[-1], len(new_gromet.opi)-1)
            
        # handle_function_def() will visit the body of the function and take care of
        # wiring any GroMEt FNs in its body
        self.handle_function_def(node, new_gromet, node.body)
            
        self.var_environment["args"] = {}
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
        ref = node.source_code_data_type
        source_code_metadata = self.create_source_code_reference(node.source_refs[0])

        code_data_metadata = SourceCodeDataType(metadata_type="source_code_data_type", provenance=generate_provenance(), source_language=ref[0], source_language_version=ref[1], data_type=str(ref[2]))
        val = LiteralValue(node.value_type, node.value)

        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, GrometBoxFunction(function_type=FunctionType.LITERAL, value=val, metadata=[code_data_metadata,source_code_metadata]))
        parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(box=len(parent_gromet_fn.bf))) 

        # Perhaps we may need to return something in the future
        # an idea: the index of where this exists

    @_visit.register
    def visit_list(self, node: AnnCastList, parent_gromet_fn, parent_cast_node):
        self.visit_node_list(node.values, parent_gromet_fn, parent_cast_node)

    @_visit.register
    def visit_loop(self, node: AnnCastLoop, parent_gromet_fn, parent_cast_node):
        # Create empty gromet box loop that gets filled out before
        # being added to the parent gromet_fn
        gromet_bl = GrometBoxLoop()

        # Insert the gromet box loop into the parent gromet
        parent_gromet_fn.bl = insert_gromet_object(parent_gromet_fn.bl, gromet_bl)

        # Create the pil and pol ports that the gromet box loop uses
        # Also, create any necessary wires that the pil uses
        for (_,val) in node.used_vars.items():
            parent_gromet_fn.pil = insert_gromet_object(parent_gromet_fn.pil, GrometPort(name=val,box=len(parent_gromet_fn.bl)))
            if val in self.var_environment["local"]:
                local_env = self.var_environment["local"]
                entry = local_env[val]
                parent_gromet_fn.wfl = insert_gromet_object(parent_gromet_fn.wfl, GrometWire(src=len(parent_gromet_fn.pil), tgt=entry[2]+1))
            elif val in self.var_environment["args"]:
                arg_env = self.var_environment["args"]
                entry = arg_env[val]
                parent_gromet_fn.wlopi = insert_gromet_object(parent_gromet_fn.wlopi, GrometWire(src=len(parent_gromet_fn.pil), tgt=entry[2]+1))


        # print(node.used_vars.items())

        ######### Loop Init (if one exists)
        # TODO
        ######### Loop Condition

        # print("-------------- PREDICATE -")
        # This creates a predicate Gromet FN
        gromet_predicate_fn = GrometFN()
        self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN, value=gromet_predicate_fn))
        self.set_index()

        # The predicate then gets visited
        gromet_predicate_fn.b = insert_gromet_object(gromet_predicate_fn.b, GrometBoxFunction(function_type=FunctionType.PREDICATE))
        self.visit(node.expr, gromet_predicate_fn, node) # visit condition

        # Create the predicate's opo and wire it appropriately
        gromet_predicate_fn.opo = insert_gromet_object(gromet_predicate_fn.opo, GrometPort(box=len(gromet_predicate_fn.b)))
        gromet_predicate_fn.wfopo = insert_gromet_object(gromet_predicate_fn.wfopo, GrometWire(src=len(gromet_predicate_fn.opo),tgt=len(gromet_predicate_fn.pof)))

        ref = node.expr.source_refs[0]
        metadata = [self.create_source_code_reference(ref)]
        
        # Insert the predicate as the condition field of this loop's Gromet box loop
        gromet_bl_bf = GrometBoxFunction(function_type=FunctionType.PREDICATE, contents=len(self.gromet_module.attributes), metadata=metadata)
        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, gromet_bl_bf)
        gromet_bl.condition = len(parent_gromet_fn.bf) # NOTE: gromet_bl and gromet_bc store numbers in their fields, not lists or bfs, the numbers point to bfs

        # Create pif for predicate and wire the wlcargs
        # NOTE: This method will need some expansion later on
        for opi in gromet_predicate_fn.opi:
            opi_idx = find_existing_pil(parent_gromet_fn, opi.name)
            assert opi_idx != -1
            parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf)))
            parent_gromet_fn.wl_cargs = insert_gromet_object(parent_gromet_fn.wl_cargs, GrometWire(src=len(parent_gromet_fn.pif), tgt=opi_idx))
            
            # Pil and opis shouldn't have names, clean them out
            # parent_gromet_fn.pil[opi_idx-1].name = None
            opi.name = None
        
        for opo in gromet_predicate_fn.opo:
            parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(box=len(parent_gromet_fn.bf)))

        ######### Loop Body

        # print("-------------- LOOP BODY -")
        # The body section of the loop is itself a Gromet FN, so we create one and add it to our global list of FNs for this overall module
        gromet_body_fn = GrometFN()
        
        ref = node.body[0].source_refs[0]
        metadata = [self.create_source_code_reference(ref)]
        
        gromet_body_fn.b = insert_gromet_object(gromet_body_fn.b, GrometBoxFunction(function_type=FunctionType.FUNCTION, metadata=metadata))
        self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN, value=gromet_body_fn))
        self.set_index()

        # Then, we need the body's 'call' bf in the parent GroMEt FN this loop exists in, so we add it here
        gromet_body_bf = GrometBoxFunction(function_type=FunctionType.FUNCTION, contents=len(self.gromet_module.attributes))
        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, gromet_body_bf)
        gromet_bl.body = len(parent_gromet_fn.bf)

        # The 'call' bf for the body FN needs to have its pifs and pofs generated here as well
        for (_,val) in node.used_vars.items():
            parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf)))
            parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(name=val, box=len(parent_gromet_fn.bf)))
        
        # Because the code in a loop body is technically a function on its own, we have to create a new
        # Variable environment for the local variables and function arguments
        # While preserving the old one
        # After we're done with the body of the loop, we restore the old environment
        previous_func_def_args = deepcopy(self.var_environment["args"])
        previous_local_args = deepcopy(self.var_environment["local"])

        self.var_environment["args"] = {}

        # The Gromet FN for the loop body needs to have its opis and opos generated here, since it isn't an actual FunctionDef here to make it with
        # Any opis we create for this Gromet FN are also added to the variable environment
        for (_,val) in node.used_vars.items():
            # print(val)
            gromet_body_fn.opi = insert_gromet_object(gromet_body_fn.opi, GrometPort(box=len(gromet_body_fn.b)))
            arg_env = self.var_environment["args"]
            arg_env[val] = (AnnCastFunctionDef(None,None,None,None), gromet_body_fn.opi[-1], len(gromet_body_fn.opi)-1)
            gromet_body_fn.opo = insert_gromet_object(gromet_body_fn.opo, GrometPort(name=val, box=len(gromet_body_fn.b)))
        
        self.handle_function_def(AnnCastFunctionDef(None,None,None,None), gromet_body_fn, node.body)

        # Go through all the statements in the loop's body and have the visitors appropriately fill out the loop body's FN
        # for n in node.body:
        #    self.visit(n, gromet_body_fn, node)

        # Restore the old variable environment
        self.var_environment["args"] = previous_func_def_args  
        self.var_environment["local"] = previous_local_args 

        # pols become 'locals' from this point on
        # That is, any code that is after the while loop should be looking at the pol ports to fetch data for
        # any variables that were used in the loop even if they weren't directly modified by it 
        for (_,val) in node.used_vars.items():
            parent_gromet_fn.pol = insert_gromet_object(parent_gromet_fn.pol, GrometPort(name=val,box=len(parent_gromet_fn.bl)))
            self.add_var_to_env(val, AnnCastLoop(None,None,None,None), parent_gromet_fn.pol[-1], len(parent_gromet_fn.pol)-1, node)


        # print("-------------- LOOP DONE -")
        # print(node.bot_interface_out)

    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak, parent_gromet_fn, parent_cast_node):
        pass

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue, parent_gromet_fn, parent_cast_node):
        pass

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf, parent_gromet_fn, parent_cast_node):
        ref = node.source_refs[0]
        metadata = [self.create_source_code_reference(ref)]
        gromet_bc = GrometBoxConditional(metadata=metadata)        

        # This creates a predicate Gromet FN NOTE: The location of this predicate creation might change later 
        gromet_predicate_fn = GrometFN()
        self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN, value=gromet_predicate_fn))
        self.set_index()

        parent_gromet_fn.bc = insert_gromet_object(parent_gromet_fn.bc, gromet_bc)

        for val in node.expr_vars_accessed_before_mod.items():
            parent_gromet_fn.pic = insert_gromet_object(parent_gromet_fn.pic, GrometPort(box=len(parent_gromet_fn.bc)))
        
        for _,val in node.bot_interface_vars.items():
            parent_gromet_fn.poc = insert_gromet_object(parent_gromet_fn.poc, GrometPort(name=val,box=len(parent_gromet_fn.bc)))

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
        
        ########### Predicate generation

        # print("-------------- PREDICATE -")
        # Visit the predicate afterwards
        gromet_predicate_fn.b = insert_gromet_object(gromet_predicate_fn.b, GrometBoxFunction(function_type=FunctionType.PREDICATE))
        self.visit(node.expr, gromet_predicate_fn, node)

        # Create the predicate's opo and wire it appropriately
        gromet_predicate_fn.opo = insert_gromet_object(gromet_predicate_fn.opo, GrometPort(box=len(gromet_predicate_fn.b)))
        gromet_predicate_fn.wfopo = insert_gromet_object(gromet_predicate_fn.wfopo, GrometWire(src=len(gromet_predicate_fn.opo),tgt=len(gromet_predicate_fn.pof)))

        ref = node.expr.source_refs[0]
        metadata = [self.create_source_code_reference(ref)]
        # Assign the predicate
        predicate_bf = GrometBoxFunction(function_type=FunctionType.PREDICATE, contents=len(self.gromet_module.attributes), metadata=metadata)
        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, predicate_bf)
        gromet_bc.condition = len(parent_gromet_fn.bf) # NOTE: this is an index into the bf array of the Gromet FN that this if statement is in
        parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf)))
        parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(box=len(parent_gromet_fn.bf)))

        # TODO: put this in a loop to handle more than one argument
        parent_gromet_fn.wl_cargs = insert_gromet_object(parent_gromet_fn.wl_cargs, GrometWire(src=len(parent_gromet_fn.pif),
                                                                                                tgt=len(parent_gromet_fn.pic)))
        
        ########### If true generation

        # print("-------------- IF TRUE  ---")
        # Visit the body (if cond true part) of the gromet fn
        body_if_fn = GrometFN()
        body_if_fn.b = insert_gromet_object(body_if_fn.b, GrometBoxFunction(function_type=FunctionType.FUNCTION))
        self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN, value=body_if_fn))
        self.set_index()

        ref = node.body[0].source_refs[0]
        metadata = [self.create_source_code_reference(ref)]

        body_if_bf = GrometBoxFunction(function_type=FunctionType.FUNCTION, contents=len(self.gromet_module.attributes), metadata=metadata)
        self.visit(node.body[0], body_if_fn, node)

        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, body_if_bf)
        gromet_bc.body_if = len(parent_gromet_fn.bf) # NOTE: this is an index into the bf array of the Gromet FN this if statement is in
        parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf)))
        parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(box=len(parent_gromet_fn.bf)))

        ########### If false generation

        # print("-------------- IF FALSE ---")
        # Visit the else (if cond false part) of the gromet fn
        body_else_fn = GrometFN()
        body_else_fn.b = insert_gromet_object(body_else_fn.b, GrometBoxFunction(function_type=FunctionType.FUNCTION))
        self.gromet_module.attributes = insert_gromet_object(self.gromet_module.attributes, TypedValue(type=GrometType.FN, value=body_else_fn))
        self.set_index()

        ref = node.orelse[0].source_refs[0]
        metadata = [self.create_source_code_reference(ref)]
        body_else_bf = GrometBoxFunction(function_type=FunctionType.FUNCTION, contents=len(self.gromet_module.attributes), metadata=metadata)
        self.visit(node.orelse[0], body_else_fn, node)

        parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, body_else_bf)
        gromet_bc.body_else = len(parent_gromet_fn.bf) # NOTE: this is an index to the bf array of the Gromet FN this if statement is in
        parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf)))
        parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(box=len(parent_gromet_fn.bf)))

        # print("-------------- IF DONE  ---")


    @_visit.register
    def visit_model_return(self, node: AnnCastModelReturn, parent_gromet_fn, parent_cast_node):
        if not isinstance(node.value, AnnCastTuple):
            self.visit(node.value, parent_gromet_fn, node)
        ref = node.source_refs[0]

        # A binary op sticks a single return value in the opo
        # Where as a tuple can stick multiple opos, one for each thing being returned
        if isinstance(node.value, AnnCastBinaryOp):
            parent_gromet_fn.opo = insert_gromet_object(parent_gromet_fn.opo, GrometPort(box=len(parent_gromet_fn.b),metadata=[self.create_source_code_reference(ref)]))
        elif isinstance(node.value, AnnCastTuple):
            # print(len(node.value.values))
            for elem in node.value.values:
                parent_gromet_fn.opo = insert_gromet_object(parent_gromet_fn.opo, GrometPort(box=len(parent_gromet_fn.b),metadata=[self.create_source_code_reference(ref)]))

    @_visit.register
    def visit_module(self, node: AnnCastModule, parent_gromet_fn, parent_cast_node):
        # We create a new GroMEt FN and add it to the GroMEt FN collection

        # Creating a new Function Network (FN) where the outer box is a module
        # i.e. a gray colored box in the drawings
        # It's like any FN but it doesn't have any outer ports, or inner/outer port boxes
        # on it (i.e. little squares on the gray box in a drawing)

        file_name = node.source_refs[0].source_file_name
        self.var_environment["global"] = {}

        # Have a FN constructor to build the GroMEt FN
        # and pass this FN to maintain a 'nesting' approach (boxes within boxes)
        # instead of passing a GrFNSubgraph through the visitors
        new_gromet = GrometFN()

        # Initialize the Gromet module's SourceCodeCollection of CodeFileReferences
        code_file_references = [CodeFileReference(uid=str(uuid.uuid4()), name=file_name, path="")]
        self.gromet_module.metadata = [] 
        self.gromet_module.metadata.append(GrometCreation(provenance=generate_provenance()))
        self.gromet_module.metadata.append(SourceCodeCollection(provenance=generate_provenance(), name="", global_reference_id="", files=code_file_references))
        
        # Outer module box only has name 'module' and its type 'Module'
        new_gromet.b = insert_gromet_object(new_gromet.b, GrometBoxFunction(name="module", function_type=FunctionType.MODULE, metadata=[self.create_source_code_reference(node.source_refs[0])]))

        # Module level GroMEt FN sits in its own special field dicating the module node
        self.gromet_module.fn = new_gromet

        # Set the name of the outer Gromet module to be the source file name
        self.gromet_module.name = file_name.replace(".py", "")
        
        self.visit_node_list(node.body, new_gromet, node)

        self.var_environment["global"] = {}

    @_visit.register
    def visit_name(self, node: AnnCastName, parent_gromet_fn, parent_cast_node):
        # NOTE: Maybe make wfopi between the function input and where it's being used 
        
        # If this name access comes from a return node then we make the opo for the GroMEt FN that this
        # return is in
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
        # node.value - 'beta'
        # node.op - negation (-) 
        if node.op == "USub":
            ref = node.source_refs[0]
            metadata = [self.create_source_code_reference(ref)]
            parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, GrometBoxFunction(name="*", function_type=FunctionType.PRIMITIVE, metadata=metadata))
            parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf)))
            parent_gromet_fn.pif = insert_gromet_object(parent_gromet_fn.pif, GrometPort(box=len(parent_gromet_fn.bf)))
            parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(box=len(parent_gromet_fn.bf)))
            
            val = LiteralValue("Integer", -1)
            parent_gromet_fn.bf = insert_gromet_object(parent_gromet_fn.bf, GrometBoxFunction(function_type=FunctionType.LITERAL, value=val, metadata=metadata))
            parent_gromet_fn.pof = insert_gromet_object(parent_gromet_fn.pof, GrometPort(box=len(parent_gromet_fn.bf)))
            parent_gromet_fn.wff = insert_gromet_object(parent_gromet_fn.wff, GrometWire(src=len(parent_gromet_fn.pif)-1,tgt=len(parent_gromet_fn.pof)-1))
            if isinstance(node.value, AnnCastLiteralValue):
                self.visit(node.value, parent_gromet_fn, parent_cast_node)
                parent_gromet_fn.wff = insert_gromet_object(parent_gromet_fn.wff, GrometWire(src=len(parent_gromet_fn.pif),tgt=len(parent_gromet_fn.pof)))
            elif isinstance(node.value, AnnCastName):
                if parent_gromet_fn.b[0].function_type != FunctionType.FUNCTION:
                    # This check is used for when the unary operation is part of a Function and not an Expression
                    # In which case the Function Def handles creating opis
                    parent_gromet_fn.opi = insert_gromet_object(parent_gromet_fn.opi, GrometPort(name=node.value.name,box=len(parent_gromet_fn.b)))
                    parent_gromet_fn.wfopi = insert_gromet_object(parent_gromet_fn.wfopi, GrometWire(src=len(parent_gromet_fn.pif),tgt=len(parent_gromet_fn.opi)))
                else:
                    # If we are in a function def then we retrieve where the variable is 
                    # Whether it's in the local or the args environment
                    self.wire_from_var_env(node.value.name, parent_gromet_fn)

    @_visit.register
    def visit_var(self, node: AnnCastVar, parent_gromet_fn, parent_cast_node):
        self.visit(node.val, parent_gromet_fn, parent_cast_node)
