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
        self.if_count = defaultdict(int)
        self.loop_count = defaultdict(int)
        for node in self.ann_cast.nodes:
            self.print_then_visit(node,[])
        self.nodes = self.ann_cast.nodes

    def next_if_scope(self, enclosing_con_scope):
        scopestr = "".join(enclosing_con_scope)
        count = self.if_count[scopestr]
        self.if_count[scopestr] += 1
        return enclosing_con_scope + [f"if{count}"]

    def next_loop_scope(self, enclosing_con_scope):
        scopestr = "".join(enclosing_con_scope)
        count = self.loop_count[scopestr]
        self.loop_count[scopestr] += 1
        return enclosing_con_scope + [f"loop{count}"]

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
        enclosing_con_scope = ["module"]
        for n in node.body:
            self.print_then_visit(n, enclosing_con_scope)

    @visit.register
    def visit_function_def(self, node: AnnCastFunctionDef, enclosing_con_scope):
        # Modify scope to include the function name
        funcscope = enclosing_con_scope + [node.name]
        # Each argument is a AnnCastVar node
        # Initialize each Name and visit to modify its scope
        for arg in node.func_args:
            self.print_then_visit(arg, funcscope)
        
        for n in node.body:
            self.print_then_visit(n, funcscope)
            
    @visit.register
    def visit_call(self, node: AnnCastCall, enclosing_con_scope):
        assert(isinstance(node.func, AnnCastName))
        func_name = node.func.name
        node.func.container_scope = enclosing_con_scope
        for n in node.arguments:
            self.print_then_visit(n, enclosing_con_scope)

    @visit.register
    def visit_class_def(self, node: AnnCastClassDef, enclosing_con_scope):
        # We do not visit the name because it is a string
        assert(isinstance(node.name, str))
        # node.bases is a list of strings
        # node.funcs is a list of Vars
        for n in node.funcs:
            self.print_then_visit(n, enclosing_con_scope)
        # node.fields is a list of Vars
        for n in node.fields:
            self.print_then_visit(n, enclosing_con_scope)

    @visit.register
    def visit_model_if(self, node: AnnCastModelIf, enclosing_con_scope):
        # want orig enclosing
        # TODO-what if the condition has a side-effect?
        ifscope = self.next_if_scope(enclosing_con_scope)
        self.print_then_visit(node.expr, ifscope) 

        ifbodyscope = ifscope + ["ifbody"]

        # [" module", "func1", "if0", "ifbody"]
        for n in node.body:
            self.print_then_visit(n, ifbodyscope)

        # [" module", "func1", "if0", "elsebody"]
        orelsebodyscope = ifscope + ["elsebody"]
        for n in node.orelse:
            self.print_then_visit(n, orelsebodyscope)

    @visit.register
    def visit_list(self, node: AnnCastList, enclosing_con_scope):
        for n in node.values:
            self.print_then_visit(n, enclosing_con_scope)

    @visit.register
    def visit_loop(self, node: AnnCastLoop, enclosing_con_scope):
        loopscope = self.next_loop_scope(enclosing_con_scope)
        self.print_then_visit(node.expr, loopscope)

        # [" module", "func1", "loop0", "loopbody"]
        loopbodyscope = loopscope + ["loopbody"]
        for n in node.body:
            self.print_then_visit(n, loopbodyscope)
            
    @visit.register
    def visit_expr(self, node: AnnCastExpr, enclosing_con_scope):
        self.print_then_visit(node.expr, enclosing_con_scope)

    @visit.register
    def visit_assignment(self, node: AnnCastAssignment, enclosing_con_scope):
        # TODO: what if the rhs has side-effects
        self.print_then_visit(node.right, enclosing_con_scope)
        assert(isinstance(node.left, AnnCastVar))
        self.print_then_visit(node.left, enclosing_con_scope)

    @visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp, enclosing_con_scope):
        # visit LHS first
        self.print_then_visit(node.left, enclosing_con_scope)

        # visit RHS second
        self.print_then_visit(node.right, enclosing_con_scope)

    @visit.register
    def visit_unary_op(self, node: AnnCastUnaryOp, enclosing_con_scope):
        self.print_then_visit(node.value, enclosing_con_scope)
 
    @visit.register
    def visit_return(self, node: AnnCastModelReturn, enclosing_con_scope):
        child = node.value
        self.print_then_visit(child, enclosing_con_scope)

    @visit.register
    def visit_var(self, node: AnnCastVar, enclosing_con_scope):
        self.print_then_visit(node.val, enclosing_con_scope)
        
    @visit.register
    def visit_name(self, node: AnnCastName, enclosing_con_scope):
        node.container_scope = enclosing_con_scope

    @visit.register
    def visit_str(self, node: AnnCastString, enclosing_con_scope):
        pass
        
    @visit.register
    def visit_number(self, node: AnnCastNumber, enclosing_con_scope):
        pass



