from functools import singledispatchmethod
import typing

from automates.program_analysis.CAST2GrFN.ann_cast.annotated_cast import *
from automates.program_analysis.CAST2GrFN.ann_cast.ann_cast_helpers import (
        CON_STR_SEP,
        FULLID_SEP,
        LOOPBODY,
        ELSEBODY,
        IFBODY,
        LOOPEXPR,
        IFEXPR,
        MODULE_SCOPE,
        VAR_INIT_VERSION,
        VAR_EXIT_VERSION,
        LOOP_VAR_UPDATED_VERSION,
        GrfnContainerSrcRef,
        GrfnAssignment,
        cast_op_to_str,
        source_ref_dict,
        combine_source_refs,
        generate_domain_metadata,
        generate_from_source_metadata,
        generate_variable_node_span_metadata,
        add_metadata_from_name_node,
        add_metadata_to_grfn_var,
        create_lambda_node_metadata,
        create_container_metadata,
        combine_grfn_con_src_refs,
        union_dicts,
        con_scope_to_str,
        var_dict_to_str,
        interface_to_str,
        decision_in_to_str,
        make_cond_var_name,
        make_loop_exit_name,
        is_literal_assignment,
        is_func_def_main,
        function_container_name,
        func_def_argument_name,
        func_def_ret_val_name,
        specialized_global_name,
        call_argument_name,
        call_param_name,
        call_container_name,
        call_ret_val_name,
        ann_cast_name_to_fullid,
        build_fullid,
        parse_fullid,
        lambda_var_from_fullid,
        var_name_from_fullid,
        create_grfn_literal_node,
        create_grfn_assign_node,
        create_grfn_var_from_name_node,
        create_grfn_var
)


class GrfnAssignmentPass:
    def __init__(self, pipeline_state: PipelineState):
        self.pipeline_state = pipeline_state
        self.nodes = self.pipeline_state.nodes
        # Any other state variables that are needed during
        # the pass
        for node in self.pipeline_state.nodes:
            add_to = {}
            self.visit(node, add_to)

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
        metadata = create_lambda_node_metadata(node.source_refs)
        if is_literal_assignment(node.right):
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

    # TODO: Update
    @_visit.register
    def visit_call(self, node: AnnCastCall, add_to: typing.Dict):
        if node.is_grfn_2_2:
            self.visit_call_grfn_2_2(node, add_to)
            return 

        # add ret_val to add_to dict
        for id, fullid in node.out_ret_val.items():
            grfn_var = self.pipeline_state.get_grfn_var(fullid)
            add_to[fullid] = grfn_var.uid
            
        # populate `arg_assignments` attribute of node
        for i, n in enumerate(node.arguments):
            # grab GrFN variable for argument
            arg_fullid = node.arg_index_to_fullid[i]
            arg_grfn_var = self.pipeline_state.get_grfn_var(arg_fullid)
            
            # create GrfnAssignment based on assignment type
            metadata = create_lambda_node_metadata(node.source_refs)
            if is_literal_assignment(n):
                arg_assignment = GrfnAssignment(create_grfn_literal_node(metadata), LambdaType.LITERAL)
            else:
                arg_assignment = GrfnAssignment(create_grfn_assign_node(metadata), LambdaType.ASSIGN)

            # store argument as output to GrfnAssignment
            arg_assignment.outputs[arg_fullid] = arg_grfn_var.uid
            # populate GrfnAssignment inputs for arguments
            self.visit(n, arg_assignment.inputs)
            # store GrfnAssignment for this argument
            node.arg_assignments[i] = arg_assignment


        # DEBUGGING
        print(f"Call after processing arguments:")
        for pos, grfn_assignment in node.arg_assignments.items():
            print(f"     {pos} : {str(grfn_assignment)}")

    def visit_call_grfn_2_2(self, node: AnnCastCall, add_to: typing.Dict):
        assert isinstance(node.func, AnnCastName)
        # add ret_val to add_to dict
        for id, fullid in node.out_ret_val.items():
            grfn_var = self.pipeline_state.get_grfn_var(fullid)
            add_to[fullid] = grfn_var.uid
            
        # populate `arg_assignments` attribute of node
        for i, n in enumerate(node.arguments):
            # grab GrFN variable for argument
            arg_fullid = node.arg_index_to_fullid[i]
            arg_grfn_var = self.pipeline_state.get_grfn_var(arg_fullid)
            
            # create GrfnAssignment based on assignment type
            metadata = create_lambda_node_metadata(node.source_refs)
            if is_literal_assignment(n):
                arg_assignment = GrfnAssignment(create_grfn_literal_node(metadata), LambdaType.LITERAL)
            else:
                arg_assignment = GrfnAssignment(create_grfn_assign_node(metadata), LambdaType.ASSIGN)

            # store argument as output to GrfnAssignment
            arg_assignment.outputs[arg_fullid] = arg_grfn_var.uid
            # populate GrfnAssignment inputs for arguments
            self.visit(n, arg_assignment.inputs)
            # store GrfnAssignment for this argument
            node.arg_assignments[i] = arg_assignment

        self.visit_function_def(node.func_def_copy, {})

        # DEBUGGING
        print(f"Call after processing arguments:")
        for pos, grfn_assignment in node.arg_assignments.items():
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
        # TODO: decide what to do for function parameters this is likely needed for non GrFN2.2 generation
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
        # create the assignment LambdaNode for this return statement
        metadata = create_lambda_node_metadata(node.source_refs)
        if is_literal_assignment(node.value):
            node.grfn_assignment = GrfnAssignment(create_grfn_literal_node(metadata), LambdaType.LITERAL)
        else:
            node.grfn_assignment = GrfnAssignment(create_grfn_assign_node(metadata), LambdaType.ASSIGN)
            


        self.visit(node.value, node.grfn_assignment.inputs)

        for id, fullid in node.owning_func_def.in_ret_val.items():
            grfn_var = self.pipeline_state.get_grfn_var(fullid)
            node.grfn_assignment.outputs[fullid] = grfn_var.uid

        # DEBUGGING
        print(f"GrFN RETURN with type {node.grfn_assignment.assignment_type} after visiting children:")
        print(f"     grfn_assignment.inputs:  {node.grfn_assignment.inputs}")
        print(f"     grfn_assignment.outputs: {node.grfn_assignment.outputs}")

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
