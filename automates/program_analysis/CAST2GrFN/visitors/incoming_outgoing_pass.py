import typing
from collections import defaultdict
from functools import singledispatchmethod
from dataclasses import dataclass
import copy

from automates.program_analysis.CAST2GrFN.visitors.annotated_cast import *

@dataclass
class VariableIdentifier:
    namespace: str
    scope: str
    var_name: str
    index: int
    metadata: List

def merge_vars(incoming_vars: Dict, outgoing_vars: Dict) -> Dict:
    """
    Given the `incoming_vars` to a CAST node, and the `outgoing_vars` from its descendants,
    calculate the outgoing variables to be return to this nodes parent.

    This operation is like an overwriting union i.e. the keys of the returned dict are the union of keys
    from `incoming_vars` and `outgoing_vars`.  The value of each key will be the `Name` node with the highest
    version.
    """
    to_return = {}

    compare_versions = lambda n1, n2: n1 if n1.version > n2.version else n2

    # the update method mutates and returns None, so we call them
    # on seperate lines
    keys = set(incoming_vars.keys())
    keys.update(outgoing_vars.keys())

    for k in keys:
        to_insert = None
        if k in incoming_vars and k in outgoing_vars:
            to_insert = compare_versions(incoming_vars[k], outgoing_vars[k])
        elif k in incoming_vars:
            to_insert = incoming_vars[k]
        else:
            to_insert = outgoing_vars[k]
        to_return[k] = to_insert

    return to_return


def make_grfn_variable(node: AnnCastNode):
    return VariableIdentifier("default_ns", 
                               con_scope_to_str(node.con_scope), 
                               node.name, 
                               node.version,
                               [])

# For DEBUGGING - make a string of the variable dictionary
def mkstr(var_dict):
    s = "{"
    for key, val in var_dict.items():
        s += str(key) + ": (" + val.name + "," + str(val.id) + "," + \
               str(val.con_scope) + " v:" + str(val.version) + "),"
    return s + "}"
 
class IncomingOutgoingPass:
    def __init__(self, ann_cast: AnnCast):
        self.ann_cast = ann_cast
        self.nodes = self.ann_cast.nodes

        # process all nodes
        incoming_vars = {}
        for node in self.ann_cast.nodes:
            outgoing_vars = self.visit(node, incoming_vars)

    def collect_global_variables(self, node: AnnCastModule) -> Dict:
        """
        Returns a dict mapping the variable id to Name node
        for the global variables declared in this module 
        """
        nodes_to_consider = [n for n in node.body if isinstance(n, (AnnCastAssignment, AnnCastVar))]

        def grab_global(n):
            var_node = None
            if isinstance(n, AnnCastAssignment):
                var_node = n.left
            else:
                assert(isinstance(n, AnnCastVar))
                var_node = n
            
            # grab the Name from the AnnCastVar node
            name = var_node.val

            return (name.id, name)

        return dict(map(grab_global, nodes_to_consider))

    def visit(self, node: AnnCastNode, incoming_vars: Dict):
        """
        External visit that calls the internal visit
        Useful for debugging/development.  For example,
        printing the nodes that are visited
        """
        # debug printing
        class_name = node.__class__.__name__
        print(f"\nProcessing node type {class_name}")

        # call internal visit
        return self._visit(node, incoming_vars)

    def visit_node_list(self, node_list: typing.List[AnnCastNode], incoming_vars: Dict):
        outgoing_vars = {}
        for node in node_list:
            outgoing_vars_new = self.visit(node, incoming_vars)
            incoming_vars = merge_vars(incoming_vars, outgoing_vars_new)
            outgoing_vars = merge_vars(outgoing_vars_new, outgoing_vars)

        outgoing_vars = merge_vars(incoming_vars, outgoing_vars)
        return outgoing_vars

    @singledispatchmethod
    def _visit(self, node: AnnCastNode, incoming_vars: Dict):
        """
        Internal visit
        """
        raise NameError(f"Unrecognized node type: {type(node)}")

    @_visit.register
    def visit_assignment(self, node: AnnCastAssignment, incoming_vars: Dict) -> Dict:
        node.incoming_vars = incoming_vars
        # visit RHS first since it may update variables
        outgoing_vars = self.visit(node.right, incoming_vars)
        print(f"in Assignment after visit RHS outgoing_vars: ", mkstr(outgoing_vars))

        lhs = node.left
        assert(isinstance(lhs, AnnCastVar))
        # add the variable id/Name node pair to the outgoing variables
        name_node = lhs.val
        # TODO - this will not always be true, since there may be
        #        an indexed list, parallel assignment w/ tuple, etc, on the LHS
        assert(isinstance(name_node, AnnCastName))

        #TODO - Create the GrFN var and add to the dictionary

        print(f"in Assignment name node on lhs: {name_node.name} {name_node.id}")
        outgoing_vars = merge_vars(outgoing_vars, {name_node.id: name_node})
        print(f"in Assignment after merge outgoing_vars: ", mkstr(outgoing_vars))
        node.outgoing_vars = outgoing_vars

        return node.outgoing_vars

    @_visit.register
    def visit_attribute(self, node: AnnCastAttribute, incoming_vars: Dict):
        pass

    @_visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp, incoming_vars: Dict):
        node.incoming_vars = incoming_vars
        # visit LHS first
        outgoing_vars_left = self.visit(node.left, incoming_vars)
        incoming_vars = merge_vars(incoming_vars, outgoing_vars_left)

        # visit RHS second
        outgoing_vars_right = self.visit(node.right, incoming_vars)
        outgoing_vars = merge_vars(outgoing_vars_left, outgoing_vars_right)
        node.outgoing_vars = outgoing_vars
        return outgoing_vars

    @_visit.register
    def visit_boolean(self, node: AnnCastBoolean, incoming_vars: Dict):
        pass

    @_visit.register
    def visit_call(self, node: AnnCastCall, incoming_vars: Dict):
        pass

    @_visit.register
    def visit_class_def(self, node: AnnCastClassDef, incoming_vars: Dict):
        pass

    @_visit.register
    def visit_dict(self, node: AnnCastDict, incoming_vars: Dict):
        pass

    # TODO - Incomplete. The expr may have side-effects. For now assume it
    #        does not.
    @_visit.register
    def visit_expr(self, node: AnnCastExpr, incoming_vars: Dict):
        node.incoming_vars = incoming_vars
        node.outgoing_vars = {}
        return node.outgoing_vars

    @_visit.register
    def visit_function_def(self, node: AnnCastFunctionDef, incoming_vars: Dict) -> Dict:
        """
        """

        print(f"FunctionDef con_scop: {node.con_scope}")

        # Each argument is a AnnCastVar node
        # create a GrFN VariableIdentifier for each argument
        # and add it to the collection of GrFN variables
        # Also add it to the incoming_vars
        for arg in node.func_args:
            name = arg.val
            incoming_vars[name.id] = name
            self.var_ids_to_grfn_var[name.id] = make_grfn_var(name)
        
        node.incoming_vars = incoming_vars
        print(f"For function {node.name} :incoming_vars = {incoming_vars}")

        outgoing_vars = {}
        for n in node.body:
            print(f"\nbody node :incoming_vars = ", mkstr(incoming_vars))
            outgoing_vars_new = self.visit(n, incoming_vars)
            incoming_vars = merge_vars(incoming_vars, outgoing_vars_new)
            outgoing_vars = merge_vars(outgoing_vars_new, outgoing_vars)
            print(f"\nbody node :outgoing_vars = ", mkstr(outgoing_vars))
            
        outgoing_vars = merge_vars(incoming_vars, outgoing_vars)
        node.outgoing_vars = outgoing_vars
        print(f"After processing function {node.name} :outgoing_vars = ", mkstr(outgoing_vars))
        return outgoing_vars

    @_visit.register
    def visit_list(self, node: AnnCastList, incoming_vars: Dict):
        pass

    @_visit.register
    def visit_loop(self, node: AnnCastLoop, incoming_vars: Dict):
        node.incoming_vars = incoming_vars
        outgoing_vars = self.visit(node.expr, incoming_vars)

        # since the conditional expression may have side-effects,
        # visit it first and update in the incoming variables
        # that will be propagated to the loop body
        incoming_vars  = merge_vars(incoming_vars, outgoing_vars)

        # get the outgoing vars from loop body; the incoming variables
        # should be those obtained from visiting expr
        outgoing_vars = {}
        for n in node.body:
            outgoing_vars_new = self.visit(n, incoming_vars)
            incoming_vars = merge_vars(incoming_vars, outgoing_vars_new)
            outgoing_vars = merge_vars(outgoing_vars_new, outgoing_vars)

        #print("before copying loop body outgoing: ", mkstr(outgoing_vars))

        # If a variable is modified in the loop body, it will appear in the 
        # outgoing variables. Those variables will be connected with the
        # variables in the modified variables attribute.

        # For each variable in the outgoing variables, we create a new
        # Name node with an incremented version of that variable
        # That version will eventually be an output of a GrFN decision node 
        # Store that version in the outgoing_vars field of the loop node
        for k, name_node in outgoing_vars.items():
            new_name = copy.copy(name_node)
            new_name.version += 1
            # TODO - the scope should be changed to the scope of the
            # statement that contains this if (verify).
            new_name.con_scope = node.con_scope[:-1]
            outgoing_vars[k] = new_name

        #print("after  copying loop body outgoing: ", mkstr(outgoing_vars))

        node.outgoing_vars = outgoing_vars

        return node.outgoing_vars

    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak, incoming_vars: Dict):
        pass

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue, incoming_vars: Dict):
        pass

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf, incoming_vars: Dict):

        # We don't really need to save these in an attribute
        node.incoming_vars = incoming_vars

        # TODO
        # set the node.incoming_interface_in to the  incoming_vars

        # TODO
        # For each variable in the union of the modified and accessed vars,
        # create a GrFN var and add it to the collection of GrFN vars
        # These variables will be assgined to node.incoming_interface_out

        # Note: the interface will need to 'connect' the GrFN variables, i.e.,
        #       connect incoming_interface_in to incoming_interfacae_out

        outgoing_vars = self.visit(node.expr, incoming_vars)

        # since the conditional expression may have side-effects,
        # visit it first and update in the incoming variables
        # that will be propagated to the if and else branches
        incoming_vars  = merge_vars(incoming_vars, outgoing_vars)

        # get the outgoing vars on the if branch; the incoming variables
        # should be those obtained from visiting expr
        ifincoming_vars = incoming_vars.copy()
        ifoutgoing_vars = {}
        for n in node.body:
            ifoutgoing_vars_new = self.visit(n, ifincoming_vars)
            ifincoming_vars = merge_vars(ifincoming_vars, ifoutgoing_vars_new)
            ifoutgoing_vars = merge_vars(ifoutgoing_vars_new, ifoutgoing_vars)

        # If a variable is modified in the if block, it will appear in the 
        # ifoutgoing variables. 
        print(f"in If: ifoutgoing_vars: ", mkstr(ifoutgoing_vars))

        # get the outgoing vars on the else branch if it exists; the incoming variables
        # should be those obtained from visiting expr
        elseincoming_vars = incoming_vars.copy()
        elseoutgoing_vars = {}
        for n in node.orelse:
            elseoutgoing_vars_new = self.visit(n, elseincoming_vars)
            elseincoming_vars = merge_vars(elseincoming_vars, elseoutgoing_vars_new)
            elseoutgoing_vars = merge_vars(elseoutgoing_vars_new, elseoutgoing_vars)

        # If a variable is modified in the else block, it will appear in the 
        # elseoutgoing variables. 
        print(f"in If: elseoutgoing_vars: ", mkstr(elseoutgoing_vars))


        # merge the outgoing variables from the if and else branches 
        outgoing_vars = merge_vars(ifoutgoing_vars, elseoutgoing_vars)

        # For each variable in the merged outgoing variables, we create a new
        # Name node with an incremented version of that variable
        # That version will eventually be an output of a GrFN decision node 
        # Store that version in the outgoing_vars field of the if node
        for k, name_node in outgoing_vars.items():
            new_name = copy.copy(name_node)
            new_name.version += 1
            # TODO - the scope should be changed to the scope of the
            # statement that contains this if (verify).
            new_name.con_scope = node.con_scope[:-1]
            outgoing_vars[k] = new_name

        node.outgoing_vars = outgoing_vars

        return node.outgoing_vars
        
    @_visit.register
    def visit_model_return(self, node: AnnCastModelReturn, incoming_vars: Dict):
        node.incoming_vars = incoming_vars
        outgoing_vars =  self.visit(node.value, incoming_vars)
        node.outgoing_vars = outgoing_vars
        return node.outgoing_vars

    @_visit.register
    def visit_module(self, node: AnnCastModule, incoming_vars: Dict):
        node.incoming_vars = incoming_vars

        # process global variable definitions first
        outgoing_vars = {}
        for n in node.body:
            # TODO - Do all globals precede function definitions in the CAST?
            if isinstance(n, AnnCastFunctionDef):
                continue 
            assert(isinstance(n, AnnCastAssignment))
            outgoing_vars_new = self.visit(n, incoming_vars)
            incoming_vars = merge_vars(incoming_vars, outgoing_vars)
            outgoing_vars = merge_vars(outgoing_vars_new, outgoing_vars)
        
        # TODO - correct to add the global variables to the incoming_vars 
        # for all functions?
        incoming_vars = merge_vars(incoming_vars, outgoing_vars)

        # process function definitions
        for n in node.body:
            if not isinstance(n, AnnCastFunctionDef):
                continue
            # process next function definition
            # we don't propagate the outgoing vars accross function definitions 
            outgoing_vars_new = self.visit(n, incoming_vars)

        # TODO - need to address outgoing vars of modules 
        #        this would be relevant for imports
        node.outgoing_vars = outgoing_vars
        return node.outgoing_vars

    @_visit.register
    def visit_name(self, node: AnnCastName, incoming_vars: Dict):
        node.incoming_vars = incoming_vars
        # Name nodes do not update anything
        node.outgoing_vars = {}
        return node.outgoing_vars

    @_visit.register
    def visit_number(self, node: AnnCastNumber, incoming_vars: Dict):
        node.incoming_vars = incoming_vars
        # Number nodes do not update anything
        node.outgoing_vars = {}
        return node.outgoing_vars

    @_visit.register
    def visit_set(self, node: AnnCastSet, incoming_vars: Dict):
        node.incoming_vars = incoming_vars
        # Set nodes do not update anything
        node.outgoing_vars = {}
        return node.outgoing_vars

    @_visit.register
    def visit_string(self, node: AnnCastString, incoming_vars: Dict):
        node.incoming_vars = incoming_vars
        # String nodes do not update anything
        node.outgoing_vars = {}
        return node.outgoing_vars

    @_visit.register
    def visit_subscript(self, node: AnnCastSubscript, incoming_vars: Dict):
        # TODO
        pass

    @_visit.register
    def visit_tuple(self, node: AnnCastTuple, incoming_vars: Dict):
        # TODO
        pass

    @_visit.register
    def visit_unary_op(self, node: AnnCastUnaryOp, incoming_vars: Dict):
        node.incoming_vars = incoming_vars
        node.outgoing_vars = {}
        return node.outgoing_vars

    @_visit.register
    def visit_var(self, node: AnnCastVar, incoming_vars: Dict):
        node.incoming_vars = incoming_vars
        # we do not need to visit the Name node
        node.outgoing_vars = {}
        return node.outgoing_vars
