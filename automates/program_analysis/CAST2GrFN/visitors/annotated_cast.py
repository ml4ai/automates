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

class AnnotatedCastNode(AstNode):
    def __init__(self,*args, **kwargs):
        self._input_vars = {}
        self._updated_vars = {}
        AstNode.__init__(self)

class AnnotatedCastAssignment(AnnotatedCastNode):
    def __init__(self, left, right, source_refs ):
        self.left = left
        self.right = right
        self.source_refs = source_refs

    def __str__(self):
        return Assignment.__str__(self)

class AnnotatedCastAttribute(AnnotatedCastNode):
    def __init__(self, value, attr, source_refs):
        self.value = value
        self.attr = attr
        self.source_refs = source_refs

    def __str__(self):
        return Attribute.__str__(self)

class AnnotatedCastBinaryOp(AnnotatedCastNode):
    def __init__(self, op, left, right, source_refs):
        self.op = op
        self.left = left
        self.right = right
        self.source_refs = source_refs

    def __str__(self):
        return BinaryOp.__str__(self)

'''TODO: Not sure about BinaryOperator'''

class AnnotatedCastBoolean(AnnotatedCastNode, Boolean):
    def __init__(self, node:Boolean):
        self.boolean = node.boolean
        self.source_refs = node.source_refs

    def __str__(self):
        return Boolean.__str__(self)

class AnnotatedCastCall(AnnotatedCastNode, Call):
    def __init__(self, func, arguments, source_refs):
        self.func = func
        self.arguments = arguments
        self.source_refs = source_refs

    def __str__(self):
        return Call.__str__(self)

class AnnotatedCastClassDef(AnnotatedCastNode):
    def __init__(self, name, bases, func, fields, source_refs):
        self.name = node.name
        self.bases = node.bases
        self.func = node.func
        self.fields = node.fields
        self.source_refs = node.source_refs

    def __str__(self):
        return ClassDef.__str__(self)

class AnnotatedCastDict(AnnotatedCastNode):
    def __init__(self, keys, values, source_refs):
        self.keys = keys
        self.values = values
        self.source_refs = source_refs

    def __str__(self):
        return Dict.__str__(self)

class AnnotatedCastExpr(AnnotatedCastNode):
    def __init__(self, expr, source_refs):
        self.expr = expr
        self.source_refs = source_refs

    def __str__(self):
        return Expr.__str__(self)

class AnnotatedCastFunctionDef(AnnotatedCastNode):
    def __init__(self, name, func_args, body, source_refs):
        self.name = name
        self.func_args = func_args
        self.body = body
        self.source_refs = source_refs

    def __str__(self):
        return FunctionDef.__str__(self)

class AnnotatedCastList(AnnotatedCastNode, List):
    def __init__(self, node:List):
        self.values = node.values
        self.source_refs = node.source_refs

    def __str__(self):
        return List.__str__(self)


class AnnotatedCastLoop(AnnotatedCastNode):
    def __init__(self, expr, body, source_refs):
        self.expr = expr
        self.body = body
        self.source_refs = source_refs

        # Dicts mapping strings to Names
        self.loop_body_variables = {}
        self.entry_variables = {}

        # Entry and Exit condition variables
        # used at the top decision to determin `entry_variables`
        self.entry_condition_variables = {}

        # used at the bottom decision to determin `exit_variables`
        # NOTE: depending on how Decision nodes are handled in GrFN, this
        # condition variable may not be necessary
        self.exit_condition_var = None

    def __str__(self):
        return Loop.__str__(self)


class AnnotatedCastModelBreak(AnnotatedCastNode):
    def __init__(self, source_refs):
        self.source_refs = source_refs

    def __str__(self):
        return ModelBreak.__str__(self)

class AnnotatedCastModelContinue(AnnotatedCastNode):
    def __init__(self, node:ModelContinue):
        self.source_refs = node.source_refs

    def __str__(self):
        return ModelContinue.__str__(self)

class AnnotatedCastModelIf(AnnotatedCastNode):
    def __init__(self, expr, body, orelse, source_refs):
        self.expr = expr
        self.body = body
        self.orelse = orelse

        self.updated_vars_if_branch = {}
        self.updated_vars_else_branch = {}

        self.source_refs = source_refs

    def __str__(self):
        return ModelIf.__str__(self)

class AnnotatedCastModelReturn(AnnotatedCastNode):
    def __init__(self, value, source_refs):
        self.value = value
        self.source_refs = source_refs

    def __str__(self):
        return ModelReturn.__str__(self)

class AnnotatedCastModule(AnnotatedCastNode):
    def __init__(self, name, body, source_refs):
        self.name = name
        self.body = body
        self.source_refs = source_refs

    def __str__(self):
        return Module.__str__(self)


class AnnotatedCastName(AnnotatedCastNode):
    def __init__(self, name, id, source_refs):
        self.name = name
        self.id = id
        self.source_refs = source_refs

    def __str__(self):
        return Name.__str__(self)


class AnnotatedCastNumber(AnnotatedCastNode):
    def __init__(self, number, source_refs):
        self.number = number
        self.source_refs = source_refs

    def __str__(self):
        return Number.__str__(self)

class AnnotatedCastSet(AnnotatedCastNode, Set):
    def __init__(self, node:Set):
        self.values = node.values
        self.source_refs = node.source_refs

    def __str__(self):
        return Set.__str__(self)

class AnnotatedCastString(AnnotatedCastNode, String):
    def __init__(self, node:String):
        self.string = node.string
        self.source_refs = node.source_refs

    def __str__(self):
        return String.__str__(self)

'''TODO: not sure about Source Ref '''

class AnnotatedCastSubscript(AnnotatedCastNode, Subscript):
    def __init__(self, node:Subscript):
        self.value = node.value
        self.slice = node.slice
        self.source_refs = node.source_refs

    def __str__(self):
        return Subscript.__str__(self)

class AnnotatedCastTuple(AnnotatedCastNode, Tuple):
    def __init__(self, node:Tuple):
        self.values = node.values
        self.zz = node.zz
        self.source_refs = node.source_refs

    def __str__(self):
        return Tuple.__str__(self)

class AnnotatedCastUnaryOp(AnnotatedCastNode):
    def __init__(self, op, value, source_refs):
        self.op = op
        self.value = value
        self.source_refs = source_refs

    def __str__(self):
        return UnaryOp.__str__(self)

'''TODO: not sure about UnaryOperator '''
'''TODO: not sure about VarType'''


class AnnotatedCastVar(AnnotatedCastNode):
    def __init__(self, val, type, source_refs):
        self.val = val
        self.type = type
        self.source_refs = source_refs

    def __str__(self):
        return Var.__str__(self)

