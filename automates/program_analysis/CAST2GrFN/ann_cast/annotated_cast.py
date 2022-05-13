import typing
import difflib


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

from automates.model_assembly.networks import GroundedFunctionNetwork, VariableNode

class PipelineState:
    def __init__(self, ann_nodes: typing.List, grfn2_2: bool):
        self.GENERATE_GRFN_2_2 = grfn2_2
        self.PRINT_DEBUGGING_INFO = False
        self.nodes = ann_nodes
        # populated after IdCollapsePass, and used to give ids to GrFN condition variables
        self.collapsed_id_counter = 0
        # dict mapping FunctionDef container scopestr to its id
        self.func_con_scopestr_to_id = {}
        # dict mapping container scope strings to their nodes
        self.con_scopestr_to_node = {}
        # dict mapping function IDs to their FunctionDef nodes.  
        self.func_id_to_def = {}
        self.grfn_id_to_grfn_var = {}
        # the fullid of a AnnCastName node is a string which includes its 
        # variable name, numerical id, version, and scope
        self.fullid_to_grfn_id = {}
        # `module_node` is simply a reference to the AnnCastModule node
        # FUTURE: to handle multiple modules for Python this will need to be extended
        # for the most part, the module node is used to determine globals
        self.module_node = None
        # GrFN stored after ToGrfnPass
        self.grfn: typing.Optional[GroundedFunctionNetwork] = None

        # flag deciding whether or not to use GE's interpretation of From Source 
        # when populating metadata information
        # 
        # For GE, all instances of a variable which exists in the source code should 
        # be considered from source.  
        # We think this loses information about the GrFN variables we create to facilitate
        # transition between interfaces. That is, we create many GrFN variables which
        # do not literally exist in source, and so don't consider those to be from source
        self.FROM_SOURCE_FOR_GE = True

    def get_nodes(self):
        return self.nodes

    def is_var_local_to_func(self, scopestr: str, id: int):
        """
        Precondition: scopestr is the scopestr of a FunctionDef 
        Check if the variable with id `id` is neither a global nor a formal parameter
        """
        if self.is_global_var(id):
            return False

        func_def_node = self.func_def_node_from_scopestr(scopestr)
        for param in func_def_node.func_args:
            if id == param.val.id:
                return False

        return True

    def is_container(self, scopestr: str): 
        """ 
        Check if scopestr is a container scopestr
        """
        return scopestr in self.con_scopestr_to_node

    def con_node_from_scopestr(self, scopestr: str):
        """
        Precondition: scopestr is a container scopestr
        Return the container node associated with scopestr
        """
        return self.con_scopestr_to_node[scopestr]

    def get_grfn(self) -> typing.Optional[GroundedFunctionNetwork]:
        return self.grfn

    def func_def_exists(self, id: int) -> bool:
        """
        Check if there is a FuncionDef for id
        """
        return id in self.func_id_to_def

    def is_con_scopestr_func_def(self, con_scopestr: str):
        return con_scopestr in  self.func_con_scopestr_to_id

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

    def equiv(self, other): 
        """
        Check if the PipelineState nodes are equivalent to other's
        Used in the test suite
        """
        # FUTURE: once the PiplelineState nodes attribute stores multiple modules,
        # we may need to check that the ordering is consistent.  Currently,
        # CAST and the AnnnotatedCast nodes only have a single module, so this is not a concern
        for i, node in enumerate(self.nodes):
            if not node.equiv(other.nodes[i]):
                # printing diff to help locating difference
                # because we do not overwrite the __str__() methods, 
                # this has limited usefullness, but its better than nothing
                print(f"AnnCast equiv failed:")
                self_lines = str(node).splitlines()
                other_lines = str(other.nodes[i]).splitlines()
                for i, diff in enumerate(difflib.ndiff(self_lines, other_lines)):
                    if diff[0]==' ': 
                        continue
                    print(f"Line {i}: {diff}")

                return False
        
        return True

class AnnCastNode(AstNode):
    def __init__(self,*args, **kwargs):
        super().__init__(self)
        self.expr_str: str = ""

    def to_dict(self):
        result = super().to_dict()
        result["expr_str"] = self.expr_str
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastNode):
            return False
        return self.to_dict() == other.to_dict()

class AnnCastAssignment(AnnCastNode):
    def __init__(self, left, right, source_refs ):
        super().__init__(self)
        self.left = left
        self.right = right
        self.source_refs = source_refs

        self.grfn_assignment: GrfnAssignment

    def to_dict(self):
        result = super().to_dict()
        result["left"] = self.left.to_dict()
        result["right"] = self.right.to_dict()
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastAssignment):
            return False
        return self.to_dict() == other.to_dict()
        
    def __str__(self):
        return Assignment.__str__(self)

class AnnCastAttribute(AnnCastNode):
    def __init__(self, value, attr, source_refs):
        super().__init__(self)
        self.value = value
        self.attr = attr
        self.source_refs = source_refs

    def to_dict(self):
        result = super().to_dict()
        # FUTURE: add value and attr to result
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastAttribute):
            return False
        return self.to_dict() == other.to_dict()
        
    def __str__(self):
        return Attribute.__str__(self)

class AnnCastBinaryOp(AnnCastNode):
    def __init__(self, op, left, right, source_refs):
        super().__init__(self)
        self.op = op
        self.left = left
        self.right = right
        self.source_refs = source_refs

    def to_dict(self):
        result = super().to_dict()
        result["op"] = str(self.op)
        result["left"] = self.left.to_dict()
        result["right"] = self.right.to_dict()
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastBinaryOp):
            return False
        return self.to_dict() == other.to_dict()

    def __str__(self):
        return BinaryOp.__str__(self)

class AnnCastBoolean(AnnCastNode):
    def __init__(self, boolean, source_refs):
        super().__init__(self)
        self.boolean = boolean
        self.source_refs = source_refs

    def to_dict(self):
        result = super().to_dict()
        result["boolean"] = self.boolean
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastBoolean):
            return False
        return self.to_dict() == other.to_dict()
        
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
        self.top_interface_vars = {}
        self.bot_interface_vars = {}
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

    def to_dict(self):
        result = super().to_dict()
        result["func"] = self.func.to_dict()
        result["arguments"] = [arg.to_dict() for arg in self.arguments]
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastCall):
            return False
        return self.to_dict() == other.to_dict()
        
    def __str__(self):
        return Call.__str__(self)

class AnnCastDict(AnnCastNode):
    def __init__(self, keys, values, source_refs):
        super().__init__(self)
        self.keys = keys
        self.values = values
        self.source_refs = source_refs

    def to_dict(self):
        result = super().to_dict()
        # FUTURE: add keys and values to result
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastDict):
            return False
        return self.to_dict() == other.to_dict()

    def __str__(self):
        return Dict.__str__(self)

class AnnCastExpr(AnnCastNode):
    def __init__(self, expr, source_refs):
        super().__init__(self)
        self.expr = expr
        self.source_refs = source_refs

    def to_dict(self):
        result = super().to_dict()
        result["expr"] = self.expr.to_dict()
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastExpr):
            return False
        return self.to_dict() == other.to_dict()
        
    def __str__(self):
        return Expr.__str__(self)

class AnnCastFunctionDef(AnnCastNode):
    def __init__(self, name, func_args, body, source_refs):
        super().__init__(self)
        self.name = name
        self.func_args = func_args
        self.body = body
        self.source_refs = source_refs

        self.con_scope: typing.List

        # For CAST coming from C, we determine if the function 
        # has a return value by looking for a CAST Return node.
        # We do this during the ContainerScopePass.
        # FUTURE: What should be done with CAST coming from Python? 
        # In Python, every function returns something, 
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
        # for now, top_interface_vars and bot_interface_vars only include globals
        # since those variables cross the container boundaries
        self.top_interface_vars: typing.Dict[int, str] = {}
        self.bot_interface_vars: typing.Dict[int, str] = {}
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

        # dummy assignments to handle Python dynamic variable creation
        self.dummy_grfn_assignments = []

    def to_dict(self):
        result = super().to_dict()
        result["name"] = self.name.to_dict()
        result["func_args"] = [arg.to_dict() for arg in self.func_args]
        result["body"] = [node.to_dict() for node in self.body]
        result["con_scope"] = self.con_scope
        result["has_ret_val"] = self.has_ret_val
        # FUTURE: add attributes to enhance test coverage
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastFunctionDef):
            return False
        return self.to_dict() == other.to_dict()
        
    def __str__(self):
        return FunctionDef.__str__(self)

class AnnCastList(AnnCastNode):
    def __init__(self, values, source_refs):
        super().__init__(self)
        self.values = values
        self.source_refs = source_refs

    def to_dict(self):
        result = super().to_dict()
        # FUTURE: add values to result
        # result["values"] = [val.to_dict() for val in self.values]
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastList):
            return False
        return self.to_dict() == other.to_dict()
        
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

    def to_dict(self):
        result = super().to_dict()
        # FUTURE: add attributes to result
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastClassDef):
            return False
        return self.to_dict() == other.to_dict()
        
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
        self.top_interface_vars: typing.Dict[int, str] = {}
        self.top_interface_updated_vars: typing.Dict[int, str] = {}
        self.bot_interface_vars: typing.Dict[int, str] = {}

        # dicts mapping Name id to highest version at end of "block"
        self.expr_highest_var_vers = {}
        self.body_highest_var_vers = {}

        # dicts mapping a Name id to variable string name
        # for variables used in the Loop expr
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

        # GrFN lambda expressions
        self.top_interface_lambda: str
        self.bot_interface_lambda: str
        self.condition_lambda: str
        # metadata attributes
        self.grfn_con_src_ref: GrfnContainerSrcRef

    def to_dict(self):
        result = super().to_dict()
        result["expr"] = self.expr.to_dict()
        result["body"] = [node.to_dict() for node in self.body]
        result["con_scope"] = self.con_scope
        result["base_func_scopestr"] = self.base_func_scopestr
        # FUTURE: add attributes to enhance test coverage
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastLoop):
            return False
        return self.to_dict() == other.to_dict()

    def __str__(self):
        return Loop.__str__(self)


class AnnCastModelBreak(AnnCastNode):
    def __init__(self, source_refs):
        super().__init__(self)
        self.source_refs = source_refs

    def to_dict(self):
        result = super().to_dict()
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastModelBreak):
            return False
        return self.to_dict() == other.to_dict()
        
    def __str__(self):
        return ModelBreak.__str__(self)

class AnnCastModelContinue(AnnCastNode):
    def __init__(self, node:ModelContinue):
        super().__init__(self)
        self.source_refs = node.source_refs

    def to_dict(self):
        result = super().to_dict()
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastModelContinue):
            return False
        return self.to_dict() == other.to_dict()
        
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
        self.top_interface_vars: typing.Dict[int, str] = {}
        self.bot_interface_vars: typing.Dict[int, str] = {}
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
        
    def to_dict(self):
        result = super().to_dict()
        result["expr"] = self.expr.to_dict()
        result["body"] = [node.to_dict() for node in self.body]
        result["orelse"] = [node.to_dict() for node in self.orelse]
        result["con_scope"] = self.con_scope
        result["base_func_scopestr"] = self.base_func_scopestr
        # FUTURE: add attributes to enhance test coverage
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastModelIf):
            return False
        return self.to_dict() == other.to_dict()

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

    def to_dict(self):
        result = super().to_dict()
        result["value"] = self.value.to_dict()
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastModelReturn):
            return False
        return self.to_dict() == other.to_dict()
        
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

    def to_dict(self):
        result = super().to_dict()
        result["name"] = str(self.name)
        result["body"] = [node.to_dict() for node in self.body]
        result["con_scope"] = self.con_scope
        # FUTURE: add attributes to enhance test coverage
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastModule):
            return False
        return self.to_dict() == other.to_dict()
        
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

    def to_dict(self):
        result = super().to_dict()
        result["name"] = self.name
        result["id"] = self.id
        result["version"] = self.version
        result["con_scope"] = self.con_scope
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastName):
            return False
        return self.to_dict() == other.to_dict()
        
    def __str__(self):
        return Name.__str__(self)


class AnnCastNumber(AnnCastNode):
    def __init__(self, number, source_refs):
        super().__init__(self)
        self.number = number
        self.source_refs = source_refs

    def to_dict(self):
        result = super().to_dict()
        result["number"] = self.number
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastNumber):
            return False
        return self.to_dict() == other.to_dict()
        
    def __str__(self):
        return Number.__str__(self)

class AnnCastSet(AnnCastNode):
    def __init__(self, values, source_refs):
        super().__init__(self)
        self.values = values
        self.source_refs = source_refs

    def to_dict(self):
        result = super().to_dict()
        # FUTURE: add values to result
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastSet):
            return False
        return self.to_dict() == other.to_dict()
        
    def __str__(self):
        return Set.__str__(self)

class AnnCastString(AnnCastNode):
    def __init__(self, string, source_refs):
        super().__init__(self)
        self.string = string
        self.source_refs = source_refs

    def to_dict(self):
        result = super().to_dict()
        result["string"] = self.string
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastString):
            return False
        return self.to_dict() == other.to_dict()

        
    def __str__(self):
        return String.__str__(self)

class AnnCastSubscript(AnnCastNode):
    def __init__(self, value, slice, source_refs):
        super().__init__(self)
        self.value = value
        self.slice = slice
        self.source_refs = source_refs

    def to_dict(self):
        result = super().to_dict()
        # FUTURE: add value and slice to result
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastSubscript):
            return False
        return self.to_dict() == other.to_dict()

    def __str__(self):
        return Subscript.__str__(self)

class AnnCastTuple(AnnCastNode):
    def __init__(self, values, source_refs):
        super().__init__(self)
        self.values = values
        self.source_refs = source_refs

    def to_dict(self):
        result = super().to_dict()
        # FUTURE: add values to result
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastTuple):
            return False
        return self.to_dict() == other.to_dict()
        
    def __str__(self):
        return Tuple.__str__(self)

class AnnCastUnaryOp(AnnCastNode):
    def __init__(self, op, value, source_refs):
        super().__init__(self)
        self.op = op
        self.value = value
        self.source_refs = source_refs

    def to_dict(self):
        result = super().to_dict()
        result["op"] = str(self.op)
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastUnaryOp):
            return False
        return self.to_dict() == other.to_dict()
        
    def __str__(self):
        return UnaryOp.__str__(self)

class AnnCastVar(AnnCastNode):
    def __init__(self, val, type, source_refs):
        super().__init__(self)
        self.val = val
        self.type = type
        self.source_refs = source_refs

    def to_dict(self):
        result = super().to_dict()
        result["val"] = self.val.to_dict()
        result["type"] = str(self.type)
        return result

    def equiv(self, other):
        if not isinstance(other, AnnCastVar):
            return False
        return self.to_dict() == other.to_dict()
        
    def __str__(self):
        return Var.__str__(self)
