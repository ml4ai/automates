from functools import singledispatchmethod
from dataclasses import dataclass
from collections import defaultdict
import copy
import typing
import re


from automates.utils.misc import uuid
from .cast_visitor import CASTVisitor
from automates.program_analysis.CAST2GrFN.visitors.annotated_cast import *


class ContainerData:
    modified_vars: typing.Dict[id, str]
    accessed_vars: typing.Dict[id, str]
    used_vars: typing.Dict[id, str]

    def __init__(self):
        self.modified_vars = {}
        self.accessed_vars = {}
        self.used_vars = {}


class ContainerScopePass:
    def __init__(self, ann_cast: AnnCast):
        self.ann_cast = ann_cast
        # dicts mapping container scope strs to the if/loop count inside
        # the container
        self.if_count = defaultdict(int)
        self.loop_count = defaultdict(int)
        # dict mapping containter scope str to AnnCastNode
        self.con_str_to_node = {}
        # dict mapping container scope str to cached Container Data
        self.con_str_to_con_data = {}

        for node in self.ann_cast.nodes:
            # assign_lhs is False at the start of our visitor
            base_scopestr = ""
            enclosing_con_scope = []
            self.visit(node, base_scopestr, enclosing_con_scope, False)
        self.nodes = self.ann_cast.nodes

        # add cached container data to container nodes
        self.add_container_data_to_nodes()

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

    def add_container_data_to_expr(self, container, data):
        """
        Adds container data to `expr_*_vars` attributes of ModelIf and Loop nodes
        """
        container.expr_accessed_vars = data.accessed_vars
        container.expr_modified_vars = data.modified_vars
        container.expr_used_vars = data.used_vars


    def add_container_data_to_nodes(self):
        for scopestr, data in self.con_str_to_con_data.items():
            print(f"For scopestr: {scopestr} found data with")
            modified_vars = var_dict_to_str("  Modified: ", data.modified_vars)
            print(modified_vars)
            accessed_vars = var_dict_to_str("  Accessed: ", data.accessed_vars)
            print(accessed_vars)
            used_vars = var_dict_to_str("  Used: ", data.accessed_vars)
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
            container.accessed_vars = data.accessed_vars
            container.modified_vars = data.modified_vars
            container.used_vars = data.used_vars

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
            self, node: AnnCastNode, base_func_scopestr: str, enclosing_con_scope: typing.List, assign_lhs: bool
    ):
        # type(node) is a string which looks like
        # "class '<path.to.class.ClassName>'"
        class_name = str(type(node))
        last_dot = class_name.rfind(".")
        class_name = class_name[last_dot + 1 : -2]
        print(f"\nProcessing node type {class_name}")
        return self._visit(node, base_func_scopestr, enclosing_con_scope, assign_lhs)

    @singledispatchmethod
    def _visit(
            self, node: AnnCastNode, base_func_scopestr: str, enclosing_con_scope: typing.List, assign_lhs: bool
    ) -> typing.Dict:
        """
        Visit each AnnCastNode
        Parameters:
          - `assign_lhs`: this denotes whether we are visiting the LHS or RHS of an AnnCastAssignment
                      This is used to determine whether a variable (AnnCastName node) is
                      accessed or modified in that context
        """
        raise Exception(f"Unimplemented AST node of type: {type(node)}")

    def visit_node_list(
        self, node_list: typing.List[AnnCastNode], base_func_scopestr, enclosing_con_scope, assign_lhs
    ):
        return [self.visit(node, base_func_scopestr, enclosing_con_scope, assign_lhs) for node in node_list]

    @_visit.register
    def visit_assignment(
        self, node: AnnCastAssignment, base_func_scopestr, enclosing_con_scope, assign_lhs
    ):
        # TODO: what if the rhs has side-effects
        self.visit(node.right, base_func_scopestr, enclosing_con_scope, assign_lhs)
        assert isinstance(node.left, AnnCastVar)
        self.visit(node.left, base_func_scopestr, enclosing_con_scope, True)

    @_visit.register
    def visit_attribute(self, node: AnnCastAttribute, base_func_scopestr, enclosing_con_scope, assign_lhs):
        pass

    @_visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp, base_func_scopestr, enclosing_con_scope, assign_lhs):
        # visit LHS first
        self.visit(node.left, base_func_scopestr, enclosing_con_scope, assign_lhs)

        # visit RHS second
        self.visit(node.right, base_func_scopestr, enclosing_con_scope, assign_lhs)

    @_visit.register
    def visit_boolean(self, node: AnnCastBoolean, assign_lhs):
        pass


    @_visit.register
    def visit_call(self, node: AnnCastCall, base_func_scopestr, enclosing_con_scope, assign_lhs):
        assert isinstance(node.func, AnnCastName)
        # if we are trying to generate GrFN 2.2 and this call has an associated
        # FunctionDef, make a GrFN 2.2 container for it
        if GENERATE_GRFN_2_2 and node.func.id in self.ann_cast.func_id_to_def:
            node.is_grfn_2_2 = True
            self.visit_call_grfn_2_2(node, base_func_scopestr, enclosing_con_scope, assign_lhs)
            return

        node.func.con_scope = enclosing_con_scope
        self.visit_node_list(node.arguments, base_func_scopestr, enclosing_con_scope, assign_lhs)

    def visit_call_grfn_2_2(self, node: AnnCastCall, base_func_scopestr, enclosing_con_scope, assign_lhs):
        assert isinstance(node.func, AnnCastName)

        node.func.con_scope = enclosing_con_scope
        self.visit_node_list(node.arguments, base_func_scopestr, enclosing_con_scope, assign_lhs)

        node.func_def_copy = copy.deepcopy(self.ann_cast.func_id_to_def[node.func.id])
        # make a new id for the copy's Name node, and store in func_id_to_def
        node.func_def_copy.name.id = self.ann_cast.next_collapsed_id()
        self.ann_cast.func_id_to_def[node.func_def_copy.name.id] = node.func_def_copy
        calling_scope = enclosing_con_scope + [call_container_name(node)]
        call_assign_lhs = False
        self.visit_function_def(node.func_def_copy, base_func_scopestr, calling_scope, call_assign_lhs)

    # TODO: What to do for classes about modified/accessed vars?
    @_visit.register
    def visit_class_def(self, node: AnnCastClassDef, base_func_scopestr, enclosing_con_scope, assign_lhs):
        # We do not visit the name because it is a string
        assert isinstance(node.name, str)
        classscope = enclosing_con_scope + [node.name]
        # node.bases is a list of strings
        # node.funcs is a list of Vars
        # ClassDef's reset the `base_func_scopestr`
        base_scopestr = con_scope_to_str(classscope)
        self.visit_node_list(node.funcs, base_scopestr, classscope, assign_lhs)
        # node.fields is a list of Vars
        self.visit_node_list(node.fields, base_scopestr, classscope, assign_lhs)

    @_visit.register
    def visit_dict(self, node: AnnCastDict, assign_lhs):
        pass

    @_visit.register
    def visit_expr(self, node: AnnCastExpr, base_func_scopestr, enclosing_con_scope, assign_lhs):
        self.visit(node.expr, base_func_scopestr, enclosing_con_scope, assign_lhs)

    @_visit.register
    def visit_function_def(
        self, node: AnnCastFunctionDef, base_func_scopestr, enclosing_con_scope, assign_lhs
    ):
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
        self.visit_node_list(node.func_args, base_scopestr, funcscope, assign_lhs)

        self.visit_node_list(node.body, base_scopestr, funcscope, assign_lhs)

    @_visit.register
    def visit_list(self, node: AnnCastList, base_func_scopestr, enclosing_con_scope, assign_lhs):
        self.visit_node_list(node.values, base_func_scopestr, enclosing_con_scope, assign_lhs)

    @_visit.register
    def visit_loop(self, node: AnnCastLoop, base_func_scopestr, enclosing_con_scope, assign_lhs):
        loopscope = self.next_loop_scope(enclosing_con_scope)
        self.initialize_con_scope_data(loopscope, node)
        node.con_scope = loopscope
        # TODO: What if expr has side-effects?
        loopexprscope = loopscope + [LOOPEXPR]
        # we store an additional ContainerData for the loop expression, but
        # we store the Loop node in `self.con_str_to_node`         
        self.initialize_con_scope_data(loopexprscope, node)
        self.visit(node.expr, base_func_scopestr, loopexprscope, assign_lhs)

        loopbodyscope = loopscope + [LOOPBODY]
        self.visit_node_list(node.body, base_func_scopestr, loopbodyscope, assign_lhs)

    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak, assign_lhs):
        pass

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue, assign_lhs):
        pass

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf, base_func_scopestr, enclosing_con_scope, assign_lhs):
        # want orig enclosing
        ifscope = self.next_if_scope(enclosing_con_scope)
        self.initialize_con_scope_data(ifscope, node)
        node.con_scope = ifscope

        # TODO-what if the condition has a side-effect?
        ifexprscope = ifscope + [IFEXPR]
        # we store an additional ContainerData for the if expression, but
        # we store the ModelIf node in `self.con_str_to_node`         
        self.initialize_con_scope_data(ifexprscope, node)
        self.visit(node.expr, base_func_scopestr, ifexprscope, assign_lhs)

        ifbodyscope = ifscope + [IFBODY]
        self.visit_node_list(node.body, base_func_scopestr, ifbodyscope, assign_lhs)

        orelsebodyscope = ifscope + [ELSEBODY]
        self.visit_node_list(node.orelse, base_func_scopestr, orelsebodyscope, assign_lhs)

    @_visit.register
    def visit_return(self, node: AnnCastModelReturn, base_func_scopestr, enclosing_con_scope, assign_lhs):
        # store the owning FunctionDef, and mark it as having a return value
        function_def = self.ann_cast.get_func_node_from_scopestr(base_func_scopestr)
        node.owning_func_def = function_def
        node.owning_func_def.has_ret_val = True

        self.visit(node.value, base_func_scopestr, enclosing_con_scope, assign_lhs)

    @_visit.register
    def visit_module(self, node: AnnCastModule, base_func_scopestr, enclosing_con_scope, assign_lhs):
        module_con_scope = [MODULE_SCOPE]
        node.con_scope = module_con_scope
        # modulde resets the `base_func_scopestr`
        base_scopestr = con_scope_to_str(module_con_scope)
        # initialize container data for module which will store global variables
        self.initialize_con_scope_data(module_con_scope, node)
        self.visit_node_list(node.body, base_scopestr, module_con_scope, assign_lhs)

    @_visit.register
    def visit_name(self, node: AnnCastName, base_func_scopestr, enclosing_con_scope, assign_lhs):
        node.con_scope = enclosing_con_scope

        # check every prefix of enclosing_con_scope and add this Name node
        # to the associated container data if either
        #  1. the container scopestr extends base_func_scopestr
        #  2. this Name node is a global variable
        scopestr = ""
        for index, name in enumerate(enclosing_con_scope):
            # add separator between container scope component names
            if index != 0:
                scopestr += f"{CON_STR_SEP}"
            scopestr += f"{name}"
            
            # if this Name node is a global, or if the scopestr extends base_func_scopestr
            # we will add the node to scopestr's container data
            # otherwise, we skip it
            if not (self.ann_cast.is_global_var(node.id) or scopestr.startswith(base_func_scopestr)):
                continue

            # fill in container data if this is a cached container str
            if scopestr in self.con_str_to_con_data:
                con_data = self.con_str_to_con_data[scopestr]
                # if we are on LHS of assignment, this Name should be
                # added to modified vars
                if assign_lhs:
                    con_data.modified_vars[node.id] = node.name
                # otherwise it should be added to accessed_vars
                else:
                    con_data.accessed_vars[node.id] = node.name
                # for any type of use, add to containers used_vars
                con_data.used_vars[node.id] = node.name

            # TODO: decide if there is a better solution, or atleast document this better
            # we add global variables to modules used vars earlier
            if scopestr == MODULE_SCOPE:
                self.ann_cast.module_node.used_vars[node.id] = node.name
                

    @_visit.register
    def visit_number(self, node: AnnCastNumber, base_func_scopestr, enclosing_con_scope, assign_lhs):
        pass

    @_visit.register
    def visit_set(self, node: AnnCastSet, assign_lhs):
        pass

    @_visit.register
    def visit_string(self, node: AnnCastString, base_func_scopestr, enclosing_con_scope, assign_lhs):
        pass

    @_visit.register
    def visit_subscript(self, node: AnnCastSubscript, assign_lhs):
        pass

    @_visit.register
    def visit_tuple(self, node: AnnCastTuple, assign_lhs):
        pass

    @_visit.register
    def visit_unary_op(self, node: AnnCastUnaryOp, base_func_scopestr, enclosing_con_scope, assign_lhs):
        self.visit(node.value, base_func_scopestr, enclosing_con_scope, assign_lhs)

    @_visit.register
    def visit_var(self, node: AnnCastVar, base_func_scopestr, enclosing_con_scope, assign_lhs):
        self.visit(node.val, base_func_scopestr, enclosing_con_scope, assign_lhs)
