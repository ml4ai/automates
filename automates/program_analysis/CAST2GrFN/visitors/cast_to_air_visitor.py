import typing
from functools import singledispatchmethod
from collections.abc import Iterable

from .cast_visitor import CASTVisitor
from automates.program_analysis.CAST2GrFN.model.cast_to_air_model import (
    C2AException,
    C2AState,
    C2ALambdaType,
    C2AExpressionLambda,
    C2AVariable,
    C2ASourceRef,
    C2AFunctionDefContainer,
    C2ALoopContainer,
    C2AIfContainer,
    C2AContainerCallLambda,
    C2ATypeDef,
    C2AIdentifierInformation,
    C2AIdentifierType,
    C2AVariableContext,
    C2ATypeError,
    C2AValueError,
)
from automates.program_analysis.CAST2GrFN.model.cast import (
    AstNode,
    Assignment,
    Attribute,
    BinaryOp,
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
    SourceRef,
    Subscript,
    Tuple,
    UnaryOp,
    UnaryOperator,
    VarType,
    Var,
    source_ref,
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
        previous_context = self.state.current_context
        self.state.set_variable_context(C2AVariableContext.LOAD)
        right_res = self.visit(node.right)
        self.state.set_variable_context(C2AVariableContext.STORE)
        left_res = self.visit(node.left)
        self.state.set_variable_context(previous_context)

        source_ref = C2ASourceRef("", -1, -1, -1, -1)
        if node.source_refs is not None and len(node.source_refs) > 0:
            source_ref = self.retrieve_source_ref(node.source_refs[0])

        input_variables = right_res[-1].input_variables
        output_variables = list()
        updated_variables = list()
        if isinstance(node.left, (Attribute, Var)):
            # If we are assigning to strictly a var, create
            # the new version of the var
            assigned_var = left_res[-1].input_variables[0]
            assigned_var_name = assigned_var.get_name()
            new_ver = self.state.find_next_var_version(assigned_var_name)
            new_var = C2AVariable(
                C2AIdentifierInformation(
                    assigned_var_name,
                    self.state.get_scope_stack(),
                    self.state.current_module,
                    C2AIdentifierType.VARIABLE,
                ),
                new_ver,
                assigned_var.type_name,
                source_ref=source_ref,
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
                source_ref,
                lambda_expr,
                node,
            )
        ]

    @visit.register
    def _(self, node: Attribute):
        """
        TODO
        """
        additional_lambdas = []
        if isinstance(node.value, Name):

            prev_context = self.state.current_context
            self.state.set_variable_context(C2AVariableContext.ATTR_VALUE)
            value_result = self.visit(node.value)
            self.state.set_variable_context(prev_context)

            value_var = value_result[-1].input_variables[0]

            attr_var_name = f"{node.value.name}_{node.attr.name}"
            cur_attr_var = self.state.find_highest_version_var_in_current_scope(
                attr_var_name
            )

            new_attr_var = cur_attr_var
            # If the cur_attr_var doesnt exist, create it
            if cur_attr_var is None:
                # TODO lookup type of field and use here
                cast_attr_var = Var(
                    val=Name(name=attr_var_name),
                    type="Unknown",
                )
                attr_var_result = self.visit(cast_attr_var)
                new_attr_var = attr_var_result[-1].input_variables[0]
                new_attr_var.source_ref = value_var.source_ref

            if (
                self.state.current_context == C2AVariableContext.LOAD
                and self.state.attribute_access_state.need_attribute_extract(
                    value_var, new_attr_var
                )
            ):
                # If cur attr var is not none then  we found an exisiting var for this
                # attribute. In this case, we need to make a new version of this
                # attr var to output from the extract node.
                if cur_attr_var is not None:
                    cast_attr_var = Var(
                        val=Name(name=attr_var_name),
                        type=cur_attr_var.type_name,
                        source_refs=[cur_attr_var.source_ref],
                    )
                    attr_var_result = self.visit(cast_attr_var)
                    new_attr_var = attr_var_result[-1].input_variables[0]
                self.state.add_variable(new_attr_var)

                new_extract_lambda = (
                    self.state.attribute_access_state.add_attribute_access(
                        value_var, new_attr_var
                    )
                )

                if new_extract_lambda is not None:
                    additional_lambdas.append(new_extract_lambda)

            elif self.state.current_context == C2AVariableContext.STORE:
                # If we are storing into the attr var, we need to udpate the input
                # version of the var into the pack node. However, we are not actually
                # creating the updated var here, that is handled in the assignment
                # node. So, just create the var object to update the packed version.
                if cur_attr_var is not None:
                    new_attr_var = C2AVariable(
                        new_attr_var.identifier_information,
                        new_attr_var.version + 1,
                        new_attr_var.type_name,
                        new_attr_var.source_ref,
                    )
                self.state.attribute_access_state.add_attribute_to_pack(
                    value_var, new_attr_var
                )

            return additional_lambdas + [
                C2AExpressionLambda(
                    C2AIdentifierInformation(
                        C2ALambdaType.UNKNOWN,
                        self.state.get_scope_stack(),
                        self.state.current_module,
                        C2AIdentifierType.LAMBDA,
                    ),
                    [new_attr_var],
                    [],
                    [],
                    C2ALambdaType.UNKNOWN,
                    C2ASourceRef("", -1, -1, -1, -1),
                    f"{attr_var_name}",
                    node,
                )
            ]

        else:
            # TODO custom exception
            raise Exception(
                f"Error: Unable to handle expression on left side of attribute type {type(node.value)}: {node.value}"
            )

    def get_op(self, op):
        op_map = {
            "Mult": "*",
            "Add": "+",
            "Sub": "-",
            "Div": "/",
            "Gt": ">",
            "Gte": ">=",
            "Lt": "<",
            "Lte": "<=",
            "Not": "not ",
        }
        return op_map[op] if op in op_map else None

    @visit.register
    def _(self, node: BinaryOp):
        """
        TODO
        """
        left_result = self.visit(node.left)
        right_result = self.visit(node.right)
        op_result = self.get_op(node.op)
        source_ref = self.retrieve_source_ref(node.source_refs[0])

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
                    source_ref,
                    f"{left_result[-1].lambda_expr} {op_result} {right_result[-1].lambda_expr}",
                    node,
                )
            ]
        )

    def check_and_add_container_var(self, v):
        v_name = v.identifier_information.name
        var_obj = self.state.find_highest_version_var_in_current_scope(v_name)

        if var_obj is None:
            var_obj = C2AVariable(
                C2AIdentifierInformation(
                    v_name,
                    self.state.get_scope_stack(),
                    self.state.current_module,
                    C2AIdentifierType.VARIABLE,
                ),
                -1,
                v.type_name,
                v.source_ref,
            )
            self.state.add_variable(var_obj)
            container = self.state.find_container(var_obj.identifier_information.scope)
            container.add_arguments([var_obj])

        return var_obj

    @visit.register
    def _(self, node: Call):
        """
        TODO
        """
        called_func_name = node.func.name
        # Skip printf calls for now
        if called_func_name == "printf":
            return []
        # TODO throw error if not found
        # TODO also what happens if func is defined after call

        matching_funcs = [
            c
            for c in self.state.containers
            if c.identifier_information.name == called_func_name
        ]
        called_func = None
        called_func_identifier = None
        lambda_type = C2ALambdaType.CONTAINER
        if matching_funcs:
            called_func = matching_funcs[0]
            called_func_identifier = called_func.identifier_information
        else:
            lambda_type = C2ALambdaType.OPERATOR
            called_func_identifier = (
                C2AIdentifierInformation(
                    called_func_name,
                    self.state.get_scope_stack(),
                    self.state.current_module,
                    C2AIdentifierType.CONTAINER,
                ),
            )

        input_vars = []
        output_vars = []
        arg_assign_lambdas = []
        for arg in node.arguments:
            if isinstance(arg, Name):
                name_res = self.visit(arg)
                input_vars.extend(name_res[-1].input_variables)
            else:
                arg_name = f"{called_func_name}_ARG_{len(input_vars)}"
                arg_assign = Assignment(
                    left=Var(val=Name(name=arg_name), type="Unknown"),
                    right=arg,
                    source_refs=arg.source_refs,
                )
                assign_res = self.visit(arg_assign)
                arg_assign_lambdas.extend(assign_res)
                input_vars.extend(assign_res[-1].output_variables)

        # Gather what global variables need to be inputted into the container.
        # These would have been added as additional arguments to the container
        # during previous processing.
        arg_start = len(node.arguments)
        container_args_list = called_func.arguments if called_func is not None else []
        while arg_start < len(container_args_list):
            v = container_args_list[arg_start]
            input_var = self.check_and_add_container_var(v)
            input_vars.append(input_var)

            output_var = C2AVariable(
                C2AIdentifierInformation(
                    input_var.identifier_information.name,
                    self.state.get_scope_stack(),
                    self.state.current_module,
                    C2AIdentifierType.VARIABLE,
                ),
                input_var.version + 1,
                input_var.type_name,
                input_var.source_ref,
            )

            self.state.add_variable(output_var)
            output_vars.append(output_var)

            arg_start += 1

        src_ref = self.retrieve_source_ref(node.source_refs[0])
        container_call_lambda = C2AContainerCallLambda(
            called_func_identifier,
            list(set(input_vars)),
            list(set(output_vars)),
            [],
            lambda_type,
            src_ref,
        )
        results = arg_assign_lambdas + [container_call_lambda]

        if self.state.current_context == C2AVariableContext.LOAD:
            result_name = f"{called_func_name}_RESULT"
            result_var = Var(val=Name(name=result_name), type="Unknown")
            result_var_res = self.visit(result_var)[-1]
            self.state.add_variable(result_var_res.input_variables[0])
            container_call_lambda.output_variables.extend(
                result_var_res.input_variables
            )
            results.append(result_var_res)

        return results

    @visit.register
    def _(self, node: ClassDef):
        """
        TODO
        """
        return NotImplemented

    @visit.register
    def _(self, node: Dict):
        """
        TODO
        """
        return NotImplemented

    @visit.register
    def _(self, node: Expr):
        """
        TODO
        """
        return NotImplemented

    def handle_packs_exiting_container(self, con):
        # If there are outstanding updates to an object that need to be packed,
        # handle that here
        aas = self.state.attribute_access_state
        if aas.has_outstanding_pack_nodes():
            all_packs = aas.get_outstanding_pack_nodes()
            con.add_body_lambdas(all_packs)
            vars_output_from_packs = {v for n in all_packs for v in n.output_variables}
            for v in vars_output_from_packs:
                self.state.add_variable(v)
            con.add_outputs(vars_output_from_packs)

    @visit.register
    def _(self, node: FunctionDef):
        """
        TODO
        """
        source_ref = SourceRef("", -1, -1, -1, -1)
        if node.source_refs is not None and len(node.source_refs) > 0:
            source_ref = self.retrieve_source_ref(node.source_refs[0])

        self.state.current_function = C2AFunctionDefContainer(
            C2AIdentifierInformation(
                node.name,
                self.state.get_scope_stack(),
                self.state.current_module,
                C2AIdentifierType.CONTAINER,
            ),
            list(),
            list(),
            list(),
            list(),
            source_ref,
            "return_type",  # TODO
        )
        self.state.add_container(self.state.current_function)

        self.state.push_scope(node.name)
        args_result = self.visit_node_list_and_flatten(node.func_args)
        argument_vars = []
        for arg in args_result:
            for var in arg.input_variables:
                self.state.add_variable(var)
                argument_vars.append(var)
        self.state.current_function.add_arguments(argument_vars)

        body_result = self.visit_node_list_and_flatten(node.body)
        self.state.current_function.add_body_lambdas(body_result)

        self.state.pop_scope()

        self.handle_packs_exiting_container(self.state.current_function)
        self.state.reset_current_function()
        self.state.reset_conditional_count()

    @visit.register
    def _(self, node: List):
        """
        TODO
        """
        return NotImplemented

    def build_var_with_incremented_version(self, var):
        return C2AVariable(
            C2AIdentifierInformation(),
        )

    def handle_control_node_type(
        self, expr, body, orelse, condition_type, condition_num, current_cond_block
    ):
        node_name = f"{condition_type}_{condition_num}"

        cond_source_ref = C2ASourceRef("", -1, -1, -1, -1)
        source_file_name = cond_source_ref.file
        # Create and add If/Loop container TODO need loop
        container_type = C2AIfContainer if condition_type == "IF" else C2ALoopContainer
        cond_con = container_type(
            C2AIdentifierInformation(
                node_name,
                self.state.get_scope_stack(),
                self.state.current_module,
                C2AIdentifierType.CONTAINER,
            ),
            [],
            [],
            [],
            [],
            C2ASourceRef("", -1, -1, -1, -1),
            cond_source_ref,
        )
        self.state.add_container(cond_con)
        self.state.push_scope(node_name)

        cond_expr_var_name = f"COND_{condition_num}_{current_cond_block}"
        cond_assign = Assignment(
            left=Var(val=Name(name=cond_expr_var_name), type="Boolean"),
            right=expr,
            source_refs=expr.source_refs,
        )
        cond_assign_result = self.visit(cond_assign)
        cond_assign_lambda = cond_assign_result[-1]
        cond_assign_lambda_with_correct_type = C2AExpressionLambda(
            cond_assign_lambda.identifier_information,
            cond_assign_lambda.input_variables,
            cond_assign_lambda.output_variables,
            cond_assign_lambda.updated_variables,
            C2ALambdaType.CONDITION,
            cond_source_ref,
            cond_assign_lambda.lambda_expr,
            cond_assign_lambda.cast,
        )

        # Add the condition var into the variable list
        for v in cond_assign_lambda_with_correct_type.output_variables:
            self.state.add_variable(v)

        body_result = self.visit_node_list_and_flatten(body)
        body_result.extend(cond_assign_result[:-1])
        body_result.append(cond_assign_lambda_with_correct_type)

        line_low = -1
        line_high = -1
        for b in body_result:
            if b.source_ref.line_start is not None:
                if b.source_ref.line_start > -1 and b.source_ref.line_start < line_low:
                    line_low = b.source_ref.line_start
                elif (
                    b.source_ref.line_end is not None
                    and b.source_ref.line_end > line_high
                ):
                    line_high = b.source_ref.line_end
                elif b.source_ref.line_start > line_high:
                    line_high = b.source_ref.line_start

        cond_con.add_body_source_ref(
            C2ASourceRef(source_file_name, line_low, -1, line_high, -1)
        )

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

        # Just the name of all currently defined vars
        external_vars = [
            v.identifier_information.name
            for v in self.state.variables
            if v.identifier_information.scope[: len(self.state.scope_stack)]
            != self.state.scope_stack
        ]

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
                    op=UnaryOperator.NOT,
                    value=Name(name=cond_expr_var_name),
                    source_refs=expr.source_refs,
                ),
                source_refs=expr.source_refs,
            )
            decision_assign_result = self.visit(decision_assign)
            body_result.extend(decision_assign_result)

            # We have to pass each input var through the
            matching_vars = [
                (iv, ov)
                for iv in cond_con.arguments
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
                            if name in decision_var_names:
                                new_var = C2AVariable(
                                    v.identifier_information,
                                    v.version + 1,
                                    v.type_name,
                                    v.source_ref,
                                )
                                vars[idx] = new_var
                                names_to_output_from_input_decision[name] = v

                                if new_var not in set(self.state.variables):
                                    self.state.add_variable(new_var)

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
                        ov.identifier_information,
                        ov.version + 1,
                        ov.type_name,
                        ov.source_ref,
                    )
                    new_ov = C2AVariable(
                        most_updated_in_loop.identifier_information,
                        most_updated_in_loop.version + 1,
                        most_updated_in_loop.type_name,
                        most_updated_in_loop.source_ref,
                    )
                    self.state.add_variable(most_updated_in_loop)
                    self.state.add_variable(new_ov)
                    matching_vars[idx] = (
                        iv,
                        most_updated_in_loop,
                    )
                    callee_output_vars.append(new_ov)

                to_output_from_input_decision = [
                    C2AVariable(v.identifier_information, 0, v.type_name, v.source_ref)
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
                    C2ASourceRef(source_file_name, line_high, -1, -1, -1),
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
                    C2ASourceRef(source_file_name, line_high, -1, -1, -1),
                    # TODO actually fill out lambda and ast
                    "lambda : None",
                    None,
                )

                body_result.insert(0, input_decision_node)
                body_result.append(output_decision_node)

        self.state.pop_scope()

        # Given all the output vars from this container, create the updated
        # versions of these in the caller container
        caller_output_vars = []
        caller_input_vars = []
        for ov in callee_output_vars:
            ov_name = ov.identifier_information.name
            # cur_var = self.state.find_highest_version_var_in_current_scope(ov_name)
            cur_var = self.check_and_add_container_var(ov)
            new_var = C2AVariable(
                C2AIdentifierInformation(
                    ov_name,
                    self.state.get_scope_stack(),
                    self.state.current_module,
                    C2AIdentifierType.VARIABLE,
                ),
                cur_var.version + 1,
                ov.type_name,
                ov.source_ref,
            )
            self.state.add_variable(new_var)

            caller_output_vars.append(new_var)
            caller_input_vars.append(cur_var)

        cond_con.add_body_lambdas(body_result)
        cond_con.add_outputs(list(set(callee_output_vars)))

        self.handle_packs_exiting_container(cond_con)

        return [
            C2AContainerCallLambda(
                cond_con.identifier_information,
                list(set(caller_input_vars)),
                list(set(caller_output_vars)),
                [],
                C2ALambdaType.CONTAINER,
                C2ASourceRef(source_file_name, line_low, -1, -1, -1),
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
        return NotImplemented

    @visit.register
    def _(self, node: ModelContinue):
        """
        TODO
        """
        return NotImplemented

    @visit.register
    def _(self, node: ModelReturn):
        """
        TODO
        """

        if isinstance(node.value, Number):
            return []
        elif isinstance(node.value, Name):
            val_result = self.visit(node.value)
            self.state.current_function.add_outputs(val_result[-1].input_variables)
            return []

        result_name = "RETURN_VAL"
        return_assign = Assignment(
            left=Var(val=Name(name=result_name), type="Unknown"),
            right=node.value,
            source_refs=node.source_refs,
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
        self.state.current_module = node.name

        global_var_nodes = [n for n in node.body if isinstance(n, Var)]
        non_var_nodes = [n for n in node.body if not isinstance(n, Var)]

        global_var_results = self.visit_node_list_and_flatten(global_var_nodes)
        for var_lambda in global_var_results:
            for v in var_lambda.input_variables:
                self.state.add_variable(v)
        self.visit_node_list_and_flatten(non_var_nodes)

    @visit.register
    def _(self, node: Name):
        """
        TODO
        """
        name = node.name
        var_obj = self.state.find_highest_version_var_in_current_scope(name)

        additional_lambas = []
        # In this case we are loading a var of type object but not accessing an attribute.
        # If so, check if we need to pack / produce a new version of this var before using it
        if (
            var_obj is not None
            and self.state.current_context == C2AVariableContext.LOAD
            and var_obj.type_name == "object"  # TODO AND has outstanding packs
        ):
            pack_lambda = self.state.attribute_access_state.get_outstanding_pack_node(
                var_obj
            )
            additional_lambas.append(pack_lambda)
            var_obj = pack_lambda.output_variables[-1]
        elif var_obj is None and self.state.current_context in {
            C2AVariableContext.LOAD,
            C2AVariableContext.ATTR_VALUE,
        }:
            var_obj = self.state.find_highest_version_var_in_previous_scopes(name)
            if var_obj is None:
                raise C2AValueError(f"Error: Unable to find variable with name: {name}")
            var_obj = self.check_and_add_container_var(var_obj)

        return additional_lambas + [
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
                var_obj.source_ref,
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
                C2ASourceRef("", -1, -1, -1, -1),
                node.number,
                node,
            )
        ]

    @visit.register
    def _(self, node: Set):
        """
        TODO
        """
        return NotImplemented

    @visit.register
    def _(self, node: String):
        """
        TODO
        """
        return NotImplemented

    @visit.register
    def _(self, node: Subscript):
        """
        TODO
        """
        return NotImplemented

    @visit.register
    def _(self, node: Tuple):
        """
        TODO
        """
        return NotImplemented

    @visit.register
    def _(self, node: UnaryOp):
        """
        TODO
        """
        val_result = self.visit(node.value)
        op_result = self.get_op(node.op)
        source_ref = self.retrieve_source_ref(node.source_refs[0])

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
                source_ref,
                f"{op_result}{val_result[-1].lambda_expr}",
                node,
            )
        ]

    @visit.register
    def _(self, node: VarType):
        """
        TODO
        """
        return NotImplemented

    def retrieve_source_ref(self, source_ref: SourceRef):
        return C2ASourceRef(
            file=source_ref.source_file_name,
            line_start=source_ref.row_start,
            line_end=source_ref.row_end,
            col_start=source_ref.col_start,
            col_end=source_ref.col_end,
        )

    @visit.register
    def _(self, node: Var):
        """
        TODO
        """
        name = node.val.name
        var_obj = self.state.find_highest_version_var_in_current_scope(name)
        source_ref = (
            self.retrieve_source_ref(node.source_refs[0])
            if node.source_refs is not None and len(node.source_refs) > 0
            else C2ASourceRef("", -1, -1, -1, -1)
        )
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
                source_ref,
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
                source_ref,
                name,
                node,
            )
        ]
