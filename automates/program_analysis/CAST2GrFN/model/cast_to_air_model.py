from typing import List, Dict
from enum import Enum

from automates.program_analysis.CAST2GrFN.model.cast import AstNode


class CASTToAIRException(Exception):
    pass


class C2AVariable:

    version: int
    name: str
    scope: List[str]
    module: str
    type_name: str

    def __init__(
        self, version: int, name: str, scope: List[str], module: str, type_name: str
    ):
        self.version = version
        self.name = name
        self.scope = scope
        self.module = module
        self.type_name = type_name
        pass

    def build_identifier(self):
        return f'@variable::{self.module}::{".".join(self.scope)}::{self.name}::{str(self.version)}'

    def to_AIR(self):
        return self


class C2AExpression:

    variables: List[C2AVariable]
    lambda_expr: str

    def __init__(self, variables: List[C2AVariable], lambda_expr: str):
        self.variables = variables
        self.lambda_expr = lambda_expr

    def to_AIR(self):
        return self


class C2AFunction:

    name: str
    original_cast: AstNode
    return_type_name: str

    def __init__(self, name: str, original_cast: AstNode, return_type_name: str):
        self.name = name
        self.original_cast = original_cast
        self.return_type_name = return_type_name

    def to_AIR(self):
        return self


class C2ATypeDef:
    class C2AType(Enum):
        INTEGER = 1
        FLOAT = 2
        STRING = 3
        LIST = 4
        DICT = 5
        SET = 6
        OBJECT = 7

    name: str
    given_type: C2AType
    fields: Dict[str, str]
    function_identifiers: List[str]

    def __init__(
        self,
        name: str,
        given_type: C2AType,
        fields: Dict[str, str],
        function_identifiers: List[str],
    ):
        self.name = name
        self.given_type = given_type
        self.fields = fields

    def to_AIR(self):
        return self


class C2AState:
    functions: List[C2AFunction]
    variables: List[C2AVariable]
    types: List[C2ATypeDef]
    scope_stack: List[str]
    current_module: str

    def __init__(self):
        self.functions = list()
        self.variables = list()
        self.types = list()
        self.scope_stack = ["@global"]
        self.current_module = "initial"

    def get_scope_stack(self):
        """
        Returns the current scope of the CAST to AIR state
        """
        return self.scope_stack

    def push_scope(self, scope):
        """
        Places the name scope level name onto the scope stack
        """
        self.scope_stack.append(scope)

    def pop_scope(self):
        """
        Removes the last scope name from the stack
        """
        self.scope_stack = self.scope_stack[:-1]

    def find_highest_version_var(self, var_name):
        """
        Given a variable name, finds the highest version defined
        for that variable given the current scope
        """
        # Check that the global/function_name are the same
        # TODO define what needs to e checked here etter
        def share_scope(scope1, scope2):
            return scope1[:1] == scope2[:1]

        instances = [
            v
            for v in self.variables
            if v.name == var_name and share_scope(self.scope_stack, v.scope)
        ]
        return max(instances, key=lambda v: v.version, default=None)

    def find_next_var_version(self, var_name):
        """
        Determines the next version of a variable given its name and
        variables in the current scope.
        """
        current_highest_ver = self.find_highest_version_var(var_name)
        return current_highest_ver + 1 if current_highest_ver is not None else -1

    def to_AIR(self):
        """
        Translates the model used to translate CAST to AIR into the
        final AIR structure.
        """
        func_air = [f.to_AIR() for f in self.functions]
        var_air = [v.to_AIR() for v in self.variables]
        types_air = [t.to_AIR() for t in self.types]

        # TODO actually create AIR objects for AIR -> GrFN
        # I think the AIR intermediate structure will need to change
        # to reflect changes in grfn.
        # C, V, T, D = dict(), dict(), dict(), dict()

        return {"functions": func_air, "variables": var_air, "types": types_air}
