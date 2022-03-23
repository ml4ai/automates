from functools import singledispatchmethod
from dataclasses import dataclass
from collections import defaultdict
import copy


import typing

from automates.utils.misc import uuid
from .cast_visitor import CASTVisitor
from automates.program_analysis.CAST2GrFN.visitors.annotated_cast import *


class IdCollapsePass:
    def __init__(self, ann_cast: AnnCast):
        self.ann_cast = ann_cast
        # during the pass, we collpase Name ids to a range starting from zero
        self.old_id_to_collapsed_id = {}
        # this tracks what collapsed ids we have used so far
        print("In IdCollapsePass")
        self.collapsed_id_counter = 0
        for node in self.ann_cast.nodes:
            self.visit(node)
        self.nodes = self.ann_cast.nodes
        self.store_highest_id()

    def store_highest_id(self):
        self.ann_cast.collapsed_id_counter = self.collapsed_id_counter

    def collapse_id(self, id: int) -> int:
        """
        Returns the collapsed id for id if it already exists,
        otherwise creates a collapsed id for it
        """
        if id not in self.old_id_to_collapsed_id:
            self.old_id_to_collapsed_id[id] = self.collapsed_id_counter
            self.collapsed_id_counter += 1

        return self.old_id_to_collapsed_id[id]

    def visit(self, node: AnnCastNode):
        # type(node) is a string which looks like
        # "class '<path.to.class.ClassName>'"
        class_name = str(type(node))
        last_dot = class_name.rfind(".")
        class_name = class_name[last_dot + 1 : -2]
        print(f"\nProcessing node type {class_name}")
        return self._visit(node)

    def visit_node_list(self, node_list: typing.List[AnnCastNode]):
        return [self.visit(node) for node in node_list]

    @singledispatchmethod
    def _visit(self, node: AnnCastNode) -> Dict:
        """
        Visit each AnnCastNode, collapsing AnnCastName ids along the way
        """
        raise Exception(f"Unimplemented AST node of type: {type(node)}")

    @_visit.register
    def visit_assignment(self, node: AnnCastAssignment):
        self.visit(node.right)
        assert isinstance(node.left, AnnCastVar)
        self.visit(node.left)

    @_visit.register
    def visit_attribute(self, node: AnnCastAttribute):
        value = self.visit(node.value)
        attr = self.visit(node.attr)

    @_visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp):
        # visit LHS first
        self.visit(node.left)

        # visit RHS second
        self.visit(node.right)

    @_visit.register
    def visit_boolean(self, node: AnnCastBoolean):
        pass

    @_visit.register
    def visit_call(self, node: AnnCastCall):
        assert isinstance(node.func, AnnCastName)
        node.func.id = self.collapse_id(node.func.id)

        self.visit_node_list(node.arguments)

    @_visit.register
    def visit_class_def(self, node: AnnCastClassDef):
        # Each func is an AnnCastVar node
        self.visit_node_list(node.funcs)

        # Each field (attribute) is an AnnCastVar node
        self.visit_node_list(node.fields)

    @_visit.register
    def visit_dict(self, node: AnnCastDict):
        pass

    @_visit.register
    def visit_expr(self, node: AnnCastExpr):
        self.visit(node.expr)

    @_visit.register
    def visit_function_def(self, node: AnnCastFunctionDef):
        # collapse the function id
        node.name.id = self.collapse_id(node.name.id)
        self.ann_cast.func_id_to_def[node.name.id] = node
        # Each argument is a AnnCastVar node
        # Initialize each Name and add to input_variables
        self.visit_node_list(node.func_args)

        self.visit_node_list(node.body)

    @_visit.register
    def visit_list(self, node: AnnCastList):
        self.visit_node_list(node.values)

    @_visit.register
    def visit_loop(self, node: AnnCastLoop):
        self.visit(node.expr)
        self.visit_node_list(node.body)

    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak):
        pass

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue):
        pass

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf):
        self.visit(node.expr)
        self.visit_node_list(node.body)
        self.visit_node_list(node.orelse)

    @_visit.register
    def visit_return(self, node: AnnCastModelReturn):
        self.visit(node.value)

    @_visit.register
    def visit_module(self, node: AnnCastModule) -> Dict:
        self.visit_node_list(node.body)

    @_visit.register
    def visit_name(self, node: AnnCastName):
        node.id = self.collapse_id(node.id)

    @_visit.register
    def visit_number(self, node: AnnCastNumber):
        pass

    @_visit.register
    def visit_set(self, node: AnnCastSet):
        pass

    @_visit.register
    def visit_string(self, node: AnnCastString):
        pass

    @_visit.register
    def visit_subscript(self, node: AnnCastSubscript):
        pass

    @_visit.register
    def visit_tuple(self, node: AnnCastTuple):
        pass

    @_visit.register
    def visit_unaryop(self, node: AnnCastUnaryOp):
        self.visit(node.value)

    @_visit.register
    def visit_var(self, node: AnnCastVar):
        self.visit(node.val)
