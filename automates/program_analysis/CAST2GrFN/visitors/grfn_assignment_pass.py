from functools import singledispatchmethod
import typing

from automates.program_analysis.CAST2GrFN.visitors.annotated_cast import *

def is_literal(node: AnnCastNode):
    """
    Check if the node is a Number, Boolean, or String
    This may need to updated later
    """
    if isinstance(node, AnnCastNumber) or isinstance(node, AnnCastBoolean) \
        or isinstance(node, AnnCastString):
        return True

    return False


class GrfnAssignmentPass:
    def __init__(self, ann_cast: AnnCast):
        self.ann_cast = ann_cast
        self.nodes = self.ann_cast.nodes
        # Any other state variables that are needed during
        # the pass
        for node in self.ann_cast.nodes:
            add_to = {}
            self.visit(node, add_to)

    def create_call_args_and_params(self, node: AnnCastCall):
        """
        Creates initial version for each argument and each formal parameter
        Links these argument and parameters through the `top_interface_in` and `top_interface_out`
        For each argument, creates a `GrfnAssignment` which stores the assignment `LambdaNode`
        """
        # TODO: potentially also create assoicated GrFN var for parameter 
        # inside FunctionDef?
        func_def = self.ann_cast.func_id_to_def[node.func.id]
        # call container is used to scope parameters
        call_con_name = call_container_name(node)

        # create argument and parameter variables
        # argument variables are inputs to the top interface
        # paramter variables are outputs of the top interface
        for i, n in enumerate(node.arguments):
            # argument name and scope str
            arg_name = call_argument_name(node, i)
            arg_con_scopestr = con_scope_to_str(node.func.con_scope)

            # parameter name and scopestr
            param = func_def.func_args[i]
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

            param_grfn_var = create_grfn_var(param_name, id, version, param_con_scopestr)
            param_fullid = build_fullid(param_name, id, version, param_con_scopestr)
            self.ann_cast.store_grfn_var(param_fullid, param_grfn_var)

            # link argument and parameter through top interface
            node.top_interface_in[id] = arg_fullid
            node.top_interface_out[id] = param_fullid

            # create GrfnAssignment based on assignment type
            # TODO: add correct metadata for ASSIGN/LITERAL node
            metadata = []
            if is_literal(n):
                arg_assignment = GrfnAssignment(create_grfn_literal_node(metadata), LambdaType.LITERAL)
            else:
                arg_assignment = GrfnAssignment(create_grfn_assign_node(metadata), LambdaType.ASSIGN)

            # store argument as output to GrfnAssignment
            arg_assignment.outputs[arg_fullid] = arg_grfn_var.uid

            # populate GrfnAssignment inputs
            self.visit(n, arg_assignment.inputs)

            # store GrfnAssignment for this argument
            node.arg_assigments[i] = arg_assignment

        print("After create_call_args_and_params():")
        print(f"\ttop_interface_in = {node.top_interface_in}")
        print(f"\ttop_interface_out = {node.top_interface_out}")

    def visit(self, node: AnnCastNode, add_to: typing.Dict):
        """
        `add_to` is either the input or outputs to an GrFN Assignment/Literal node
        When visiting variable nodes, we add the variable to this `add_to` dict.
        When visiting call nodes, we add the function return value to this `add_to` dict.
        """
        # debug printing
        class_name = node.__class__.__name__
        print(f"\nProcessing node type {class_name}")

        # call internal visit
        return self._visit(node, add_to)

    def visit_node_list(self, node_list: typing.List[AnnCastNode], add_to: typing.Dict):
        return [self.visit(node, add_to) for node in node_list]

    @singledispatchmethod
    def _visit(self, node: AnnCastNode, add_to: typing.Dict):
        """
        `add_to` is either the input or outputs to an GrFN Assignment/Literal node
        When visiting variable nodes, we add the variable to this `add_to` dict.
        When visiting call nodes, we add the function return value to this `add_to` dict.
        """
        raise NameError(f"Unrecognized node type: {type(node)}")

    @_visit.register
    def visit_assignment(self, node: AnnCastAssignment, add_to: typing.Dict):
        # create the LambdaNode
        # TODO: add correct metadata
        metadata = []
        if is_literal(node.right):
            node.grfn_assignment = GrfnAssignment(create_grfn_literal_node(metadata), LambdaType.LITERAL)
        else:
            node.grfn_assignment = GrfnAssignment(create_grfn_assign_node(metadata), LambdaType.ASSIGN)
            
        self.visit(node.right, node.grfn_assignment.inputs)
        assert isinstance(node.left, AnnCastVar)
        self.visit(node.left, node.grfn_assignment.outputs)

        # DEBUGGING
        print(f"GrFN {node.grfn_assignment.assignment_type} after visiting children:")
        print(f"     grfn_assignment.inputs:  {node.grfn_assignment.inputs}")
        print(f"     grfn_assignment.outputs: {node.grfn_assignment.outputs}")

    @_visit.register
    def visit_attribute(self, node: AnnCastAttribute, add_to: typing.Dict):
        pass

    @_visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp, add_to: typing.Dict):
        # visit LHS first
        self.visit(node.left, add_to)

        # visit RHS second
        self.visit(node.right, add_to)

    @_visit.register
    def visit_boolean(self, node: AnnCastBoolean, add_to: typing.Dict):
        pass

    @_visit.register
    def visit_call(self, node: AnnCastCall, add_to: typing.Dict):
        assert isinstance(node.func, AnnCastName)
        # add ret_val to add_to dict
        for fullid, grfn_id in node.out_ret_val.items():
            add_to[fullid] = grfn_id

        self.create_call_args_and_params(node)
            
        print(f"Call after processing arguments:")
        for pos, grfn_assignment in node.arg_assigments.items():
            print(f"     {pos} : {str(grfn_assignment)}")

    @_visit.register
    def visit_class_def(self, node: AnnCastClassDef, add_to: typing.Dict):
        pass

    @_visit.register
    def visit_dict(self, node: AnnCastDict, add_to: typing.Dict):
        pass

    @_visit.register
    def visit_expr(self, node: AnnCastExpr, add_to: typing.Dict):
        self.visit(node.expr, add_to)

    @_visit.register
    def visit_function_def(self, node: AnnCastFunctionDef, add_to: typing.Dict):
        # TODO: decide what to do for function parameters
        # self.visit_node_list(node.func_args)
        # TODO: do we need to pass in an emtpy dict for `add_to`?
        self.visit_node_list(node.body, add_to)

    @_visit.register
    def visit_list(self, node: AnnCastList, add_to: typing.Dict):
        self.visit_node_list(node.values, add_to)

    @_visit.register
    def visit_loop(self, node: AnnCastLoop, add_to: typing.Dict):
        # TODO: do we need to pass in an emtpy dict for `add_to`?
        self.visit(node.expr, add_to)
        self.visit_node_list(node.body, add_to)

    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak, add_to: typing.Dict):
        pass

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue, add_to: typing.Dict):
        pass

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf, add_to: typing.Dict):
        # TODO: do we need to pass in an emtpy dict for `add_to`?
        self.visit(node.expr, add_to)
        self.visit_node_list(node.body, add_to)
        self.visit_node_list(node.orelse, add_to)

    @_visit.register
    def visit_model_return(self, node: AnnCastModelReturn, add_to: typing.Dict):
        self.visit(node.value, add_to)

    @_visit.register
    def visit_module(self, node: AnnCastModule, add_to: typing.Dict):
        add_to = {}
        self.visit_node_list(node.body, add_to)

    @_visit.register
    def visit_name(self, node: AnnCastName, add_to: typing.Dict):
        fullid = ann_cast_name_to_fullid(node)

        # store fullid/grfn id in add_to
        add_to[fullid] = node.grfn_id

    @_visit.register
    def visit_number(self, node: AnnCastNumber, add_to: typing.Dict):
        pass

    @_visit.register
    def visit_set(self, node: AnnCastSet, add_to: typing.Dict):
        pass

    @_visit.register
    def visit_string(self, node: AnnCastString, add_to: typing.Dict):
        pass

    @_visit.register
    def visit_subscript(self, node: AnnCastSubscript, add_to: typing.Dict):
        pass

    @_visit.register
    def visit_tuple(self, node: AnnCastTuple, add_to: typing.Dict):
        pass

    @_visit.register
    def visit_unary_op(self, node: AnnCastUnaryOp, add_to: typing.Dict):
        self.visit(node.value, add_to)

    @_visit.register
    def visit_var(self, node: AnnCastVar, add_to: typing.Dict):
        self.visit(node.val, add_to)
