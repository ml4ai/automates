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
            node.grfn_assignment = GrfnAssignment(create_grfn_literal_node(metadata))
        else:
            node.grfn_assignment = GrfnAssignment(create_grfn_assign_node(metadata))
            
        print(f"Assignment before visiting children:")
        print(f"     grfn_assignment.inputs:  {node.grfn_assignment.inputs}")
        print(f"     grfn_assignment.outputs: {node.grfn_assignment.outputs}")

        self.visit(node.right, node.grfn_assignment.inputs)
        assert isinstance(node.left, AnnCastVar)
        self.visit(node.left, node.grfn_assignment.outputs)

        print(f"Assignment after visiting children:")
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
        for fullid, grfn_id in node.ret_val.items():
            add_to[fullid] = grfn_id

        # create argument variables
        for i, n in enumerate(node.arguments):
            var_name = f"{node.func.name}_ARG_{i}"
            id = self.ann_cast.next_collapsed_id()
            version = 0
            con_scopestr = con_scope_to_str(node.func.con_scope)

            # TODO: potentially also create assoicated GrFN var for parameter 
            # inside FunctionDef?
            # If we do this, we should also set up interaces
            grfn_var = create_grfn_var(var_name, id, version, con_scopestr)

            # TODO: add correct metadata for ASSIGN/LITERAL node
            metadata = []
            # if its a literal, there are no inputs
            if is_literal(n):
                node.grfn_assignments[i] = GrfnAssignment(create_grfn_literal_node(metadata))
            else:
                node.grfn_assignments[i] = GrfnAssignment(create_grfn_assign_node(metadata))
                # add to assignment inputs by visiting `n`
                self.visit(n, node.grfn_assignments[i].inputs)

            # NOTE: node.grfn_assignments[i] will have an empty outputs dict because
            # we know what the ouptut GrFN VariableNode is, and we store it in grfn_argument_nodes
            node.grfn_argument_nodes[i] = grfn_var
            
        print(f"Call after processing arguments:")
        print(f"     grfn_argument_nodes: {node.grfn_argument_nodes}")
        print(f"     grfn_assignments:")
        for pos, grfn_asgn in node.grfn_assignments.items():
            print(f"     {pos} : {str(grfn_asgn)}")

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
