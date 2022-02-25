from functools import singledispatchmethod
from dataclasses import dataclass
from collections import defaultdict
import copy


from typing import Dict

from automates.utils.misc import uuid
from .cast_visitor import CASTVisitor
from automates.program_analysis.CAST2GrFN.visitors.annotated_cast import *

class IdCollapsePass:
    def __init__(self, ann_cast: AnnCast):
        self.ann_cast = ann_cast
        # during the pass, we collpase Name ids to a range starting from zero
        self.old_id_to_collapsed_id = {}
        # this tracks what collapsed ids we have used so far
        self.collapsed_id_counter = 0
        for node in self.ann_cast.nodes:
            self.print_then_visit(node)
        self.nodes = self.ann_cast.nodes

    def collapse_id(self, id:int) -> int:
        """
        Returns the collapsed id for id if it already exists, 
        otherwise creates a collapsed id for it
        """
        if id not in self.old_id_to_collapsed_id:
            self.old_id_to_collapsed_id[id] = self.collapsed_id_counter
            self.collapsed_id_counter += 1
        
        return self.old_id_to_collapsed_id[id]

    def print_then_visit(self, node: AnnCastNode):
        # type(node) is a string which looks like
        # "class '<path.to.class.ClassName>'"
        class_name = str(type(node))
        last_dot = class_name.rfind(".")
        class_name = class_name[last_dot+1:-2]
        print(f"\nProcessing node type {class_name}")
        return self.visit(node)


    @singledispatchmethod
    def visit(self, node: AnnCastNode) -> Dict:
        """
        Visit each AnnCastNode, collapsing AnnCastName ids along the way
        """
        raise Exception(f"Unimplemented AST node of type: {type(node)}")


    @visit.register
    def visit_module(self, node: AnnCastModule) -> Dict:
        for n in node.body:
            updated_variables_new = self.print_then_visit(n)

    @visit.register
    def visit_function_def(self, node: AnnCastFunctionDef):
        # Each argument is a AnnCastVar node
        # Initialize each Name and add to input_variables
        for arg in node.func_args:
            self.print_then_visit(arg)
        
        for n in node.body:
            updated_variables_new = self.print_then_visit(n)
            
    @visit.register
    def visit_call(self, node: AnnCastCall):
        # CHECK: nothing to do here?
        assert(isinstance(node.func, Name))
        func_name = node.func.name

    @visit.register
    def visit_model_if(self, node: AnnCastModelIf):
        for n in node.body:
            self.print_then_visit(n)
        for n in node.orelse:
            self.print_then_visit(n)

    @visit.register
    def visit_expr(self, node: AnnCastExpr):
        self.print_then_visit(node.expr)


    @visit.register
    def visit_assignment(self, node: AnnCastAssignment):
        self.print_then_visit(node.right)
        assert(isinstance(node.left, AnnCastVar))
        self.print_then_visit(node.left)

    @visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp):
        # visit LHS first
        self.print_then_visit(node.left)

        # visit RHS second
        self.print_then_visit(node.right)

    @visit.register
    def visit_return(self, node: AnnCastModelReturn):
        child = node.value
        self.print_then_visit(child)

    @visit.register
    def visit_var(self, node: AnnCastVar):
        self.visit(node.val)
        
    @visit.register
    def visit_name(self, node: AnnCastName):
        node.id = self.collapse_id(node.id)
        
    @visit.register
    def visit_number(self, node: AnnCastNumber):
        pass



