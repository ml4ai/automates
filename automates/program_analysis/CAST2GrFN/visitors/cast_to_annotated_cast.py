from functools import singledispatchmethod
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

from .annotated_cast import *

class CASTTypeError(TypeError):
    """Used to create errors in the visitor, in particular
    when the visitor encounters some value that it wasn't expecting.

    Args:
        Exception: An exception that occurred during execution.
    """
    pass


class CastToAnnotatedCastVisitor(CASTVisitor):
    '''
    class CastToAnnotatedCastVisitor - A visitor that traverses CAST nodes
    and generates an annotated cast version of the CAST.

    The AnnotatedCastNodes have additional attributes (fields) that are used
    in a later pass to maintain scoping information for GrFN containers.
    '''

    def __init__(self, cast: CAST):
        self.cast = cast

    def generate_annotated_cast(self):
        nodes = self.cast.nodes
        print(len(nodes))
        print("top nodes are:")
        for node in nodes:
            class_name = str(type(node))
            last_dot = class_name.rfind(".")
            print(f"\nnode type {class_name}")

        annotated_cast = []
        for node in nodes:
            annotated_cast.append(self.print_then_visit(node))

        return annotated_cast


    def print_then_visit(self, node: AstNode) -> AnnotatedCastNode:
        # type(node) is a string which looks like
        # "class '<path.to.class.ClassName>'"
        class_name = str(type(node))
        last_dot = class_name.rfind(".")
        class_name = class_name[last_dot+1:-2]
        print(f"\nProcessing node type {class_name}")
        return self.visit(node)

    @singledispatchmethod
    def visit(self, node: AstNode):
        raise NameError(f"Unrecognized node type: {type(node)}")

    @visit.register
    def _(self, node: Assignment):
        left = self.print_then_visit(node.left)
        right = self.print_then_visit(node.right)
        return AnnotatedCastAssignment(left, right, node.source_refs)

    @visit.register
    def _(self, node: Attribute):
        #TODO: Is the attr considered a variable?
        value = self.print_then_visit(node.value)
        attr  = self.print_then_visit(node.attr)
        return AnnotatedCastAttribute(value, attr, node.source_refs)

    @visit.register
    def _(self, node: BinaryOp):
        left = self.print_then_visit(node.left)
        right = self.print_then_visit(node.right)
        return AnnotatedCastBinaryOp(node.op, left, right, node.source_refs)

    '''TODO: Not sure about BinaryOperator'''

    @visit.register
    def _(self, node: Call):
        #TODO: Is node.func just a string name?
        #TODO: Is node.arguments a list of nodes?
        arguments = self.print_then_visit(node.arguments)
        return AnnotatedCastCall(node.func, arguments, node.source_refs)

    @visit.register
    def _(self, node: ClassDef):
        #TODO: Is node.name just a string name?
        name = self.print_then_visit(node.name)
        #TODO: Is node.fields a list?
        #TODO: Is node.bases a list?
        bases = self.print_then_visit(node.bases)
        fields = self.print_then_visit(node.fields)
        return AnnotatedCastClassDef(name, bases, func, fields, node.source_refs)

    @visit.register
    def _(self, node: Dict):
        #TODO: are these lists?
        keys = self.print_then_visit(node.keys)
        values = self.print_then_visit(node.values)
        return AnnotatedCastDict(keys, values, node.source_refs)

    @visit.register
    def _(self, node: Expr):
        #TODO: is this a list?
        expr = self.print_then_visit(node.name)
        return AnnotatedCastExpr(name, body, node.source_refs)

    @visit.register
    def _(self, node: FunctionDef):
        name = node.name
        annotated_body = []
        for stmt in node.body:
            annotated_body.append(self.print_then_visit(stmt))
        # TODO: visit the func_args
        return AnnotatedCastFunctionDef(name, node.func_args, annotated_body, node.source_refs)
        
    @visit.register
    def _(self, node: List):
        #TODO - a list of values?
        values = self.print_then_visit(node.values)
        return AnnotatedCastList(values, node.source_refs)

    @visit.register
    def _(self, node: Loop):
        print(f"in Loop: body is type {type(node.body)}")
        print(f"in Loop: expr is type {type(node.expr)}")
        expr = self.print_then_visit(node.expr)
        annotated_body = []
        for stmt in node.body:
            annotated_body.append(self.print_then_visit(stmt))
        return AnnotatedCastLoop(expr, annotated_body, node.source_refs)

    @visit.register
    def _(self, node: ModelBreak):
        return AnnotatedCastModelBreak(node.source_refs)

    @visit.register
    def _(self, node: ModelContinue):
        return AnnotatedCastModelContinue(node.source_refs)

    @visit.register
    def _(self, node: ModelIf):
        expr = self.print_then_visit(node.expr)
        body = self.print_then_visit(node.body)
        orelse = self.print_then_visit(node.orelse)
        return AnnotatedCastModelIf(expr, body, orelse, node.source_refs)

    @visit.register
    def _(self, node: ModelReturn):
        return AnnotatedCastModelReturn(node.value, node.source_refs)
        
    @visit.register
    def _(self, node: Module):
        print(f"in visit Module name is {node.name}")
        print(f"len of body is {len(node.body)}")
        annotated_body = []
        for stmt in node.body:
            annotated_body.append(self.print_then_visit(stmt))
        return AnnotatedCastModule(node.name, annotated_body, node.source_refs)
    @visit.register
    def _(self, node: Name):
        return AnnotatedCastName(node.name, node.id, node.source_refs)

    @visit.register
    def _(self, node: Number):
        return AnnotatedCastNumber(node.number, node.source_refs)

    @visit.register
    def _(self, node: UnaryOp):
        value = self.print_then_visit(node.value)
        return AnnotatedCastUnaryOp(node.op, value, node.source_refs)

    #TODO: set, string,subscript, tuple

    @visit.register
    def _(self, node: Var):
        return AnnotatedCastVar(node.val, node.type, node.source_refs)

    '''TODO: not sure about UnaryOperator '''
    '''TODO: not sure about VarType'''
