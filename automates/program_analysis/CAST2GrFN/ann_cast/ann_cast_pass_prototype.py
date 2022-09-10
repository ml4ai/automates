from functools import singledispatchmethod
import typing

from automates.program_analysis.CAST2GrFN.ann_cast.annotated_cast import *


class AnnCastPass:
    def __init__(self, ann_cast: AnnCast):
        self.ann_cast = ann_cast
        self.nodes = self.ann_cast.nodes
        # Any other state variables that are needed during
        # the pass
        for node in self.ann_cast.nodes:
            self.visit(node)

    def visit(self, node: AnnCastNode):
        """
        External visit that calls the internal visit
        Useful for debugging/development.  For example,
        printing the nodes that are visited
        """
        # print current node being visited.  
        # this can be useful for debugging 
        # class_name = node.__class__.__name__
        # print(f"\nProcessing node type {class_name}")

        # call internal visit
        return self._visit(node)

    def visit_node_list(self, node_list: typing.List[AnnCastNode]):
        return [self.visit(node) for node in node_list]

    @singledispatchmethod
    def _visit(self, node: AnnCastNode):
        """
        Internal visit
        """
        raise NameError(f"Unrecognized node type: {type(node)}")

    @_visit.register
    def visit_assignment(self, node: AnnCastAssignment):
        pass

    @_visit.register
    def visit_attribute(self, node: AnnCastAttribute):
        pass

    @_visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp):
        pass

    @_visit.register
    def visit_boolean(self, node: AnnCastBoolean):
        pass

    @_visit.register
    def visit_call(self, node: AnnCastCall):
        pass

    @_visit.register
    def visit_class_def(self, node: AnnCastClassDef):
        pass

    @_visit.register
    def visit_dict(self, node: AnnCastDict):
        pass

    @_visit.register
    def visit_expr(self, node: AnnCastExpr):
        pass

    @_visit.register
    def visit_function_def(self, node: AnnCastFunctionDef):
        pass

    @_visit.register
    def visit_list(self, node: AnnCastList):
        pass

    @_visit.register
    def visit_loop(self, node: AnnCastLoop):
        pass

    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak):
        pass

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue):
        pass

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf):
        pass

    @_visit.register
    def visit_model_return(self, node: AnnCastModelReturn):
        pass

    @_visit.register
    def visit_module(self, node: AnnCastModule):
        pass

    @_visit.register
    def visit_name(self, node: AnnCastName):
        pass

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
    def visit_unary_op(self, node: AnnCastUnaryOp):
        pass

    @_visit.register
    def visit_var(self, node: AnnCastVar):
        pass
