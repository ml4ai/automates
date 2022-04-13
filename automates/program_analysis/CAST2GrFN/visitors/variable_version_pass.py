import typing
from collections import defaultdict
from functools import singledispatchmethod

from automates.program_analysis.CAST2GrFN.visitors.annotated_cast import *

class VariableVersionPass:
    def __init__(self, ann_cast: AnnCast):
        self.ann_cast = ann_cast
        self.nodes = self.ann_cast.nodes

        # dict mapping container scopes strs to dicts which
        # map Name id to highest version in that container scope
        self.con_scope_to_highest_var_vers = {}

        for node in self.ann_cast.nodes:
            # when visitor starts, assign_lhs is False
            self.visit(node, False)

    def init_highest_var_vers_dict(self, con_scopestr, var_ids):
        """
        Initialize highest var version dict for scope `con_scopestr`
        If the scope is the module, then use a defaultdict starting at zero
        otherwise, create a dictionary mapping each of the ids to zero
        """
        # TODO: Could we ever have a container with no modified or accessed variables?
        #       Maybe a debugging function that only prints?
        # Yes, if the module container
        # assert(len(var_ids) > 0)
        self.con_scope_to_highest_var_vers[con_scopestr] = {}
        for id in var_ids:
            self.con_scope_to_highest_var_vers[con_scopestr][id] = 0
        print(f"initialized highest_vars_vers_dict {self.con_scope_to_highest_var_vers[con_scopestr]}")
                       

    def get_highest_ver_in_con_scope(self, con_scopestr, id):
        """
        Grab the current version of `id` in scope for `con_scopestr`
        Should only be called after `con_scopestr` is in the `self.con_scope_to_highest_var_vers`
        """
        return self.con_scope_to_highest_var_vers[con_scopestr][id]

    def is_var_in_con_scope(self, con_scopestr: str, id: int):
        return id in self.con_scope_to_highest_var_vers[con_scopestr]

    def incr_version_in_con_scope(self, con_scopestr: str, id: int, var_name: str):
        """
        Grab the next version of `id` in scope for `con_scopestr`
        Should only be called after `con_scopestr` is in the `self.con_scope_to_highest_var_vers`

        Also creates a GrFN variable for the newly added version
        """
        # DEBUGGING
        print(f"incr: id={id}  scope dictionary {con_scopestr}={self.con_scope_to_highest_var_vers[con_scopestr]} ")
        

        if id in self.con_scope_to_highest_var_vers[con_scopestr]:
            self.con_scope_to_highest_var_vers[con_scopestr][id] += 1
        # otherwise, add it as version VAR_INIT_VERSION
        else:
            self.con_scope_to_highest_var_vers[con_scopestr][id] = VAR_INIT_VERSION

        # Create a GrFN variable for the newly created version
        version = self.con_scope_to_highest_var_vers[con_scopestr][id]
        grfn_var = create_grfn_var(var_name, id, version, con_scopestr)
        fullid = build_fullid(var_name, id, version, con_scopestr)
        self.ann_cast.store_grfn_var(fullid, grfn_var)

    def incr_vars_in_con_scope(self, scopestr, vars):
        """
        This will increment all versions of variables in `scopestr` that are
        in the dict `vars` which contains variable ids mapped to AnnCastName nodes
        """
        for var_id, var_name in vars.items():
            self.incr_version_in_con_scope(scopestr, var_id, var_name)

    def populate_interface(self, con_scopestr, vars, interface):
        """
        Parameters:
          - `con_scopestr`: a cached container scope 
          - `vars`: a dict mapping numerical ids to variable names
          - `interface`: a dict mapping numerical variable ids to fullids 
                         (e.g. the top or bottom interface of a container node)

        For each variable from `vars`, put the highest version of that variable
        from container `con_scopestr` into `interface` 
        """
        # add vars to interface
        for id, var_name in vars.items():
            highest_ver = self.get_highest_ver_in_con_scope(con_scopestr, id)
            fullid = build_fullid(var_name, id, highest_ver, con_scopestr)
            interface[id] = fullid

    def populate_loop_interfaces(self, node: AnnCastLoop):
        # populate interfaces and increment versions in previous scope of modified variables
        prev_scopestr = con_scope_to_str(node.con_scope[:-1])
        # populate top interface initial
        # these are versions coming in from enclosing scope
        self.populate_interface(prev_scopestr, node.used_vars, node.top_interface_initial)
        # increment versions of modified vars 
        self.incr_vars_in_con_scope(prev_scopestr, node.modified_vars)
        # populate bot interface out
        self.populate_interface(prev_scopestr, node.modified_vars, node.bot_interface_out)

        # populate "inside" of interfaces
        con_scopestr = con_scope_to_str(node.con_scope)
        # populate top interface updated
        # these are versions of modified variables at the bottom of the loop
        for id, var_name in node.modified_vars.items():
            version = LOOP_VAR_UPDATED_VERSION
            fullid = build_fullid(var_name, id, version, con_scopestr)
            node.top_interface_updated[id] = fullid
        # populate top interface out
        # the top interface chooses between initial and updated versions; 
        # by convention the produced version is `VAR_INIT_VERSION`
        # which is consistent with other containers 
        for id, var_name in node.used_vars.items():
            version = VAR_INIT_VERSION
            fullid = build_fullid(var_name, id, version, con_scopestr)
            node.top_interface_out[id] = fullid
        # populate bot interface in
        # the bot interface takes `VAR_EXIT_VERSION` modified variables
        # During GrFN Variable Creation, these versions will be aliased to 
        # the highest version occuring in the loop expr
        for id, var_name in node.modified_vars.items():
            version = VAR_EXIT_VERSION
            fullid = build_fullid(var_name, id, version, con_scopestr)
            node.bot_interface_in[id] = fullid

    def populate_model_if_interfaces(self, node: AnnCastModelIf):
        # populate interfaces and increment versions in previous scope of modified variables
        prev_scopestr = con_scope_to_str(node.con_scope[:-1])
        # populate top interface in
        self.populate_interface(prev_scopestr, node.used_vars, node.top_interface_in)
        # increment versions 
        self.incr_vars_in_con_scope(prev_scopestr, node.modified_vars)
        # populate bot interface out
        self.populate_interface(prev_scopestr, node.modified_vars, node.bot_interface_out)

        # populate "inside" of interfaces
        con_scopestr = con_scope_to_str(node.con_scope)
        # populate top interface out 
        # by convention the top interface produces version VAR_INIT_VERSION variables
        # and these are propagated to if expr, if body, and else body 
        for id, var_name in node.used_vars.items():
            version = VAR_INIT_VERSION
            fullid = build_fullid(var_name, id, version, con_scopestr)
            node.top_interface_out[id] = fullid
        # populate bot interface in
        # by convention, the bot interface in takes version VAR_EXIT_VERSION variables
        # these versions are produced by the Decision node (which is done during GrFN Variable Creation)
        for id, var_name in node.modified_vars.items():
            version = VAR_EXIT_VERSION
            fullid = build_fullid(var_name, id, version, con_scopestr)
            node.bot_interface_in[id] = fullid

    def func_def_top_interface_args(self, node: AnnCastFunctionDef):
        """
        Creates initial version for each argument and each formal parameter
        Links these argument and parameters through the `top_interface_in` and `top_interface_out`
        """
        # function container is used to scope parameters
        param_con_scopestr = con_scope_to_str(node.con_scope)
        # enclosing container is used to scope arguments
        enclosing_con_scope = node.con_scope[:-1]
        arg_con_scopestr = con_scope_to_str(enclosing_con_scope)

        # create argument and parameter variables
        # argument variables are inputs to the top interface
        # paramter variables are outputs of the top interface
        for i, param in enumerate(node.func_args):
            # argument name and scope str
            arg_name = func_def_argument_name(node, i)

            # parameter name and scopestr
            assert(isinstance(param, AnnCastVar))
            param_name = param.val.name

            # argument and parameter share id, and start with initial version
            id = self.ann_cast.next_collapsed_id()
            version = VAR_INIT_VERSION

            # build and store GrFN variables for argument and parameter
            arg_grfn_var = create_grfn_var(arg_name, id, version, arg_con_scopestr)
            arg_fullid = build_fullid(arg_name, id, version, arg_con_scopestr)
            self.ann_cast.store_grfn_var(arg_fullid, arg_grfn_var)
            # store arg_fullid
            node.arg_index_to_fullid[i] = arg_fullid

            param_grfn_var = create_grfn_var(param_name, id, version, param_con_scopestr)
            param_fullid = build_fullid(param_name, id, version, param_con_scopestr)
            self.ann_cast.store_grfn_var(param_fullid, param_grfn_var)
            # store param_fullid
            node.param_index_to_fullid[i] = param_fullid

            # link argument and parameter through top interface
            node.top_interface_in[id] = arg_fullid
            node.top_interface_out[id] = param_fullid

        print(f"For FunctionDef {node.name.name}")
        print("After func_def_top_iface_args():")
        print(f"\ttop_interface_in = {node.top_interface_in}")
        print(f"\ttop_interface_out = {node.top_interface_out}")

    def func_def_ret_val_creation(self, node: AnnCastFunctionDef):
        """
        Creates two GrFN variables for the FunctionDef's return value.
        One is in the interior of the container and links
        to the bot interface in.  The other is outside the container and
        links to the bot interface out.
        """
        # Create new GrFN for return value for bot interface in and bot interface out
        var_name = func_def_ret_val_name(node)
        id = self.ann_cast.next_collapsed_id()
        version = VAR_INIT_VERSION

        # interior container scope
        func_scopestr = con_scope_to_str(node.con_scope)

        in_ret_val = create_grfn_var(var_name, id, version, func_scopestr)
        in_fullid = build_fullid(var_name, id, version, func_scopestr)
        self.ann_cast.store_grfn_var(in_fullid, in_ret_val)

        # exterior container scope
        enclosing_con = node.con_scope[:-1]
        enclosing_scopestr = con_scope_to_str(enclosing_con)
        out_ret_val = create_grfn_var(var_name, id, version, enclosing_scopestr)
        out_fullid = build_fullid(var_name, id, version, enclosing_scopestr)
        self.ann_cast.store_grfn_var(out_fullid, out_ret_val)

        # store created fullid and grfn_id in node's ret_val
        node.out_ret_val[id] = out_fullid
        node.in_ret_val[id] = in_fullid
        # link ret values on bot interface
        node.bot_interface_in[id] = in_fullid
        node.bot_interface_out[id] = out_fullid

        print(f"For FunctionDef {node.name.name}")
        print("\tAfter func_def_ret_val_creation():")
        print(f"\ttop_interface_in = {node.top_interface_in}")
        print(f"\ttop_interface_out = {node.top_interface_out}")

    def add_globals_to_main_func_def_interfaces(self, node: AnnCastFunctionDef):
        """
        Populates top and bot interface of main FunctionDef with global variables
          - Adds incoming global variable version to top_interface_in
          - Increments modified globals versions in enclosing scope
          - Adds incremented version to bot_interface_out
          - Creates VAR_INIT_VERSION global variables and adds to top_interface_out
          - Add `body_highest_var_vers` global variables to bot_interface_in
        """
        # in the enclosing scope, increment all versions of global variables
        # that are modified by main
        enclosing_con_scope = node.con_scope[:-1]
        enclosing_scopestr = con_scope_to_str(enclosing_con_scope)

        # add globals to exterior interfaces
        # TODO: if we only want globals which are accessed before modification in to come 
        # into the top interface, then we need to rethink the top interface of Loop and ModelIf
        # containers, since their top interfaces are all used variables
        # top_interface_globals = node.globals_accessed_before_mod
        # add global variables to top_interface_in
        # these are all used globals
        top_interface_globals = node.used_globals
        self.populate_interface(enclosing_scopestr, top_interface_globals, node.top_interface_in)
        # the bot interface globals are all modified globals
        bot_interface_globals = node.modified_globals
        # increment versions of all modified global variables
        self.incr_vars_in_con_scope(enclosing_scopestr, bot_interface_globals)
        # add modified globals to bot interface out
        self.populate_interface(enclosing_scopestr, bot_interface_globals, node.bot_interface_out)

        # add globals to interior interfaces
        # interior container scope
        func_scopestr = con_scope_to_str(node.con_scope)
        # create globals for top_interface_out and bot interface in
        # by convention the top interface produces version VAR_INIT_VERSION variables
        # by convention, the bot interface in takes version VAR_EXIT_VERSION variables
        for id, var_name in top_interface_globals.items():
            version = VAR_INIT_VERSION
            init_fullid = build_fullid(var_name, id, version, func_scopestr)
            init_global = create_grfn_var(var_name, id, version, func_scopestr)
            self.ann_cast.store_grfn_var(init_fullid, init_global)
            node.top_interface_out[id] = init_fullid
    
        # we do not create the GrFN VariableNode for the highest version global
        # here, since it is done while visitng Assignment node during GrfnVarCreation pass
        for id, var_name in bot_interface_globals.items():
            version = node.body_highest_var_vers[id]
            exit_fullid = build_fullid(var_name, id, version, func_scopestr)
            node.bot_interface_in[id] = exit_fullid

        print(f"For FunctionDef {node.name.name}")
        print("\tAfter add_globals_to_main_func_def_interfaces():")
        print(f"\ttop_interface_in = {node.top_interface_in}")
        print(f"\ttop_interface_out = {node.top_interface_out}")

    def add_globals_to_non_main_func_def_interfaces(self, node: AnnCastFunctionDef):
        """
        Populates top and bot interface of FunctionDef with global variables
        For each global, we make an addtional global whose name is specialized to
        this function.  This is to separate the globals that "main" uses
        from the globals that are used in other FunctionDef's because of main's
        special role.
          - Creates VAR_INIT_VERSION version for each specialized global and
            Links these specialized globals through the `top_interface_in` and `top_interface_out`
          - Creates VAR_EXIT_VERSION version for each specialized global and
            Links these specialized globals through the `bot_interface_in` and `bot_interface_out`
        """
        enclosing_con_scope = node.con_scope[:-1]
        enclosing_scopestr = con_scope_to_str(enclosing_con_scope)
        # interior container scope
        func_scopestr = con_scope_to_str(node.con_scope)

        # TODO: if we only want globals which are accessed before modification in to come 
        # into the top interface, then we need to rethink the top interface of Loop and ModelIf
        # containers, since their top interfaces are all used variables
        # top_interface_globals = node.globals_accessed_before_mod
        # add global variables to top_interface_in
        # these are all used globals
        top_interface_globals = node.used_globals
        # the bot interface globals are all modified globals
        bot_interface_globals = node.modified_globals

        # create specialized globals for top interface
        # by convention the top interface produces version VAR_INIT_VERSION variables
        version = VAR_INIT_VERSION
        for var_name in top_interface_globals.values():
            id = self.ann_cast.next_collapsed_id()
            # exterior specialized top global
            in_fullid = build_fullid(var_name, id, version, enclosing_scopestr)
            in_global = create_grfn_var(var_name, id, version, enclosing_scopestr)
            self.ann_cast.store_grfn_var(in_fullid, in_global)
            node.top_interface_in[id] = in_fullid
            # interior specialized top global
            out_fullid = build_fullid(var_name, id, version, func_scopestr)
            out_global = create_grfn_var(var_name, id, version, func_scopestr)
            self.ann_cast.store_grfn_var(out_fullid, out_global)
            node.top_interface_out[id] = out_fullid
    
        # create specialized globals for bot interface
        # by convention, the bot interface in takes version VAR_EXIT_VERSION variables
        version = VAR_EXIT_VERSION
        for var_name in bot_interface_globals.values():
            id = self.ann_cast.next_collapsed_id()
            # interior specialized bot global
            in_fullid = build_fullid(var_name, id, version, func_scopestr)
            in_global = create_grfn_var(var_name, id, version, func_scopestr)
            self.ann_cast.store_grfn_var(in_fullid, in_global)
            node.top_interface_in[id] = in_fullid
            # exterior specialized bot global
            out_fullid = build_fullid(var_name, id, version, enclosing_scopestr)
            out_global = create_grfn_var(var_name, id, version, enclosing_scopestr)
            self.ann_cast.store_grfn_var(out_fullid, out_global)
            node.top_interface_out[id] = out_fullid

        print(f"For FunctionDef {node.name.name}")
        print("\tAfter add_globals_to_non_main_func_def_interfaces():")
        print(f"\ttop_interface_in = {node.top_interface_in}")
        print(f"\ttop_interface_out = {node.top_interface_out}")

    def populate_call_top_interface_with_args_and_params(self, node: AnnCastCall):
        """
        Creates initial version for each argument and each formal parameter
        Links these argument and parameters through the `top_interface_in` and `top_interface_out`
       
        During GrfnAssignmentPass, 
        for each argument, creates a `GrfnAssignment` which stores the assignment `LambdaNode`
        """
        # call container is used to scope parameters
        call_con_name = call_container_name(node)

        # create argument and parameter variables
        # argument variables are inputs to the top interface
        # paramter variables are outputs of the top interface
        # if we are generating GrFN 2.2, we would like the parameter to lie in the 
        # copied function def container, we do this by aliasing versions during GrfnVarCreation pass
        for i, n in enumerate(node.arguments):
            # argument name and scope str
            arg_name = call_argument_name(node, i)
            arg_con_scopestr = con_scope_to_str(node.func.con_scope)

            # parameter name and scopestr
            param_name = call_param_name(node, i)
            param_con_scopestr = con_scope_to_str(node.func.con_scope + [call_con_name])
            

            # argument and parameter share id, and start with initial version
            id = self.ann_cast.next_collapsed_id()
            version = VAR_INIT_VERSION

            # build and store GrFN variables for argument and parameter
            arg_grfn_var = create_grfn_var(arg_name, id, version, arg_con_scopestr)
            arg_fullid = build_fullid(arg_name, id, version, arg_con_scopestr)
            self.ann_cast.store_grfn_var(arg_fullid, arg_grfn_var)
            # store arg_fullid
            node.arg_index_to_fullid[i] = arg_fullid

            param_grfn_var = create_grfn_var(param_name, id, version, param_con_scopestr)
            param_fullid = build_fullid(param_name, id, version, param_con_scopestr)
            self.ann_cast.store_grfn_var(param_fullid, param_grfn_var)
            # store param_fullid
            node.param_index_to_fullid[i] = param_fullid

            # link argument and parameter through top interface
            node.top_interface_in[id] = arg_fullid
            node.top_interface_out[id] = param_fullid


        print("After create_call_args_and_params():")
        print(f"\ttop_interface_in = {node.top_interface_in}")
        print(f"\ttop_interface_out = {node.top_interface_out}")

    def populate_call_bot_interface_with_ret_val(self, node: AnnCastCall):
        """
        Creates two GrFN variables for the Call's return value.
        One is in the interior of the container and links
        to the bot interface in.  The other is outside the container and
        links to the bot interface out.
        """
        # Create new GrFN for return value for bot interface in and bot interface out
        var_name = call_ret_val_name(node)
        id = self.ann_cast.next_collapsed_id()
        version = VAR_INIT_VERSION

        # interior container scope
        call_con_scopestr = con_scope_to_str(node.func.con_scope + [call_container_name(node)])

        in_ret_val = create_grfn_var(var_name, id, version, call_con_scopestr)
        in_fullid = build_fullid(var_name, id, version, call_con_scopestr)
        self.ann_cast.store_grfn_var(in_fullid, in_ret_val)

        # exterior container scope
        con_scopestr = con_scope_to_str(node.func.con_scope)
        out_ret_val = create_grfn_var(var_name, id, version, con_scopestr)
        out_fullid = build_fullid(var_name, id, version, con_scopestr)
        self.ann_cast.store_grfn_var(out_fullid, out_ret_val)

        # store created fullid and grfn_id in node's ret_val
        node.out_ret_val[id] = out_fullid
        node.in_ret_val[id] = in_fullid
        # link ret values on bot interface
        node.bot_interface_in[id] = in_fullid
        node.bot_interface_out[id] = out_fullid

    def grfn_2_2_call_top_interface_args(self, node: AnnCastCall):
        """
        Creates initial version for each argument and each formal parameter
        Links these argument and parameters through the `top_interface_in` and `top_interface_out`
       
        During GrfnAssignmentPass, 
        for each argument, creates a `GrfnAssignment` which stores the assignment `LambdaNode`
        """
        # call container is used to scope parameters
        call_con_name = call_container_name(node)

        # create argument and parameter variables
        # argument variables are inputs to the top interface
        # paramter variables are outputs of the top interface
        # if we are generating GrFN 2.2, we would like the parameter to lie in the 
        # copied function def container, we do this by aliasing versions during GrfnVarCreation pass
        for i, n in enumerate(node.arguments):
            # argument name and scope str
            arg_name = call_argument_name(node, i)
            arg_con_scopestr = con_scope_to_str(node.func.con_scope)

            # parameter name and scopestr
            param = node.func_def_copy.func_args[i]
            assert(isinstance(param, AnnCastVar))
            param_name = param.val.name
            param_con_scopestr = con_scope_to_str(node.func.con_scope + [call_con_name])
            

            # argument and parameter share id, and start with initial version
            id = self.ann_cast.next_collapsed_id()
            version = VAR_INIT_VERSION

            # build and store GrFN variables for argument and parameter
            arg_grfn_var = create_grfn_var(arg_name, id, version, arg_con_scopestr)
            arg_fullid = build_fullid(arg_name, id, version, arg_con_scopestr)
            self.ann_cast.store_grfn_var(arg_fullid, arg_grfn_var)
            # store arg_fullid
            node.arg_index_to_fullid[i] = arg_fullid

            param_grfn_var = create_grfn_var(param_name, id, version, param_con_scopestr)
            param_fullid = build_fullid(param_name, id, version, param_con_scopestr)
            self.ann_cast.store_grfn_var(param_fullid, param_grfn_var)
            # store param_fullid
            node.param_index_to_fullid[i] = param_fullid

            # link argument and parameter through top interface
            node.top_interface_in[id] = arg_fullid
            node.top_interface_out[id] = param_fullid


        print("After create_call_args_and_params():")
        print(f"\ttop_interface_in = {node.top_interface_in}")
        print(f"\ttop_interface_out = {node.top_interface_out}")

    def grfn_2_2_call_ret_val_creation(self, node: AnnCastCall):
        """
        Creates two GrFN variables for the Call's return value.
        One is in the interior of the container and links
        to the bot interface in.  The other is outside the container and
        links to the bot interface out.

        Note: the ret_val variables going through the Call's bot interface
        are consistent between GrFN 2.2 and GrFN 3
        """
        # Create new GrFN for return value for bot interface in and bot interface out
        var_name = call_ret_val_name(node)
        id = self.ann_cast.next_collapsed_id()
        version = VAR_INIT_VERSION

        # interior container scope
        call_con_scopestr = con_scope_to_str(node.func.con_scope + [call_container_name(node)])

        in_ret_val = create_grfn_var(var_name, id, version, call_con_scopestr)
        in_fullid = build_fullid(var_name, id, version, call_con_scopestr)
        self.ann_cast.store_grfn_var(in_fullid, in_ret_val)

        # exterior container scope
        con_scopestr = con_scope_to_str(node.func.con_scope)
        out_ret_val = create_grfn_var(var_name, id, version, con_scopestr)
        out_fullid = build_fullid(var_name, id, version, con_scopestr)
        self.ann_cast.store_grfn_var(out_fullid, out_ret_val)

        # store created fullid and grfn_id in node's ret_val
        node.out_ret_val[id] = out_fullid
        node.in_ret_val[id] = in_fullid
        # link ret values on bot interface
        node.bot_interface_in[id] = in_fullid
        node.bot_interface_out[id] = out_fullid

        # also, store the created ret_val in the copied function def
        # this is done so that we can assign to the ret val when
        # parsing return statements
        node.func_def_copy.in_ret_val[id] = in_fullid

    def add_globals_to_grfn_2_2_call_interfaces(self, node: AnnCastCall):
        """
        Populates top and bot interface with global variables
          - Adds incoming global variable version to top_interface_in
          - Increments modified globals versions in enclosing scope
          - Adds incremented version to bot_interface_out
          - Creates VAR_INIT_VERSION global variables in Call contianer scope and 
            adds them to top_interface_out
          - Creates VAR_INIT_VERSION global variables in copied FunctionDef scope and 
            aliases them to their corresponding Call container scope globals
          - Creates VAR_EXIT_VERSION global variables and adds to bot_interface_in
        """
        # in the current scope, increment all versions of global variables
        # that are modified by this call
        # the calling container scope is stored in the Call's AnnCastName node
        calling_scopestr = con_scope_to_str(node.func.con_scope)

        # add globals to exterior interfaces
        # TODO: if we only want globals which are accessed before modification in to come 
        # into the top interface, then we need to rethink the top interface of Loop and ModelIf
        # containers, since their top interfaces are all used variables
        # top_interface_globals = node.globals_accessed_before_mod
        # add global variables to top_interface_in
        # these are all used globals
        top_interface_globals = node.func_def_copy.used_globals
        self.populate_interface(calling_scopestr, top_interface_globals, node.top_interface_in)
        # the bot interface globals are all modified globals
        bot_interface_globals = node.func_def_copy.modified_globals
        # increment versions of all modified global variables
        self.incr_vars_in_con_scope(calling_scopestr, bot_interface_globals)
        # add modified globals to bot interface out
        self.populate_interface(calling_scopestr, bot_interface_globals, node.bot_interface_out)

        # add globals to interior interfaces
        # interior container scope
        call_con_scopestr = con_scope_to_str(node.func.con_scope + [call_container_name(node)])
        copied_func_scopestr = con_scope_to_str(node.func_def_copy.con_scope)
        # create globals for top_interface_out and bot interface in
        # by convention the top interface produces version VAR_INIT_VERSION variables
        # by convention, the bot interface in takes version VAR_EXIT_VERSION variables
        for id, var_name in top_interface_globals.items():
            version = VAR_INIT_VERSION
            call_init_fullid = build_fullid(var_name, id, version, call_con_scopestr)
            call_init_global = create_grfn_var(var_name, id, version, call_con_scopestr)
            self.ann_cast.store_grfn_var(call_init_fullid, call_init_global)
            node.top_interface_out[id] = call_init_fullid

            func_copy_init_fullid = build_fullid(var_name, id, version, copied_func_scopestr)
            func_copy_init_global = create_grfn_var(var_name, id, version, copied_func_scopestr)
            self.ann_cast.store_grfn_var(func_copy_init_fullid, func_copy_init_global)
            self.ann_cast.alias_grfn_vars(func_copy_init_fullid, call_init_fullid)
    
        for id, var_name in bot_interface_globals.items():
            version = VAR_EXIT_VERSION
            exit_fullid = build_fullid(var_name, id, version, call_con_scopestr)
            exit_global = create_grfn_var(var_name, id, version, call_con_scopestr)
            self.ann_cast.store_grfn_var(exit_fullid, exit_global)
            node.bot_interface_in[id] = exit_fullid

    # TODO: this is unused, and code is not correct
    # we need to split into two implementations, one for when we have the functionDef
    # and one for when we don't have it
    def add_globals_to_call_interfaces(self, node: AnnCastCall):
        """
        Populates top and bot interface with global variables
          - Adds incoming global variable version to top_interface_in
          - Increments modified globals versions in enclosing scope
          - Adds incremented version to bot_interface_out
          - Creates VAR_INIT_VERSION global variables and adds to top_interface_out
          - Creates VAR_EXIT_VERSION global variables and adds to bot_interface_in
        """
        # in the current scope, increment all versions of global variables
        # that are modified by this call
        # the calling container scope is stored in the Call's AnnCastName node
        calling_scopestr = con_scope_to_str(node.func.con_scope)

        # add globals to exterior interfaces
        # TODO: if we only want globals which are accessed before modification in to come 
        # into the top interface, then we need to rethink the top interface of Loop and ModelIf
        # containers, since their top interfaces are all used variables
        # top_interface_globals = node.globals_accessed_before_mod
        # add global variables to top_interface_in
        # these are all used globals
        top_interface_globals = node.func_def_copy.used_globals
        self.populate_interface(calling_scopestr, top_interface_globals, node.top_interface_in)
        # the bot interface globals are all modified globals
        bot_interface_globals = node.func_def_copy.modified_globals
        # increment versions of all modified global variables
        self.incr_vars_in_con_scope(calling_scopestr, bot_interface_globals)
        # add modified globals to bot interface out
        self.populate_interface(calling_scopestr, bot_interface_globals, node.bot_interface_out)

        # add globals to interior interfaces
        # interior container scope
        call_con_scopestr = con_scope_to_str(node.func.con_scope + [call_container_name(node)])
        # create globals for top_interface_out and bot interface in
        # by convention the top interface produces version VAR_INIT_VERSION variables
        # by convention, the bot interface in takes version VAR_EXIT_VERSION variables
        for id, var_name in top_interface_globals.items():
            version = VAR_INIT_VERSION
            init_fullid = build_fullid(var_name, id, version, call_con_scopestr)
            init_global = create_grfn_var(var_name, id, version, call_con_scopestr)
            self.ann_cast.store_grfn_var(init_fullid, init_global)
            node.top_interface_out[id] = init_fullid
    
        for id, var_name in bot_interface_globals.items():
            version = VAR_EXIT_VERSION
            exit_fullid = build_fullid(var_name, id, version, call_con_scopestr)
            exit_global = create_grfn_var(var_name, id, version, call_con_scopestr)
            self.ann_cast.store_grfn_var(exit_fullid, exit_global)
            node.bot_interface_in[id] = exit_fullid

    def visit(self, node: AnnCastNode, assign_lhs: bool):
        # type(node) is a string which looks like
        # "class '<path.to.class.ClassName>'"
        class_name = str(type(node))
        last_dot = class_name.rfind(".")
        class_name = class_name[last_dot + 1 : -2]
        print(f"\nProcessing node type {class_name}")
        return self._visit(node, assign_lhs)

    @singledispatchmethod
    def _visit(self, node: AnnCastNode, assign_lhs: bool):
        """
        Visit each AnnCastNode
        Parameters:
          - `assign_lhs`: this denotes whether we are visiting the LHS or RHS of an AnnCastAssignment
                      This is used to determine whether a variable (AnnCastName node) is
                      accessed or modified in that context
        """
        raise Exception(f"Unimplemented AST node of type: {type(node)}")

    def visit_node_list(self, node_list: typing.List[AnnCastNode], assign_lhs):
        return [self.visit(node, assign_lhs) for node in node_list]

    @_visit.register
    def visit_assignment(self, node: AnnCastAssignment, assign_lhs: bool):
        # TODO: what if the rhs has side-effects
        self.visit(node.right, assign_lhs)
        assert isinstance(node.left, AnnCastVar)
        self.visit(node.left, True)

    @_visit.register
    def visit_attribute(self, node: AnnCastAttribute, assign_lhs: bool):
        pass

    @_visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp, assign_lhs: bool):
        # visit LHS first
        self.visit(node.left, assign_lhs)

        # visit RHS second
        self.visit(node.right, assign_lhs)

    @_visit.register
    def visit_boolean(self, node: AnnCastBoolean, assign_lhs: bool):
        pass

    # TODO: Update
    @_visit.register
    def visit_call(self, node: AnnCastCall, assign_lhs: bool):
        assert isinstance(node.func, AnnCastName)
        
        if node.is_grfn_2_2:
            self.visit_call_grfn_2_2(node, assign_lhs)
            return
        
        self.visit_node_list(node.arguments, assign_lhs)
        # populate call nodes's top interface with arguments
        # The pattern for the top interface is as follows:
        # For each argument, we create a GrFN variable using the arguments index
        # E.g. Arg0, Arg1, ...
        # top interface inputs: Arg0, Arg1,...
        # top interface outputs: NamedParam0, NamedParam1, ...

        # TODO: separate the cases if we have the FuncionDef, and if we don't
        # if we have the functiondef, we can populate parameter names, retval, and globals
        # if we don't we need to provide some default interface
        # populate top interface assuming no FunctionDef 
        self.populate_call_top_interface_with_args_and_params(node)

        # add return value to bot interface out
        # TODO: Can we infer if it has a return value?
        self.populate_call_bot_interface_with_ret_val(node)
        # self.add_globals_to_call_interfaces(node)


    def visit_call_grfn_2_2(self, node: AnnCastCall, assign_lhs: bool):
        assert isinstance(node.func, AnnCastName)
        self.visit_node_list(node.arguments, assign_lhs)
        # populate call nodes's top interface with arguments
        # The pattern for the top interface is as follows:
        # For each argument, we create a GrFN variable using the arguments index
        # E.g. Arg0, Arg1, ...
        # top interface inputs: Arg0, Arg1,...
        # top interface outputs: NamedParam0, NamedParam1, ...
        self.grfn_2_2_call_top_interface_args(node)

        # add return value to bot interface out if function_copy has a ret_val
        if node.func_def_copy.has_ret_val:
            self.grfn_2_2_call_ret_val_creation(node)

        # we visit the FunctionDef copy first, so that we know
        # the global variables which are accessed before they are modified
        # this allows us to correctly set up the top interface
        call_assign_lhs = False
        self.visit_function_def_copy(node.func_def_copy, call_assign_lhs)
        self.add_globals_to_grfn_2_2_call_interfaces(node)

    

    @_visit.register
    def visit_class_def(self, node: AnnCastClassDef, assign_lhs: bool):
    # TODO: How to handle class definitions?
        pass

    @_visit.register
    def visit_dict(self, node: AnnCastDict, assign_lhs: bool):
        pass

    @_visit.register
    def visit_expr(self, node: AnnCastExpr, assign_lhs: bool):
        self.visit(node.expr, assign_lhs)

    def visit_function_def_copy(self, node: AnnCastFunctionDef, assign_lhs: bool):
        """
        Used for GrFN 2.2 Generation
        """
        # Initialize scope_to_highest_var_vers
        con_scopestr = con_scope_to_str(node.con_scope)
        # create VAR_INIT_VERSION of any modified or accessed variables
        self.init_highest_var_vers_dict(con_scopestr, node.used_vars.keys())
        
        # visit children
        self.visit_node_list(node.func_args, assign_lhs)
        self.visit_node_list(node.body, assign_lhs)

        # store highest var version
        node.body_highest_var_vers = self.con_scope_to_highest_var_vers[con_scopestr]

        # DEBUGGING
        print(f"\nFor FUNCTION COPY: {con_scopestr}")
        print(f"  BodyHighestVers: {node.body_highest_var_vers}")

    @_visit.register
    def visit_function_def(self, node: AnnCastFunctionDef, assign_lhs: bool):
        # Initialize scope_to_highest_var_vers
        con_scopestr = con_scope_to_str(node.con_scope)
        # create versions 0 of any modified or accessed variables
        self.init_highest_var_vers_dict(con_scopestr, node.used_vars.keys())
        
        # visit children
        self.visit_node_list(node.func_args, assign_lhs)
        self.visit_node_list(node.body, assign_lhs)

        # store highest var version
        node.body_highest_var_vers = self.con_scope_to_highest_var_vers[con_scopestr]

        # populate FunctionDef nodes's top interface with arguments
        # The pattern for the top interface is as follows:
        # For each argument, we create a GrFN variable using the arguments index
        # E.g. Arg0, Arg1, ...
        # top interface inputs: Arg0, Arg1,...
        # top interface outputs: NamedParam0, NamedParam1, ...
        self.func_def_top_interface_args(node)

        # add return value to bot interface out if functiondef has a ret_val
        if node.has_ret_val:
            self.func_def_ret_val_creation(node)

        # add globals to functiondef interfaces
        if is_func_def_main(node):
            self.add_globals_to_main_func_def_interfaces(node)
        else: 
            self.add_globals_to_non_main_func_def_interfaces(node)

        # DEBUGGING
        print(f"\nFor FUNCTION: {con_scopestr}")
        print(f"  BodyHighestVers: {node.body_highest_var_vers}")

    @_visit.register
    def visit_list(self, node: AnnCastList, assign_lhs: bool):
        self.visit_node_list(node.values, assign_lhs)

    @_visit.register
    def visit_loop(self, node: AnnCastLoop, assign_lhs: bool):
        # Initialize scope_to_highest_var_version
        expr_scopestr = con_scope_to_str(node.con_scope + [LOOPEXPR])
        body_scopestr = con_scope_to_str(node.con_scope + [LOOPBODY])

        # Initialize LoopExpr
        # create versions 0 of any modified or accessed variables
        self.init_highest_var_vers_dict(expr_scopestr, node.used_vars.keys())

        # Initialize LoopBody
        # create versions 0 of any modified or accessed variables
        self.init_highest_var_vers_dict(body_scopestr, node.used_vars.keys())

        # visit children
        self.visit(node.expr, assign_lhs)
        self.visit_node_list(node.body, assign_lhs)

        # store highest var version
        node.expr_highest_var_vers = self.con_scope_to_highest_var_vers[expr_scopestr]
        node.body_highest_var_vers = self.con_scope_to_highest_var_vers[body_scopestr]

        # populate all of this loops interfaces
        self.populate_loop_interfaces(node)

        # DEBUGGING
        print(f"\nFor LOOP: {con_scope_to_str(node.con_scope)}")
        print(f"  ExprHighestVers: {node.expr_highest_var_vers}")
        print(f"  BodyHighestVers: {node.body_highest_var_vers}")

    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak, assign_lhs: bool):
        pass

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue, assign_lhs: bool):
        pass

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf, assign_lhs: bool):
        # Initialize scope_to_highest_var_version
        expr_scopestr = con_scope_to_str(node.con_scope + [IFEXPR])
        ifbody_scopestr = con_scope_to_str(node.con_scope + [IFBODY])
        elsebody_scopestr = con_scope_to_str(node.con_scope + [ELSEBODY])
        # initialize IfExpr
        # create versions 0 of any modified or accessed variables
        self.init_highest_var_vers_dict(expr_scopestr, node.used_vars.keys())

        # initialize IfBody
        # create versions 0 of any modified or accessed variables
        self.init_highest_var_vers_dict(ifbody_scopestr, node.used_vars.keys())

        # initialize ElseBody
        # create versions 0 of any modified or accessed variables
        self.init_highest_var_vers_dict(elsebody_scopestr, node.used_vars.keys())

        # visit children
        self.visit(node.expr, assign_lhs)
        self.visit_node_list(node.body, assign_lhs)
        self.visit_node_list(node.orelse, assign_lhs)

        # store highest var versions
        node.expr_highest_var_vers = self.con_scope_to_highest_var_vers[expr_scopestr]
        node.ifbody_highest_var_vers = self.con_scope_to_highest_var_vers[ifbody_scopestr]
        node.elsebody_highest_var_vers = self.con_scope_to_highest_var_vers[elsebody_scopestr]

        # populate interfaces
        self.populate_model_if_interfaces(node)

        # DEBUGGING
        print(f"\nFor IF: {con_scope_to_str(node.con_scope)}")
        print(f"  ExprHighestVers: {node.expr_highest_var_vers}")
        print(f"  IfBodyHighestVers: {node.ifbody_highest_var_vers}")
        print(f"  ElseBodyHighestVers: {node.elsebody_highest_var_vers}")

    @_visit.register
    def visit_return(self, node: AnnCastModelReturn, assign_lhs: bool):
        self.visit(node.value, assign_lhs)

    @_visit.register
    def visit_module(self, node: AnnCastModule, assign_lhs: bool):
        con_scopestr = con_scope_to_str(node.con_scope)
        # create VAR_INIT_VERSION of any modified or accessed variables
        self.init_highest_var_vers_dict(con_scopestr, node.used_vars.keys())
        self.visit_node_list(node.body, assign_lhs)

    @_visit.register
    def visit_name(self, node: AnnCastName, assign_lhs: bool):
        con_scopestr = con_scope_to_str(node.con_scope)
        if assign_lhs:
            print(f"On LHS: {node.name}:{node.id}" )
            # if not in, skip this increment
            self.incr_version_in_con_scope(con_scopestr, node.id, node.name)
            print("after incr scope dict is",  self.con_scope_to_highest_var_vers[con_scopestr])
        node.version = self.get_highest_ver_in_con_scope(con_scopestr, node.id)

        # we determine the globals which are either modified or accessed before modification here,
        # and store them in the associated FunctionDef node.
        # To determine whether the global is accessed before its modified, 
        # we check if this node's version is VAR_INIT_VERSION 
        # Note: we also skip the module container scope since these attributes 
        # are only needed to create interfaces, and the module does not currently have an interface
        
        if self.ann_cast.is_global_var(node.id) and con_scopestr != MODULE_SCOPE:
            func_node = self.ann_cast.get_func_node_from_scopestr(node.base_func_scopestr)

            if node.version == VAR_INIT_VERSION:  # only occurs on RHS
                func_node.globals_accessed_before_mod[node.id] = node.name
            # if we are assigning to the global, then it is modified
            elif assign_lhs:
                func_node.modified_globals[node.id] = node.name
            # no matter what, add to used_globals dict
            func_node.used_globals[node.id] = node.name

            # due to GrFN 2.2 FunctionDef copying, we need to also propagate up the
            # globals accessed before modification and modified globals to 
            # scopes higher than base_func_scopestr
            if GENERATE_GRFN_2_2:
                scopestr = ""
                for index, name in enumerate(node.con_scope):
                    # add separator between container scope component names
                    if index != 0:
                        scopestr += f"{CON_STR_SEP}"
                    scopestr += f"{name}"

                    # skip if scopestr is not a function scope
                    if scopestr not in self.ann_cast.func_con_scopestr_to_id:
                        continue

                    # otherwise, add to correct globals tracking dict
                    func_node = self.ann_cast.get_func_node_from_scopestr(scopestr)

                    if node.version == VAR_INIT_VERSION:  # only occurs on RHS
                        func_node.globals_accessed_before_mod[node.id] = node.name
                    # if we are assigning to the global, then it is modified
                    elif assign_lhs:
                        func_node.modified_globals[node.id] = node.name
                    # no matter what, add to used_globals dict
                    func_node.used_globals[node.id] = node.name

    @_visit.register
    def visit_number(self, node: AnnCastNumber, assign_lhs: bool):
        pass

    @_visit.register
    def visit_set(self, node: AnnCastSet, assign_lhs: bool):
        pass

    @_visit.register
    def visit_string(self, node: AnnCastString, assign_lhs: bool):
        pass

    @_visit.register
    def visit_subscript(self, node: AnnCastSubscript, assign_lhs: bool):
        pass

    @_visit.register
    def visit_tuple(self, node: AnnCastTuple, assign_lhs: bool):
        pass

    @_visit.register
    def visit_unary_op(self, node: AnnCastUnaryOp, assign_lhs: bool):
        self.visit(node.value, assign_lhs)

    @_visit.register
    def visit_var(self, node: AnnCastVar, assign_lhs: bool):
        self.visit(node.val, assign_lhs)
