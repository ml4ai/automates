import typing
import re
import sys
import difflib
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field

from automates.utils.misc import uuid

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
        VariableFromSource, MetadataMethod, VariableCreationReason
        )
from automates.model_assembly.structures import (
    VariableIdentifier,
)

from automates.model_assembly.networks import (
    LambdaNode,
    VariableNode,
    GroundedFunctionNetwork,
    GenericNode
)


# flag deciding whether or not to use GE's interpretation of From Source 
# when populating metadata information
# 
# For GE, all instances of a variable which exists in the source code should 
# be considered from source.  
# We think this loses information about the GrFN variables we create to facilitate
# transition between interfaces. That is, we create many GrFN variables which
# do not literally exist in source, and so don't consider those to be from source
FROM_SOURCE_FOR_GE = True

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
# TODO: Remove
# From Source Creastion Reason constants
# class CreationReason(str, Enum):
#     TOP_IFACE_INTRO = "Variable Introduced for Top Interface"
#     BOT_IFACE_INTRO = "Variable Introduced for Bot Interface"
#     FUNC_RET_VAL = "Function Return Value"
#     FUNC_ARG = "Function Argument"
#     COND_VAR = "Variable Introduced for Conditional Expression"
#     DUP_GLOBAL = "Duplicated Global for FunctionDef Container"
#     DUMMY_ASSIGN = "Dummy Assignment for Interface Propagation"


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

def generate_from_source_metadata(from_source: bool, reason: VariableCreationReason):
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
    return VariableFromSource.from_ann_cast_data(data=data)

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

def add_metadata_from_name_node(grfn_var, name_node):
    """
    Adds metadata to the GrFN VariableNode inferred from the (Ann)CAST Name node

    Currently, all Name nodes are obtained from source, so we generate
    the from source metadata accordingly.
    """
    from_source = True
    from_source_mdata = generate_from_source_metadata(from_source, VariableCreationReason.UNKNOWN)
    span_mdata = generate_variable_node_span_metadata(name_node.source_refs)
    add_metadata_to_grfn_var(grfn_var, from_source_mdata, span_mdata) 

def add_metadata_to_grfn_var(grfn_var, from_source_mdata=None, span_mdata=None, domain_mdata=None):
    if from_source_mdata is None:
        from_source = True
        from_source_mdata = generate_from_source_metadata(True, VariableCreationReason.UNKNOWN)
    
    # if this GrFN variable is from source, and we don't have span metadata, create
    # an blank SourceRef for its span metadata
    if from_source_mdata.from_source and span_mdata is None:
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
    if isinstance(node, (AnnCastNumber, AnnCastBoolean, AnnCastString)):
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
    # TODO: Maybe change this to take an FunctionDef instead of Name node?
    # That might make more sense when calling it
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

def specialized_global_name(node, var_name) -> str:
    """
    Parameters: 
        - node: a AnnCastFunctionDef 
        - var_name: the variable name for the global
    Returns the specialized global name for FunctionDef `func_def_node` 
    """
    return f"{function_container_name(node.name)}_{var_name}"


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
    return build_fullid(node.name, node.id, node.version, con_scope_to_str(node.con_scope))

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

def lambda_var_from_fullid(fullid: str) -> str:
    """
    Return a suitable lambda variable name for variable with fullid `fullid`
    """
    parsed = parse_fullid(fullid)
    return f"{parsed['var_name']}_{parsed['id']}"

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
    # lambda_uuid = str(uuid.uuid4())
    lambda_uuid = GenericNode.create_node_id()
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
    # TODO: update the namespace and scope we provide, e.g. use :: instead of . as delimiter?
    identifier = VariableIdentifier("default_ns", con_scopestr, var_name, version)

    # TODO: change this uid to a UUID and
    # replace the calls to uuid4() in later passes with 
    # GenericNode.create_node_id() 
    # uid = GenericNode.create_node_id()
    uid = build_fullid(var_name, id, version, con_scopestr)
    
    # we initialize the GrFN VariableNode with an empty metadata list.
    # we fill in the metadata later with a call to add_metadata_to_grfn_var()
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
# TODO: move all/most above code to a utility file