from functools import singledispatchmethod
from dataclasses import dataclass
from collections import defaultdict
import copy
import typing


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
            self.visit(node, [])
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

    def visit(self, node: AnnCastNode, enclosing_con_scope: typing.List):
        # type(node) is a string which looks like
        # "class '<path.to.class.ClassName>'"
        class_name = str(type(node))
        last_dot = class_name.rfind(".")
        class_name = class_name[last_dot + 1 : -2]
        print(f"\nProcessing node type {class_name}")
        return self._visit(node, enclosing_con_scope)

    @singledispatchmethod
    def _visit(
        self, node: AnnCastNode, enclosing_con_scope: typing.List
    ) -> typing.Dict:
        """
        Visit each AnnCastNode
        """
        raise Exception(f"Unimplemented AST node of type: {type(node)}")

    def visit_node_list(self, node_list: typing.List[AnnCastNode], enclosing_con_scope):
        return [self.visit(node, enclosing_con_scope) for node in node_list]

    @_visit.register
    def visit_assignment(self, node: AnnCastAssignment, enclosing_con_scope):
        # TODO: what if the rhs has side-effects
        self.visit(node.right, enclosing_con_scope)
        assert isinstance(node.left, AnnCastVar)
        self.visit(node.left, enclosing_con_scope)

    @_visit.register
    def visit_attribute(self, node: AnnCastAttribute):
        pass

    @_visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp, enclosing_con_scope):
        # visit LHS first
        self.visit(node.left, enclosing_con_scope)

        # visit RHS second
        self.visit(node.right, enclosing_con_scope)

    @_visit.register
    def visit_boolean(self, node: AnnCastBoolean):
        pass

    @_visit.register
    def visit_call(self, node: AnnCastCall, enclosing_con_scope):
        assert isinstance(node.func, AnnCastName)
        func_name = node.func.name
        node.func.container_scope = enclosing_con_scope
        self.visit_node_list(node.arguments, enclosing_con_scope)

    @_visit.register
    def visit_class_def(self, node: AnnCastClassDef, enclosing_con_scope):
        # We do not visit the name because it is a string
        assert isinstance(node.name, str)
        classscope = enclosing_con_scope + [node.name]
        # node.bases is a list of strings
        # node.funcs is a list of Vars
        self.visit_node_list(node.funcs, classscope)
        # node.fields is a list of Vars
        self.visit_node_list(node.fields, classscope)

    @_visit.register
    def visit_dict(self, node: AnnCastDict):
        pass

    @_visit.register
    def visit_expr(self, node: AnnCastExpr, enclosing_con_scope):
        self.visit(node.expr, enclosing_con_scope)

    @_visit.register
    def visit_function_def(self, node: AnnCastFunctionDef, enclosing_con_scope):
        # Modify scope to include the function name
        funcscope = enclosing_con_scope + [node.name]
        # Each argument is a AnnCastVar node
        # Initialize each Name and visit to modify its scope
        self.visit_node_list(node.func_args, funcscope)

        self.visit_node_list(node.body, funcscope)

    @_visit.register
    def visit_list(self, node: AnnCastList, enclosing_con_scope):
        self.visit_node_list(node.values, enclosing_con_scope)

    @_visit.register
    def visit_loop(self, node: AnnCastLoop, enclosing_con_scope):
        loopscope = self.next_loop_scope(enclosing_con_scope)
        self.visit(node.expr, loopscope)

        loopbodyscope = loopscope + ["loopbody"]
        self.visit_node_list(node.body, loopbodyscope)

    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak):
        pass

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue):
        pass

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf, enclosing_con_scope):
        # want orig enclosing
        # TODO-what if the condition has a side-effect?
        ifscope = self.next_if_scope(enclosing_con_scope)
        self.visit(node.expr, ifscope)

        ifbodyscope = ifscope + ["ifbody"]
        self.visit_node_list(node.body, ifbodyscope)

        orelsebodyscope = ifscope + ["elsebody"]
        self.visit_node_list(node.orelse, orelsebodyscope)

    @_visit.register
    def visit_return(self, node: AnnCastModelReturn, enclosing_con_scope):
        child = node.value
        self.visit(child, enclosing_con_scope)

    @_visit.register
    def visit_module(self, node: AnnCastModule, enclosing_con_scope) -> typing.Dict:
        # Enclosing scope for the module consists of the global variables
        # preceded by the module name, e.g., for globals g1 and g2 in module program, the
        # enclosing scope is initialized as ["program::g1_0", "program::g2_0"]

        # Get each global and add it as version 0 to initialize the
        # the enclosing container scope
        enclosing_con_scope = ["module"]
        self.visit_node_list(node.body, enclosing_con_scope)

    @_visit.register
    def visit_name(self, node: AnnCastName, enclosing_con_scope):
        node.container_scope = enclosing_con_scope

    @_visit.register
    def visit_number(self, node: AnnCastNumber, enclosing_con_scope):
        pass

    @_visit.register
    def visit_set(self, node: AnnCastSet):
        pass

    @_visit.register
    def visit_string(self, node: AnnCastString, enclosing_con_scope):
        pass

    @_visit.register
    def visit_subscript(self, node: AnnCastSubscript):
        pass

    @_visit.register
    def visit_tuple(self, node: AnnCastTuple):
        pass

    @_visit.register
    def visit_unary_op(self, node: AnnCastUnaryOp, enclosing_con_scope):
        self.visit(node.value, enclosing_con_scope)

    @_visit.register
    def visit_var(self, node: AnnCastVar, enclosing_con_scope):
        self.visit(node.val, enclosing_con_scope)
