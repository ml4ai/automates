import typing
from functools import singledispatchmethod

from automates.program_analysis.CAST2GrFN.visitors.annotated_cast import *

def lambda_for_grfn_assignment(grfn_assignment: GrfnAssignment, lambda_body: str) -> str:
    var_names = map(var_name_from_fullid, grfn_assignment.inputs.keys())

    param_str = ", ".join(var_names)
    lambda_expr = f"lambda {param_str}: {lambda_body}"  

    # Debugging:
    print(f"LambdExpr: {lambda_expr}")

    return lambda_expr

def lambda_for_decision(condition_fullid: str, decision_in: typing.Dict) -> str:
    """
    Lambdas for decision nodes chooses betweeen IFBODY and ELSEBODY variables from
    interface_in based on condition_in
    """
    cond_name = var_name_from_fullid(condition_fullid)

    lambda_body = ""

    # TODO: if body and else body versions also need to be parameters to the lambda
    # and the variables names need to be modified e.g. appending if and else
    # e.g lambda cond, x_if, x_else, y_if, y_else: (x_if, y_if) if cond else (x_else, y_else)
    if_names = []
    else_names = []
    for dec in decision_in.values():
        if_fullid = dec[IFBODY]
        if_names.append(var_name_from_fullid(if_fullid))
        else_fullid = dec[ELSEBODY]
        else_names.append(var_name_from_fullid(else_fullid))

    if_names_str = ", ".join(if_names)
    else_names_str = ", ".join(else_names)

    lambda_body = f"({if_names_str}) if {cond_name} else ({else_names_str})"

    lambda_expr = f"lambda {cond_name}: {lambda_body}"  

    # Debugging:
    print(f"LambdExpr: {lambda_expr}")

    return lambda_expr


def lambda_for_interface(interface_in: typing.Dict) -> str:
    """
    Lambdas for plain interface nodes are simply multi-parameter identity functions
    """
    if len(interface_in) == 0:
        return ""

    get_name = lambda fullid: parse_fullid(fullid)["var_name"]
    var_names = map(get_name, interface_in.values())
    param_str = ", ".join(var_names)

    lambda_expr = f"lambda {param_str}: {param_str}"  

    # Debugging:
    print(f"LambdExpr: {lambda_expr}")

    return lambda_expr

def lambda_for_loop_top_interface(interface_in: typing.Dict) -> str:
    """
    Lambdas for loop top interface  chooses between initial and updated version
    of variables 
    """
    lambda_expr = None

    # Debugging:
    print(f"LambdExpr: {lambda_expr}")

    return lambda_expr



class LambdaExpressionPass:
    def __init__(self, ann_cast: AnnCast):
        self.ann_cast = ann_cast
        self.nodes = self.ann_cast.nodes
        # Any other state variables that are needed during
        # the pass
        for node in self.ann_cast.nodes:
            self.visit(node)

    def visit(self, node: AnnCastNode) -> str:
        """
        External visit that calls the internal visit
        Useful for debugging/development.  For example,
        printing the nodes that are visited
        """
        # debug printing
        class_name = node.__class__.__name__
        print(f"\nProcessing node type {class_name}")

        # call internal visit
        return self._visit(node)

    def visit_node_list(self, node_list: typing.List[AnnCastNode]) -> typing.List[str]:
        return [self.visit(node) for node in node_list]

    @singledispatchmethod
    def _visit(self, node: AnnCastNode) -> str:
        """
        Internal visit
        """
        raise NameError(f"Unrecognized node type: {type(node)}")

    @_visit.register
    def visit_assignment(self, node: AnnCastAssignment) -> str:
        right = self.visit(node.right)
        # build the lambda expression for the ret_val assignment
        # and store in GrfnAssignment
        lambda_expr = lambda_for_grfn_assignment(node.grfn_assignment, right)
        node.grfn_assignment.lambda_expr = lambda_expr
        node.expr_str = lambda_expr

        return node.expr_str

    @_visit.register
    def visit_attribute(self, node: AnnCastAttribute) -> str:
        return node.expr_str

    @_visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp) -> str:
        op = cast_op_to_str(node.op)
        right = self.visit(node.right)
        left = self.visit(node.left)
        node.expr_str = f"({left} {op} {right})"
        return node.expr_str

    @_visit.register
    def visit_boolean(self, node: AnnCastBoolean) -> str:
        if node.boolean is not None:
            node.expr_str = str(node.boolean)
        return node.expr_str

    @_visit.register
    def visit_call(self, node: AnnCastCall) -> str:
        return node.expr_str

    @_visit.register
    def visit_class_def(self, node: AnnCastClassDef) -> str:
        return node.expr_str

    @_visit.register
    def visit_dict(self, node: AnnCastDict) -> str:
        return node.expr_str

    @_visit.register
    def visit_expr(self, node: AnnCastExpr) -> str:
        node.expr_str = self.visit(node.expr)
        return node.expr_str

    @_visit.register
    def visit_function_def(self, node: AnnCastFunctionDef) -> str:
        node.top_interface_lambda = lambda_for_interface(node.top_interface_in)
        args_expr = self.visit_node_list(node.func_args)
        body_expr = self.visit_node_list(node.body)
        node.bot_interface_lambda = lambda_for_interface(node.bot_interface_in)
        
        # DEBUGGING
        print(f"FunctionDef {node.name.name}")
        print(f"\t Args Expressions:")
        for e in args_expr:
            print(f"\t\t{e}")
        print(f"\t Body Expressions:")
        for e in body_expr:
            print(f"\t\t{e}")
        return node.expr_str

    @_visit.register
    def visit_list(self, node: AnnCastList) -> str:
        return node.expr_str

    @_visit.register
    def visit_loop(self, node: AnnCastLoop) -> str:
        return node.expr_str

    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak) -> str:
        return node.expr_str

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue) -> str:
        return node.expr_str

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf) -> str:
        # TODO: make condition lambda
        # self.visit(node.expr)
        self.visit_node_list(node.body)
        self.visit_node_list(node.orelse)

        cond_fullid = list(node.condition_out.values())[0]
        node.decision_lambda = lambda_for_decision(cond_fullid, node.decision_in)
        return node.expr_str

    @_visit.register
    def visit_model_return(self, node: AnnCastModelReturn) -> str:
        val = self.visit(node.value)
        # build the lambda expression for the ret_val assignment
        # and store in GrfnAssignment
        lambda_expr = lambda_for_grfn_assignment(node.grfn_assignment, val)
        node.grfn_assignment.lambda_expr = lambda_expr
        node.expr_str = lambda_expr
        # TODO: do we need to return an empty string?
        return node.expr_str

    @_visit.register
    def visit_module(self, node: AnnCastModule) -> str:
        self.visit_node_list(node.body)
        return node.expr_str

    @_visit.register
    def visit_name(self, node: AnnCastName) -> str:
        node.expr_str = node.name
        return node.expr_str

    @_visit.register
    def visit_number(self, node: AnnCastNumber) -> str:
        node.expr_str = str(node.number)
        return node.expr_str

    @_visit.register
    def visit_set(self, node: AnnCastSet) -> str:
        return node.expr_str

    @_visit.register
    def visit_string(self, node: AnnCastString) -> str:
        return node.expr_str

    @_visit.register
    def visit_subscript(self, node: AnnCastSubscript) -> str:
        return node.expr_str

    @_visit.register
    def visit_tuple(self, node: AnnCastTuple) -> str:
        return node.expr_str

    @_visit.register
    def visit_unary_op(self, node: AnnCastUnaryOp) -> str:
        op = cast_op_to_str(node.op)
        val = self.visit(node.value)
        node.expr_str = f"({op}{val})"
        return node.expr_str

    @_visit.register
    def visit_var(self, node: AnnCastVar) -> str:
        node.expr_str = self.visit(node.val)
        return node.expr_str
