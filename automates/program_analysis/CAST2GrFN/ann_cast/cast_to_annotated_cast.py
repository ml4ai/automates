from functools import singledispatchmethod
import typing

from automates.program_analysis.CAST2GrFN.cast import CAST

from automates.program_analysis.CAST2GrFN.model.cast import (
    AstNode,
    Assignment,
    Attribute,
    BinaryOp,
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
    Subscript,
    Tuple,
    UnaryOp,
    Var,
)

from automates.program_analysis.CAST2GrFN.ann_cast.annotated_cast import *

class CASTTypeError(TypeError):
    """Used to create errors in the visitor, in particular
    when the visitor encounters some value that it wasn't expecting.

    Args:
        Exception: An exception that occurred during execution.
    """

class CastToAnnotatedCastVisitor():
    '''
    class CastToAnnotatedCastVisitor - A visitor that traverses CAST nodes
    and generates an annotated cast version of the CAST.

    The AnnCastNodes have additional attributes (fields) that are used
    in a later pass to maintain scoping information for GrFN containers.
    '''

    def __init__(self, cast: CAST):
        self.cast = cast

    def visit_node_list(self, node_list: typing.List[AstNode]):
        return [self.visit(node) for node in node_list]

    def generate_annotated_cast(self, grfn_2_2: bool=False):
        nodes = self.cast.nodes

        annotated_cast = []
        for node in nodes:
            annotated_cast.append(self.visit(node))

        return PipelineState(annotated_cast, grfn_2_2)

    def visit(self, node: AstNode) -> AnnCastNode:
        # print current node being visited.  
        # this can be useful for debugging 
        class_name = node.__class__.__name__
        print(f"\nProcessing node type {class_name}")
        return self._visit(node)

    @singledispatchmethod
    def _visit(self, node: AstNode):
        raise NameError(f"Unrecognized node type: {type(node)}")

    @_visit.register
    def visit_assignment(self, node: Assignment):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return AnnCastAssignment(left, right, node.source_refs)

    @_visit.register
    def visit_attribute(self, node: Attribute):
        value = self.visit(node.value)
        attr  = self.visit(node.attr)
        return AnnCastAttribute(value, attr, node.source_refs)

    @_visit.register
    def visit_binary_op(self, node: BinaryOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return AnnCastBinaryOp(node.op, left, right, node.source_refs)

    @_visit.register
    def visit_boolean(self, node: Boolean):
        boolean = node.boolean
        if boolean is not None:
            boolean = self.visit(boolean)
        return AnnCastBoolean(boolean, node.source_refs)

    @_visit.register
    def visit_call(self, node: Call):
        func = self.visit(node.func)
        arguments = self.visit_node_list(node.arguments)

        return AnnCastCall(func, arguments, node.source_refs)


    @_visit.register
    def visit_class_def(self, node: ClassDef):
        funcs = self.visit_node_list(node.funcs)
        fields = self.visit_node_list(node.fields)
        return AnnCastClassDef(node.name, node.bases, funcs, fields, node.source_refs)

    @_visit.register
    def visit_dict(self, node: Dict):
        keys = self.visit_node_list(node.keys)
        values = self.visit_node_list(node.values)
        return AnnCastDict(keys, values, node.source_refs)

    @_visit.register
    def visit_expr(self, node: Expr):
        expr = self.visit(node.expr)
        return AnnCastExpr(expr, node.source_refs)

    @_visit.register
    def visit_function_def(self, node: FunctionDef):
        name = node.name
        args = self.visit_node_list(node.func_args)
        body = self.visit_node_list(node.body)
        return AnnCastFunctionDef(name, args, body, node.source_refs)
        
    @_visit.register
    def visit_list(self, node: List):
        values = self.visit_node_list(node.values)
        return AnnCastList(values, node.source_refs)

    @_visit.register
    def visit_loop(self, node: Loop):
        expr = self.visit(node.expr)
        body = self.visit_node_list(node.body)
        return AnnCastLoop(expr,body, node.source_refs)

    @_visit.register
    def visit_model_break(self, node: ModelBreak):
        return AnnCastModelBreak(node.source_refs)

    @_visit.register
    def visit_model_continue(self, node: ModelContinue):
        return AnnCastModelContinue(node.source_refs)

    @_visit.register
    def visit_model_if(self, node: ModelIf):
        expr = self.visit(node.expr)
        body = self.visit_node_list(node.body)
        orelse = self.visit_node_list(node.orelse)
        return AnnCastModelIf(expr, body, orelse, node.source_refs)

    @_visit.register
    def visit_model_return(self, node: ModelReturn):
        value = self.visit(node.value)
        return AnnCastModelReturn(value, node.source_refs)
        
    @_visit.register
    def visit_module(self, node: Module):
        body = self.visit_node_list(node.body)
        return AnnCastModule(node.name, body, node.source_refs)

    @_visit.register
    def visit_name(self, node: Name):
        return AnnCastName(node.name, node.id, node.source_refs)

    @_visit.register
    def visit_number(self, node: Number):
        return AnnCastNumber(node.number, node.source_refs)

    @_visit.register
    def visit_set(self, node: Set):
        values = self.visit_node_list(node.values)
        return AnnCastSet(values, node.source_refs)

    @_visit.register
    def visit_string(self, node: String):
        return AnnCastString(node.string, node.source_refs)

    @_visit.register
    def visit_subscript(self, node: Subscript):
        value = self.visit(node.value)
        slice = self.visit(node.slice)
        return AnnCastSubscript(value, slice, node.source_refs)

    @_visit.register
    def visit_tuple(self, node: Tuple):
        values = self.visit_node_list(node.values)
        return AnnCastTuple(values, node.source_refs)

    @_visit.register
    def visit_unary_op(self, node: UnaryOp):
        value = self.visit(node.value)
        return AnnCastUnaryOp(node.op, value, node.source_refs)

    @_visit.register
    def visit_var(self, node: Var):
        val = self.visit(node.val)
        return AnnCastVar(val, node.type, node.source_refs)
