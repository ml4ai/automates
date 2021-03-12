import typing
from functools import singledispatchmethod
from collections.abc import Iterable

from .cast_visitor import CASTVisitor
from automates.program_analysis.CAST2GrFN.model.cast_to_air_model import (
    C2AState,
    C2ALambda,
    C2ALambdaType,
    C2AExpressionLambda,
    C2AReturnLambda,
    C2AVariable,
    C2AFunctionDefContainer,
    C2ALoopContainer,
    C2AIfContainer,
    C2AContainerCallLambda,
    C2ATypeDef,
    C2AIdentifierInformation,
    C2AIdentifierType,
    C2ATypeError,
    C2AValueError,
)
from automates.program_analysis.CAST2GrFN.model.cast import (
    AstNode,
    Assignment,
    Attribute,
    BinaryOp,
    BinaryOperator,
    Call,
    ClassDef,
    Dict,
    Expr,
    FunctionDef,
    List,
    Loop,
    ModelBreak,
    ModelContinue,
    ModelIf,
    ModelReturn,
    Module,
    Name,
    Number,
    Set,
    String,
    Subscript,
    Tuple,
    UnaryOp,
    UnaryOperator,
    VarType,
    Var,
    var,
)


class CASTToAIRVisitor(CASTVisitor):
    cast_nodes: typing.List[AstNode]
    state: C2AState

    def __init__(self, cast_nodes: typing.List[AstNode]):
        self.cast_nodes = cast_nodes
        self.state = C2AState()

    def to_air(self):
        """
        TODO
        """
        # TODO create a function visitor to grab function definitions
        self.visit_node_list_and_flatten(self.cast_nodes)
        return self.state.to_AIR()

    def flatten(self, l):
        for el in l:
            if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
                yield from self.flatten(el)
            else:
                yield el

    def visit_node_list_and_flatten(self, nodes: List):
        return list(self.flatten(self.visit_list(nodes)))

    @singledispatchmethod
    def visit(self, node: AstNode):
        """
        TODO
        """
        raise C2ATypeError(f"Unrecognized type in CASTToAIRVisitor.visit: {type(node)}")

    @visit.register
    def _(self, node: Assignment):
        """
        TODO
        """
        left_res = self.visit(node.left)
        right_res = self.visit(node.right)

        input_variables = right_res[-1].input_variables
        output_variables = list()
        updated_variables = list()
        if isinstance(node.left, Var):
            # If we are assigning to strictly a var, create
            # the new version of the var
            assigned_var_name = left_res[-1].input_variables[0].get_name()
            new_ver = self.state.find_next_var_version(assigned_var_name)
            new_var = C2AVariable(
                C2AIdentifierInformation(
                    assigned_var_name,
                    self.state.get_scope_stack(),
                    self.state.current_module,
                    C2AIdentifierType.VARIABLE,
                ),
                new_ver,
                node.left.type,
            )
            output_variables.append(new_var)
            self.state.add_variable(new_var)
        else:
            raise C2AValueError(
                f"Unable to handle left hand of assignment of type {type(node.left)}"
            )

        # TODO ensure sorted order of lambda params
        lambda_expr = f"lambda {','.join({v.get_name() for v in right_res[-1].input_variables})}: {right_res[-1].lambda_expr}"

        return right_res[:-1] + [
            C2AExpressionLambda(
                C2AIdentifierInformation(
                    C2ALambdaType.ASSIGN,
                    self.state.get_scope_stack(),
                    self.state.current_module,
                    C2AIdentifierType.LAMBDA,
                ),
                input_variables,
                output_variables,
                updated_variables,
                C2ALambdaType.ASSIGN,
                lambda_expr,
                node,
            )
        ]

    @visit.register
    def _(self, node: Attribute):
        """
        TODO
        """
        return "NotImplemented"

    def get_op(self, op):
        op_map = {"Mult": "*", "Add": "+", "Sub": "-", "Gt": ">", "Not": "not "}
        return op_map[op] if op in op_map else None

    @visit.register
    def _(self, node: BinaryOp):
        """
        TODO
        """
        left_result = self.visit(node.left)
        right_result = self.visit(node.right)
        op_result = self.get_op(node.op)

        return (
            left_result[:-1]
            + right_result[:-1]
            + [
                C2AExpressionLambda(
                    C2AIdentifierInformation(
                        C2ALambdaType.UNKNOWN,
                        self.state.get_scope_stack(),
                        self.state.current_module,
                        C2AIdentifierType.LAMBDA,
                    ),
                    left_result[-1].input_variables + right_result[-1].input_variables,
                    [],
                    [],
                    C2ALambdaType.UNKNOWN,
                    f"{left_result[-1].lambda_expr} {op_result} {right_result[-1].lambda_expr}",
                    node,
                )
            ]
        )

    @visit.register
    def _(self, node: BinaryOperator):
        """
        TODO
        """

    @visit.register
    def _(self, node: Call):
        """
        TODO
        """
        name = node.func.name
        # TODO throw error if not found
        # TODO also what happens if func is defined after call
        called_func_name = [
            c.identifier_information
            for c in self.state.containers
            if c.identifier_information.name == name
        ][0]

        input_vars = []
        arg_assign_lambdas = []
        for arg in node.arguments:
            if isinstance(arg, Name):
                name_res = self.visit(arg)
                input_vars.extend(name_res[-1].input_variables)
            else:
                arg_name = f"{called_func_name.name}_ARG_{len(input_vars)}"
                arg_assign = Assignment(
                    left=Var(val=Name(name=arg_name), type="Unknown"), right=arg
                )
                assign_res = self.visit(arg_assign)
                arg_assign_lambdas.extend(assign_res)
                input_vars.extend(assign_res[-1].output_variables)

        result_name = f"{called_func_name.name}_RESULT"
        result_var = Var(val=Name(name=result_name), type="Unknown")
        result_var_res = self.visit(result_var)[0]
        self.state.add_variable(result_var_res.input_variables[0])

        # TODO
        return arg_assign_lambdas + [
            C2AContainerCallLambda(
                called_func_name,
                set(input_vars),
                set(result_var_res.input_variables),
                [],
                C2ALambdaType.CONTAINER,
            ),
            result_var_res,
        ]

    @visit.register
    def _(self, node: ClassDef):
        """
        TODO
        """
        return "NotImplemented"

    @visit.register
    def _(self, node: Dict):
        """
        TODO
        """
        return "NotImplemented"

    @visit.register
    def _(self, node: Expr):
        """
        TODO
        """
        return "NotImplemented"

    @visit.register
    def _(self, node: FunctionDef):
        """
        TODO
        """
        self.state.current_function = C2AFunctionDefContainer(
            C2AIdentifierInformation(
                node.name,
                self.state.get_scope_stack(),
                self.state.current_module,
                C2AIdentifierType.CONTAINER,
            ),
            [],
            [],
            [],
            [],
            "",  # TODO
        )

        self.state.push_scope(node.name)
        args_result = self.visit_node_list_and_flatten(node.func_args)
        argument_vars = []
        for arg in args_result:
            for var in arg.input_variables:
                self.state.add_variable(var)
                argument_vars.append(var)
        body_result = self.visit_node_list_and_flatten(node.body)
        self.state.pop_scope()

        self.state.current_function.add_arguments(argument_vars)
        self.state.current_function.add_body_lambdas(body_result)
        self.state.add_container(self.state.current_function)

        self.state.reset_current_function()
        self.state.reset_conditional_count()

    @visit.register
    def _(self, node: List):
        """
        TODO
        """
        return "NotImplemented"

    def build_var_with_incremented_version(self, var):
        return C2AVariable(
            C2AIdentifierInformation(),
        )

    def handle_control_node_type(
        self, expr, body, orelse, condition_type, condition_num, current_cond_block
    ):
        node_name = f"{condition_type}_{condition_num}"
        self.state.push_scope(node_name)

        cond_expr_var_name = f"COND_{condition_num}_{current_cond_block}"
        cond_assign = Assignment(
            left=Var(val=Name(name=cond_expr_var_name), type="Boolean"), right=expr
        )
        cond_assign_result = self.visit(cond_assign)
        cond_assign_lambda = cond_assign_result[-1]
        temp = C2AExpressionLambda(
            cond_assign_lambda.identifier_information,
            cond_assign_lambda.input_variables,
            cond_assign_lambda.output_variables,
            cond_assign_lambda.updated_variables,
            C2ALambdaType.CONDITION,
            cond_assign_lambda.lambda_expr,
            cond_assign_lambda.cast,
        )

        body_result = self.visit_node_list_and_flatten(body)
        body_result.extend(cond_assign_result[:-1])
        body_result.append(temp)

        # TODO add orelse result information in
        if len(orelse) > 0:
            next_block = orelse[0]
            if isinstance(next_block, ModelIf):
                self.handle_control_node_type(
                    next_block.expr,
                    next_block.body,
                    next_block.orelse,
                    condition_type,
                    condition_num,
                    current_cond_block + 1,
                )
            else:
                self.visit(next_block)

        # All variables that do not share the scope of the inside of the if
        # must be inputted to the container
        caller_input_vars = []
        callee_input_vars = []
        for b in body_result:
            for (idx, v) in enumerate(b.input_variables):
                # If the var was defined outside of this conditional body
                if (
                    v.identifier_information.scope[: len(self.state.scope_stack)]
                    != self.state.scope_stack
                ):
                    # Add the argument in the caller container
                    caller_input_vars.append(v)
                    # Create new version of this var in the conditional container
                    iv_name = v.identifier_information.name
                    new_ver = self.state.find_next_var_version(iv_name)
                    new_var = C2AVariable(
                        C2AIdentifierInformation(
                            iv_name,
                            self.state.get_scope_stack(),
                            self.state.current_module,
                            C2AIdentifierType.VARIABLE,
                        ),
                        -1,
                        v.type_name,
                    )
                    if not [
                        v
                        for v in callee_input_vars
                        if v.identifier_information.name
                        == new_var.identifier_information.name
                    ]:
                        callee_input_vars.append(new_var)
                        self.state.add_variable(new_var)
                    # Update the input var in the lambda with the new one inside
                    # this container
                    b.input_variables[idx] = new_var

        # Just the name of all currently defined vars
        external_vars = [
            v.identifier_information.name
            for v in self.state.variables
            if v.identifier_information.scope[: len(self.state.scope_stack)]
            != self.state.scope_stack
        ]

        self.state.pop_scope()

        # Gather the maximum updated version of variables for variables that
        # were defined outside of this if block
        max_output_vars = {}
        for b in body_result:
            for v in b.output_variables:
                name = v.identifier_information.name
                if name in external_vars and (
                    name not in max_output_vars
                    or v.version > max_output_vars[name].version
                ):
                    max_output_vars[name] = v
        callee_output_vars = list(max_output_vars.values())

        if condition_type == "LOOP":
            # Create exit condition variable assign
            exit_expr_var_name = f"EXIT"
            decision_assign = Assignment(
                left=Var(val=Name(name=exit_expr_var_name), type="Boolean"),
                right=UnaryOp(
                    op=UnaryOperator.NOT, value=Name(name=cond_expr_var_name)
                ),
            )
            decision_assign_result = self.visit(decision_assign)
            body_result.extend(decision_assign_result)

            # We have to pass each input var through the
            matching_vars = [
                (iv, ov)
                for iv in callee_input_vars
                for ov in callee_output_vars
                if ov.identifier_information.name == iv.identifier_information.name
            ]
            if matching_vars:
                decision_var_names = [
                    v[1].identifier_information.name for v in matching_vars
                ]

                names_to_output_from_input_decision = dict()
                for b in body_result:

                    def enumerate_vars_and_update_version(vars):
                        for (idx, v) in enumerate(vars):
                            name = v.identifier_information.name
                            if (
                                name
                                in decision_var_names
                                # and name not in names_to_output_from_input_decision
                            ):
                                new_var = C2AVariable(
                                    v.identifier_information, v.version + 1, v.type_name
                                )
                                vars[idx] = new_var
                                names_to_output_from_input_decision[name] = v

                    enumerate_vars_and_update_version(b.input_variables)
                    enumerate_vars_and_update_version(b.output_variables)
                    enumerate_vars_and_update_version(b.updated_variables)

                # Update version of vars held in matching_vars
                callee_output_vars = []
                output_decision_input = []
                for (idx, v_pair) in enumerate(matching_vars):
                    iv = v_pair[0]
                    ov = v_pair[1]
                    most_updated_in_loop = C2AVariable(
                        ov.identifier_information, ov.version + 1, ov.type_name
                    )
                    new_ov = C2AVariable(
                        most_updated_in_loop.identifier_information,
                        most_updated_in_loop.version + 1,
                        most_updated_in_loop.type_name,
                    )
                    self.state.add_variable(most_updated_in_loop)
                    self.state.add_variable(new_ov)
                    matching_vars[idx] = (
                        iv,
                        most_updated_in_loop,
                    )
                    callee_output_vars.append(new_ov)

                to_output_from_input_decision = [
                    C2AVariable(v.identifier_information, 0, v.type_name)
                    for (_, v) in names_to_output_from_input_decision.items()
                ]
                for v in to_output_from_input_decision:
                    self.state.add_variable(v)

                input_decision_node_inputs = {vars[0] for vars in matching_vars}.union(
                    {vars[1] for vars in matching_vars}
                )
                input_decision_node = C2AExpressionLambda(
                    C2AIdentifierInformation(
                        C2ALambdaType.UNKNOWN,
                        self.state.get_scope_stack(),
                        self.state.current_module,
                        C2AIdentifierType.DECISION,
                    ),
                    input_decision_node_inputs,
                    to_output_from_input_decision,
                    [],
                    C2ALambdaType.DECISION,
                    # TODO actually fill out lambda and ast
                    "lambda : None",
                    None,
                )

                output_decision_node_inputs = set(to_output_from_input_decision).union(
                    {vars[1] for vars in matching_vars}
                )
                output_decision_node = C2AExpressionLambda(
                    C2AIdentifierInformation(
                        C2ALambdaType.UNKNOWN,
                        self.state.get_scope_stack(),
                        self.state.current_module,
                        C2AIdentifierType.DECISION,
                    ),
                    output_decision_node_inputs,
                    callee_output_vars,
                    [],
                    C2ALambdaType.DECISION,
                    # TODO actually fill out lambda and ast
                    "lambda : None",
                    None,
                )

                body_result.insert(0, input_decision_node)
                body_result.append(output_decision_node)

        # Given all the output vars from this container, create the updated
        # versions of these in the caller container
        caller_output_vars = []
        for ov in callee_output_vars:
            ov_name = ov.identifier_information.name
            new_ver = self.state.find_next_var_version(ov_name)
            new_var = C2AVariable(
                C2AIdentifierInformation(
                    ov_name,
                    self.state.get_scope_stack(),
                    self.state.current_module,
                    C2AIdentifierType.VARIABLE,
                ),
                new_ver,
                ov.type_name,
            )
            caller_output_vars.append(new_var)
            self.state.add_variable(new_var)

        # Create and add If/Loop container TODO need loop
        container_type = C2AIfContainer if condition_type == "IF" else C2ALoopContainer
        cond_con = container_type(
            C2AIdentifierInformation(
                node_name,
                self.state.get_scope_stack(),
                self.state.current_module,
                C2AIdentifierType.CONTAINER,
            ),
            set(callee_input_vars),
            set(callee_output_vars),
            [],
            body_result,
        )
        self.state.add_container(cond_con)

        return [
            C2AContainerCallLambda(
                cond_con.identifier_information,
                set(caller_input_vars),
                set(caller_output_vars),
                [],
                C2ALambdaType.CONTAINER,
            )
        ]

    @visit.register
    def _(self, node: Loop):
        """
        TODO
        """
        return self.handle_control_node_type(
            node.expr,
            node.body,
            [],
            "LOOP",
            self.state.get_next_conditional(),
            0,
        )

    @visit.register
    def _(self, node: ModelIf):
        """
        TODO
        """
        return self.handle_control_node_type(
            node.expr,
            node.body,
            node.orelse,
            "IF",
            self.state.get_next_conditional(),
            0,
        )

    @visit.register
    def _(self, node: ModelBreak):
        """
        TODO
        """
        return "NotImplemented"

    @visit.register
    def _(self, node: ModelContinue):
        """
        TODO
        """
        return "NotImplemented"

    @visit.register
    def _(self, node: ModelReturn):
        """
        TODO
        """

        if isinstance(node.value, (Name, Number)):
            val_result = self.visit(node.value)
            self.state.current_function.add_outputs(val_result.input_variables)
            return []

        result_name = "RETURN_VAL"
        return_assign = Assignment(
            left=Var(val=Name(name=result_name), type="Unknown"), right=node.value
        )
        assign_res = self.visit(return_assign)

        # TODO
        # If not a var or literal, store the resulting value in a variable then
        # return that variable
        self.state.current_function.add_outputs(assign_res[-1].output_variables)
        return assign_res

    @visit.register
    def _(self, node: Module):
        """
        TODO
        """
        # TODO module cast node should be updated with name
        body_res = self.visit_node_list_and_flatten(node.body)

    @visit.register
    def _(self, node: Name):
        """
        TODO
        """
        name = node.name
        var_obj = self.state.find_highest_version_var(name)

        return [
            C2AExpressionLambda(
                C2AIdentifierInformation(
                    C2ALambdaType.UNKNOWN,
                    self.state.get_scope_stack(),
                    self.state.current_module,
                    C2AIdentifierType.LAMBDA,
                ),
                [var_obj],
                [],
                [],
                C2ALambdaType.UNKNOWN,
                name,
                node,
            )
        ]

    @visit.register
    def _(self, node: Number):
        """
        TODO
        """
        return [
            C2AExpressionLambda(
                C2AIdentifierInformation(
                    C2ALambdaType.UNKNOWN,
                    self.state.get_scope_stack(),
                    self.state.current_module,
                    C2AIdentifierType.LAMBDA,
                ),
                [],
                [],
                [],
                C2ALambdaType.UNKNOWN,
                node.number,
                node,
            )
        ]

    @visit.register
    def _(self, node: Set):
        """
        TODO
        """
        return "NotImplemented"

    @visit.register
    def _(self, node: String):
        """
        TODO
        """
        return "NotImplemented"

    @visit.register
    def _(self, node: Subscript):
        """
        TODO
        """
        return "NotImplemented"

    @visit.register
    def _(self, node: Tuple):
        """
        TODO
        """
        return "NotImplemented"

    @visit.register
    def _(self, node: UnaryOp):
        """
        TODO
        """
        val_result = self.visit(node.value)
        op_result = self.get_op(node.op)

        return val_result[:-1] + [
            C2AExpressionLambda(
                C2AIdentifierInformation(
                    C2ALambdaType.UNKNOWN,
                    self.state.get_scope_stack(),
                    self.state.current_module,
                    C2AIdentifierType.LAMBDA,
                ),
                val_result[-1].input_variables,
                [],
                [],
                C2ALambdaType.UNKNOWN,
                f"{op_result}{val_result[-1].lambda_expr}",
                node,
            )
        ]

    @visit.register
    def _(self, node: VarType):
        """
        TODO
        """
        return "NotImplemented"

    @visit.register
    def _(self, node: Var):
        """
        TODO
        """
        name = node.val.name
        var_obj = self.state.find_highest_version_var(name)
        if var_obj is None:
            var_obj = C2AVariable(
                C2AIdentifierInformation(
                    name,
                    self.state.get_scope_stack(),
                    self.state.current_module,
                    C2AIdentifierType.VARIABLE,
                ),
                -1,
                node.type,
            )

        return [
            C2AExpressionLambda(
                C2AIdentifierInformation(
                    C2ALambdaType.UNKNOWN,
                    self.state.get_scope_stack(),
                    self.state.current_module,
                    C2AIdentifierType.LAMBDA,
                ),
                [var_obj],
                [],
                [],
                C2ALambdaType.UNKNOWN,
                name,
                node,
            )
        ]
