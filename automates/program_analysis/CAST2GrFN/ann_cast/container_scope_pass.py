from functools import singledispatchmethod
from collections import defaultdict
import copy
import typing
from enum import Enum


from automates.program_analysis.CAST2GrFN.ann_cast.annotated_cast import *

class AssignSide(Enum):
    NEITHER = 0
    LEFT = 1
    RIGHT = 2


class ContainerData:
    modified_vars: typing.Dict[id, str]
    vars_accessed_before_mod: typing.Dict[id, str]
    used_vars: typing.Dict[id, str]

    def __init__(self):
        self.modified_vars = {}
        self.vars_accessed_before_mod = {}
        self.used_vars = {}


class ContainerScopePass:
    def __init__(self, ann_cast: AnnCast):
        self.ann_cast = ann_cast
        # dicts mapping container scope strs to the if/loop count inside
        # the container
        self.if_count = defaultdict(int)
        self.loop_count = defaultdict(int)
        # dict mapping container scope str to AnnCastNode
        self.con_str_to_node = {}
        # dict mapping container scope str to cached Container Data
        self.con_str_to_con_data = {}
        self.calls_to_process = list()

        for node in self.ann_cast.nodes:
            # assign_side is False at the start of our visitor
            base_scopestr = ""
            enclosing_con_scope = []
            self.visit(node, base_scopestr, enclosing_con_scope, AssignSide.NEITHER)
        self.nodes = self.ann_cast.nodes

        # add cached container data to container nodes
        self.add_container_data_to_nodes()
 
        # save the dict mapping container scope to AnnCastNode
        self.ann_cast.con_scopestr_to_node = self.con_str_to_node

        self.propagate_globals_through_calls()
        print("Done")

    def next_if_scope(self, enclosing_con_scope):
        scopestr = con_scope_to_str(enclosing_con_scope)
        count = self.if_count[scopestr]
        self.if_count[scopestr] += 1
        return enclosing_con_scope + [f"if{count}"]

    def next_loop_scope(self, enclosing_con_scope):
        scopestr = con_scope_to_str(enclosing_con_scope)
        count = self.loop_count[scopestr]
        self.loop_count[scopestr] += 1
        return enclosing_con_scope + [f"loop{count}"]

    def propagate_globals_through_calls(self):
        for call_node in self.calls_to_process:
            func_def = self.ann_cast.func_def_node_from_id(call_node.func.id)

            # propagate up used variables to enclosing container scopes
            scopestr = ""
            for index, name in enumerate(call_node.func.con_scope):
                scopestr2 = CON_STR_SEP.join(call_node.func.con_scope[:index+1])
                # add separator between container scope component names
                if index != 0:
                    scopestr += f"{CON_STR_SEP}"
                scopestr += f"{name}"
                assert(scopestr == scopestr2)

                if scopestr == MODULE_SCOPE or not self.ann_cast.is_container(scopestr):
                    continue

                container_node = self.ann_cast.con_node_from_scopestr(scopestr)

                if self.ann_cast.is_con_scopestr_func_def(scopestr):
                    container_node.used_globals.update(func_def.used_globals)
                    container_node.modified_globals.update(func_def.modified_globals)
                    container_node.globals_accessed_before_mod.update(func_def.globals_accessed_before_mod)
                container_node.used_vars.update(func_def.used_globals)
                container_node.modified_vars.update(func_def.modified_globals)
                container_node.vars_accessed_before_mod.update(func_def.globals_accessed_before_mod)
                
    def add_container_data_to_expr(self, container, data):
        """
        Adds container data to `expr_*_vars` attributes of ModelIf and Loop nodes
        """
        container.expr_vars_accessed_before_mod = data.vars_accessed_before_mod
        container.expr_modified_vars = data.modified_vars
        container.expr_used_vars = data.used_vars


    def add_container_data_to_nodes(self):
        for scopestr, data in self.con_str_to_con_data.items():
            print(f"For scopestr: {scopestr} found data with")
            modified_vars = var_dict_to_str("  Modified: ", data.modified_vars)
            print(modified_vars)
            vars_accessed_before_mod = var_dict_to_str("  Accessed: ", data.vars_accessed_before_mod)
            print(vars_accessed_before_mod)
            used_vars = var_dict_to_str("  Used: ", data.vars_accessed_before_mod)
            print(used_vars)

            # Note: for the ModelIf.Expr and Loop.Expr nodes,
            # we put the ModelIf and Loop nodes respectively in
            # `con_str_to_node`.
            # We need to put the container data for the Expr nodes in
            # the expr_*_vars attributes of their associated container nodes
            # so we call `add_container_data_to_expr()`
            if_expr_suffix = CON_STR_SEP + IFEXPR
            if scopestr.endswith(if_expr_suffix):
                if_container = self.con_str_to_node[scopestr]
                self.add_container_data_to_expr(if_container, data)
                continue

            loop_expr_suffix = CON_STR_SEP + LOOPEXPR
            if scopestr.endswith(loop_expr_suffix):
                loop_container = self.con_str_to_node[scopestr]
                self.add_container_data_to_expr(loop_container, data)
                continue

            # otherwise, store container data, in the container nodes 
            # *_vars attributes
            container = self.con_str_to_node[scopestr]
            container.vars_accessed_before_mod = data.vars_accessed_before_mod
            container.modified_vars = data.modified_vars
            container.used_vars = data.used_vars

            # if the container is a FunctionDef, we want to store how globals are used
            if isinstance(container, AnnCastFunctionDef):
                all_globals = self.ann_cast.all_globals_dict()
                for id, name in all_globals.items():
                    if id in container.vars_accessed_before_mod:
                        container.globals_accessed_before_mod[id] = name
                    if id in container.modified_vars:
                        container.modified_globals[id] = name
                    if id in container.used_vars:
                        container.used_globals[id] = name

                print("Globals added")
            
            # DEBUGGING:
            print(container.grfn_con_src_ref)

    def initialize_con_scope_data(self, con_scope: typing.List, node):
        """
        Create an empty `ContainterData` in `self.con_str_to_con_data`
        and cache the container `node` in `self.con_str_to_node`
        """
        con_scopestr = con_scope_to_str(con_scope)
        # initialize container data for this node
        self.con_str_to_con_data[con_scopestr] = ContainerData()

        # map con_scopestr to passed in node
        self.con_str_to_node[con_scopestr] = node
        
    def visit(
            self, node: AnnCastNode, base_func_scopestr: str, enclosing_con_scope: typing.List, assign_side: AssignSide
    ):
        # type(node) is a string which looks like
        # "class '<path.to.class.ClassName>'"
        class_name = str(type(node))
        last_dot = class_name.rfind(".")
        class_name = class_name[last_dot + 1 : -2]
        print(f"\nProcessing node type {class_name}")
        children_src_ref = self._visit(node, base_func_scopestr, enclosing_con_scope, assign_side)
        if children_src_ref is None:
            children_src_ref = GrfnContainerSrcRef(None, None, None)

        # to keep determine GrfnContainerSrcRef for enclosing containers
        # each node we visit returns None or a GrfnContainerSrcRef with data copied from the nodes
        # source_refs attribute
        grfn_src_ref = GrfnContainerSrcRef(None, None, None)
        if node.source_refs is not None:
            src_ref = combine_source_refs(node.source_refs)
            grfn_src_ref = GrfnContainerSrcRef(line_begin=src_ref.row_start, line_end=src_ref.row_end,
                                               source_file_name=src_ref.source_file_name)

        return combine_grfn_con_src_refs([children_src_ref, grfn_src_ref])

    @singledispatchmethod
    def _visit(
            self, node: AnnCastNode, base_func_scopestr: str, enclosing_con_scope: typing.List, assign_side: AssignSide
    ):
        """
        Visit each AnnCastNode
        Parameters:
          - `assign_side`: this denotes whether we are visiting the LHS or RHS of an AnnCastAssignment
                            or if we are not under an AnnCastAssignment
                      This is used to determine whether a variable (AnnCastName node) is
                      accessed or modified in that context
        """
        raise Exception(f"Unimplemented AST node of type: {type(node)}")

    def visit_node_list(
        self, node_list: typing.List[AnnCastNode], base_func_scopestr, enclosing_con_scope, assign_side
    ):
        grfn_src_refs = [self.visit(node, base_func_scopestr, enclosing_con_scope, assign_side) for node in node_list]
        return combine_grfn_con_src_refs(grfn_src_refs)

    @_visit.register
    def visit_assignment(
        self, node: AnnCastAssignment, base_func_scopestr, enclosing_con_scope, assign_side
    ):
        # TODO: what if the rhs has side-effects
        right_src_ref = self.visit(node.right, base_func_scopestr, enclosing_con_scope, AssignSide.RIGHT)
        assert isinstance(node.left, AnnCastVar)
        left_src_ref = self.visit(node.left, base_func_scopestr, enclosing_con_scope, AssignSide.LEFT)

        return combine_grfn_con_src_refs([right_src_ref, left_src_ref])

    @_visit.register
    def visit_attribute(self, node: AnnCastAttribute, base_func_scopestr, enclosing_con_scope, assign_side):
        pass

    @_visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp, base_func_scopestr, enclosing_con_scope, assign_side):
        # visit LHS first
        left_src_ref = self.visit(node.left, base_func_scopestr, enclosing_con_scope, assign_side)

        # visit RHS second
        right_src_ref = self.visit(node.right, base_func_scopestr, enclosing_con_scope, assign_side)
        return combine_grfn_con_src_refs([right_src_ref, left_src_ref])

    @_visit.register
    def visit_boolean(self, node: AnnCastBoolean, base_func_scopestr, enclosing_con_scope, assign_side):
        pass


    @_visit.register
    def visit_call(self, node: AnnCastCall, base_func_scopestr, enclosing_con_scope, assign_side):
        assert isinstance(node.func, AnnCastName)
        # if this call is on the RHS of an assignment, then it should have a ret val
        if assign_side == AssignSide.RIGHT:
            node.has_ret_val = True

        node.func.con_scope = enclosing_con_scope
        # if we are trying to generate GrFN 2.2 and this call has an associated
        # FunctionDef, make a GrFN 2.2 container for it
        if GENERATE_GRFN_2_2 and node.has_func_def:
            node.is_grfn_2_2 = True
            return self.visit_call_grfn_2_2(node, base_func_scopestr, enclosing_con_scope, assign_side)

        # Code that works, but does not allow recursive functions
        # the children GrFN source ref for the call node is the src ref of the call's arguments
#         args_src_ref = self.visit_node_list(node.arguments, base_func_scopestr, enclosing_con_scope, assign_side)
# 
#         # we make a func_def copy for both GrFN2.2 and non 2.2 Calls
#         # for non 2.2 calls, the copied function def allows us to easily propagate 
#         # globals to enclosing scopes which are needed for the Call's interfaces
#         node.func_def_copy = copy.deepcopy(self.ann_cast.func_id_to_def[node.func.id])
#         calling_scope = enclosing_con_scope + [call_container_name(node)]
#         
#         # for GrFN 2.2, the copied FunctionDef container will be a subcontainer of the container
#         # for base_func_scopestr
#         if node.is_grfn_2_2:
#             # make a new id for the copy's Name node, and store in func_id_to_def
#             node.func_def_copy.name.id = self.ann_cast.next_collapsed_id()
#             self.ann_cast.func_id_to_def[node.func_def_copy.name.id] = node.func_def_copy
#             self.visit_function_def(node.func_def_copy, base_func_scopestr, calling_scope, AssignSide.NEITHER)
#         # for non GrFN 2.2 calls, we use calling_scopestr for base_func_scopestr 
#         # this ensures no locals from the FunctionDef body are propagated up to enclosing scopes
#         # instead only globals are propagated
#         else:
#             calling_scopestr = con_scope_to_str(calling_scope)
#             self.visit_function_def(node.func_def_copy, calling_scopestr, calling_scope, AssignSide.NEITHER) 
# 
#             # For GrFN 2.2 calls, we store a GrfnContainerSrcRef for them
#             grfn_src_ref = GrfnContainerSrcRef(None, None, None)
#             if node.source_refs is not None:
#                 src_ref = combine_source_refs(node.source_refs)
#                 grfn_src_ref = GrfnContainerSrcRef(line_begin=src_ref.row_start, line_end=src_ref.row_end,
#                                                    source_file_name=src_ref.source_file_name)
#             node.grfn_con_src_ref = grfn_src_ref
# 
#         return args_src_ref
#         
        # otherwise, this Call should not be treated as a non GrFN 2.2 call,
        # so we store a GrfnContainerSrcRef for it
        grfn_src_ref = GrfnContainerSrcRef(None, None, None)
        if node.source_refs is not None:
            src_ref = combine_source_refs(node.source_refs)
            grfn_src_ref = GrfnContainerSrcRef(line_begin=src_ref.row_start, line_end=src_ref.row_end,
                                               source_file_name=src_ref.source_file_name)
        node.grfn_con_src_ref = grfn_src_ref
        
        # queue node to process globals through interfaces later if we have the associated FunctionDef
        if node.has_func_def:
            self.calls_to_process.append(node)

        # # globals which are used by this Call's FunctionDef while be added to the Call's interface
        # # so, we need to propagate the use of these globals to enclosing containers
        # # to do this, we visit the body of the associated FunctionDef, and the propagation occurs in visit_name()
        # func_def = self.ann_cast.func_def_node_from_id(node.func.id)
        # call_con_scopestr = con_scope_to_str(enclosing_con_scope + [call_container_name(node)])
        # # in this call to visit_node_list we use call_con_scope for base_func_scopestr 
        # # this ensures no locals from the FunctionDef body are propagated up to enclosing scopes
        # # instead only globals are propagated
        # self.visit_node_list(func_def.body, call_con_scopestr, enclosing_con_scope, AssignSide.NEITHER)
        # For a call, we do not care about the arguments source refs
        return self.visit_node_list(node.arguments, base_func_scopestr, enclosing_con_scope, assign_side)

    def visit_call_grfn_2_2(self, node: AnnCastCall, base_func_scopestr, enclosing_con_scope, assign_side):
        assert isinstance(node.func, AnnCastName)

        # the children GrFN source ref for the call node is the src ref of the call's arguments
        args_src_ref = self.visit_node_list(node.arguments, base_func_scopestr, enclosing_con_scope, assign_side)

        node.func_def_copy = copy.deepcopy(self.ann_cast.func_id_to_def[node.func.id])
        # make a new id for the copy's Name node, and store in func_id_to_def
        node.func_def_copy.name.id = self.ann_cast.next_collapsed_id()
        self.ann_cast.func_id_to_def[node.func_def_copy.name.id] = node.func_def_copy
        calling_scope = enclosing_con_scope + [call_container_name(node)]
        call_assign_side = AssignSide.NEITHER
        self.visit_function_def(node.func_def_copy, base_func_scopestr, calling_scope, call_assign_side)

        return args_src_ref

    # TODO: What to do for classes about modified/accessed vars?
    @_visit.register
    def visit_class_def(self, node: AnnCastClassDef, base_func_scopestr, enclosing_con_scope, assign_side):
        # we believe the start of the container should not be on either side of an assignment
        assert(assign_side == AssignSide.NEITHER)
        # We do not visit the name because it is a string
        assert isinstance(node.name, str)
        classscope = enclosing_con_scope + [node.name]
        # node.bases is a list of strings
        # node.funcs is a list of Vars
        # ClassDef's reset the `base_func_scopestr`
        base_scopestr = con_scope_to_str(classscope)
        funcs_src_ref = self.visit_node_list(node.funcs, base_scopestr, classscope, assign_side)
        # node.fields is a list of Vars
        fields_src_ref = self.visit_node_list(node.fields, base_scopestr, classscope, assign_side)

        return combine_grfn_con_src_refs([funcs_src_ref, fields_src_ref])

    @_visit.register
    def visit_dict(self, node: AnnCastDict, assign_side):
        pass

    @_visit.register
    def visit_expr(self, node: AnnCastExpr, base_func_scopestr, enclosing_con_scope, assign_side):
        return self.visit(node.expr, base_func_scopestr, enclosing_con_scope, assign_side)

    @_visit.register
    def visit_function_def(
        self, node: AnnCastFunctionDef, base_func_scopestr, enclosing_con_scope, assign_side
    ):
        # we believe the start of the container should not be on either side of an assignment
        assert(assign_side == AssignSide.NEITHER)
        # store GrfnContainerSrcRef for this function def
        grfn_src_ref = GrfnContainerSrcRef(None, None, None)
        if node.source_refs is not None:
            src_ref = combine_source_refs(node.source_refs)
            grfn_src_ref = GrfnContainerSrcRef(line_begin=src_ref.row_start, line_end=src_ref.row_end,
                                               source_file_name=src_ref.source_file_name)
        node.grfn_con_src_ref = grfn_src_ref

        # Modify scope to include the function name
        funcscope = enclosing_con_scope + [function_container_name(node.name)]

        self.initialize_con_scope_data(funcscope, node)
        node.con_scope = funcscope
        # FunctionDef's reset the `base_func_scopestr`
        base_scopestr = con_scope_to_str(funcscope)

        # Cache function container scopestr for use during Variable Version pass
        self.ann_cast.func_con_scopestr_to_id[base_scopestr] = node.name.id

        # Each argument is a AnnCastVar node
        # Initialize each Name and visit to modify its scope
        args_src_ref = self.visit_node_list(node.func_args, base_scopestr, funcscope, assign_side)

        body_src_ref = self.visit_node_list(node.body, base_scopestr, funcscope, assign_side)

        # return children GrfnContainerSrcRef
        return combine_grfn_con_src_refs([args_src_ref, body_src_ref])

    @_visit.register
    def visit_list(self, node: AnnCastList, base_func_scopestr, enclosing_con_scope, assign_side):
        return self.visit_node_list(node.values, base_func_scopestr, enclosing_con_scope, assign_side)

    @_visit.register
    def visit_loop(self, node: AnnCastLoop, base_func_scopestr, enclosing_con_scope, assign_side):
        # we believe the start of the container should not be on either side of an assignment
        assert(assign_side == AssignSide.NEITHER)
        # store the base_func_scopestr for this container
        node.base_func_scopestr = base_func_scopestr

        loopscope = self.next_loop_scope(enclosing_con_scope)
        self.initialize_con_scope_data(loopscope, node)
        node.con_scope = loopscope
        # TODO: What if expr has side-effects?
        loopexprscope = loopscope + [LOOPEXPR]
        # we store an additional ContainerData for the loop expression, but
        # we store the Loop node in `self.con_str_to_node`         
        self.initialize_con_scope_data(loopexprscope, node)
        expr_src_ref = self.visit(node.expr, base_func_scopestr, loopexprscope, assign_side)

        loopbodyscope = loopscope + [LOOPBODY]
        body_src_ref = self.visit_node_list(node.body, base_func_scopestr, loopbodyscope, assign_side)

        # store GrfnContainerSrcRef for this loop
        node.grfn_con_src_ref = combine_grfn_con_src_refs([expr_src_ref, body_src_ref])
        # return the children GrfnContainerSrcRef
        return node.grfn_con_src_ref

    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak, assign_side):
        pass

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue, assign_side):
        pass

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf, base_func_scopestr, enclosing_con_scope, assign_side):
        # we believe the start of the container should not be on either side of an assignment
        assert(assign_side == AssignSide.NEITHER)
        # store the base_func_scopestr for this container
        node.base_func_scopestr = base_func_scopestr
        # want orig enclosing
        ifscope = self.next_if_scope(enclosing_con_scope)
        self.initialize_con_scope_data(ifscope, node)
        node.con_scope = ifscope

        # TODO-what if the condition has a side-effect?
        ifexprscope = ifscope + [IFEXPR]
        # we store an additional ContainerData for the if expression, but
        # we store the ModelIf node in `self.con_str_to_node`         
        self.initialize_con_scope_data(ifexprscope, node)
        expr_src_ref = self.visit(node.expr, base_func_scopestr, ifexprscope, assign_side)

        ifbodyscope = ifscope + [IFBODY]
        body_src_ref = self.visit_node_list(node.body, base_func_scopestr, ifbodyscope, assign_side)

        orelsebodyscope = ifscope + [ELSEBODY]
        orelse_src_ref = self.visit_node_list(node.orelse, base_func_scopestr, orelsebodyscope, assign_side)

        # store GrfnContainerSrcRef for this loop
        node.grfn_con_src_ref = combine_grfn_con_src_refs([expr_src_ref, body_src_ref, orelse_src_ref])
        # return the children GrfnContainerSrcRef
        return node.grfn_con_src_ref

    @_visit.register
    def visit_return(self, node: AnnCastModelReturn, base_func_scopestr, enclosing_con_scope, assign_side):
        # store the owning FunctionDef, and mark it as having a return value
        function_def = self.ann_cast.func_def_node_from_scopestr(base_func_scopestr)
        node.owning_func_def = function_def
        node.owning_func_def.has_ret_val = True

        return self.visit(node.value, base_func_scopestr, enclosing_con_scope, assign_side)

    @_visit.register
    def visit_module(self, node: AnnCastModule, base_func_scopestr, enclosing_con_scope, assign_side):
        # we believe the start of the container should not be on either side of an assignment
        assert(assign_side == AssignSide.NEITHER)
        module_con_scope = [MODULE_SCOPE]
        node.con_scope = module_con_scope
        # modulde resets the `base_func_scopestr`
        base_scopestr = con_scope_to_str(module_con_scope)
        # initialize container data for module which will store global variables
        self.initialize_con_scope_data(module_con_scope, node)
        body_src_ref = self.visit_node_list(node.body, base_scopestr, module_con_scope, assign_side)

        # store GrfnContainerSrcRef for the module
        node.grfn_con_src_ref = body_src_ref
        # return the children GrfnContainerSrcRef
        return node.grfn_con_src_ref

    @_visit.register
    def visit_name(self, node: AnnCastName, base_func_scopestr, enclosing_con_scope, assign_side):
        node.con_scope = enclosing_con_scope
        node.base_func_scopestr = base_func_scopestr

        # check every prefix of enclosing_con_scope and add this Name node
        # to the associated container data if either
        #  1. the container scopestr extends base_func_scopestr
        #  2. this Name node is a global variable
        scopestr = ""
        for index, name in enumerate(enclosing_con_scope):
            scopestr2 = CON_STR_SEP.join(enclosing_con_scope[:index+1])
            # add separator between container scope component names
            if index != 0:
                scopestr += f"{CON_STR_SEP}"
            scopestr += f"{name}"
            assert(scopestr == scopestr2)
            
            # if this Name node is a global, or if the scopestr extends base_func_scopestr
            # we will add the node to scopestr's container data
            # otherwise, we skip it
            # this check is more complex than we would like because of GrFN 2.2 copied function defs
            # we would like to stop propagation of variable use at the base_func_scopestr, but
            # because of copied function defs we cannot.  globals which are used in a copied function
            # def must be propagated above the base_func_scopestr
            if not (self.ann_cast.is_global_var(node.id) or scopestr.startswith(base_func_scopestr)):
                continue

            # fill in container data if this is a cached container str
            if scopestr in self.con_str_to_con_data:
                con_data = self.con_str_to_con_data[scopestr]
                # if we are on LHS of assignment, this Name should be
                # added to modified vars
                if assign_side == AssignSide.LEFT:
                    con_data.modified_vars[node.id] = node.name
                # if this is the first time visiting the variable id in this scope, 
                # then it is accessed before modified
                elif node.id not in con_data.used_vars:
                    con_data.vars_accessed_before_mod[node.id] = node.name

                # for any type of use, add to containers used_vars
                con_data.used_vars[node.id] = node.name

    @_visit.register
    def visit_number(self, node: AnnCastNumber, base_func_scopestr, enclosing_con_scope, assign_side):
        pass

    @_visit.register
    def visit_set(self, node: AnnCastSet, assign_side):
        pass

    @_visit.register
    def visit_string(self, node: AnnCastString, base_func_scopestr, enclosing_con_scope, assign_side):
        pass

    @_visit.register
    def visit_subscript(self, node: AnnCastSubscript, assign_side):
        pass

    @_visit.register
    def visit_tuple(self, node: AnnCastTuple, assign_side):
        pass

    @_visit.register
    def visit_unary_op(self, node: AnnCastUnaryOp, base_func_scopestr, enclosing_con_scope, assign_side):
        return self.visit(node.value, base_func_scopestr, enclosing_con_scope, assign_side)

    @_visit.register
    def visit_var(self, node: AnnCastVar, base_func_scopestr, enclosing_con_scope, assign_side):
        return self.visit(node.val, base_func_scopestr, enclosing_con_scope, assign_side)
