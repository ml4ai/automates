from functools import singledispatchmethod
from automates.utils.misc import uuid
import typing

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

    def visit_list(self, node_list: typing.List[AstNode]):
        return [self.print_then_visit(node) for node in node_list]

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
        print(f"Assignment: type of rhs is {type(node.right)}")
        left = self.print_then_visit(node.left)
        right = self.print_then_visit(node.right)
        return AnnotatedCastAssignment(left, right, node.source_refs)

    @visit.register
    def _(self, node: Attribute):
        value = self.print_then_visit(node.value)
        attr  = self.print_then_visit(node.attr)
        return AnnotatedCastAttribute(value, attr, node.source_refs)

    @visit.register
    def _(self, node: BinaryOp):
        print(f"BinaryOp: type of lhs is {type(node.left)}")
        print(f"BinaryOp: type of rhs is {type(node.right)}")
        left = self.print_then_visit(node.left)
        right = self.print_then_visit(node.right)
        return AnnotatedCastBinaryOp(node.op, left, right, node.source_refs)

    @visit.register
    def _(self, node: Boolean):
        print(f"Boolean: type of boolean attribute is {type(node.boolean)}")
        boolean = self.print_then_visit(node.boolean)
        return AnnotatedCastBoolean(boolean, node.source_refs)

    @visit.register
    def _(self, node: Call):
        #TODO: Is node.func just a string name? yes
        #TODO: Is node.arguments a list of nodes?
        print(f"Call: type of arguments is {type(node.arguments)}")
        arguments = self.print_then_visit(node.arguments)
        return AnnotatedCastCall(node.func, arguments, node.source_refs)

    @visit.register
    def _(self, node: ClassDef):
        #TODO: Is node.name just a string name? Yes
        #TODO: Is node.fields a list? yes, list of Vars
        #TODO: Is node.bases a list? yes, just a list of strings
        funcs = self.visit_list(node.funcs)
        fields = self.visit_list(node.fields)
        return AnnotatedCastClassDef(node.name, node.bases, funcs, fields, node.source_refs)

    @visit.register
    def _(self, node: Dict):
        #TODO: are keys and values lists? yes
        print(f"Dict: type of keys is {type(node.keys)}")
        print(f"Dict: type of values is {type(node.values)}")
        keys = self.visit_list(node.keys)
        values = self.visit_list(node.values)
        return AnnotatedCastDict(keys, values, node.source_refs)

    @visit.register
    def _(self, node: Expr):
        expr = self.print_then_visit(node.expr)
        return AnnotatedCastExpr(expr, node.source_refs)

    @visit.register
    def _(self, node: FunctionDef):
        name = node.name
        body = self.visit_list(node.body)
        args = self.visit_list(node.func_args)
        return AnnotatedCastFunctionDef(name, args, body, node.source_refs)
        
    @visit.register
    def _(self, node: List):
        #TODO - a list of values? yes
        values = self.visit_list(node.values)
        return AnnotatedCastList(values, node.source_refs)

    @visit.register
    def _(self, node: Loop):
        print(f"in Loop: body is type {type(node.body)}")
        print(f"in Loop: expr is type {type(node.expr)}")
        expr = self.print_then_visit(node.expr)
        body = self.visit_list(node.body)
        return AnnotatedCastLoop(expr,body, node.source_refs)

    @visit.register
    def _(self, node: ModelBreak):
        return AnnotatedCastModelBreak(node.source_refs)

    @visit.register
    def _(self, node: ModelContinue):
        return AnnotatedCastModelContinue(node.source_refs)

    @visit.register
    def _(self, node: ModelIf):
        expr = self.print_then_visit(node.expr)
        print(f"in ModelIf: body is type {type(node.body)}")
        body = self.visit_list(node.body)
        print(f"in ModelIf: orelse is type {type(node.orelse)}")
        orelse = self.visit_list(node.orelse)
        return AnnotatedCastModelIf(expr, body, orelse, node.source_refs)

    @visit.register
    def _(self, node: ModelReturn):
        return AnnotatedCastModelReturn(node.value, node.source_refs)
        
    @visit.register
    def _(self, node: Module):
        print(f"in visit Module name is {node.name}")
        print(f"len of body is {len(node.body)}")
        body = self.visit_list(node.body)
        return AnnotatedCastModule(node.name, body, node.source_refs)

    @visit.register
    def _(self, node: Name):
        return AnnotatedCastName(node.name, node.id, node.source_refs)

    @visit.register
    def _(self, node: Number):
        return AnnotatedCastNumber(node.number, node.source_refs)

    @visit.register
    def _(self, node: Set):
        values = self.visit_list(node.values)
        return AnnotatedCastSet(values, node.source_refs)

    @visit.register
    def _(self, node: String):
        string = self.print_then_visit(node.string)
        return AnnotatedCastString(string, node.source_refs)

    @visit.register
    def _(self, node: Subscript):
        #TODO: Not quite sure what the types of value and slice are
        value = self.print_then_visit(node.value)
        slice = self.print_then_visit(node.slice)
        return AnnotatedCastSubscript(value, slice, node.source_refs)

    @visit.register
    def _(self, node: Tuple):
        #TODO: Is values a list of nodes? Yes.
        values = self.visit_list(node.values)
        return AnnotatedCastTuple(values, node.source_refs)

    @visit.register
    def _(self, node: UnaryOp):
        value = self.print_then_visit(node.value)
        return AnnotatedCastUnaryOp(node.op, value, node.source_refs)

    @visit.register
    def _(self, node: Var):
        val = self.print_then_visit(node.val)
        return AnnotatedCastVar(val, node.type, node.source_refs)
