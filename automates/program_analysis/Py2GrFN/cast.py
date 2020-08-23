import ast
from functools import singledispatch


class CAST2GrFN:
    def __init__(self, tree: ast.Module):
        self.functions = dict()
        self.containers = dict()
        self.variables = dict()
        self.types = dict()
        self.cur_statements = list()
        self.cur_function = None
        self.cur_parent_node = None
        self.cur_node = None

    @singledispatch
    def translate(self, node: ast.AbstractNode):
        raise NotImplementedError(f"Unknown AST node of type: {type(node)}")

    # ==========================================================================
    # FUNCTION AND DEFINITION NODES
    # ==========================================================================
    @translate.register
    def _(self, node: ast.FunctionDef):
        if len(self.cur_statements) > 0 and self.cur_function is not None:
            self.functions[self.cur_function] = self.cur_statements
        inputs = self.translate(node.args)
        updated = list()  # Figure out how to populate this
        returned = self.translate(node.returns)
        body = self.translate(node.body)

    @translate.register
    def _(self, node: ast.Import):
        # TODO: finish implementing this function
        aliases = [self.translate(name) for name in node.names]
        return NotImplemented

    @translate.register
    def _(self, node: ast.ImportFrom):
        # TODO: finish implementing this function
        module_names = [self.translate(name) for name in node.names]
        return NotImplemented

    @translate.register
    def _(self, node: ast.Alias):
        mod_name = node.name
        new_name = node.asname  # NOTE: This can be None

        # TODO: finish implementing this function
        return NotImplemented

    # ==========================================================================

    # ==========================================================================
    # CONTROL FLOW NODES
    # ==========================================================================
    @translate.register
    def _(self, node: ast.If):
        # TODO: Implement this function
        test_comparison = self.translate(node.test)
        statements = self.translate(node.body)
        next_condition = self.translate(node.orelse)
        return NotImplemented

    @translate.register
    def _(self, node: ast.For):
        # TODO: Implement this function
        return NotImplemented

    # ==========================================================================

    # ==========================================================================
    # STATEMENT NODES
    # ==========================================================================
    @translate.register
    def _(self, node: ast.Assign):
        outputs = [self.translate(var) for var in node.targets]
        lambda_expr = self.translate(node.value)
        inputs = self.get_input_nodes(node.value)

        self.cur_statements.append(
            {
                "function": {
                    "name": None,  # TODO: figure this out
                    "type": "lambda",
                    "code": lambda_expr,
                },
                "input": inputs,
                "output": outputs,
                "updated": [],
            }
        )

    @translate.register
    def _(self, node: ast.AnnAssign):
        output = self.translate(node.target)
        lambda_expr = self.translate(node.value)
        inputs = []

    @translate.register
    def _(self, node: ast.AugAssign):
        # TODO: Implement this function
        return NotImplemented

    @translate.register
    def _(self, node: ast.Print):
        # NOTE: Nothing to be done for now
        pass

    @translate.register
    def _(self, node: ast.Raise):
        # NOTE: Nothing to be done for now
        pass

    @translate.register
    def _(self, node: ast.Assert):
        # NOTE: Nothing to be done for now
        pass

    @translate.register
    def _(self, node: ast.Delete):
        # NOTE: Nothing to be done for now
        pass

    @translate.register
    def _(self, node: ast.Pass):
        # NOTE: Nothing to be done for now
        pass

    # ==========================================================================
