from functools import singledispatchmethod
from dataclasses import dataclass
from collections import defaultdict
import copy


from typing import Dict

from automates.utils.misc import uuid
from .cast_visitor import CASTVisitor
from automates.program_analysis.CAST2GrFN.cast import CAST
from automates.program_analysis.CAST2GrFN.model.cast import (
    AstNode,
    Assignment,
    Attribute,
    BinaryOp,
    BinaryOperator,
    Boolean,
    Call,
    ClassDef,
    Dict,
    Expr,
    FunctionDef,
    List,
    Loop,
    ModelBreak,
    ModelContinue,
    ModelIf,
    ModelReturn,
    Module,
    Name,
    Number,
    Set,
    String,
    SourceRef,
    Subscript,
    Tuple,
    UnaryOp,
    UnaryOperator,
    VarType,
    Var,
)

def combine_input_and_updated_vars(input_vars: Dict, updated_vars: Dict) -> Dict:
    """
    Given the `input_vars` to a CAST node, and the `updated_vars` from its descendants,
    calculate the updated variables to be stored at this CAST node.

    This operation is like an overwriting union i.e. the keys of the returned dict are the union of keys
    from `input_vars` and `updated_vars`.  The value of each key will be the `Name` node with the highest
    version.
    """
    to_return = {}

    compare_versions = lambda n1, n2: n1 if n1.version > n2.version else n2


    # if you do the call to update on the same line, it can result in NoneType if 
    # there are no keys
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


class CastToAnnotatedCast:
    def __init__(self, cast: CAST):
        # we will start variable versions at -1 for now
        self.highest_variable_version: Dict = defaultdict(lambda: -2)
        self.cast = cast
        # start processing nodes
        input_vars = {}
        for node in cast.nodes:
            updated_vars = self.print_then_visit(node, input_vars)


    def print_then_visit(self, node: AstNode, input_variables: Dict) -> Dict:
        print(f"Processing node type {type(node)}")
        return self.visit(node, input_variables)


    @singledispatchmethod
    def visit(self, node: AstNode, input_variables: Dict) -> Dict:
        """
        Visit each AstNode, taking the input_variables, and return updated_variables
        """
        raise Exception(f"Unimplemented AST node of type: {type(node)}")


    @visit.register
    def visit_module(self, node: Module, input_variables: Dict) -> Dict:
        # NOTE: we believe we can identify global variables during CAST creation, and store that in
        # is_global field of Name nodes
        # if not, iterate over Var/Assignment nodes like in cast_to_air_visitor.py
        node._input_variables = input_variables

        for n in node.body:
            updated_variables = self.print_then_visit(n, input_variables)
            input_variables = combine_input_and_updated_vars(input_variables, updated_variables)
        
        updated_variables = combine_input_and_updated_vars(input_variables, updated_variables)
        node.updated_variables = updated_variables
        return updated_variables


    @visit.register
    def visit_function_def(self, node: FunctionDef, input_variables: Dict) -> Dict:
        # Each argument is a Var node
        # Initialize each Name and add to input_variables
        for arg in node.func_args:
            name = arg.val
            name.version = -1
            input_variables[name.name] = name
        
        node._input_variables = input_variables

        for n in node.body:
            updated_variables = self.print_then_visit(n, input_variables)
            input_variables = combine_input_and_updated_vars(input_variables, updated_variables)
            
        
        updated_variables = combine_input_and_updated_vars(input_variables, updated_variables)
        node.updated_variables = updated_variables
        print(f"After processing function {node.name} updated_variables = {updated_variables}")
        return updated_variables

    @visit.register
    def visit_model_if(self, node: ModelIf, input_variables: Dict) -> Dict:
        node._input_variables = input_variables

        # we visit expression first, because we need to pass
        # any updated variables to the if/else branches
        # NOTE: The `expr` stored at node is just an `AstNode`, and we do not
        # process enough to visit it.  For now, we will skip it
        # node.updated_vars_expr = self.print_then_visit(node.expr, input_variables)
        # input_variables = combine_input_and_updated_vars(input_variables, node.updated_vars_expr)
        
        # vist nodes in if branch, make a copy of input_variables, since it
        # needs the same input variables need to go in both if and else branches
        # shallow copy is okay here, because we are not mutating values, only keys
        if_branch_input = input_variables.copy()
        if_updated_vars = {}
        for n in node.body:
            if_updated_vars = self.print_then_visit(n, if_branch_input)
            if_branch_input = combine_input_and_updated_vars(if_branch_input, if_updated_vars)
        node.updated_vars_if_branch = if_updated_vars
        # get the updated vars on the else branch if it exists, the input variables
        # should be those obtained from visiting expr
        else_branch_input = input_variables.copy()
        else_updated_vars = {}
        for n in node.orelse:
            else_updated_vars = self.print_then_visit(n, else_branch_input)
            else_branch_input = combine_input_and_updated_vars(else_branch_input, else_updated_vars)
        node.updated_vars_else_branch = else_updated_vars

        # For each variable occuring in updated_vars_if_branch or updated_vars_else_branch
        #  we create a new Name node with an incremented version of that variable
        # That version will be an output of a GrFN decision node and store this
        # version in updated_vars field inherited from AstNode

        # if you do the call to update on the same line, it can result in NoneType if 
        # there are no keys
        new_var_keys = set(node.updated_vars_if_branch.keys())
        new_var_keys.update(node.updated_vars_else_branch.keys())
        updated_vars = {}
        for k in new_var_keys:
            name = None
            if k in node.updated_vars_if_branch:
                name = node.updated_vars_if_branch[k]
            else:
                name = node.updated_vars_else_branch[k]
            new_name = copy.copy(name)
            new_name.version = self.highest_variable_version[k] + 1
            updated_vars[k] = new_name

        node._updated_variables = updated_vars

        return updated_vars

    # NOTE: This is incomplete.  If there is a call to a function in the expression
    # it is possible that variables will be mutated, and updated versions need to 
    # be returned.  For now, we just assume that expressions will not change variable 
    # versions.
    @visit.register
    def visit_expr(self, node: Expr, input_variables: Dict) -> Dict:
        node._input_variables = input_variables
        updated_vars = {}
        node._updated_variables = updated_vars
        return updated_vars


    @visit.register
    def visit_assignment(self, node: Assignment, input_variables: Dict) -> Dict:
        node._input_variables = input_variables

        # visit RHS first, because we may create a new version
        updated_variables = self.print_then_visit(node.right, input_variables)
        updated_variables = combine_input_and_updated_vars(input_variables, updated_variables)
        

        lhs = node.left
        assert(isinstance(lhs, Var))

        var_name = lhs.val
        new_version = self.highest_variable_version[var_name.name] + 1
        print(f"\tNew version of variable {var_name} is {new_version}")
        self.highest_variable_version[var_name.name] = new_version
        var_name.version = new_version

        updated_variables = combine_input_and_updated_vars(updated_variables, {var_name.name: var_name})
        node._updated_variables = updated_variables
        
        return updated_variables

    @visit.register
    def visit_binary_op(self, node: BinaryOp, input_variables: Dict) -> Dict:
        node._input_variables = input_variables

        # visit LHS first
        updated_variables = self.print_then_visit(node.right, input_variables)
        updated_variables = combine_input_and_updated_vars(input_variables, updated_variables)

        # visit RHS second
        updated_variables = self.print_then_visit(node.right, input_variables)
        updated_variables = combine_input_and_updated_vars(input_variables, updated_variables)
        
        node._updated_variables = updated_variables
        return updated_variables

    @visit.register
    def visit_return(self, node: ModelReturn, input_variables: Dict):
        node._input_variables = input_variables
        child = node.value

        updated_vars = self.print_then_visit(child, input_variables)
        node._updated_variables = updated_vars

        return updated_vars


    @visit.register
    def visit_var(self, node: Var, input_variables: Dict):
        node._input_variables = input_variables

        # we believe Var nodes do not update anything 
        updated_vars = {}
        node._updated_variables = updated_vars

        # we will not visit the associated Name and VarType nodes
        # since they also do not update anything
        
        return updated_vars

    @visit.register
    def visit_name(self, node: Name, input_variables: Dict):
        node._input_variables = input_variables

        # Name nodes do not update anything
        updated_vars = {}
        node._updated_variables = updated_vars

        return updated_vars
        
    @visit.register
    def visit_number(self, node: Number, input_variables: Dict):
        node._input_variables = input_variables

        # Number nodes do no update antying
        updated_vars = {}
        node._updated_variables = updated_vars

        return updated_vars



