import typing
from functools import singledispatchmethod

from automates.model_assembly.metadata import LambdaType
from automates.program_analysis.CAST2GrFN.ann_cast.ann_cast_helpers import (
    GrfnAssignment,
    ann_cast_name_to_fullid,
    create_grfn_assign_node,
    create_grfn_literal_node,
    create_lambda_node_metadata,
    is_literal_assignment,
)
from automates.program_analysis.CAST2GrFN.ann_cast.annotated_cast import *


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
        # print current node being visited.  
        # this can be useful for debugging 
        # class_name = node.__class__.__name__
        # print(f"\nProcessing node type {class_name}")

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

        # DEBUG printing
        if self.pipeline_state.PRINT_DEBUGGING_INFO:
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


        # DEBUG printing
        if self.pipeline_state.PRINT_DEBUGGING_INFO:
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

        # DEBUG printing
        if self.pipeline_state.PRINT_DEBUGGING_INFO:
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
        # linking function arguments to formal parameters through the top 
        # interface is handled during VariableVersionPass, so we don't need to visit
        # func_args here
        self.visit_node_list(node.body, add_to)

    @_visit.register
    def visit_list(self, node: AnnCastList, add_to: typing.Dict):
        self.visit_node_list(node.values, add_to)

    @_visit.register
    def visit_loop(self, node: AnnCastLoop, add_to: typing.Dict):
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

        # DEBUG printing
        if self.pipeline_state.PRINT_DEBUGGING_INFO:
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
