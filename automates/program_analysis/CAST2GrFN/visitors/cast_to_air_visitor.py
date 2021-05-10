import typing
from functools import singledispatchmethod

from .cast_visitor import CASTVisitor
from automates.program_analysis.CAST2GrFN.model.cast_to_air_model import (
    C2AState,
    C2ALambda,
    C2ALambdaType,
    C2AExpressionLambda,
    C2AVariable,
    C2AFunctionDefContainer,
    C2ATypeDef,
    C2AIdentifierInformation,
    C2AIdentifierType,
    C2ATypeError,
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
        self.visit_list(self.cast_nodes)
        return self.state.to_AIR()

    @singledispatchmethod
    def visit(self, node: AstNode):
        """
        TODO
        """
        raise C2ATypeError(
            f"Unrecognized type in CASTToAIRVisitor.visit: {type(node)}"
        )

    @visit.register
    def _(self, node: Assignment):
        """
        TODO
        """
        left_res = self.visit(node.left)
        right_res = self.visit(node.right)

        input_variables = right_res.input_variables
        output_variables = list()
        updated_variables = list()
        if isinstance(node.left, Var):
            # If we are assigning to strictly a var, create
            # the new version of the var
            assigned_var_name = left_res.input_variables[0].get_name()
            new_ver = self.state.find_next_var_version(assigned_var_name)
            new_var = C2AVariable(
                C2AIdentifierInformation(
                    assigned_var_name,
                    self.state.scope_stack,
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
        lambda_expr = f"lambda {','.join({v.get_name() for v in right_res.input_variables})}: {right_res.lambda_expr}"

        return C2AExpressionLambda(
            C2AIdentifierInformation(
                C2ALambdaType.ASSIGN,
                self.state.scope_stack,
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

    @visit.register
    def _(self, node: Attribute):
        """
        TODO
        """
        return NotImplemented

    @visit.register
    def _(self, node: BinaryOp):
        """
        TODO
        """
        return NotImplemented

    @visit.register
    def _(self, node: BinaryOperator):
        """
        TODO
        """
        return NotImplemented

    @visit.register
    def _(self, node: Call):
        """
        TODO
        """
        return NotImplemented

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

    @visit.register
    def _(self, node: FunctionDef):
        """
        TODO
        """
        self.state.push_scope(node.name)

        args_result = self.visit_list(node.func_args)
        body_result = self.visit_list(node.body)

        self.state.pop_scope()

        func_con = C2AFunctionDefContainer(
            C2AIdentifierInformation(
                node.name,
                self.state.scope_stack,
                self.state.current_module,
                C2AIdentifierType.CONTAINER,
            ),
            args_result,
            [],
            [],
            body_result,
            "",  # TODO
        )
        self.state.add_container(func_con)

    @visit.register
    def _(self, node: List):
        """
        TODO
        """
        return NotImplemented

    @visit.register
    def _(self, node: Loop):
        """
        TODO
        """
        return NotImplemented

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
    def _(self, node: ModelIf):
        """
        TODO
        """
        return NotImplemented

    @visit.register
    def _(self, node: ModelReturn):
        """
        TODO
        """
        return NotImplemented

    @visit.register
    def _(self, node: Module):
        """
        TODO
        """
        # TODO module cast node should be updated with name
        body_res = self.visit_list(node.body)

    @visit.register
    def _(self, node: Name):
        """
        TODO
        """
        return node.name

    @visit.register
    def _(self, node: Number):
        """
        TODO
        """
        return C2AExpressionLambda(
            C2AIdentifierInformation(
                C2ALambdaType.UNKNOWN,
                self.state.scope_stack,
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
        return NotImplemented

    @visit.register
    def _(self, node: UnaryOperator):
        """
        TODO
        """
        return NotImplemented

    @visit.register
    def _(self, node: VarType):
        """
        TODO
        """
        return NotImplemented

    @visit.register
    def _(self, node: Var):
        """
        TODO
        """
        name = node.val
        var_obj = self.state.find_highest_version_var(name)
        if var_obj is None:
            var_obj = C2AVariable(
                C2AIdentifierInformation(
                    name,
                    self.state.scope_stack,
                    self.state.current_module,
                    C2AIdentifierType.VARIABLE,
                ),
                -1,
                node.type,
            )

        return C2AExpressionLambda(
            C2AIdentifierInformation(
                C2ALambdaType.UNKNOWN,
                self.state.scope_stack,
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
