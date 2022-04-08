import uuid
import typing
from dataclasses import dataclass, field

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

from automates.model_assembly.metadata import LambdaType
from automates.model_assembly.structures import (
    VariableIdentifier,
)

from automates.model_assembly.networks import (
    LambdaNode,
    VariableNode
)

GENERATE_GRFN_2_2 = True

# used in ContainerScopePass functions `con_scope_to_str()` and `visit_name()`
CON_STR_SEP = "."

# TODO: do we need to add any other characters to ensure the name 
# is an illegal identifier
LOOPBODY = "loop-body"
ELSEBODY = "else-body"
IFBODY = "if-body"
LOOPEXPR = "loop-expr"
IFEXPR = "if-expr"

MODULE_SCOPE = "module"

VAR_INIT_VERSION = 0
# TODO: better name for exit version?
VAR_EXIT_VERSION = 1

# the variable versions for loop interface are extended 
# to include `LOOP_VAR_UPDATED_VERSION`
# because the top loop interface has special semantics
# it chooses between the initial version, or the version
# updated after loop body execution
# However, the top_interface_out produces `VAR_INIT_VERSION`
# and bot_interface_in accepts `VAR_EXIT_VERSION` which is consistent
# with other containers
LOOP_VAR_UPDATED_VERSION = 2


def con_scope_to_str(scope: typing.List):
    return CON_STR_SEP.join(scope)

def var_dict_to_str(str_start, vars):
    vars_id_and_names = [f" {name}: {id}" for id, name in vars.items()]
    return str_start + ", ".join(vars_id_and_names)

def interface_to_str(str_start, interface):
    return str_start + ", ".join(interface.values())

def decision_in_to_str(str_start, decision):
    if_else_fullids = []
    for d in decision.values():
        ifid = d[IFBODY]
        elseid = d[ELSEBODY]
        if_else_fullids.append(f" If: {ifid}; Else: {elseid}")

    return str_start + ", ".join(if_else_fullids)

def make_cond_var_name(con_scopestr):
    """
    Make a condition variable name from the scope string `con_scopestr`
    """
    var_name = "".join(re.findall("if\d*\.",con_scopestr))
    var_name = var_name.replace(".","_").replace("if","")
    return "COND_" + var_name[:-1]

def make_loop_exit_name(con_scopestr):
    """
    Makes a Loop exit variable to be used for GrFN condition node
    """
    # TODO: do we want any loop context in the name?
    return "Exit"

def is_literal_assignment(node):
    """
    Check if the node is a Number, Boolean, or String
    This may need to updated later
    """
    if isinstance(node, AnnCastNumber) or isinstance(node, AnnCastBoolean) \
        or isinstance(node, AnnCastString):
        return True

    return False

def function_container_name(node) -> str:
    """
    Parameter: AnnCastNameNode
    Returns function container name in the form "name#id"
    """
    return f"{node.name}-id{node.id}"

def call_argument_name(node, arg_index: int) -> str:
    """
    Returns the call site argument name for argument with index `arg_index`
    Used for the AnnCastCall's top interface in
    """
    return f"{function_container_name(node.func)}-call{node.invocation_index}-arg{arg_index}"

def call_container_name(node) -> str:
    """
    Returns the call site container name
    Used for the AnnCastCall's top interface out and bot interface in
    """
    return f"{function_container_name(node.func)}-call{node.invocation_index}"

def call_ret_val_name(node) -> str:
    """
    Returns the call site return value name
    Used for the AnnCastCall's bot interface out
    """
    return f"{function_container_name(node.func)}-call{node.invocation_index}-ret_val"


def ann_cast_name_to_fullid(node):
    """
    Returns a string representing the fullid of the name node.
    The fullid has format
      'name.id.version.con_scopestr'
    This should only be called after both VariableVersionPass and 
    ContainerScopePass have completed
    """
    pieces = [node.name, str(node.id), str(node.version), con_scope_to_str(node.con_scope)]
    return CON_STR_SEP.join(pieces)

def build_fullid(var_name: str, id: int, version: int, con_scopestr: str):
    """
    Returns a string representing the fullid.
    The fullid has format
      'var_name.id.version.con_scopestr'
    """
    pieces = [var_name, str(id), str(version), con_scopestr]
    return CON_STR_SEP.join(pieces)

def parse_fullid(fullid: str) -> typing.Dict:
    """
    Parses the fullid, returning a dict with mapping the strings
      - "var_name"
      - "id"
      - "version"
      - "con_scopestr"
    to their respective values determined by the fullid
    """
    keys = ["var_name", "id", "version", "con_scopestr"]
    values = fullid.split(CON_STR_SEP)

    assert(len(keys) == len(values))

    return dict(zip(keys, values))

def var_name_from_fullid(fullid: str) -> str:
    """
    Return the variable name for variable with fullid `fullid`
    """
    return parse_fullid(fullid)["var_name"]

def create_grfn_literal_node(metadata: typing.List):
    """
    Creates a GrFN `LambdaNode` with type `LITERAL` and metadata `metadata`.
    The created node has an empty lambda expression (`func_str` attribute)
    """
    lambda_uuid = str(uuid.uuid4())
    # we fill out lambda expression in a later pass
    lambda_str = ""
    lambda_func = lambda: None
    lambda_type = LambdaType.LITERAL
    return LambdaNode(lambda_uuid, lambda_type,
                      lambda_str, lambda_func, metadata)

def create_grfn_assign_node(metadata: typing.List):
    """
    Creates a GrFN `LambdaNode` with type `ASSIGN` and metadata `metadata`.
    The created node has an empty lambda expression (`func_str` attribute)
    """
    lambda_uuid = str(uuid.uuid4())
    # we fill out lambda expression in a later pass
    lambda_str = ""
    lambda_func = lambda: None
    lambda_type = LambdaType.ASSIGN
    return LambdaNode(lambda_uuid, lambda_type,
                      lambda_str, lambda_func, metadata)
    
def create_grfn_var_from_name_node(node):
    """
    Creates a GrFN `VariableNode` for this `AnnCastName` node.
    """
    con_scopestr = con_scope_to_str(node.con_scope)
    return create_grfn_var(node.name, node.id, node.version, con_scopestr)

def create_grfn_var(var_name:str, id: int, version: int, con_scopestr: str):
    """
    Creates a GrFN `VariableNode` using the parameters
    """
    # TODO: For now, we are passing in an empty Metadata
    # list.  We should update this to include the necessary
    # metadata
    # We may also need to update the namespace and scope 
    # we provide, e.g. use :: instead of . as delimiter
    identifier = VariableIdentifier("default_ns", con_scopestr, var_name, version)

    # TODO: change to using UUIDs?
    # uid = GenericNode.create_node_id()
    uid = build_fullid(var_name, id, version, con_scopestr)
    # TODO: fill in metadata
    metadata = []
    return VariableNode(uid, identifier, metadata)


@dataclass
class GrfnAssignment():  
        assignment_node: LambdaNode
        assignment_type: LambdaType
        # inputs and outputs map fullid to GrFN Var uid
        inputs: typing.Dict[str, str] = field(default_factory=dict)
        outputs: typing.Dict[str, str] = field(default_factory=dict)


# class GrfnAssignment:
#     def __init__(self, grfn_node: LambdaNode):
#         self.grfn_node = grfn_node
#         self.inputs = {}
#         self.outputs = {}
# 
#     def __str__(self):
#         return f"GrFNasgn: {str(self.grfn_node)}\n\t inputs  : {self.inputs}\n\t outputs : {self.outputs}"

class AnnCast:
    def __init__(self, ann_nodes: typing.List):
        self.nodes = ann_nodes
        # populated after IdCollapsePass, and used to give ids to GrFN condition variables
        self.collapsed_id_counter = 0
        # dict mapping FunctionDef container scopestr to its id
        self.func_con_scopestr_to_id = {}
        # dict mapping function IDs to their FunctionDef nodes.  
        self.func_id_to_def = {}
        self.grfn_id_to_grfn_var = {}
        # the fullid of a AnnCastName node is a string which includes its 
        # variable name, numerical id, version, and scope
        self.fullid_to_grfn_id = {}
        # TODO: do we need to store multiple modules?
        self.module_node = None

    def get_func_node_from_scopestr(self, con_scopestr: str):
        """
        Return the AnnCastFuncitonDef node for the container scope 
        defined by `con_scopestr`
        """
        function_id = self.func_con_scopestr_to_id[con_scopestr]
        return self.func_id_to_def[function_id]
        

    def is_global_var(self, id: int):
        """
        Check if id is in the used_variables attribute of the module node
        """
        return id in self.module_node.used_vars


    def next_collapsed_id(self):
        """
        Return the next collapsed id, and increment `collapsed_id_counter`
        """
        to_return = self.collapsed_id_counter
        self.collapsed_id_counter += 1
        return to_return

    def store_grfn_var(self, fullid: str, grfn_var: VariableNode):
        """
        Cache `grfn_var` in `grfn_id_to_grfn_var` and add `fullid` to `fullid_to_grfn_id`
        """
        self.fullid_to_grfn_id[fullid] = grfn_var.uid
        self.grfn_id_to_grfn_var[grfn_var.uid] = grfn_var

    def grfn_var_exists(self, fullid: str):
        """
        Returns the whether the GrFN VariableNode associated with `fullid` has already been created
        """
        return fullid in self.fullid_to_grfn_id

    def get_grfn_var(self, fullid: str):
        """
        Returns the cached GrFN VariableNode associated with `fullid`
        """
        grfn_id = self.fullid_to_grfn_id[fullid]
        return self.grfn_id_to_grfn_var[grfn_id]

class AnnCastNode(AstNode):
    def __init__(self,*args, **kwargs):
        self.incoming_vars = {}
        self.outgoing_vars = {}
        AstNode.__init__(self)

class AnnCastAssignment(AnnCastNode):
    def __init__(self, left, right, source_refs ):
        self.left = left
        self.right = right
        self.source_refs = source_refs

        self.grfn_assignment: GrfnAssignment


    def __str__(self):
        return Assignment.__str__(self)

class AnnCastAttribute(AnnCastNode):
    def __init__(self, value, attr, source_refs):
        self.value = value
        self.attr = attr
        self.source_refs = source_refs

    def __str__(self):
        return Attribute.__str__(self)

class AnnCastBinaryOp(AnnCastNode):
    def __init__(self, op, left, right, source_refs):
        self.op = op
        self.left = left
        self.right = right
        self.source_refs = source_refs

    def __str__(self):
        return BinaryOp.__str__(self)

class AnnCastBoolean(AnnCastNode):
    def __init__(self, boolean, source_refs):
        self.boolean = boolean
        self.source_refs = source_refs

    def __str__(self):
        return Boolean.__str__(self)

class AnnCastCallGrfn2_2(AnnCastNode):
    def __init__(self, func, arguments, source_refs):
        self.func: AnnCastName = func
        self.arguments = arguments
        self.source_refs = source_refs

        # the index of this Call node over all invocations of this function
        self.invocation_index: int 
        
        # dicts mapping a Name id to its fullid
        self.top_interface_in = {}
        self.top_interface_out = {}
        self.bot_interface_in = {}
        self.bot_interface_out = {}

        # for top_interface_out
        # mapping Name id to fullid
        # to determine this, we check if we store version 0 on any Name node
        self.globals_accessed_before_mod = {}

        # for bot_interface
        # map Name id to fullid
        self.in_ret_val = {}
        self.out_ret_val = {}
        self.modified_globals = {} # Store when accumulating modified variables


        # copied function def for GrFN 2.2
        self.func_def_copy: typing.Optional[AnnCastFunctionDef] = None

        # dict mapping argument index to created argument fullid
        self.arg_index_to_fullid = {}
        self.param_index_to_fullid = {}
        # this dict maps argument positional index to GrfnAssignment's
        # Each GrfnAssignment stores the ASSIGN/LITERAL node, 
        # the inputs to the ASSIGN/LITERAL node, and the outputs to the ASSIGN/LITERAL node
        # In this case, the output will map the arguments fullid to its grfn_id
        self.arg_assignments: typing.Dict[int, GrfnAssignment] = {}

    def __str__(self):
        return Call.__str__(self)

class AnnCastCall(AnnCastNode):
    def __init__(self, func, arguments, source_refs):
        self.func: AnnCastName = func
        self.arguments = arguments
        self.source_refs = source_refs

        # the index of this Call node over all invocations of this function
        self.invocation_index: int 
        
        # dicts mapping a Name id to its fullid
        self.top_interface_in = {}
        self.top_interface_out = {}
        self.bot_interface_in = {}
        self.bot_interface_out = {}

        # for top_interface_out
        # mapping Name id to fullid
        # to determine this, we check if we store version 0 on any Name node
        self.globals_accessed_before_mod = {}

        # for bot_interface
        # map Name id to fullid
        self.in_ret_val = {}
        self.out_ret_val = {}
        self.modified_globals = {} # Store when accumulating modified variables

        # dict mapping argument index to created argument fullid
        self.arg_index_to_fullid = {}
        self.param_index_to_fullid = {}
        # this dict maps argument positional index to GrfnAssignment's
        # Each GrfnAssignment stores the ASSIGN/LITERAL node, 
        # the inputs to the ASSIGN/LITERAL node, and the outputs to the ASSIGN/LITERAL node
        # In this case, the output will map the arguments fullid to its grfn_id
        self.arg_assignments: typing.Dict[int, GrfnAssignment] = {}

    def __str__(self):
        return Call.__str__(self)

class AnnCastClassDef(AnnCastNode):
    def __init__(self, name, bases, func, fields, source_refs):
        self.name = node.name
        self.bases = node.bases
        self.func = node.func
        self.fields = node.fields
        self.source_refs = node.source_refs

    def __str__(self):
        return ClassDef.__str__(self)

class AnnCastDict(AnnCastNode):
    def __init__(self, keys, values, source_refs):
        self.keys = keys
        self.values = values
        self.source_refs = source_refs

    def __str__(self):
        return Dict.__str__(self)

class AnnCastExpr(AnnCastNode):
    def __init__(self, expr, source_refs):
        self.expr = expr
        self.source_refs = source_refs

    def __str__(self):
        return Expr.__str__(self)

class AnnCastFunctionDef(AnnCastNode):
    def __init__(self, name, func_args, body, source_refs):
        self.name = name
        self.func_args = func_args
        self.body = body
        self.source_refs = source_refs

        # TODO:
        # How does this example work with interfaces? 
        # How does g1 get added to func2's imported_globals?
        # int g1 = 1;
        # int func1() {
        #     func2();
        # }
        #
        # int func2() {
        #     g1 = 0;
        # }
        #
        # int main() {
        #     func1();
        # }
        self.con_scope: typing.List

        # For CAST coming from C, we determine if the function 
        # has a return value by looking for a CAST Return node.
        # We do this during the ContainerScopePass.
        # TODO: What should be done with CAST coming from Python? 
        # Every function returns something
        # either None, or the explicit return value
        self.has_ret_val: bool = False
        # for bot_interface
        # in_ret_val and out_ret_val map Name id to fullid
        self.in_ret_val = {}
        self.out_ret_val = {}

        # dicts mapping a Name id to its string name
        # used for container interfaces
        self.modified_vars: typing.Dict[id, str]
        self.accessed_vars: typing.Dict[id, str]
        self.used_vars: typing.Dict[id, str]
        # dicts for global variables
        # for top_interface_out
        self.globals_accessed_before_mod = {}
        # for bot interface in
        self.modified_globals = {} 
        # TODO: remove?
        self.used_globals = {}
    
        # dicts mapping a Name id to its fullid
        self.top_interface_in = {}
        self.top_interface_out = {}
        self.bot_interface_in = {}
        self.bot_interface_out = {}

        # dict mapping Name id to highest version at end of "block"
        # TODO: What about using a default dict
        self.body_highest_var_vers = {}

    def __str__(self):
        return FunctionDef.__str__(self)

class AnnCastList(AnnCastNode):
    def __init__(self, values, source_refs):
        self.values = values
        self.source_refs = source_refs

    def __str__(self):
        return List.__str__(self)

class AnnCastClassDef(AnnCastNode):
    def __init__(self, name, bases, funcs, fields, source_refs):
        self.name = name
        self.bases = bases
        self.funcs = funcs
        self.fields = fields
        self.source_refs = source_refs

    def __str__(self):
        return ClassDef.__str__(self)

class AnnCastLoop(AnnCastNode):
    def __init__(self, expr, body, source_refs):
        self.expr = expr
        self.body = body
        self.source_refs = source_refs

        # dicts mapping a Name id to its string name
        # used for container interfaces
        self.modified_vars: typing.Dict[id, str]
        self.accessed_vars: typing.Dict[id, str]
        self.used_vars: typing.Dict[id, str]
        self.con_scope: typing.List

        # dicts mapping Name id to highest version at end of "block"
        self.expr_highest_var_vers = {}
        self.body_highest_var_vers = {}

        # dicts mapping a Name id to variable string name
        # for variables used in the if expr
        self.expr_accessed_vars = {}
        self.expr_modified_vars = {}
        self.expr_used_vars = {}

        # dicts mapping a Name id to its fullid
        # initial versions for the top interface come from enclosing scope
        # updated version for the top interface are versions 
        # at the bottom of the loop after one or more executions of the loop
        self.top_interface_initial = {}
        self.top_interface_updated = {}
        self.top_interface_out = {}
        self.bot_interface_in = {}
        self.bot_interface_out = {}
        self.condition_in = {}
        self.condition_out = {}
        # GrFN VarialeNode for the condition node
        self.condition_var = None
        # TODO: decide type of exit
        self.exit = None

        # TODO: Might delete below attributes
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


class AnnCastModelBreak(AnnCastNode):
    def __init__(self, source_refs):
        self.source_refs = source_refs

    def __str__(self):
        return ModelBreak.__str__(self)

class AnnCastModelContinue(AnnCastNode):
    def __init__(self, node:ModelContinue):
        self.source_refs = node.source_refs

    def __str__(self):
        return ModelContinue.__str__(self)

class AnnCastModelIf(AnnCastNode):
    def __init__(self, expr, body, orelse, source_refs):
        self.expr = expr
        self.body = body
        self.orelse = orelse

        # dicts mapping a Name id to string name
        # used for container interfaces
        self.modified_vars: typing.Dict[id, str]
        self.accessed_vars: typing.Dict[id, str]
        self.used_vars: typing.Dict[id, str]
        self.con_scope: typing.List
        # dicts mapping a Name id to variable string name
        # for variables used in the if expr
        self.expr_accessed_vars = {}
        self.expr_modified_vars = {}
        self.expr_used_vars = {}
        # dicts mapping Name id to highest version at end of "block"
        # TODO: What about using a default dict
        self.expr_highest_var_vers = {}
        self.ifbody_highest_var_vers = {}
        self.elsebody_highest_var_vers = {}

        # dicts mapping a Name id to its fullid
        self.top_interface_in = {}
        self.top_interface_out = {}
        self.bot_interface_in = {}
        self.bot_interface_out = {}
        self.condition_in = {}
        self.condition_out = {}
        self.decision_in = {}
        self.decision_out = {}
        # GrFN VarialeNode for the condition node
        self.condition_var = None

        self.source_refs = source_refs

        # TODO: Maybe delete
        self.updated_vars_if_branch = {}
        self.updated_vars_else_branch = {}

        

    def __str__(self):
        return ModelIf.__str__(self)

class AnnCastModelReturn(AnnCastNode):
    def __init__(self, value, source_refs):
        self.value = value
        self.source_refs = source_refs
        # cache the FunctionDef node that this return statement lies in
        self.owning_func_def: typing.Optional[AnnCastFunctionDef] = None
        # store GrfnAssignment for use in GrFN generation
        self.grfn_assignment: typing.Optional[GrfnAssignment] = None

    def __str__(self):
        return ModelReturn.__str__(self)

class AnnCastModule(AnnCastNode):
    def __init__(self, name, body, source_refs):
        self.name = name
        self.body = body
        self.source_refs = source_refs

        # dicts mapping a Name id to string name
        # used for container interfaces
        self.modified_vars: typing.Dict[int, str] = {}
        self.accessed_vars: typing.Dict[int, str] = {}
        self.used_vars: typing.Dict[int, str] = {}
        self.con_scope: typing.List

    def __str__(self):
        return Module.__str__(self)


class AnnCastName(AnnCastNode):
    def __init__(self, name, id, source_refs):
        self.name = name
        self.id = id
        self.source_refs = source_refs
        # container_scope is used to aid GrFN generation
        self.con_scope: typing.List = []
        # versions are bound to the cope of the variable
        self.version = None
        self.grfn_id = None

    def __str__(self):
        return Name.__str__(self)


class AnnCastNumber(AnnCastNode):
    def __init__(self, number, source_refs):
        self.number = number
        self.source_refs = source_refs

    def __str__(self):
        return Number.__str__(self)

class AnnCastSet(AnnCastNode):
    def __init__(self, values, source_refs):
        self.values = values
        self.source_refs = source_refs

    def __str__(self):
        return Set.__str__(self)

class AnnCastString(AnnCastNode):
    def __init__(self, string, source_refs):
        self.string = string
        self.source_refs = source_refs

    def __str__(self):
        return String.__str__(self)

class AnnCastSubscript(AnnCastNode):
    def __init__(self, value, slice, source_refs):
        self.value = node.value
        self.slice = node.slice
        self.source_refs = source_refs

    def __str__(self):
        return Subscript.__str__(self)

class AnnCastTuple(AnnCastNode):
    def __init__(self, values, source_refs):
        self.values = values
        self.source_refs = source_refs

    def __str__(self):
        return Tuple.__str__(self)

class AnnCastUnaryOp(AnnCastNode):
    def __init__(self, op, value, source_refs):
        self.op = op
        self.value = value
        self.source_refs = source_refs

    def __str__(self):
        return UnaryOp.__str__(self)

class AnnCastVar(AnnCastNode):
    def __init__(self, val, type, source_refs):
        self.val = val
        self.type = type
        self.source_refs = source_refs

    def __str__(self):
        return Var.__str__(self)

