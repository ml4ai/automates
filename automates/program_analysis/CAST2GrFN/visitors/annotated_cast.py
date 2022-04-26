import uuid
import typing
import re
import sys
from datetime import datetime
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

from automates.model_assembly.metadata import (
        LambdaType, TypedMetadata, CodeSpanReference, Domain, ProvenanceData, 
        VariableFromSource, MetadataMethod
        )
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
# delimiter for fullids
FULLID_SEP = ":"

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

def cast_op_to_str(op):
    op_map = {
        "Pow": "^",
        "Mult": "*",
        "Add": "+",
        "Sub": "-",
        "Div": "/",
        "Gt": ">",
        "Gte": ">=",
        "Lt": "<",
        "Lte": "<=",
        "Eq": "==",
        "NotEq": "!=",
        "BitXor": "^",
        "BitAnd": "&",
        "BitOr": "|",
        "LShift": "<<",
        "RShift": ">>",
        "Not": "not ",
        "Invert": "~",
        "USub": "- ",
        "And": "&&",
        "Or": "||",
        "Mod": "%",
    }
    return op_map[op] if op in op_map else None

# Metadata functions
def source_ref_dict(source_ref: SourceRef):
    # We want the following fields in the GrFN Metadata
    # line_begin=source_ref.row_start,
    # line_end=source_ref.row_end,
    # col_start=source_ref.col_start,
    # col_end=source_ref.col_end,
    to_return = dict()
    to_return["line_begin"] = source_ref.row_start
    to_return["line_end"] = source_ref.row_end
    to_return["col_start"] = source_ref.col_start
    to_return["col_end"] = source_ref.col_end
    return to_return

def combine_source_refs(source_refs: typing.List[SourceRef]):
    """
    From a list of SourceRefs return a single SourceRef with 
    row and column range covering all row/column ranges from the list
    """
    row_start = sys.maxsize
    row_end = -1
    col_start = sys.maxsize
    col_end = -1
    source_file_name = None

    for src_ref in source_refs:
        if src_ref.row_start is not None and src_ref.row_start < row_start:
            row_start = src_ref.row_start
        if src_ref.row_end is not None and src_ref.row_end > row_end:
            row_end = src_ref.row_end
        if src_ref.col_start is not None and src_ref.col_start < col_start:
            col_start = src_ref.col_start
        if src_ref.col_end is not None and src_ref.col_end > col_end:
            col_end = src_ref.col_end
        if src_ref.source_file_name is not None:
            assert(source_file_name is None or source_file_name == src_ref.source_file_name)
            source_file_name = src_ref.source_file_name


    # use None instead of providing incorrect data
    row_start = None if row_start in [-1, sys.maxsize] else row_start
    row_end = None if row_end in [-1, sys.maxsize] else row_end
    col_start = None if col_start in [-1, sys.maxsize] else col_start
    col_end = None if col_end in [-1, sys.maxsize] else col_end

    # due to incomplete source ref data, it is possible
    # to combine source refs and end up in a situation where we no longer have a valid
    # range i.e. row_end < row_start.  
    # if we run into this, we swap them
    if row_end is not None and row_start is not None and row_end < row_start:
        row_end, row_start = row_start, row_end
    if col_end is not None and col_start is not None and col_end < col_start:
        col_end, col_start = col_start, col_end

    return SourceRef(source_file_name, col_start, col_end, row_start, row_end)

def generate_domain_metadata():
    # TODO: this needs to be updated
    data = dict()
    data["type"] = "domain"
    data["provenance"] = ProvenanceData.from_data({
                "method": "PROGRAM_ANALYSIS_PIPELINE",
                "timestamp": datetime.now(),
                })
    data["data_type"] = "integer"
    data["measurement_scale"] = "discrete"
    data["elements"] = []

    return Domain.from_data(data=data)

def generate_from_source_metadata(from_source: bool, reason: str):
    provenance = ProvenanceData(
        MetadataMethod.PROGRAM_ANALYSIS_PIPELINE,
        ProvenanceData.get_dt_timestamp()
    )
    data = {
            "type": "FROM_SOURCE",
            "provenance": provenance,
            "from_source": str(from_source),
            "creation_reason": reason,
        }
    return VariableFromSource.from_data(data=data)

def generate_variable_node_span_metadata(source_refs):
    src_ref_dict = {}
    file_ref = ""
    if source_refs:
        # TODO: decide which element of source_refs we want to use
        src_ref = source_refs[0]
        src_ref_dict = source_ref_dict(src_ref)
        file_ref = src_ref.source_file_name

    code_span_data = {
        "source_ref": src_ref_dict,
        "file_uid": file_ref,
        "code_type": "identifier",
    }
    return CodeSpanReference.from_air_data(code_span_data)

def add_metadata_to_grfn_var(grfn_var, from_source_mdata=None, span_mdata=None, domain_mdata=None):
    if from_source_mdata is None:
        from_source_mdata = generate_from_source_metadata(True, "UNKNOWN")

    if span_mdata is None:
        source_refs = [SourceRef(None, None, None, None, None)]
        span_mdata = generate_variable_node_span_metadata(source_refs)

    if domain_mdata is None:
        # TODO: this is copied from C2AVarialble.to_AIR
        # note sure if we need to use it
        domain = {
            "type": "type",  # TODO what is this field?
            "mutable": False,  # TODO probably only mutable if object/list/dict type
            "name": "Number",  # TODO probably only mutable if object/list/dict type
        }
        domain_mdata = generate_domain_metadata()

    new_metadata = [from_source_mdata, domain_mdata, span_mdata]
    grfn_var.metadata = new_metadata

def create_lambda_node_metadata(source_refs):
    """
    source_refs is either None or a List of SourceRefs
    This is what the spec for CAST implements
    """
    src_ref_dict = {}
    file_ref = ""
    if source_refs:
        # TODO: decide which element of source_refs we want to use
        src_ref = source_refs[0]
        src_ref_dict = source_ref_dict(src_ref)
        file_ref = src_ref.source_file_name

    code_span_data = {
        "source_ref": src_ref_dict,
        "file_uid": file_ref,
        "code_type": "block",
    }
    metadata = [CodeSpanReference.from_air_data(code_span_data)]

    return metadata

@dataclass
class GrfnContainerSrcRef:
    """
    Used to track the line begin, line end, and source file for ModelIf and Loop
    Containers.  This data will eventually be added to the containers metadata
    """
    line_begin: typing.Optional[int]
    line_end: typing.Optional[int]
    source_file_name: typing.Optional[str]

def create_container_metadata(grfn_src_ref: GrfnContainerSrcRef):
    src_ref_dict = {}
    src_ref_dict["line_begin"] = grfn_src_ref.line_begin
    src_ref_dict["line_end"] = grfn_src_ref.line_end

    code_span_data = {
        "source_ref": src_ref_dict,
        "file_uid": grfn_src_ref.source_file_name,
        "code_type": "block",
    }
    metadata = [CodeSpanReference.from_air_data(code_span_data)]

    return metadata

def combine_grfn_con_src_refs(source_refs: typing.List[GrfnContainerSrcRef]):
    """
    From a list of GrfnContainerSrcRef return a single GrfnContainerSrcRef with 
    line range covering all line ranges from the list
    """
    line_begin = sys.maxsize
    line_end = -1
    source_file_name = None

    for src_ref in source_refs:
        if src_ref.line_begin is not None and src_ref.line_begin < line_begin:
            line_begin = src_ref.line_begin
        if src_ref.line_end is not None and src_ref.line_end > line_end:
            line_end = src_ref.line_end
        if src_ref.source_file_name is not None:
            source_file_name = src_ref.source_file_name

    # use None instead of providing incorrect data
    line_begin = None if line_begin in [-1, sys.maxsize] else line_begin
    line_end = None if line_end in [-1, sys.maxsize] else line_end

    # due to incomplete source ref data, it is possible
    # to combine source refs and end up in a situation where we no longer have a valid
    # range i.e. line_end < line_begin.  
    # if we run into this, we swap them
    if line_end is not None and line_begin is not None and line_end < line_begin:
        line_end, line_begin = line_begin, line_end


    return GrfnContainerSrcRef(line_begin, line_end, source_file_name)

# End Metadata functions

def union_dicts(dict1, dict2):
    """
    Combines the key value pairs of dict1 and dict2.
    For collisions, don't assume which key-value pair will be chosen.
    """
    return {**dict1, **dict2}


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


def is_func_def_main(node) -> bool:
    """
    Parameter: AnnCastFuncitonDef
    Checks if node is the FunctionDef for "main"
    """
    # TODO: this may need to be extended for Python
    MAIN_FUNC_DEF_NAME = "main"
    return node.name.name == MAIN_FUNC_DEF_NAME

def function_container_name(node) -> str:
    """
    Parameter: AnnCastNameNode
    Returns function container name in the form "name#id"
    """
    return f"{node.name}_id{node.id}"

def func_def_argument_name(node, arg_index: int) -> str:
    """
    Returns the FunctionDef argument name for argument with index `arg_index`
    Used for the AnnCastCall's top interface in
    """
    return f"{function_container_name(node.name)}_arg{arg_index}"

def func_def_ret_val_name(node) -> str:
    """
    Returns the FunctionDef return value name
    Used for the AnnCastCall's bot interface out
    """
    return f"{function_container_name(node.name)}_ret_val"

def call_argument_name(node, arg_index: int) -> str:
    """
    Returns the call site argument name for argument with index `arg_index`
    Used for the AnnCastCall's top interface in
    """
    return f"{function_container_name(node.func)}_call{node.invocation_index}_arg{arg_index}"

def call_param_name(node, arg_index: int) -> str:
    """
    Returns the call site parameter name for argument with index `arg_index`
    Used for the AnnCastCall's top interface in
    """
    return f"{function_container_name(node.func)}_call{node.invocation_index}_param{arg_index}"

def call_container_name(node) -> str:
    """
    Returns the call site container name
    Used for the AnnCastCall's top interface out and bot interface in
    """
    return f"{function_container_name(node.func)}_call{node.invocation_index}"

def call_ret_val_name(node) -> str:
    """
    Returns the call site return value name
    Used for the AnnCastCall's bot interface out
    """
    return f"{function_container_name(node.func)}_call{node.invocation_index}_ret_val"


def ann_cast_name_to_fullid(node):
    """
    Returns a string representing the fullid of the name node.
    The fullid has format
      'name.id.version.con_scopestr'
    This should only be called after both VariableVersionPass and 
    ContainerScopePass have completed
    """
    pieces = [node.name, str(node.id), str(node.version), con_scope_to_str(node.con_scope)]
    return FULLID_SEP.join(pieces)

def build_fullid(var_name: str, id: int, version: int, con_scopestr: str):
    """
    Returns a string representing the fullid.
    The fullid has format
      'var_name.id.version.con_scopestr'
    """
    pieces = [var_name, str(id), str(version), con_scopestr]
    return FULLID_SEP.join(pieces)

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
    values = fullid.split(FULLID_SEP)

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
    
    # this will be filled out later
    metadata = []
    return VariableNode(uid, identifier, metadata)




@dataclass
class GrfnAssignment():  
        assignment_node: LambdaNode
        assignment_type: LambdaType
        # inputs and outputs map fullid to GrFN Var uid
        inputs: typing.Dict[str, str] = field(default_factory=dict)
        outputs: typing.Dict[str, str] = field(default_factory=dict)
        lambda_expr: str = ""


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

    def func_def_exists(self, id: int) -> bool:
        """
        Check if there is a FuncionDef for id
        """
        return id in self.func_id_to_def

    def func_def_node_from_scopestr(self, con_scopestr: str):
        """
        Return the AnnCastFuncitonDef node for the container scope 
        defined by `con_scopestr`
        """
        function_id = self.func_con_scopestr_to_id[con_scopestr]
        return self.func_id_to_def[function_id]

    def func_def_node_from_id(self, id: int):
        """
        Return the FunctionDef for `id`
        """
        assert(self.func_def_exists(id))
        return self.func_id_to_def[id]
        
    def is_global_var(self, id: int):
        """
        Check if id is in the used_variables attribute of the module node
        """
        return id in self.module_node.used_vars

    def all_globals_dict(self):
        """
        Return a dict mapping id to string name for all global variables
        """
        return self.module_node.used_vars

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

    def alias_grfn_vars(self, src_fullid: str, tgt_fullid: str):
        """
        Put the GrFN id associated with `tgt_fullid` into dict `fullid_to_grfn_id` for key
        `src_fullid` 
        """
        self.fullid_to_grfn_id[src_fullid] = self.fullid_to_grfn_id[tgt_fullid]
    

class AnnCastNode(AstNode):
    def __init__(self,*args, **kwargs):
        super().__init__(self)
        self.incoming_vars = {}
        self.outgoing_vars = {}
        self.expr_str: str = ""

class AnnCastAssignment(AnnCastNode):
    def __init__(self, left, right, source_refs ):
        super().__init__(self)
        self.left = left
        self.right = right
        self.source_refs = source_refs

        self.grfn_assignment: GrfnAssignment


        
    def __str__(self):
        return Assignment.__str__(self)

class AnnCastAttribute(AnnCastNode):
    def __init__(self, value, attr, source_refs):
        super().__init__(self)
        self.value = value
        self.attr = attr
        self.source_refs = source_refs

        
    def __str__(self):
        return Attribute.__str__(self)

class AnnCastBinaryOp(AnnCastNode):
    def __init__(self, op, left, right, source_refs):
        super().__init__(self)
        self.op = op
        self.left = left
        self.right = right
        self.source_refs = source_refs

        
    def __str__(self):
        return BinaryOp.__str__(self)

class AnnCastBoolean(AnnCastNode):
    def __init__(self, boolean, source_refs):
        super().__init__(self)
        self.boolean = boolean
        self.source_refs = source_refs

        
    def __str__(self):
        return Boolean.__str__(self)

class AnnCastCall(AnnCastNode):
    def __init__(self, func, arguments, source_refs):
        super().__init__(self)
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
        # dicts mapping Name id to Name string
        self.top_interface_globals = {}
        self.bot_interface_globals = {}
        # GrFN lambda expressions
        self.top_interface_lambda: str
        self.bot_interface_lambda: str

        # for top_interface_out
        # mapping Name id to fullid
        # to determine this, we check if we store version 0 on any Name node
        self.globals_accessed_before_mod = {}
        self.used_globals = {}

        # for bot_interface
        # map Name id to fullid
        self.in_ret_val = {}
        self.out_ret_val = {}

        # if this is a GrFN 2.2 Call, we will copy the associated FunctionDef
        # to make the GrFN 2.2 container
        self.is_grfn_2_2: bool = False
        # copied function def for GrFN 2.2
        self.func_def_copy: typing.Optional[AnnCastFunctionDef] = None

        # keep track of whether the Call has an associated FunctionDef
        # and if the Call should return a value
        self.has_func_def: bool = False
        self.has_ret_val: bool = False

        # dict mapping argument index to created argument fullid
        self.arg_index_to_fullid = {}
        self.param_index_to_fullid = {}
        # this dict maps argument positional index to GrfnAssignment's
        # Each GrfnAssignment stores the ASSIGN/LITERAL node, 
        # the inputs to the ASSIGN/LITERAL node, and the outputs to the ASSIGN/LITERAL node
        # In this case, the output will map the arguments fullid to its grfn_id
        self.arg_assignments: typing.Dict[int, GrfnAssignment] = {}

        # metadata attributes
        self.grfn_con_src_ref: GrfnContainerSrcRef

        
    def __str__(self):
        return Call.__str__(self)


class AnnCastClassDef(AnnCastNode):
    def __init__(self, name, bases, func, fields, source_refs):
        super().__init__(self)
        self.name = node.name
        self.bases = node.bases
        self.func = node.func
        self.fields = node.fields
        self.source_refs = node.source_refs

        
    def __str__(self):
        return ClassDef.__str__(self)

class AnnCastDict(AnnCastNode):
    def __init__(self, keys, values, source_refs):
        super().__init__(self)
        self.keys = keys
        self.values = values
        self.source_refs = source_refs

        
    def __str__(self):
        return Dict.__str__(self)

class AnnCastExpr(AnnCastNode):
    def __init__(self, expr, source_refs):
        super().__init__(self)
        self.expr = expr
        self.source_refs = source_refs

        
    def __str__(self):
        return Expr.__str__(self)

class AnnCastFunctionDef(AnnCastNode):
    def __init__(self, name, func_args, body, source_refs):
        super().__init__(self)
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
        # In Python, every function retruns something, 
        # either None or the explicit return value
        self.has_ret_val: bool = False
        # for bot_interface
        # in_ret_val and out_ret_val map Name id to fullid
        self.in_ret_val = {}
        self.out_ret_val = {}

        # dicts mapping a Name id to its string name
        # used for container interfaces
        self.modified_vars: typing.Dict[int, str]
        self.vars_accessed_before_mod: typing.Dict[int, str]
        self.used_vars: typing.Dict[int, str]
        self.top_interface_globals: typing.Dict[int, str]
        self.bot_interface_globals: typing.Dict[int, str]
        # dicts for global variables
        # for top_interface_out
        # mapping Name id to fullid
        # to determine this, we check if we store version 0 on any Name node
        self.globals_accessed_before_mod = {}
        self.used_globals = {}
        # for bot interface in
        self.modified_globals = {} 

        # dict mapping argument index to created argument fullid
        self.arg_index_to_fullid = {}
        self.param_index_to_fullid = {}
    
        # dicts mapping a Name id to its fullid
        self.top_interface_in = {}
        self.top_interface_out = {}
        self.bot_interface_in = {}
        self.bot_interface_out = {}
        # GrFN lambda expressions
        self.top_interface_lambda: str
        self.bot_interface_lambda: str

        # dict mapping Name id to highest version at end of "block"
        self.body_highest_var_vers = {}

        # metadata attributes
        self.grfn_con_src_ref: GrfnContainerSrcRef

        
    def __str__(self):
        return FunctionDef.__str__(self)

class AnnCastList(AnnCastNode):
    def __init__(self, values, source_refs):
        super().__init__(self)
        self.values = values
        self.source_refs = source_refs

        
    def __str__(self):
        return List.__str__(self)

class AnnCastClassDef(AnnCastNode):
    def __init__(self, name, bases, funcs, fields, source_refs):
        super().__init__(self)
        self.name = name
        self.bases = bases
        self.funcs = funcs
        self.fields = fields
        self.source_refs = source_refs

        
    def __str__(self):
        return ClassDef.__str__(self)

class AnnCastLoop(AnnCastNode):
    def __init__(self, expr, body, source_refs):
        super().__init__(self)
        self.expr = expr
        self.body = body
        self.source_refs = source_refs

        # Loop container scope
        self.con_scope: typing.List
        # Function scopestr this Loop node is "living" in 
        self.base_func_scopestr: str = ""

        # dicts mapping a Name id to its string name
        # used for container interfaces
        self.modified_vars: typing.Dict[int, str]
        self.vars_accessed_before_mod: typing.Dict[int, str]
        self.used_vars: typing.Dict[int, str]
        self.top_interface_vars: typing.Dict[int, str]
        self.top_interface_updated_vars: typing.Dict[int, str]
        self.bot_interface_vars: typing.Dict[int, str]

        # dicts mapping Name id to highest version at end of "block"
        self.expr_highest_var_vers = {}
        self.body_highest_var_vers = {}

        # dicts mapping a Name id to variable string name
        # for variables used in the if expr
        self.expr_vars_accessed_before_mod = {}
        self.expr_modified_vars = {}
        self.expr_used_vars = {}

        # dicts mapping a Name id to its fullid
        # initial versions for the top interface come from enclosing scope
        # updated versions for the top interface are versions 
        # at the bottom of the loop after one or more executions of the loop
        self.top_interface_initial = {}
        self.top_interface_updated = {}
        self.top_interface_out = {}
        self.bot_interface_in = {}
        self.bot_interface_out = {}
        self.condition_in = {}
        self.condition_out = {}
        # GrFN VariableNode for the condition node
        self.condition_var = None
        # TODO: decide type of exit
        self.exit = None

        # GrFN lambda expressions
        self.top_interface_lambda: str
        self.bot_interface_lambda: str
        self.condition_lambda: str
        # metadata attributes
        self.grfn_con_src_ref: GrfnContainerSrcRef


        
    def __str__(self):
        return Loop.__str__(self)


class AnnCastModelBreak(AnnCastNode):
    def __init__(self, source_refs):
        super().__init__(self)
        self.source_refs = source_refs

        
    def __str__(self):
        return ModelBreak.__str__(self)

class AnnCastModelContinue(AnnCastNode):
    def __init__(self, node:ModelContinue):
        super().__init__(self)
        self.source_refs = node.source_refs

        
    def __str__(self):
        return ModelContinue.__str__(self)

class AnnCastModelIf(AnnCastNode):
    def __init__(self, expr, body, orelse, source_refs):
        super().__init__(self)
        self.expr = expr
        self.body = body
        self.orelse = orelse
        self.source_refs = source_refs

        # ModelIf container scope
        self.con_scope: typing.List
        # Function scopestr this ModelIf node is "living" in 
        self.base_func_scopestr: str = ""

        # dicts mapping a Name id to string name
        # used for container interfaces
        self.modified_vars: typing.Dict[int, str]
        self.vars_accessed_before_mod: typing.Dict[int, str]
        self.used_vars: typing.Dict[int, str]
        self.top_interface_vars: typing.Dict[int, str]
        self.bot_interface_vars: typing.Dict[int, str]
        # dicts mapping a Name id to variable string name
        # for variables used in the if expr
        self.expr_vars_accessed_before_mod = {}
        self.expr_modified_vars = {}
        self.expr_used_vars = {}
        # dicts mapping Name id to highest version at end of "block"
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
        # GrFN VariableNode for the condition node
        self.condition_var = None

        # GrFN lambda expressions
        self.top_interface_lambda: str
        self.bot_interface_lambda: str
        self.condition_lambda: str
        self.decision_lambda: str

        # metadata attributes
        self.grfn_con_src_ref: GrfnContainerSrcRef
        
    def __str__(self):
        return ModelIf.__str__(self)

class AnnCastModelReturn(AnnCastNode):
    def __init__(self, value, source_refs):
        super().__init__(self)
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
        super().__init__(self)
        self.name = name
        self.body = body
        self.source_refs = source_refs

        # dicts mapping a Name id to string name
        # used for container interfaces
        self.modified_vars: typing.Dict[int, str] = {}
        self.vars_accessed_before_mod: typing.Dict[int, str] = {}
        self.used_vars: typing.Dict[int, str] = {}
        self.con_scope: typing.List

        # metadata attributes
        self.grfn_con_src_ref: GrfnContainerSrcRef
        
    def __str__(self):
        return Module.__str__(self)


class AnnCastName(AnnCastNode):
    def __init__(self, name, id, source_refs):
        super().__init__(self)
        self.name = name
        self.id = id
        self.source_refs = source_refs
        # container_scope is used to aid GrFN generation
        self.con_scope: typing.List = []
        # Function scopestr this Name node is "living" in 
        self.base_func_scopestr: str = ""
        # versions are bound to the cope of the variable
        self.version = None
        self.grfn_id = None

        
    def __str__(self):
        return Name.__str__(self)


class AnnCastNumber(AnnCastNode):
    def __init__(self, number, source_refs):
        super().__init__(self)
        self.number = number
        self.source_refs = source_refs

        
    def __str__(self):
        return Number.__str__(self)

class AnnCastSet(AnnCastNode):
    def __init__(self, values, source_refs):
        super().__init__(self)
        self.values = values
        self.source_refs = source_refs

        
    def __str__(self):
        return Set.__str__(self)

class AnnCastString(AnnCastNode):
    def __init__(self, string, source_refs):
        super().__init__(self)
        self.string = string
        self.source_refs = source_refs

        
    def __str__(self):
        return String.__str__(self)

class AnnCastSubscript(AnnCastNode):
    def __init__(self, value, slice, source_refs):
        super().__init__(self)
        self.value = node.value
        self.slice = node.slice
        self.source_refs = source_refs

        
    def __str__(self):
        return Subscript.__str__(self)

class AnnCastTuple(AnnCastNode):
    def __init__(self, values, source_refs):
        super().__init__(self)
        self.values = values
        self.source_refs = source_refs

        
    def __str__(self):
        return Tuple.__str__(self)

class AnnCastUnaryOp(AnnCastNode):
    def __init__(self, op, value, source_refs):
        super().__init__(self)
        self.op = op
        self.value = value
        self.source_refs = source_refs

        
    def __str__(self):
        return UnaryOp.__str__(self)

class AnnCastVar(AnnCastNode):
    def __init__(self, val, type, source_refs):
        super().__init__(self)
        self.val = val
        self.type = type
        self.source_refs = source_refs

        
    def __str__(self):
        return Var.__str__(self)

