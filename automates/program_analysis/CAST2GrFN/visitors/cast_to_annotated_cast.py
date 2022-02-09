from functools import singledispatchmethod
from dataclasses import dataclass
from collections import defaultdict

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

class CASTToAIRVisitor:
    def __init__(self, cast: CAST):
        # we will start variable versions at -1 for now
        self.highest_variable_version: Dict[str, int] = defaultdict(lambda: -2)
        self.cast = cast

    @singledispatchmethod
    def visit(self, node: AstNode, input_variables: Dict) -> Dict:
        """
        Visit each AstNode, taking the input_variables, and return output_variables
        """
        raise C2ATypeError(f"Unimplemented AST node of type: {type(node)}")

    @visit.register
    def visit_module(self, node: Module, input_variables: Dict) -> Dict:
        # NOTE: we believe we can identify global variables during CAST creation, and store that in
        # is_global field of Name nodes
        # if not, iterate over Var/Assignment nodes like in cast_to_air_visitor.py

        node._input_variables = input_variables

        for n in node.body:
            updated_variables = self.visit(n, input_variables)
            input_variables = combine_input_and_output_vars(input_variables, updated_variables)
        
        updated_variables = combine_input_and_output_vars(input_variables, updated_variables)
        node.updated_variables = updated_variables
        return updated_variables


    def visit_function_def(self, node: FunctionDef, input_variables: Dict) -> Dict:
        # Each argument is a Var node
        # Initialize each Name and add to input_variables
        for arg in node.func_args:
            name = arg.val
            name.version = -1
            input_variables[name.name] = name
        
        node._input_variables = input_variables

        for n in node.body:
            updated_variables = self.visit(n, input_variables)
            input_variables = combine_input_and_output_vars(input_variables, updated_variables)
            
        
        updated_variables = combine_input_and_output_vars(input_variables, updated_variables)
        node.updated_variables = updated_variables
        return updated_variables

    def visit_assignment(self, node: Assignment, input_variables: Dict) -> Dict:
        self.node._input_variables = input_variables

        # visit RHS first, because we may create a new version
        updated_variables = self.visit(node.right, input_variables)
        updated_variables = combine_input_and_output_vars(input_variables, output_variables)
        

        lhs = node.left
        assert(isinstance(lhs, Var))

        var_name = lhs.val
        new_version = self.highest_variable_version[var_name.name] + 1
        self.highest_variable_version[var_name.name] = new_version
        var_name.version = new_version

        updated_variables = combine_input_and_output_vars(updated_variables, {var_name.name: var_name})
        node._updated_variables = updated_variables
        
        return updated_variables

    





