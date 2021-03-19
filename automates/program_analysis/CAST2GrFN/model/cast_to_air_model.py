from typing import List, Dict, Set
from enum import Enum
from dataclasses import dataclass

from automates.program_analysis.CAST2GrFN.model.cast import AstNode, var


class C2ATypeError(TypeError):
    """
    Used to create exceptions during the CAST to AIR execution

    Args:
        Exception: An exception that occured during CAST to AIR execution
    """

    pass


class C2ARuntimeError(Exception):
    """
    Used for any runtime errors that occur during CAST --> AIR processing

    Args:
        Exception: An exception that occured during CAST to AIR execution
    """

    pass


class C2ANameError(NameError):
    """
    Used when name errors occur (such as a missing member variable for some
    object) during CAST

    Args:
        Exception: An exception that occured during CAST to AIR execution
    """

    pass


class C2AValueError(Exception):
    """
    Used when an operation cannot be performed for a given value during CAST

    Args:
        Exception: An exception that occured during CAST to AIR execution
    """

    pass


class C2AException(Exception):
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
    DECISION = "decision"
    PACK = "pack"
    EXTRACT = "extract"


@dataclass(repr=True, frozen=True)
class C2AIdentifierInformation(object):

    name: str
    scope: List[str]
    module: str
    identifier_type: C2AIdentifierType

    def build_identifier(self):
        return f'@{self.identifier_type}::{self.module}::{".".join(self.scope)}::{self.name}'


# @dataclass(repr=True, frozen=True)
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
        # TODO
        air_type = ""
        if self.type_name == "Number":
            air_type = "float"
        else:
            air_type = self.type_name

        return {
            "name": self.build_identifier(),
            "source_refs": [],
            "domain": {
                "name": air_type,
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
    EXIT = "exit"
    RETURN = "return"
    CONTAINER = "container"
    OPERATOR = "operator"
    EXTRACT = "extract"
    PACK = "pack"


@dataclass(repr=True, frozen=True)
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

    def build_name(self):
        var = None
        # TODO how should we build the name if there is multiple updated/output vars?
        # Will this situation be possible?
        if len(self.output_variables) > 0:
            var = self.output_variables[0]
        elif len(self.updated_variables) > 0:
            var = self.updated_variables[0]
        else:
            raise C2AException(f"No variables output or updated by lambda")

        return (
            f"{self.identifier_information.module}"
            f"__{'.'.join(self.identifier_information.scope)}"
            f"__{self.container_type}"
            f"__{var.identifier_information.name}"
            f"__{var.version}"
        )

    def to_AIR(self):
        return self


@dataclass(repr=True, frozen=True)
class C2AExpressionLambda(C2ALambda):
    """
    A type of function within AIR that represents an executable lambda expression that transitions
    between states of the data flow of the program
    """

    lambda_expr: str
    cast: AstNode

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


@dataclass(repr=True, frozen=True)
class C2AContainerCallLambda(C2ALambda):
    """
    Represents the call/passing to another container found in the body of a container definition
    """

    def build_name(self):
        return self.identifier_information.build_identifier()

    def to_AIR(self):
        return {
            "function": {
                "name": self.identifier_information.build_identifier(),
                "type": "container",
            },
            "input": [v.build_identifier() for v in self.input_variables],
            "output": [v.build_identifier() for v in self.output_variables],
            "updated": [v.build_identifier() for v in self.updated_variables],
        }


@dataclass(repr=True, frozen=True)
class C2AReturnLambda(C2ALambda):
    """
    Represents the return from a container found in the body of a container definition
    """

    def to_AIR(self):
        return {
            "function": {
                "name": self.identifier_information.build_identifier(),
                "type": "lambda",
            },
            "input": [v.build_identifier() for v in self.input_variables],
            "output": [v.build_identifier() for v in self.output_variables],
            "updated": [v.build_identifier() for v in self.updated_variables],
        }


@dataclass(repr=True, frozen=True)
class C2AObjectLambda(C2ALambda):
    """
    Represents the return from a container found in the body of a container definition
    """

    def to_AIR(self):
        return {
            "function": {
                "name": self.identifier_information.build_identifier(),
                "type": "container",
            },
            "input": [v.build_identifier() for v in self.input_variables],
            "output": [v.build_identifier() for v in self.output_variables],
            "updated": [v.build_identifier() for v in self.updated_variables],
        }


@dataclass(repr=True, frozen=True)
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

    def build_identifier(self):
        return self.identifier_information.build_identifier()

    def to_AIR(self):
        return self

    def add_arguments(self, arguments_to_add: List[C2AVariable]):
        for v in arguments_to_add:
            if v not in set(self.arguments):
                self.arguments.append(v)

    def add_outputs(self, output_variables_to_add: List[C2AVariable]):
        # self.output_variables.update(set(output_variables_to_add))
        for v in output_variables_to_add:
            if v not in set(self.output_variables):
                self.output_variables.append(v)

    def add_updated(self, updated_variables_to_add: List[C2AVariable]):
        # self.updated_variables.update(set(updated_variables_to_add))
        for v in updated_variables_to_add:
            if v not in set(self.updated_variables):
                self.updated_variables.append(v)

    def add_body_lambdas(self, body_to_add: List[C2ALambda]):
        self.body.extend(body_to_add)


@dataclass(repr=True, frozen=True)
class C2AFunctionDefContainer(C2AContainerDef):
    """
    Represents a top level container definition. Input variables will represent the arguments to the funciton in the AIR. Also contains a body.
    """

    return_type_name: str

    def to_AIR(self):
        body_without_returns = [
            bb for bb in self.body if not isinstance(bb, C2AReturnLambda)
        ]
        # TODO
        return_lambda = [bb for bb in self.body if not isinstance(bb, C2AReturnLambda)]
        # TODO multiple returns? probably need a decision node with all possible
        # return vals going in?

        return {
            # TODO
            "name": self.identifier_information.build_identifier(),
            "source_refs": [],
            "type": "function",
            "arguments": {v.build_identifier() for v in self.arguments},
            "updated": {v.build_identifier() for v in self.updated_variables},
            "return_value": {v.build_identifier() for v in self.output_variables},
            "body": [i.to_AIR() for i in body_without_returns],
        }


@dataclass(repr=True, frozen=True)
class C2ALoopContainer(C2AContainerDef):
    """
    Represents a top level container definition. Input variables will represent
    the arguments that go through the loop interface. Also contains a body.
    """

    def to_AIR(self):
        body_without_returns = [
            bb for bb in self.body if not isinstance(bb, C2AReturnLambda)
        ]
        # TODO
        returns = [bb for bb in self.body if not isinstance(bb, C2AReturnLambda)]

        return {
            # TODO
            "name": self.identifier_information.build_identifier(),
            "source_refs": [],
            "type": "loop",
            "arguments": {v.build_identifier() for v in self.arguments},
            "updated": {v.build_identifier() for v in self.updated_variables},
            "return_value": {v.build_identifier() for v in self.output_variables},
            "body": [i.to_AIR() for i in body_without_returns],
        }


class C2AIfContainer(C2AContainerDef):
    """
    Represents a top level container definition. Input variables will represent
    the arguments that go through the if interface. Also contains a body.
    """

    def to_AIR(self):
        body_without_returns = [
            bb for bb in self.body if not isinstance(bb, C2AReturnLambda)
        ]
        # TODO
        returns = [bb for bb in self.body if not isinstance(bb, C2AReturnLambda)]

        return {
            # TODO
            "name": self.identifier_information.build_identifier(),
            "source_refs": [],
            "type": "if-block",
            "arguments": {v.build_identifier() for v in self.arguments},
            "updated": {v.build_identifier() for v in self.updated_variables},
            "return_value": {v.build_identifier() for v in self.output_variables},
            "body": [i.to_AIR() for i in body_without_returns],
        }


@dataclass(repr=True, frozen=True)
class C2ABlockContainer(C2AContainerDef):
    """"""

    original_cast: AstNode
    return_type_name: str

    def to_AIR(self):
        return self


@dataclass(repr=True, frozen=True)
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

    def to_AIR(self):
        return self


class C2AAttributeAccessState(object):

    var_to_current_extract_node: Dict[str, C2ALambda]
    var_to_current_pack_node: Dict[str, C2ALambda]

    def __init__(self):
        self.var_to_current_extract_node = {}
        self.var_to_current_pack_node = {}

    def need_attribute_extract(self, var, attr_var):
        # Check if the attr_var name appears in either the extract node for the
        # var or the current pack var. If it exists in either, we should not
        # add the same attribute for extract.
        vars_to_check = (
            self.var_to_current_extract_node[var].output_variables
            if var in self.var_to_current_extract_node
            else []
        ) + (
            self.var_to_current_pack_node[var].input_variables
            if var in self.var_to_current_pack_node
            else []
        )

        return not any(
            [
                v.identifier_information.name == attr_var.identifier_information.name
                for v in vars_to_check
            ]
        )

    def add_attribute_access(self, var, attr_var):
        extract_lambda = self.var_to_current_extract_node.get(var, None)
        if extract_lambda is None:
            id = var.identifier_information
            extract_lambda = C2AExpressionLambda(
                C2AIdentifierInformation(
                    "EXTRACT", id.scope, id.module, C2AIdentifierType.CONTAINER
                ),
                [var],
                [attr_var],
                [],
                C2ALambdaType.EXTRACT,
                "lambda : None",  # TODO
                None,
            )
            self.var_to_current_extract_node[var] = extract_lambda
            return extract_lambda

        extract_lambda.output_variables.append(attr_var)

    def add_attribute_to_pack(self, var, attr_var):
        pack_lambda = self.var_to_current_pack_node.get(var, None)
        if pack_lambda is None:
            id = var.identifier_information
            pack_lambda = C2AExpressionLambda(
                C2AIdentifierInformation(
                    "PACK", id.scope, id.module, C2AIdentifierType.CONTAINER
                ),
                [var],
                [],
                [],
                C2ALambdaType.PACK,
                "lambda : None",  # TODO
                None,
            )

        for v in pack_lambda.input_variables:
            if v.identifier_information.name == attr_var.identifier_information.name:
                pack_lambda.input_variables.remove(v)
        pack_lambda.input_variables.append(attr_var)

        self.var_to_current_pack_node[var] = pack_lambda

    def has_outstanding_pack_nodes(self):
        return bool(self.var_to_current_pack_node)

    def get_outstanding_pack_node(self, var):
        pack_lambda = self.var_to_current_pack_node.get(var)
        new_var = C2AVariable(
            var.identifier_information, var.version + 1, var.type_name
        )
        pack_lambda.output_variables.append(new_var)

        # Delete upon retrieval
        del self.var_to_current_pack_node[var]

        if var in self.var_to_current_extract_node:
            del self.var_to_current_extract_node[var]

        return pack_lambda

    def get_outstanding_pack_nodes(self):
        return [
            self.get_outstanding_pack_node(k)
            for k in self.var_to_current_pack_node.copy().keys()
        ]


class C2AVariableContext(Enum):
    LOAD = 0
    STORE = 1
    ATTR_VALUE = 2
    UNKNOWN = 3


class C2AState(object):
    containers: List[C2AContainerDef]
    variables: List[C2AVariable]
    types: List[C2ATypeDef]
    scope_stack: List[str]
    current_module: str
    current_function: C2AFunctionDefContainer
    current_conditional: int
    attribute_access_state: C2AAttributeAccessState
    current_context: C2AVariableContext

    def __init__(self):
        self.containers = list()
        self.variables = list()
        self.types = list()
        self.scope_stack = ["global"]
        self.current_module = "initial"
        self.current_function = None
        self.current_conditional = 0
        self.current_context = C2AVariableContext.UNKNOWN
        self.attribute_access_state = C2AAttributeAccessState()

    def add_container(self, con: C2AContainerDef):
        self.containers.append(con)

    def add_variable(self, var: C2AVariable):
        self.variables.append(var)

    def get_scope_stack(self):
        """
        Returns the current scope of the CAST to AIR state
        """
        return self.scope_stack.copy()

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

    def find_highest_version_var_in_scope(self, var_name, scope):
        """
        Given a variable name, finds the highest version defined
        for that variable given a scope
        """
        # Check that the global/function_name are the same
        # TODO define what needs to be checked here better
        def share_scope(scope1, scope2):
            return scope1 == scope2

        instances = [
            v
            for v in self.variables
            if v.identifier_information.name == var_name
            and share_scope(scope, v.identifier_information.scope)
        ]
        return max(instances, key=lambda v: v.version, default=None)

    def find_highest_version_var_in_previous_scopes(self, var_name):
        """
        Given a variable name, finds the highest version defined
        for that variable along our current scope path
        """
        # Subtract one so we look at all scopes except "global"
        i = len(self.scope_stack)
        while i >= 0:
            res = self.find_highest_version_var_in_scope(var_name, self.scope_stack[:i])
            if res is not None:
                return res
            i -= 1

        return None

    def find_highest_version_var_in_current_scope(self, var_name):
        """
        Given a variable name, finds the highest version defined
        for that variable given the current scope
        """
        return self.find_highest_version_var_in_scope(var_name, self.scope_stack)

    def find_next_var_version(self, var_name):
        """
        Determines the next version of a variable given its name and
        variables in the current scope.
        """
        current_highest_ver = self.find_highest_version_var_in_current_scope(var_name)
        return (
            current_highest_ver.version + 1 if current_highest_ver is not None else -1
        )

    def find_container(self, scope):
        matching = [
            c
            for c in self.containers
            if c.identifier_information.scope + [c.identifier_information.name] == scope
        ]

        return matching[0] if matching else None

    def get_next_conditional(self):
        cur_cond = self.current_conditional
        self.current_conditional += 1
        return cur_cond

    def reset_conditional_count(self):
        self.current_conditional = 0

    def reset_current_function(self):
        self.current_function = None

    def set_variable_context(self, context):
        self.current_context = context

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
