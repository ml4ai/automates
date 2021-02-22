from typing import List, Dict
from enum import Enum

from automates.program_analysis.CAST2GrFN.model.cast import AstNode


class CASTToAIRException(Exception):
    """
    Used to create exceptions during the CAST to AIR execution

    Args:
        Exception: An exception that occured during CAST to AIR execution
    """

    pass


class C2AIdentifierType(str, Enum):
    UNKNOWN = "unknown"
    VARIABLE = "variable"
    CONTAINER = "container"
    LAMBDA = "lambda"


class C2AIdentifierInformation(object):

    name: str
    scope: List[str]
    module: str
    identifier_type: C2AIdentifierType

    def __init__(
        self,
        name: str,
        scope: List[str],
        module: str,
        identifier_type: C2AIdentifierType,
    ):
        self.name = name
        self.scope = scope
        self.module = module
        self.identifier_type = identifier_type

    def build_identifier(self):
        return f'@{self.identifier_type}::{self.module}::{".".join(self.scope)}::{self.name}'


class C2AVariable(object):

    identifier_information: C2AIdentifierInformation
    version: int
    type_name: str

    def __init__(
        self,
        identifier_information: C2AIdentifierInformation,
        version: int,
        type_name: str,
    ):
        self.identifier_information = identifier_information
        self.version = version
        self.type_name = type_name

    def get_name(self):
        return self.identifier_information.name

    def build_identifier(self):
        """
        Builds the variable identifier which uses the identifier from identifier
        information plus the variable version

        Returns:
            str: Unique variable identifier
        """
        return f"{self.identifier_information.build_identifier()}::{str(self.version)}"

    def to_AIR(self):
        return {
            "name": self.build_identifier(),
            "source_refs": [],
            "domain": {
                "name": self.type_name,
                "type": "type",  # TODO what is this field
                "mutable": False,  # TODO probably only mutable if object/list/dict type
            },
            "domain_constraint": "(and (> v -infty) (< v infty))",  # TODO
        }


class C2ALambdaType(str, Enum):
    UNKNOWN = "unknown"
    ASSIGN = "assign"
    CONDITION = "condition"
    DECISION = "decision"


class C2ALambda(object):
    """
    Represents an executable container/ function to transition between states in AIR

    lambda, container, if-block, function
    """

    # Identifying information for lambda function
    identifier_information: C2AIdentifierInformation
    # Represents the variables coming into a lambda or container
    input_variables: List[C2AVariable]
    # Represents the new versions of variables that are created and output
    output_variables: List[C2AVariable]
    # Represents variables that were updated (typically list/dict/object with fields changed)
    updated_variables: List[C2AVariable]
    # The type of the container.
    container_type: C2ALambdaType

    def __init__(
        self,
        identifier_information: C2AIdentifierInformation,
        input_variables: List[C2AVariable],
        output_variables: List[C2AVariable],
        updated_variables: List[C2AVariable],
        container_type: C2ALambdaType,
    ):
        self.identifier_information = identifier_information
        self.input_variables = input_variables
        self.output_variables = output_variables
        self.updated_variables = updated_variables
        self.container_type = container_type

    def build_name(self):
        var = None
        # TODO how should we build the name if there is multiple updated/output vars?
        # Will this situation be possible?
        if len(self.output_variables) > 0:
            var = self.output_variables[0]
        elif len(self.updated_variables) > 0:
            var = self.updated_variables[0]
        else:
            raise CASTToAIRException(f"No variables output or updated by lambda")

        return (
            f"{self.identifier_information.module}"
            f"__{'.'.join(self.identifier_information.scope)}"
            f"__{self.container_type}"
            f"__{var.identifier_information.name}"
            f"__{var.version}"
        )

    def to_AIR(self):
        return self


class C2AExpressionLambda(C2ALambda):
    """
    A type of function within AIR that represents an executable lambda expression that transitions
    between states of the data flow of the program
    """

    lambda_expr: str
    cast: AstNode

    def __init__(
        self,
        identifier_information: C2AIdentifierInformation,
        input_variables: List[C2AVariable],
        output_variables: List[C2AVariable],
        updated_variables: List[C2AVariable],
        container_type: C2ALambdaType,
        lambda_expr: str,
        cast: AstNode,
    ):
        super().__init__(
            identifier_information,
            input_variables,
            output_variables,
            updated_variables,
            container_type,
        )
        self.lambda_expr = lambda_expr
        self.cast = cast

    def to_AIR(self):
        return {
            "function": {
                "name": self.build_name(),
                "type": "lambda",
                "code": self.lambda_expr,
            },
            "input": [v.build_identifier() for v in self.input_variables],
            "output": [v.build_identifier() for v in self.output_variables],
            "updated": [v.build_identifier() for v in self.updated_variables],
        }


class C2AContainerCallLambda(C2ALambda):
    """
    Represents the call/passing to another container found in the body of a container definition
    """

    name: str
    original_cast: AstNode
    return_type_name: str

    def __init__(
        self,
        input_variables: List[C2AVariable],
        output_variables: List[C2AVariable],
        updated_variables: List[C2AVariable],
        name: str,
        original_cast: AstNode,
        return_type_name: str,
    ):
        super().__init__(input_variables, output_variables, updated_variables)
        self.name = name
        self.original_cast = original_cast
        self.return_type_name = return_type_name

    def to_AIR(self):
        return self


class C2AContainerDef(object):
    """
    Represents a top level AIR container def. Has its arguments, outputs/ updates, and a body

    lambda, container, if-block, function
    """

    # Name of the containrt
    identifier_information: C2AIdentifierInformation
    # Represents the variables coming into a lambda or container
    arguments: List[C2AVariable]
    # Represents the new versions of variables that are created and output
    output_variables: List[C2AVariable]
    # Represents variables that were updated (typically list/dict/object with fields changed)
    updated_variables: List[C2AVariable]
    # Represents the executable body statements
    body: List[C2ALambda]

    def __init__(
        self,
        identifier_information: C2AIdentifierInformation,
        arguments: List[C2AVariable],
        output_variables: List[C2AVariable],
        updated_variables: List[C2AVariable],
        body: List[C2ALambda],
    ):
        self.identifier_information = identifier_information
        self.arguments = arguments
        self.output_variables = output_variables
        self.updated_variables = updated_variables
        self.body = body

    def build_identifier(self):
        return self.identifier_information.build_identifier()

    def to_AIR(self):
        return self


class C2AFunctionDefContainer(C2AContainerDef):
    """
    Represents a top level container definition. Input variables will represent the arguments to the funciton in the AIR. Also contains a body.
    """

    return_type_name: str

    def __init__(
        self,
        identifier_information: C2AIdentifierInformation,
        arguments: List[C2AVariable],
        output_variables: List[C2AVariable],
        updated_variables: List[C2AVariable],
        body: List[C2ALambda],
        return_type_name: str,
    ):
        super().__init__(
            identifier_information, arguments, output_variables, updated_variables, body
        )
        self.return_type_name = return_type_name

    def to_AIR(self):
        return {
            # TODO
            "name": self.identifier_information.build_identifier(),
            "source_refs": [],
            "type": "function",
            "arguments": [v.build_identifier() for v in self.arguments],
            "updated": [v.build_identifier() for v in self.updated_variables],
            # TODO change to specify a single return val
            "return_value": [v.build_identifier() for v in self.output_variables],
            "body": [i.to_AIR() for i in self.body],
        }


class C2ABlockContainer(C2AContainerDef):
    """"""

    original_cast: AstNode
    return_type_name: str

    def __init__(self, name: str, original_cast: AstNode, return_type_name: str):
        self.name = name
        self.original_cast = original_cast
        self.return_type_name = return_type_name

    def to_AIR(self):
        return self


class C2ATypeDef(object):
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


class C2AState(object):
    containers: List[C2AContainerDef]
    variables: List[C2AVariable]
    types: List[C2ATypeDef]
    scope_stack: List[str]
    current_module: str

    def __init__(self):
        self.containers = list()
        self.variables = list()
        self.types = list()
        self.scope_stack = ["@global"]
        self.current_module = "initial"

    def add_container(self, con: C2AContainerDef):
        self.containers.append(con)

    def add_variable(self, var: C2AVariable):
        self.variables.append(var)

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
        container_air = [c.to_AIR() for c in self.containers]
        var_air = [v.to_AIR() for v in self.variables]
        types_air = [t.to_AIR() for t in self.types]

        # TODO actually create AIR objects for AIR -> GrFN
        # I think the AIR intermediate structure will need to change
        # to reflect changes in grfn such as typing.
        # C, V, T, D = dict(), dict(), dict(), dict()

        return {"containers": container_air, "variables": var_air, "types": types_air}
