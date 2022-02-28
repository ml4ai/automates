from functools import singledispatchmethod
from dataclasses import dataclass
from collections import defaultdict
import copy


from typing import Dict

from automates.utils.misc import uuid
from .cast_visitor import CASTVisitor
from automates.program_analysis.CAST2GrFN.visitors.annotated_cast import *

class ContainerScopePass:
    def __init__(self, ann_cast: AnnCast):
        self.ann_cast = ann_cast
        # some state variables possibly
        # e.g. how many ifs/loops we've seen in current scope
        self.if_count = 0
        self.loop_count = 0
        for node in self.ann_cast.nodes:
            self.print_then_visit(node,[])
        self.nodes = self.ann_cast.nodes

    def print_then_visit(self, node: AnnCastNode, enclosing_con_scope: List):
        # type(node) is a string which looks like
        # "class '<path.to.class.ClassName>'"
        class_name = str(type(node))
        last_dot = class_name.rfind(".")
        class_name = class_name[last_dot+1:-2]
        print(f"\nProcessing node type {class_name}")
        return self.visit(node,enclosing_con_scope)


    @singledispatchmethod
    def visit(self, node: AnnCastNode, enclosing_con_scope: List) -> Dict:
        """
        Visit each AnnCastNode
        """
        raise Exception(f"Unimplemented AST node of type: {type(node)}")


    @visit.register
    def visit_module(self, node: AnnCastModule, enclosing_con_scope) -> Dict:
        # Enclosing scope for the module consists of the global variables
        # preceded by the module name, e.g., for globals g1 and g2 in module program, the
        # enclosing scope is initialized as ["program::g1_0", "program::g2_0"]

        # Get each global and add it as version 0 to initialize the 
        # the enclosing container scope
        enclosing_con_scope = [f"{node.name}::"]
        for n in node.body:
                if n.isinstance(Assignment):
                    updated_variables_new = self.print_then_visit(n, enclosing_con_scope)

    @visit.register
    def visit_function_def(self, node: AnnCastFunctionDef, enclosing_con_scope):
        # Each argument is a AnnCastVar node
        # Initialize each Name and add to input_variables
        for arg in node.func_args:
            self.print_then_visit(arg, enclosing_con_scope)
        
        for n in node.body:
            updated_variables_new = self.print_then_visit(n, enclosing_con_scope)
            
    @visit.register
    def visit_call(self, node: AnnCastCall, enclosing_con_scope):
        # CHECK: nothing to do here?
        assert(isinstance(node.func, Name))
        func_name = node.func.name

    @visit.register
    def visit_model_if(self, node: AnnCastModelIf, enclosing_con_scope):
        # For each variable in enclosing_con_scope
        for n in node.body:
            self.print_then_visit(n, enclosing_con_scope)
        for n in node.orelse:
            self.print_then_visit(n, enclosing_con_scope)
            
    @visit.register
    def visit_expr(self, node: AnnCastExpr, enclosing_con_scope):
        self.print_then_visit(node.expr, enclosing_con_scope)


    @visit.register
    def visit_assignment(self, node: AnnCastAssignment, enclosing_con_scope):
        output_variables = self.print_then_visit(node.right, enclosing_con_scope)
        assert(isinstance(node.left, AnnCastVar))
        output_variables = self.print_then_visit(node.left, enclosing_con_scope)

    @visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp, enclosing_con_scope):
        # visit LHS first
        self.print_then_visit(node.left, enclosing_con_scope)

        # visit RHS second
        self.print_then_visit(node.right, enclosing_con_scope)

    @visit.register
    def visit_return(self, node: AnnCastModelReturn, enclosing_con_scope):
        child = node.value
        self.print_then_visit(child, enclosing_con_scope)

    @visit.register
    def visit_var(self, node: AnnCastVar, enclosing_con_scope):
        self.visit(node.val, enclosing_con_scope)
        
    @visit.register
    def visit_name(self, node: AnnCastName, enclosing_con_scope):
        node.id = self.collapse_id(node.id)
        
    @visit.register
    def visit_number(self, node: AnnCastNumber, enclosing_con_scope):
        pass



