import typing
from functools import singledispatchmethod

from automates.program_analysis.CAST2GrFN.visitors.annotated_cast import *

def lambda_for_grfn_assignment(grfn_assignment: GrfnAssignment, lambda_body: str) -> str:
    var_names = map(var_name_from_fullid, grfn_assignment.inputs.keys())

    param_str = ", ".join(var_names)
    lambda_expr = f"lambda {param_str}: {lambda_body}"  

    return lambda_expr

def lambda_for_condition(condition_in: typing.Dict, lambda_body: str) -> str:
    var_names = map(var_name_from_fullid, condition_in.values())

    param_str = ", ".join(var_names)
    lambda_expr = f"lambda {param_str}: {lambda_body}"

    return lambda_expr

def lambda_for_decision(condition_fullid: str, decision_in: typing.Dict) -> str:
    """
    Lambdas for decision nodes chooses betweeen IFBODY and ELSEBODY variables from
    interface_in based on condition_in

    The lambda has for the form:
        lambda x_if, y_if, x_else, y_else: (x_if, y_if) if COND else (x_else, y_else)
    """
    cond_name = var_name_from_fullid(condition_fullid)

    lambda_body = ""

    if_names = []
    else_names = []
    for dec in decision_in.values():
        if_fullid = dec[IFBODY]
        if_names.append(var_name_from_fullid(if_fullid) + "_if")
        else_fullid = dec[ELSEBODY]
        else_names.append(var_name_from_fullid(else_fullid) + "_else")

    if_names_str = ", ".join(if_names)
    else_names_str = ", ".join(else_names)
   
    lambda_body = f"({if_names_str}) if {cond_name} else ({else_names_str})"

    lambda_expr = f"lambda {cond_name}, {if_names_str}, {else_names_str}: {lambda_body}"  

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

    lambda_expr = f"lambda {param_str}: ({param_str})"  

    return lambda_expr

def lambda_for_loop_top_interface(top_interface_initial: typing.Dict, top_interface_updated: typing.Dict) -> str:
    """
    Lambda for loop top interface chooses between initial and updated version
    of variables 

    LoopTopInterfaces are special LambdaNode's which store state on whether we have executed the 
    body of the loop at least once.  
    The returned lambda str has the form
    lambda use_initial, x_init, y_init, x_update, y_update: (x_init, y_init) if use_initial else (x_update, y_update)
    The `use_initial` value comes from the internal state of the LoopTopInterface during execution.
    """

    init_name = lambda fullid: var_name_from_fullid(fullid) + "_init"
    init_names = map(init_name, top_interface_initial.values())
    updt_name = lambda fullid: var_name_from_fullid(fullid) + "_update"
    updt_names = map(updt_name, top_interface_updated.values())

    # NOTE: the lengths of top_interface_initial and top_interface_updated may not be the same
    # in some loops, you always use the initial value of a variable because it is never modified
    # to model this, for those variables which have no updated version, 
    # we add the "init" variable to the "update" variable group of the lambda expression
    non_updated_keys = set(top_interface_initial.keys()).difference(top_interface_updated.keys())
    non_updated_vars = {k : top_interface_initial[k] for k in non_updated_keys}

    # use "init" var names for non updates variables
    non_updt_names = map(init_name, non_updated_vars.values())
    # extend updt_names to include non updated variables
    updt_names = list(updt_names) + list(non_updt_names)

    # now, the lengths of init group and update group should match
    assert(len(updt_names) == len(top_interface_initial))

    use_initial_str = "use_initial"
    init_names_str = ", ".join(init_names)
    updt_names_str = ", ".join(updt_names)

    lambda_body = f"({init_names_str}) if {use_initial_str} else ({updt_names_str})"

    lambda_expr = f"lambda {use_initial_str}, {init_names_str}, {updt_names_str}: {lambda_body}"  

    return lambda_expr

def lambda_for_loop_condition(condition_in, lambda_body):
    var_names = map(var_name_from_fullid, condition_in.values())

    param_str = ", ".join(var_names)
    lambda_expr = f"lambda {param_str}: {lambda_body}"
   
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

    def visit_call_grfn_2_2(self, node: AnnCastCall):
        # example for argument lambda expression
        #   Call: func(x + 3, y * 2)
        # GrfnAssignment with index 0 corresponds to the assignment arg_0 = x + 3
        # the lambda for this assigment looks like
        #  lambda x : x + 3
        # for the lambda body, we need to visit the Call nodes arguments
        for i, grfn_assignment in node.arg_assignments.items():
            lambda_body = self.visit(node.arguments[i])
            grfn_assignment.lambda_expr = lambda_for_grfn_assignment(grfn_assignment, lambda_body)

        # top interface lambda
        node.top_interface_lambda = lambda_for_interface(node.top_interface_in)

        # build lamba expressions for function def copy body
        body_expr = self.visit_function_def_copy(node.func_def_copy)

        # bot interface lambda
        node.bot_interface_lambda = lambda_for_interface(node.bot_interface_in)


        # DEBUGGING
        print(f"Call GrFN 2.2 {node.func.name}")
        print(f"\t Args Expressions:")
        for arg in node.arg_assignments.values():
            print(f"\t\t{arg.lambda_expr}")
        print(f"\t Top Interface:")
        print(f"\t\t{node.top_interface_lambda}")
        print(f"FunctionDefCopy {node.func_def_copy.name.name}")
        print(f"\t Body Expressions:")
        for e in body_expr:
            print(f"\t\t{e}")
        print(f"\t Bot Interface:")
        print(f"\t\t{node.bot_interface_lambda}")


    @_visit.register
    def visit_call(self, node: AnnCastCall) -> str:
        if node.is_grfn_2_2:
            self.visit_call_grfn_2_2(node)
            if node.func_def_copy.has_ret_val:
                assert(len(node.out_ret_val) == 1)
                ret_val_fullid = list(node.out_ret_val.values())[0]
                node.expr_str = var_name_from_fullid(ret_val_fullid)
            return node.expr_str

        # TODO: Non GrFN 2.2 calls

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

    def visit_function_def_copy(self, node: AnnCastFunctionDef) -> typing.List:
        body_expr = self.visit_node_list(node.body)
        return body_expr

    @_visit.register
    def visit_function_def(self, node: AnnCastFunctionDef) -> str:
        node.top_interface_lambda = lambda_for_interface(node.top_interface_in)
        # NOTE: we do not visit node.func_args because those parameters are 
        # includes in the outputs of the top interface
        body_expr = self.visit_node_list(node.body)
        node.bot_interface_lambda = lambda_for_interface(node.bot_interface_in)
        
        # DEBUGGING
        print(f"FunctionDef {node.name.name}")
        print(f"\t Top Interface:")
        print(f"\t\t{node.top_interface_lambda}")
        print(f"\t Body Expressions:")
        for e in body_expr:
            print(f"\t\t{e}")
        print(f"\t Bot Interface:")
        print(f"\t\t{node.bot_interface_lambda}")
        return node.expr_str

    @_visit.register
    def visit_list(self, node: AnnCastList) -> str:
        node.expr_str = "list()"
        return node.expr_str

    @_visit.register
    def visit_loop(self, node: AnnCastLoop) -> str:
        
        # top interface lambda
        node.top_interface_lambda = lambda_for_loop_top_interface(node.top_interface_initial, 
                                                                 node.top_interface_updated)

        # condition lambda
        loop_expr = self.visit(node.expr)
        node.condition_lambda = lambda_for_loop_condition(node.condition_in, loop_expr)


        body_expr = self.visit_node_list(node.body)

        node.bot_interface_lambda = lambda_for_interface(node.bot_interface_in)
        
        # DEBUGGING
        print(f"Loop ")
        print(f"\t Loop Top Interface:")
        print(f"\t\t{node.top_interface_lambda}")
        print(f"\t Loop Expression:")
        print(f"\t\t{node.condition_lambda}")
        print(f"\t Body Expressions:")
        for e in body_expr:
            print(f"\t\t{e}")
        print(f"\t Loop Bot Interface:")
        print(f"\t\t{node.bot_interface_lambda}")

        # What to return?  Loops don't have a resulting value.
        return node.expr_str

    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak) -> str:
        return node.expr_str

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue) -> str:
        return node.expr_str

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf) -> str:
        # top interface lambda
        node.top_interface_lambda = lambda_for_interface(node.top_interface_in)

        # make condition lambda
        expr_str = self.visit(node.expr)
        node.condition_lambda = lambda_for_condition(node.condition_in, expr_str)

        body_expr = self.visit_node_list(node.body)
        or_else_expr = self.visit_node_list(node.orelse)

        # make decision lambda
        cond_fullid = list(node.condition_out.values())[0]
        node.decision_lambda = lambda_for_decision(cond_fullid, node.decision_in)

        # bot interface lambda
        node.bot_interface_lambda = lambda_for_interface(node.bot_interface_in)

        # DEBUGGING
        print(f"If ")
        print(f"\t If Top Interface:")
        print(f"\t\t{node.top_interface_lambda}")
        print(f"\t If Expression:")
        print(f"\t\t{node.condition_lambda}")
        print(f"\t Body Expressions:")
        for e in body_expr:
            print(f"\t\t{e}")
        print(f"\t OrElse Expressions:")
        for e in or_else_expr:
            print(f"\t\t{e}")
        print(f"\t If Decision Lambda:")
        print(f"\t\t{node.decision_lambda}")
        print(f"\t If Bot Interface:")
        print(f"\t\t{node.bot_interface_lambda}")
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
        body_expr = self.visit_node_list(node.body)

        # DEBUGGING
        print(f"Module")
        print(f"\t Body Expressions:")
        for e in body_expr:
            print(f"\t\t{e}")

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
