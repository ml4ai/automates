from automates.program_analysis.CAST2GrFN.model.cast import source_ref
from automates.program_analysis.CAST2GrFN.model.cast.source_ref import SourceRef
from typing import List, Dict, NoReturn, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from automates.program_analysis.CAST2GrFN.model.cast import AstNode, var
from automates.model_assembly.metadata import (
    BaseMetadata,
    MetadataType,
    TypedMetadata,
    VariableFromSource,
)


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


@dataclass(repr=True, frozen=True)
class C2ASourceRef(object):
    """
    Represents a reference point of the containing object in the original source
    code. If a field of the line/col reference information is missing, it will
    hold the value -1.
    """

    file: str
    line_begin: int
    col_start: int
    line_end: int
    col_end: int

    def to_AIR(self):
        return self.__dict__


class C2AVariable(object):

    identifier_information: C2AIdentifierInformation
    version: int
    type_name: str
    source_ref: C2ASourceRef
    metadata: list

    def __init__(
        self,
        identifier_information: C2AIdentifierInformation,
        version: int,
        type_name: str,
        source_ref: C2ASourceRef,
    ):
        self.identifier_information = identifier_information
        self.version = version
        self.type_name = type_name
        self.source_ref = source_ref
        self.metadata = list()

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

    def add_metadata(self, data: BaseMetadata):
        self.metadata.append(data)

    def to_AIR(self):
        # TODO
        domain = {
            "type": "type",  # TODO what is this field?
            "mutable": False,  # TODO probably only mutable if object/list/dict type
        }
        if self.type_name == "Number":
            domain["name"] = "integer"
        elif self.type_name.startswith("object$"):
            name = self.type_name.split("object$")[-1]
            domain.update(
                {
                    "name": "object",
                    "object_name": name,
                }
            )
        else:
            domain["name"] = self.type_name

        has_from_source_metadata = False
        for m in self.metadata:
            if m.type == MetadataType.FROM_SOURCE:
                has_from_source_metadata = True
                break
        # If from_source does not exist already, then it wasnt handled by a special
        # case where we added a variable during processing, so add True from_source
        # metadata
        if not has_from_source_metadata:
            self.add_metadata(
                TypedMetadata.from_data(
                    {
                        "type": "FROM_SOURCE",
                        "provenance": {
                            "method": "PROGRAM_ANALYSIS_PIPELINE",
                            "timestamp": datetime.now(),
                        },
                        "from_source": True,
                        "creation_reason": "UNKNOWN",
                    }
                )
            )

        return {
            "name": self.build_identifier(),
            "source_refs": [self.source_ref.to_AIR()],
            "domain": domain,
            "domain_constraint": "(and (> v -infty) (< v infty))",  # TODO
            "metadata": [m.to_dict() for m in self.metadata],
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


def build_unique_list_with_order(l, predicate):
    new_list = []
    for i in l:
        res = predicate(i)
        if res not in new_list:
            new_list.append(res)
    return new_list


@dataclass(repr=True, frozen=False)
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
    # The reference to the source code that this lambda was derived from
    source_ref: C2ASourceRef

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


@dataclass(repr=True, frozen=False)
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
            "input": build_unique_list_with_order(
                self.input_variables, lambda v: v.build_identifier()
            ),
            "output": build_unique_list_with_order(
                self.output_variables, lambda v: v.build_identifier()
            ),
            "updated": build_unique_list_with_order(
                self.updated_variables, lambda v: v.build_identifier()
            ),
            "source_ref": self.source_ref.to_AIR(),
            "metadata": [],
        }


@dataclass(repr=True, frozen=False)
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
                "type": self.container_type.value,
            },
            # Note: Do not build a unique list because the same var could be
            # passed in multiple times
            "input": [v.build_identifier() for v in self.input_variables],
            "output": build_unique_list_with_order(
                self.output_variables, lambda v: v.build_identifier()
            ),
            "updated": build_unique_list_with_order(
                self.updated_variables, lambda v: v.build_identifier()
            ),
            "source_ref": self.source_ref.to_AIR(),
            "metadata": [],
        }


@dataclass(repr=True, frozen=False)
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
    # Defines the span of code for this container body in the original source code
    body_source_ref: C2ASourceRef
    # Tracks what variables were added as arguments to container from previous scope
    vars_from_previous_scope: List[C2AVariable]

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

    def add_body_source_ref(self, body_source_ref: SourceRef):
        self.body_source_ref = body_source_ref

    def add_var_used_from_previous_scope(self, var):
        self.vars_from_previous_scope.append(var)


@dataclass(repr=True, frozen=False)
class C2AFunctionDefContainer(C2AContainerDef):
    """
    Represents a top level container definition. Input variables will represent the arguments to the funciton in the AIR. Also contains a body.
    """

    return_type_name: str

    def to_AIR(self):
        return {
            # TODO
            "name": self.identifier_information.build_identifier(),
            "source_refs": [],
            "type": "function",
            "arguments": build_unique_list_with_order(
                self.arguments, lambda v: v.build_identifier()
            ),
            "updated": build_unique_list_with_order(
                self.updated_variables, lambda v: v.build_identifier()
            ),
            "return_value": build_unique_list_with_order(
                self.output_variables, lambda v: v.build_identifier()
            ),
            "body": [i.to_AIR() for i in self.body],
            "body_source_ref": self.body_source_ref.to_AIR(),
            "metadata": [],
        }


@dataclass(repr=True, frozen=False)
class C2ALoopContainer(C2AContainerDef):
    """
    Represents a top level container definition. Input variables will represent
    the arguments that go through the loop interface. Also contains a body.
    """

    # Represents the reference to the source code where the conditional for this loop is
    condition_source_ref: C2ASourceRef

    def to_AIR(self):
        return {
            # TODO
            "name": self.identifier_information.build_identifier(),
            "source_refs": [],
            "type": "loop",
            "arguments": build_unique_list_with_order(
                self.arguments, lambda v: v.build_identifier()
            ),
            "updated": build_unique_list_with_order(
                self.updated_variables, lambda v: v.build_identifier()
            ),
            "return_value": build_unique_list_with_order(
                self.output_variables, lambda v: v.build_identifier()
            ),
            "body": [i.to_AIR() for i in self.body],
            "body_source_ref": self.body_source_ref.to_AIR(),
            "condition_source_ref": self.condition_source_ref.to_AIR(),
            "metadata": [],
        }


@dataclass(repr=True, frozen=False)
class C2AIfContainer(C2AContainerDef):
    """
    Represents a top level container definition. Input variables will represent
    the arguments that go through the if interface. Also contains a body.
    """

    # Represents the reference to the source code where the conditional for this if is
    condition_source_ref: C2ASourceRef
    # Output vars per each condition in the if block. Represent else condition
    # as condition number -1.
    output_per_condition: Dict[int, List[C2AVariable]]

    def add_condition_outputs(self, condition_num, outputs):
        if condition_num not in self.output_per_condition:
            self.output_per_condition[condition_num] = []
        self.output_per_condition[condition_num].extend(outputs)

    def to_AIR(self):

        return {
            # TODO
            "name": self.identifier_information.build_identifier(),
            "source_refs": [],
            "type": "if-block",
            "arguments": build_unique_list_with_order(
                self.arguments, lambda v: v.build_identifier()
            ),
            "updated": build_unique_list_with_order(
                self.updated_variables, lambda v: v.build_identifier()
            ),
            "return_value": build_unique_list_with_order(
                self.output_variables, lambda v: v.build_identifier()
            ),
            "body": [i.to_AIR() for i in self.body],
            "body_source_ref": self.body_source_ref.to_AIR(),
            "condition_source_ref": self.condition_source_ref.to_AIR(),
            "metadata": [],
        }


@dataclass(repr=True, frozen=True)
class C2ATypeDef(object):
    class C2AType(str, Enum):
        INTEGER = "integer"
        FLOAT = "float"
        STRING = "string"
        LIST = "list"
        DICT = "dict"
        SET = "set"
        OBJECT = "object"

    name: str
    given_type: C2AType
    fields: Dict[str, C2AVariable]
    function_identifiers: List[str]
    source_ref: C2ASourceRef

    def to_AIR(self):
        air = self.__dict__
        air.update({"metadata": [], "metatype": "composite"})
        return air


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

    def build_extract_lambda(self, extract_var, output_variables):
        obj_var_name = extract_var.identifier_information.name
        lambda_dict_keys = [
            v.identifier_information.name.split("_", 1)[1] for v in output_variables
        ]
        lambda_dict_accesses = ",".join(
            [f'{obj_var_name}["{v}"]' for v in lambda_dict_keys if obj_var_name != v]
        )
        lambda_expr = f"lambda {obj_var_name}: ({lambda_dict_accesses})"
        return lambda_expr

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
                C2ASourceRef("", None, None, None, None),
                self.build_extract_lambda(var, [attr_var]),
                None,
            )
            self.var_to_current_extract_node[var] = extract_lambda
            return extract_lambda

        extract_lambda.output_variables.append(attr_var)
        extract_lambda.lambda_expr = self.build_extract_lambda(
            var, extract_lambda.output_variables
        )

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
                C2ASourceRef("", None, None, None, None),
                "",  # will be filled out when "get_outstandin_pack_node" is called
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
        # Add the updated version of the var after packing
        new_var = C2AVariable(
            var.identifier_information, var.version + 1, var.type_name, var.source_ref
        )
        pack_lambda.output_variables.append(new_var)

        # Add the correct lambda now that we have all vars to pack
        obj_var_name = var.identifier_information.name
        lambda_inputs = [
            v.identifier_information.name for v in pack_lambda.input_variables
        ]
        lambda_body_dict = ",".join(
            [
                f'"{v.split(f"{obj_var_name}_")[-1]}": ' + v
                for v in lambda_inputs
                if obj_var_name != v
            ]
        )
        lambda_expr = (
            f"lambda {','.join(lambda_inputs)}:"
            f"{{ **{obj_var_name}, **{{ {lambda_body_dict} }} }}"
        )
        pack_lambda.lambda_expr = lambda_expr

        # Delete from state map upon retrieval
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
        self.scope_stack = []
        self.current_module = "initial"
        self.current_function = None
        self.current_conditional = 0
        self.current_context = C2AVariableContext.UNKNOWN
        self.attribute_access_state = C2AAttributeAccessState()

    def add_container(self, con: C2AContainerDef):
        self.containers.append(con)

    def add_variable(self, var: C2AVariable):
        self.variables.append(var)

    def add_type(self, type: C2ATypeDef):
        self.types.append(type)

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
        Removes the last scope name from the stack and returns it
        """
        top = self.scope_stack[-1]
        self.scope_stack = self.scope_stack[:-1]
        return top

    def is_var_identifier_in_variables(self, identifier):
        for v in self.variables:
            if v.build_identifier() == identifier:
                return True
        return False

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

    def find_root_level_containers(self):
        called_containers = [
            s.identifier_information.build_identifier()
            for c in self.containers
            for s in c.body
            if isinstance(s, C2AContainerCallLambda)
        ]
        root_containers = [
            c.identifier_information.name
            for c in self.containers
            if c.build_identifier() not in called_containers
        ]
        return root_containers

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

        # Trim variables that are just defined and hanging. This seems like a
        # bug BUT it is actually a remnant of how GCC gives variable definitions.
        all_input_vars = {
            v for c in container_air for l in c["body"] for v in l["input"]
        }
        all_return_vars = {v for c in container_air for v in c["return_value"]}
        all_arg_vars = {v for c in container_air for v in c["arguments"]}
        # all_vars_into_lambdbas = {*all_input_vars, *all_return_vars, *all_arg_vars}

        all_vars_passed_through_lambdas = {
            v_name
            for c in container_air
            for l in c["body"]
            for v_name in l["input"] + l["output"]
            if len(l["input"]) > 0
        }
        hanging_vars = [
            v["name"]
            for v in var_air
            if v["name"] not in all_vars_passed_through_lambdas
        ]

        def is_hanging_lambda(l, c):
            hanging_lambda = len(l["input"]) == 0 and all(
                [
                    v not in {*all_input_vars, *all_return_vars, *all_arg_vars}
                    for v in l["output"]
                ]
            )
            return hanging_lambda

        for con in container_air:
            hanging_lambda_vars = [
                v for l in con["body"] if is_hanging_lambda(l, con) for v in l["output"]
            ]
            # Trim variables
            var_air = [v for v in var_air if v["name"] not in hanging_lambda_vars]
            if "return_value" in con:
                hanging_ret_vars = {v for v in con["return_value"] if v in hanging_vars}
                lambdas_calling = [
                    l
                    for c in container_air
                    for l in c["body"]
                    if l["function"]["type"] == "container"
                    and l["function"]["name"] == con["name"]
                ]

                if len(lambdas_calling) == 0:
                    con["return_value"] = [
                        v for v in con["return_value"] if v not in hanging_ret_vars
                    ]
                    all_return_vars.difference_update(hanging_ret_vars)
                    var_air = [v for v in var_air if v["name"] not in hanging_ret_vars]

            if "arguments" in con:
                hanging_arg_vars = {v for v in con["arguments"] if v in hanging_vars}
                con["arguments"] = [
                    v for v in con["arguments"] if v not in hanging_arg_vars
                ]
                all_arg_vars.difference_update(hanging_arg_vars)
                var_air = [v for v in var_air if v["name"] not in hanging_arg_vars]

            con["body"] = [l for l in con["body"] if not is_hanging_lambda(l, con)]

        return {"containers": container_air, "variables": var_air, "types": types_air}
