from functools import singledispatchmethod
from dataclasses import dataclass
from collections import defaultdict
import copy


from typing import Dict

from automates.utils.misc import uuid
from .cast_visitor import CASTVisitor
from automates.program_analysis.CAST2GrFN.visitors.annotated_cast import *

def merge_variables(input_vars: Dict, updated_vars: Dict) -> Dict:
    """
    Given the `input_vars` to a CAST node, and the `updated_vars` from its descendants,
    calculate the updated variables to be stored at this CAST node.

    This operation is like an overwriting union i.e. the keys of the returned dict are the union of keys
    from `input_vars` and `updated_vars`.  The value of each key will be the `Name` node with the highest
    version.
    """
    to_return = {}

    compare_versions = lambda n1, n2: n1 if n1.version > n2.version else n2


    # the update method mutates and returns None, so we call them
    # on seperate lines
    keys = set(input_vars.keys())
    keys.update(updated_vars.keys())

    for k in keys:
        to_insert = None
        # MAYBE: instead of branching, just use highest_variable_version?
        if k in input_vars and k in updated_vars:
            to_insert = compare_versions(input_vars[k], updated_vars[k])
        elif k in input_vars:
            to_insert = input_vars[k]
        else:
            to_insert = updated_vars[k]
        to_return[k] = to_insert

    return to_return

class VariableContext:
    def __init__(self):
        self.highest_variable_version: Dict = defaultdict(lambda: -1)
        self.id_to_ann_name: Dict


class AnnotationsPass:
    def __init__(self, ann_cast: AnnCast):
        # this dict maps Name collapsed numerical ids to the current highest version
        # this will have to depend on scope
        # we will start version numbers at 0
        self.highest_variable_version: Dict = defaultdict(lambda: -1)
        self.ann_cast = ann_cast
        self.module_functions = {}
        # start processing nodes
        input_vars = {}
        for node in self.ann_cast.nodes:
            updated_vars = self.print_then_visit(node, input_vars)

    def collapse_id(self, id:int) -> int:
        """
        Returns the collapsed id for id if it already exists, 
        otherwise creates a collapsed id for it
        """
        if id not in self.old_id_to_collapsed_id:
            self.collapsed_id_counter += 1
            self.old_id_to_collapsed_id[id] = self.collapsed_id_counter
        
        return self.old_id_to_collapsed_id[id]

    def incr_highest_variable_version(self, id: int):
        self.highest_variable_version[id] += 1
        return self.highest_variable_version[id]

    def print_then_visit(self, node: AnnCastNode, input_variables: Dict) -> Dict:
        # type(node) is a string which looks like
        # "class '<path.to.class.ClassName>'"
        class_name = str(type(node))
        last_dot = class_name.rfind(".")
        class_name = class_name[last_dot+1:-2]
        print(f"\nProcessing node type {class_name}")
        input_versions = dict([(k, input_variables[k].version) for k in input_variables.keys()])
        print(f"with input_variables = {input_versions}")
        return self.visit(node, input_variables)

    def collect_function_defs(self, node: AnnCastModule) -> Dict:
        """
        Returns a dict mapping each string function name to
        the FunctionDef node for the functions defined in this 
        Module
        """
        nodes_to_consider = [n for n in node.body if isinstance(n, FunctionDef)]
        make_function = lambda func_def: (func_def.name, func_def)

        return dict(map(make_function, nodes_to_consider))

    def collect_global_variables(self, node: AnnCastModule) -> Dict:
        """
        Returns a dict mapping the string var name to Name node
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
            # visit AnnName node to collapse id
            self.visit(name, {})

            return (name.name, name)

        return dict(map(grab_global, nodes_to_consider))


    @singledispatchmethod
    def visit(self, node: AnnCastNode, input_variables: Dict, enclosing_con_scope: List) -> Dict:
        """
        Visit each AnnCastNode, taking the input_variables, and return updated_variables
        """
        raise Exception(f"Unimplemented AST node of type: {type(node)}")


    @visit.register
    def visit_module(self, node: AnnCastModule, input_variables: Dict) -> Dict:
        node.input_variables = input_variables

        global_vars = self.collect_global_variables(node)
        input_variables = merge_variables(input_variables, global_vars)

        # cache the FunctionDef's defined in this module
        self.module_functions = self.collect_function_defs(node)

        # CLEAN UP: we need to visit global variable assignments, but we only
        # want to visit the main function
        updated_variables = {}
        for n in node.body:
            if isinstance(n, AnnCastFunctionDef) and n.name != "main":
                continue
            updated_variables_new = self.print_then_visit(n, input_variables)
            input_variables = merge_variables(input_variables, updated_variables)
            updated_variables = merge_variables(updated_variables_new, updated_variables)
        
        updated_variables = merge_variables(input_variables, updated_variables)
        node.updated_variables = updated_variables
        return updated_variables


    @visit.register
    def visit_function_def(self, node: AnnCastFunctionDef, input_variables: Dict, enclosing_con_scope: List) -> Dict:
        """
        A FunctionDef is associated with a new container scope. So, we create
        new AnnCastName nodes for every input variable, and every parameter
        of the function
        """

        # Each argument is a AnnCastVar node
        # Initialize each Name and add to input_variables
        for arg in node.func_args:
            name = arg.val
            name.version = -1
            input_variables[name.name] = name
        
        node.input_variables = input_variables
        updated_variables = {}
        for n in node.body:
            updated_variables_new = self.print_then_visit(n, input_variables)
            input_variables = merge_variables(input_variables, updated_variables_new)
            updated_variables = merge_variables(updated_variables_new, updated_variables)
            
        
        updated_variables = merge_variables(input_variables, updated_variables)
        node.updated_variables = updated_variables
        print(f"After processing function {node.name} :updated_variables = {updated_variables}")
        return updated_variables

    @visit.register
    def visit_call(self, node: AnnCastCall, input_variables: Dict) -> Dict:
        node.input_variables = input_variables
        assert(isinstance(node.func, Name))
        # we make a copy of the FunctionDef, and will visit it
        # with inputs_variables being all globals
        # TODO: once globals are correctly identified, remove next line
        # and use the commented one instead
        input_vars_to_func = input_variables
        # input_vars_to_func = dict(filter(lambda pair: pair[1].is_global, input_variables.items()))
        func_name = node.func.name
        node.copied_definition = copy.deepcopy(self.module_functions[func_name])
        updated_variables = self.print_then_visit(node.copied_definition, input_vars_to_func)

        node.updated_variables = updated_variables
        return updated_variables


    @visit.register
    def visit_model_if(self, node: AnnCastModelIf, input_variables: Dict) -> Dict:
        node.input_variables = input_variables

        # we visit expression first, because we need to pass
        # any updated variables to the if/else branches
        # NOTE: The `expr` stored at node is just an `AstNode`, and we do not
        # process enough to visit it.  For now, we will skip it
        # _expr = self.print_then_visit(node.expr, input_variables)
        # input_variables = merge_variables(input_variables, _expr)
        
        # vist nodes in if branch, make a copy of input_variables, since it
        # needs the same input variables need to go in both if and else branches
        # shallow copy is okay here, because we are not mutating values, only keys
        if_branch_input = input_variables.copy()
        ifupdated_vars = {}
        for n in node.body:
            ifupdated_vars_new = self.print_then_visit(n, if_branch_input)
            if_branch_input = merge_variables(if_branch_input, ifupdated_vars_new)
            ifupdated_vars = merge_variables(ifupdated_vars_new, ifupdated_vars)
        _if_branch = ifupdated_vars
        # get the updated vars on the else branch if it exists, the input variables
        # should be those obtained from visiting expr
        else_branch_input = input_variables.copy()
        elseupdated_vars = {}
        for n in node.orelse:
            elseupdated_vars_new = self.print_then_visit(n, else_branch_input)
            else_branch_input = merge_variables(else_branch_input, elseupdated_vars_new)
            elseupdated_vars = merge_variables(elseupdated_vars_new, elseupdated_vars)
        _else_branch = elseupdated_vars

        # For each variable occuring in updated_vars_if_branch or updated_vars_else_branch
        #  we create a new Name node with an incremented version of that variable
        # That version will be an output of a GrFN decision node and store this
        # version in updated_vars field inherited from AstNode

        # the update method mutates and returns None, so we call them
        # on seperate lines
        new_var_keys = set(_if_branch.keys())
        new_var_keys.update(_else_branch.keys())
        updated_vars = {}
        for k in new_var_keys:
            name = None
            if k in _if_branch:
                name = _if_branch[k]
            else:
                name = _else_branch[k]
            new_name = copy.copy(name)
            new_name.version = self.incr_highest_variable_version(name.name)
            updated_vars[k] = new_name

        node.updated_variables = updated_vars

        return updated_vars

    # NOTE: This is incomplete.  If there is a call to a function in the expression
    # it is possible that variables will be mutated, and updated versions need to 
    # be returned.  For now, we just assume that expressions will not change variable 
    # versions.
    @visit.register
    def visit_expr(self, node: AnnCastExpr, input_variables: Dict) -> Dict:
        node.input_variables = input_variables
        updated_vars = {}
        node.updated_variables = updated_vars
        return updated_vars


    @visit.register
    def visit_assignment(self, node: AnnCastAssignment, input_variables: Dict) -> Dict:
        node.input_variables = input_variables

        # visit RHS first, because we may create a new version
        updated_variables = self.print_then_visit(node.right, input_variables)
        
        lhs = node.left
        assert(isinstance(lhs, AnnCastVar))

        var_name = lhs.val
        collapsed_id = self.collapse_id(var_name.id)
        new_version = self.incr_highest_variable_version(collapsed_id)
        print(f"\tNew version of variable {var_name} is {new_version}")
        var_name.version = new_version

        updated_variables = merge_variables(updated_variables, {var_name.name: var_name})
        node.updated_variables = updated_variables
        
        return updated_variables

    @visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp, input_variables: Dict) -> Dict:
        node.input_variables = input_variables

        # visit LHS first
        updated_variables_left = self.print_then_visit(node.left, input_variables)
        input_variables = merge_variables(input_variables, updated_variables_left)

        # visit RHS second
        updated_variables_right = self.print_then_visit(node.right, input_variables)
        updated_variables = merge_variables(updated_variables_left, updated_variables_right)
        
        node.updated_variables = updated_variables
        return updated_variables

    @visit.register
    def visit_return(self, node: AnnCastModelReturn, input_variables: Dict):
        node.input_variables = input_variables
        child = node.value

        updated_vars = self.print_then_visit(child, input_variables)
        node.updated_variables = updated_vars

        return updated_vars


    @visit.register
    def visit_var(self, node: AnnCastVar, input_variables: Dict):
        node.input_variables = input_variables

        # we visit the Name node to collapse its id
        node.updated_variables = self.visit(node.val, input_variables)
        
        return node.updated_variables

    @visit.register
    def visit_name(self, node: AnnCastName, input_variables: Dict):
        node.input_variables = input_variables

        # Name nodes do not update anything
        # but we collapse their id
        node.updated_variables = {}
        node.id = self.collapse_id(node.id)

        return node.updated_variables
        
    @visit.register
    def visit_number(self, node: AnnCastNumber, input_variables: Dict):
        node.input_variables = input_variables

        # Number nodes do no update antying
        updated_vars = {}
        node.updated_variables = updated_vars

        return updated_vars
