import typing
from functools import singledispatchmethod

from automates.model_assembly.metadata import VariableCreationReason
from automates.program_analysis.CAST2GrFN.ann_cast.ann_cast_helpers import (
    CON_STR_SEP,
    ELSEBODY,
    IFBODY,
    IFEXPR,
    LOOP_VAR_UPDATED_VERSION,
    LOOPBODY,
    LOOPEXPR,
    VAR_EXIT_VERSION,
    VAR_INIT_VERSION,
    add_metadata_from_name_node,
    add_metadata_to_grfn_var,
    ann_cast_name_to_fullid,
    build_fullid,
    call_container_name,
    con_scope_to_str,
    create_grfn_var,
    create_grfn_var_from_name_node,
    generate_from_source_metadata,
    make_cond_var_name,
    make_loop_exit_name,
)
from automates.program_analysis.CAST2GrFN.ann_cast.annotated_cast import *


class GrfnVarCreationPass:
    def __init__(self, pipeline_state: PipelineState):
        self.pipeline_state = pipeline_state
        self.nodes = self.pipeline_state.nodes
        # the fullid of a AnnCastName node is a string which includes its 
        # variable name, numerical id, version, and scope
        for node in self.pipeline_state.nodes:
            self.visit(node)
        
        # DEBUG printing
        if self.pipeline_state.PRINT_DEBUGGING_INFO:
            self.print_created_grfn_vars()

    def visit(self, node: AnnCastNode):
        """
        External visit that callsthe internal visit
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

    def get_grfn_var_for_name_node(self, node: AnnCastName):
        """
        Obtains the GrFN variable node for the fullid of
        this AnnCastName node
        """
        fullid = ann_cast_name_to_fullid(node)
        return self.pipeline_state.grfn_id_to_grfn_var[self.pipeline_state.fullid_to_grfn_id[fullid]]

    def alias_copied_func_body_init_vers(self, node: AnnCastCall):
        """
        Precondition: This should be called after visiting copied function body.
        This is used for GrFN 2.2 generation.

        Aliases `VAR_INIT_VERSION` version variables from the function body to
        `VAR_INIT_VERSION` of calling container sccope.
        """
        func_def_copy = node.func_def_copy
        call_con_scopestr = con_scope_to_str(node.func.con_scope + [call_container_name(node)])
        func_con_scopestr = con_scope_to_str(func_def_copy.con_scope)

        # alias `VAR_INIT_VERSION` variables in call_con_scopestr
        # to the `VAR_INIT_VERSION` version occuring the func body
        version = VAR_INIT_VERSION
        # we alias globals which are used for the top interface
        for id, var_name in node.top_interface_vars.items():
            body_fullid = build_fullid(var_name, id, version, func_con_scopestr)
            call_fullid = build_fullid(var_name, id, version, call_con_scopestr)
            # we create GrFN variables with call_fullid during VariableVersionPass
            self.pipeline_state.alias_grfn_vars(body_fullid, call_fullid)

        # we also alias function parameters
        for i, call_fullid in node.param_index_to_fullid.items():
            var = func_def_copy.func_args[i]
            assert(isinstance(var, AnnCastVar))
            name = var.val
            func_id = name.id
            var_name = name.name
            func_fullid = build_fullid(var_name, func_id, version, func_con_scopestr)
            # we create GrFN variables with call_fullid during VariableVersionPass
            self.pipeline_state.alias_grfn_vars(func_fullid, call_fullid)

    def alias_copied_func_body_highest_vers(self, node: AnnCastCall):
        """
        Precondition: This should be called after visiting copied function body.
        This is used for GrFN 2.2 generation.

        Aliases highest version variables from the function body to
        `VAR_EXIT_VERSION` of calling container sccope.
        """
        func_def_copy = node.func_def_copy
        call_con_scopestr = con_scope_to_str(node.func.con_scope + [call_container_name(node)])
        func_con_scopestr = con_scope_to_str(func_def_copy.con_scope)

        # alias `VAR_EXIT_VERSION` variables in call_con_scopestr
        # to the highest version occuring the func body
        exit_version = VAR_EXIT_VERSION
        for id, var_name in node.bot_interface_vars.items():
            body_version = func_def_copy.body_highest_var_vers[id]
            body_fullid = build_fullid(var_name, id, body_version, func_con_scopestr)
            exit_fullid = build_fullid(var_name, id, exit_version, call_con_scopestr)
            self.pipeline_state.alias_grfn_vars(exit_fullid, body_fullid)

    def alias_if_expr_highest_vers(self, node: AnnCastModelIf):
        """
        Precondition: This should be called after visiting if-expr.

        Aliases highest version variables from the if expr to both
         - `VAR_INIT_VERSION` of if-body variables 
         - `VAR_INIT_VERSION` of else-body variables 
        """
        con_scopestr = con_scope_to_str(node.con_scope)

        # alias all top_interface_vars in if body and else body to the 
        # highest version GrFN variable from if-expr
        body_version = VAR_INIT_VERSION
        for id, var_name in node.top_interface_vars.items():
            expr_version = node.expr_highest_var_vers[id]
            expr_scopestr = con_scopestr + CON_STR_SEP + IFEXPR
            expr_fullid = build_fullid(var_name, id, expr_version, expr_scopestr)

            for body in [IFBODY, ELSEBODY]:
                body_scopestr = con_scopestr + CON_STR_SEP + body
                body_fullid = build_fullid(var_name, id, body_version, body_scopestr)
                self.pipeline_state.alias_grfn_vars(body_fullid, expr_fullid)

    def create_grfn_vars_model_if(self, node: AnnCastModelIf):
        """
        Create GrFN `VariableNode`s for variables which are accessed
        or modified by this ModelIf container. This does the following:
        
            - creates a version `VAR_INIT_VERSION` GrFN variable of all used variables. 
              These GrFN variables will be used for the `top_interface_out`.
            - aliases `VAR_INIT_VERSION` of if-expr variables to created `VAR_INIT_VERSION` GrFN variables
            - for modified variables, creates version `VAR_EXIT_VERSION` GrFN variables to 
               be used for the `decision_out` and `top_interface_in` 
        """
        con_scopestr = con_scope_to_str(node.con_scope)

        # by convention, we introduce version `VAR_INIT_VERSION` at the top of the container
        for id, var_name in node.top_interface_vars.items():
            version = VAR_INIT_VERSION
            grfn_var = create_grfn_var(var_name, id, version, con_scopestr)
            fullid = build_fullid(var_name, id, version, con_scopestr)
            self.pipeline_state.store_grfn_var(fullid, grfn_var)
            # create From Source metadata for the GrFN var
            # See comment above declaration for `FROM_SOURCE_FOR_GE` in annotated_cast.py 
            from_source = True if self.pipeline_state.FROM_SOURCE_FOR_GE else False
            from_source_mdata = generate_from_source_metadata(from_source, VariableCreationReason.TOP_IFACE_INTRO)
            add_metadata_to_grfn_var(grfn_var, from_source_mdata)

            # alias VAR_INIT_VERSION expr variables
            expr_scopestr = con_scopestr + CON_STR_SEP + IFEXPR
            expr_fullid = build_fullid(var_name, id, version, expr_scopestr)
            self.pipeline_state.alias_grfn_vars(expr_fullid, fullid)

        # by convention, we introduce `VAR_EXIT_VERSION` for modified variables
        # to be used as the output of the Decision node, and input to bot interface
        for id, var_name in node.bot_interface_vars.items():
            version = VAR_EXIT_VERSION
            grfn_var = create_grfn_var(var_name, id, version, con_scopestr)
            fullid = build_fullid(var_name, id, version, con_scopestr)
            self.pipeline_state.store_grfn_var(fullid, grfn_var)
            # create From Source metadata for the GrFN var
            # See comment above declaration for `FROM_SOURCE_FOR_GE` in annotated_cast.py 
            from_source = True if self.pipeline_state.FROM_SOURCE_FOR_GE else False
            from_source_mdata = generate_from_source_metadata(from_source, VariableCreationReason.BOT_IFACE_INTRO)
            add_metadata_to_grfn_var(grfn_var, from_source_mdata)

    def setup_model_if_condition(self, node: AnnCastModelIf):
        """
        Creates a GrFN `VariableNode` for the condtion variable of 
        this ModelIf container.  Populates the `condition_in` and `condition_out`
        attributes based on the if expr's used variables and the newly
        created GrFN condition variable.
        """
        if_scopestr = con_scope_to_str(node.con_scope)
        expr_scopestr = con_scope_to_str(node.con_scope + [IFEXPR])

        # inputs to condition node are the highest versions of used variables of the expr
        for id, var_name in node.expr_used_vars.items():
            highest_ver = node.expr_highest_var_vers[id]
            fullid = build_fullid(var_name, id, highest_ver, expr_scopestr)
            node.condition_in[id] = fullid

        # build condition variable
        cond_name = make_cond_var_name(if_scopestr)
        # use new collapsed id
        cond_id = self.pipeline_state.next_collapsed_id()
        cond_version = VAR_INIT_VERSION
        cond_fullid = build_fullid(cond_name, cond_id, cond_version, if_scopestr)
        cond_var = create_grfn_var(cond_name, cond_id, cond_version, if_scopestr)
        self.pipeline_state.store_grfn_var(cond_fullid, cond_var)
        # create From Source metadata for the GrFN var
        from_source = False
        from_source_mdata = generate_from_source_metadata(from_source, VariableCreationReason.COND_VAR)
        add_metadata_to_grfn_var(cond_var, from_source_mdata)

        # cache condtiional variable
        node.condition_var = cond_var

        # ouput of condition node is new condition var
        node.condition_out[cond_id] = cond_fullid

    def setup_model_if_decision(self, node: AnnCastModelIf):
        """
        Precondition: `setup_model_if_condition` has already been called on this node

        Populates `decision_in` and `decision_out` attributes of node.
        Inputs to the decision node are the highest versions of modified variables
        along if branch and else branch.
        Outputs are version `VAR_EXIT_VERSION` variables at the if container scope.

        Note, the condition variable will also have an edge to the Decision node in GrFN,
        but we do not add it to the `decision_in` dict to make iterating over that
        dict simpler
        """
        if_scopestr = con_scope_to_str(node.con_scope)
        ifbody_scopestr = con_scope_to_str(node.con_scope + [IFBODY])
        elsebody_scopestr = con_scope_to_str(node.con_scope + [ELSEBODY])
        # inputs to decision node are the highest versions in if-body and else-body
        # of variables modified within if container
        # NOTE: bot_interface_vars is the same as modified_vars
        for id, var_name in node.bot_interface_vars.items():
            if_highest = node.ifbody_highest_var_vers[id]
            if_fullid = build_fullid(var_name, id, if_highest, ifbody_scopestr)
            else_highest = node.elsebody_highest_var_vers[id]
            else_fullid = build_fullid(var_name, id, else_highest, elsebody_scopestr)
            node.decision_in[id] = {IFBODY: if_fullid, ELSEBODY: else_fullid}

        # outputs to the decision node are version `VAR_EXIT_VERSION` variables in if container scope
        out_version = VAR_EXIT_VERSION
        for id, var_name in node.bot_interface_vars.items():
            fullid = build_fullid(var_name, id, out_version, if_scopestr)
            node.decision_out[id] = fullid

    def create_grfn_vars_loop(self, node: AnnCastLoop):
        """
        Create GrFN `VariableNode`s for variables which are accessed
        or modified by this Loop container.  This does the following:
            - creates a version VAR_INIT_VERSION GrFN variable for all used variables. 
              These GrFN variables will be produced by the `top_interface_out`.
              Furthermore, they are aliased with loop expr init version variables.
            - creates a version LOOP_VAR_UPDATED_VERSION GrFN variable for all modified variables. 
              These GrFN variables are used for `top_interface_updated`.
            - creates a version VAR_EXIT_VERSION GrFN variable for all modified variables
              These GrFN variables are used for `bot_interface_in`.
        """
        con_scopestr = con_scope_to_str(node.con_scope)

        # create version `VAR_INIT_VERSION` for used variables
        for id, var_name in node.top_interface_vars.items():
            version = VAR_INIT_VERSION
            grfn_var = create_grfn_var(var_name, id, version, con_scopestr)
            fullid = build_fullid(var_name, id, version, con_scopestr)
            self.pipeline_state.store_grfn_var(fullid, grfn_var)
            # create From Source metadata for the GrFN var
            # See comment above declaration for `FROM_SOURCE_FOR_GE` in annotated_cast.py 
            from_source = True if self.pipeline_state.FROM_SOURCE_FOR_GE else False
            from_source_mdata = generate_from_source_metadata(from_source, VariableCreationReason.TOP_IFACE_INTRO)
            add_metadata_to_grfn_var(grfn_var, from_source_mdata)

            # alias VAR_INIT_VERSION expr variables
            expr_version = VAR_INIT_VERSION
            expr_scopestr = con_scopestr + CON_STR_SEP + LOOPEXPR
            expr_fullid = build_fullid(var_name, id, expr_version, expr_scopestr)
            self.pipeline_state.alias_grfn_vars(expr_fullid, fullid)

        # create version `LOOP_VAR_UPDATED_VERSION`  and `VAR_EXIT_VERSION` 
        # for modified variables (which are the same as bot interface_vars)
        for id, var_name in node.bot_interface_vars.items():
            for version in [LOOP_VAR_UPDATED_VERSION, VAR_EXIT_VERSION]:
                grfn_var = create_grfn_var(var_name, id, version, con_scopestr)
                fullid = build_fullid(var_name, id, version, con_scopestr)
                self.pipeline_state.store_grfn_var(fullid, grfn_var)
                # we intentionally do not add metadata to the GrFN variables here, since
                # these variables will be aliased to other variables created from Name nodes
                # and the metadata will be populated from those Name nodes

    def alias_loop_expr_highest_vers(self, node:AnnCastLoop):
        """
        Precondition: This should be called after visiting loop-expr.

        Aliases highest version variables from the loop expr to both
         - `VAR_INIT_VERSION` of loop-body variables 
         - `VAR_EXIT_VERSION` of modified variables
        """
        con_scopestr = con_scope_to_str(node.con_scope)

        # alias intial body version for top_interface_vars to the 
        # highest version GrFN variable from loop-expr
        # if the variable is modified, also alias 
        # exit version to highest version from loop-expr
        body_version = VAR_INIT_VERSION
        exit_version = VAR_EXIT_VERSION
        for id, var_name in node.top_interface_vars.items():
            expr_version = node.expr_highest_var_vers[id]
            expr_scopestr = con_scopestr + CON_STR_SEP + LOOPEXPR
            expr_fullid = build_fullid(var_name, id, expr_version, expr_scopestr)
            body_scopestr = con_scopestr + CON_STR_SEP + LOOPBODY
            body_fullid = build_fullid(var_name, id, body_version, body_scopestr)
            self.pipeline_state.alias_grfn_vars(body_fullid, expr_fullid)

            if id in node.bot_interface_vars:
                exit_scopestr = con_scopestr
                exit_fullid = build_fullid(var_name, id, exit_version, exit_scopestr)
                self.pipeline_state.alias_grfn_vars(exit_fullid, expr_fullid)

    def alias_loop_body_highest_vers(self, node:AnnCastLoop):
        """
        Precondition: This should be called after visiting loop-body.

        Aliases highest version variables from the loop body to
        `LOOP_VAR_UPDATED_VERSION` variables.
        """
        con_scopestr = con_scope_to_str(node.con_scope)

        # alias `LOOP_VAR_UPDATED_VERSION` modified variables 
        # to the highest version occuring the loop body
        updated_version = LOOP_VAR_UPDATED_VERSION
        for id, var_name in node.modified_vars.items():
            body_version = node.body_highest_var_vers[id]
            body_scopestr = con_scopestr + CON_STR_SEP + LOOPBODY
            body_fullid = build_fullid(var_name, id, body_version, body_scopestr)
            updated_fullid = build_fullid(var_name, id, updated_version, con_scopestr)
            self.pipeline_state.alias_grfn_vars(updated_fullid, body_fullid)

    def setup_loop_condition(self, node: AnnCastLoop):
        """
        Creates a GrFN `VariableNode` for the condtion variable of 
        this Loop container.  Populates the `condition_in` and `condition_out`
        attributes based on the loop expr's used variables and the newly
        created GrFN condition variable.
        """
        loop_scopestr = con_scope_to_str(node.con_scope)
        expr_scopestr = con_scope_to_str(node.con_scope + [LOOPEXPR])

        # inputs to condition node are the highest versions of used variables of the expr
        for id, var_name in node.expr_used_vars.items():
            highest_ver = node.expr_highest_var_vers[id]
            fullid = build_fullid(var_name, id, highest_ver, expr_scopestr)
            node.condition_in[id] = fullid

        # build condition variable
        cond_name = make_loop_exit_name(loop_scopestr)
        # use new collapsed id
        cond_id = self.pipeline_state.next_collapsed_id()
        cond_version = VAR_INIT_VERSION
        cond_fullid = build_fullid(cond_name, cond_id, cond_version, loop_scopestr)
        cond_var = create_grfn_var(cond_name, cond_id, cond_version, loop_scopestr)
        # mark the node as an exit
        cond_var.is_exit = True
        self.pipeline_state.store_grfn_var(cond_fullid, cond_var)
        # create From Source metadata for the GrFN var
        from_source = False
        from_source_mdata = generate_from_source_metadata(from_source, VariableCreationReason.COND_VAR)
        add_metadata_to_grfn_var(cond_var, from_source_mdata)

        # cache condtiional variable
        node.condition_var = cond_var

        # ouput of condition node is new condition var
        node.condition_out[cond_id] = cond_fullid

    def print_created_grfn_vars(self):
        print("Created the follwing GrFN variables")
        print("-"*50)
        print(f"{'fullid':<70}{'grfn_id':<70}{'index':<2}")
        print(f"{'------':<70}{'-------':<70}{'-----':<2}")
        for fullid, grfn_id in self.pipeline_state.fullid_to_grfn_id.items():
            grfn_var = self.pipeline_state.grfn_id_to_grfn_var[grfn_id]
            print(f"{fullid:<70}{grfn_id:<70}{grfn_var.identifier.index:<2}")

    @singledispatchmethod
    def _visit(self, node: AnnCastNode):
        """
        Internal visit
        """
        raise NameError(f"Unrecognized node type: {type(node)}")

    @_visit.register
    def visit_assignment(self, node: AnnCastAssignment):
        self.visit(node.right)
        assert isinstance(node.left, AnnCastVar)
        self.visit(node.left)

    @_visit.register
    def visit_attribute(self, node: AnnCastAttribute):
        pass

    @_visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp):
        # visit LHS first
        self.visit(node.left)

        # visit RHS second
        self.visit(node.right)

    @_visit.register
    def visit_boolean(self, node: AnnCastBoolean):
        pass

    @_visit.register
    def visit_call(self, node: AnnCastCall):
        if node.is_grfn_2_2:
            self.visit_call_grfn_2_2(node)
            return

        self.visit_node_list(node.arguments)

    def visit_call_grfn_2_2(self, node: AnnCastCall):
        assert isinstance(node.func, AnnCastName)
        # alias GrFN variables before visiting children
        self.alias_copied_func_body_init_vers(node)
        self.alias_copied_func_body_highest_vers(node)

        self.visit_node_list(node.arguments)
        self.visit_function_def_copy(node.func_def_copy)

    @_visit.register
    def visit_class_def(self, node: AnnCastClassDef):
        pass

    @_visit.register
    def visit_dict(self, node: AnnCastDict):
        pass

    @_visit.register
    def visit_expr(self, node: AnnCastExpr):
        self.visit(node.expr)

    def visit_function_def_copy(self, node: AnnCastFunctionDef):
        self.visit_node_list(node.func_args)
        self.visit_node_list(node.body)

    @_visit.register
    def visit_function_def(self, node: AnnCastFunctionDef):
        self.visit_node_list(node.func_args)
        self.visit_node_list(node.body)

    @_visit.register
    def visit_list(self, node: AnnCastList):
        self.visit_node_list(node.values)

    @_visit.register
    def visit_loop(self, node: AnnCastLoop):
        self.create_grfn_vars_loop(node)
        self.alias_loop_expr_highest_vers(node)
        self.alias_loop_body_highest_vers(node)
        # visit children
        self.visit(node.expr)
        self.setup_loop_condition(node)
        self.visit_node_list(node.body)

    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak):
        pass

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue):
        pass

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf):
        self.create_grfn_vars_model_if(node)
        # alias highest version vars inside expr to initial body versions
        self.alias_if_expr_highest_vers(node)

        # visit expr, then setup condition info
        self.visit(node.expr)
        self.setup_model_if_condition(node)

        self.visit_node_list(node.body)
        self.visit_node_list(node.orelse)
        
        # populate node.decision_in, node.decision_out
        self.setup_model_if_decision(node)

        # DEBUG printing
        if self.pipeline_state.PRINT_DEBUGGING_INFO:
            print("ModelIf Interface vars")
            print(f"    top_interface_out: {node.top_interface_out}")
            print(f"    bot_interface_out: {node.bot_interface_out}")

    @_visit.register
    def visit_model_return(self, node: AnnCastModelReturn):
        self.visit(node.value)

    @_visit.register
    def visit_module(self, node: AnnCastModule):
        self.visit_node_list(node.body)

    @_visit.register
    def visit_name(self, node: AnnCastName):
        fullid = ann_cast_name_to_fullid(node)
        # if we haven't already created the GrFN `VariableNode`, create it
        if fullid not in self.pipeline_state.fullid_to_grfn_id:
            grfn_var = create_grfn_var_from_name_node(node)
            self.pipeline_state.store_grfn_var(fullid, grfn_var)

        # now, store the grfn_id in the nane node
        node.grfn_id = self.pipeline_state.fullid_to_grfn_id[fullid]

        # store metdata for GrFN var associated to this Name node
        grfn_var = self.pipeline_state.get_grfn_var(fullid)
        add_metadata_from_name_node(grfn_var, node) 

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
        self.visit(node.value)

    @_visit.register
    def visit_var(self, node: AnnCastVar):
        self.visit(node.val)
