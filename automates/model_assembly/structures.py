from abc import ABC, abstractmethod
from enum import Enum, auto, unique
from dataclasses import dataclass
from typing import List
import re

from .code_types import CodeType


@dataclass(repr=False, frozen=True)
class GenericIdentifier(ABC):
    namespace: str
    scope: str

    @staticmethod
    def from_str(data: str):
        components = data.split("::")
        type_str = components[0]
        if type_str == "@container":
            if len(components) == 3:
                (_, ns, sc) = components
                return ContainerIdentifier(ns, sc, "--")
            (_, ns, sc, n) = components
            if sc != "@global":
                n = f"{sc}.{n}"
            return ContainerIdentifier(ns, sc, n)
        elif type_str == "@type":
            (_, ns, sc, n) = components
            return TypeIdentifier(ns, sc, n)
        elif type_str == "@variable":
            (_, ns, sc, n, idx) = components
            return VariableIdentifier(ns, sc, n, int(idx))

    def is_global_scope(self):
        return self.scope == "@global"

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    def __str__(self):
        return NotImplemented


@dataclass(repr=False, frozen=True)
class ContainerIdentifier(GenericIdentifier):
    con_name: str

    def __str__(self):
        return f"Con -- {self.con_name} ({self.namespace}.{self.scope})"


@dataclass(repr=False, frozen=True)
class TypeIdentifier(GenericIdentifier):
    type_name: str

    def __str__(self):
        return f"Type -- {self.type_name} ({self.namespace}.{self.scope})"


@dataclass(repr=False, frozen=True)
class VariableIdentifier(GenericIdentifier):
    var_name: str
    index: int

    @classmethod
    def from_str_and_con(cls, data: str, con: ContainerIdentifier):
        (_, name, idx) = data.split("::")
        return cls(con.namespace, con.con_name, name, int(idx))

    @classmethod
    def from_str(cls, var_id: str):
        (ns, sc, vn, ix) = var_id.split("::")
        return cls(ns, sc, vn, int(ix))

    def __str__(self):
        return f"{self.namespace}::{self.scope}::{self.var_name}::{self.index}"

    def __print(self):
        var_str = f"{self.var_name}::{self.index}"
        return f"Var -- {var_str} ({self.namespace}.{self.scope})"


@dataclass(frozen=True)
class GenericDefinition(ABC):
    identifier: GenericIdentifier
    type: str

    @staticmethod
    def from_dict(data: dict):
        if "domain" in data:
            if "dimensions" in data["domain"]:
                type_str = "type"
                name_str = "list"
            else:
                name_str = data["domain"]["name"]
                type_str = data["domain"]["type"]
            return VariableDefinition(
                GenericIdentifier.from_str(data["name"]),
                type_str,
                data["domain"]["mutable"],
                name_str,
                data["domain_constraint"],
                tuple(data["source_refs"]),
            )
        else:
            return TypeDefinition(
                GenericIdentifier.from_str(data["name"]),
                data["type"],
                tuple(data["attributes"]),
            )


@dataclass(frozen=True)
class VariableDefinition(GenericDefinition):
    is_mutable: bool
    domain_name: str
    domain_constraint: str
    source_refs: tuple

    @classmethod
    def from_identifier(cls, id: VariableIdentifier):
        return cls(
            id,
            "type",
            False,
            "None",
            "(and (> v -infty) (< v infty))",
            tuple(),
        )


@dataclass(frozen=True)
class TypeFieldDefinition:
    name: str
    type: str


@dataclass(frozen=True)
class TypeDefinition(GenericDefinition):
    name: str
    metatype: str
    fields: List[TypeFieldDefinition]


@dataclass(frozen=True)
class ObjectDefinition(GenericDefinition):
    pass


class GenericContainer(ABC):
    def __init__(self, data: dict):
        self.identifier = GenericIdentifier.from_str(data["name"])
        self.arguments = [
            VariableIdentifier.from_str_and_con(var_str, self.identifier)
            for var_str in data["arguments"]
        ]
        self.updated = [
            VariableIdentifier.from_str_and_con(var_str, self.identifier)
            for var_str in data["updated"]
        ]
        self.returns = [
            VariableIdentifier.from_str_and_con(var_str, self.identifier)
            for var_str in data["return_value"]
        ]
        self.statements = [
            GenericStmt.create_statement(stmt, self) for stmt in data["body"]
        ]

        # NOTE: store base name as key and update index during wiring
        self.variables = dict()
        self.code_type = CodeType.UNKNOWN
        self.code_stats = {
            "num_calls": 0,
            "max_call_depth": 0,
            "num_math_assgs": 0,
            "num_data_changes": 0,
            "num_var_access": 0,
            "num_assgs": 0,
            "num_switches": 0,
            "num_loops": 0,
            "max_loop_depth": 0,
            "num_conditionals": 0,
            "max_conditional_depth": 0,
        }

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    def __str__(self):
        args_str = "\n".join([f"\t{arg}" for arg in self.arguments])
        outputs_str = "\n".join(
            [f"\t{var}" for var in self.returns + self.updated])
        return f"Inputs:\n{args_str}\nVariables:\n{outputs_str}"

    @staticmethod
    def from_dict(data: dict):
        if "type" not in data:
            con_type = "function"
        else:
            con_type = data["type"]
        if con_type == "function":
            return FuncContainer(data)
        elif con_type == "loop":
            return LoopContainer(data)
        elif con_type == "if-block":
            return CondContainer(data)
        elif con_type == "select-block":
            return CondContainer(data)
        else:
            raise ValueError(f"Unrecognized container type value: {con_type}")


class CondContainer(GenericContainer):
    def __init__(self, data: dict):
        super().__init__(data)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        base_str = super().__str__()
        return f"<COND Con> -- {self.identifier.con_name}\n{base_str}\n"


class FuncContainer(GenericContainer):
    def __init__(self, data: dict):
        super().__init__(data)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        base_str = super().__str__()
        return f"<FUNC Con> -- {self.identifier.con_name}\n{base_str}\n"


class LoopContainer(GenericContainer):
    def __init__(self, data: dict):
        super().__init__(data)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        base_str = super().__str__()
        return f"<LOOP Con> -- {self.identifier.con_name}\n{base_str}\n"


@unique
class VarType(Enum):
    BOOLEAN = auto()
    STRING = auto()
    INTEGER = auto()
    SHORT = auto()
    LONG = auto()
    FLOAT = auto()
    DOUBLE = auto()
    ARRAY = auto()
    STRUCT = auto()
    UNION = auto()
    OBJECT = auto()
    NONE = auto()

    def __str__(self):
        return str(self.name).lower()

    @classmethod
    def from_name(cls, name: str):
        name = name.lower()
        if name == "float":
            return cls.FLOAT
        elif name == "string":
            return cls.STRING
        elif name == "boolean":
            return cls.BOOLEAN
        elif name == "integer":
            return cls.INTEGER
        # TODO update for2py pipeline to use list instead
        elif name == "list" or name == "array":
            return cls.ARRAY
        elif name == "object":
            return cls.OBJECT
        elif name == "none":
            return cls.NONE
        else:
            raise ValueError(f"VarType unrecognized name: {name}")


@unique
class DataType(Enum):
    # NOTE: Refer to this stats data type blog post:
    # https://towardsdatascience.com/data-types-in-statistics-347e152e8bee
    NONE = auto()  # Used for undefined variable types
    CATEGORICAL = auto()  # Labels used to represent a quality
    BINARY = auto()  # Categorical measure with *only two* categories
    NOMINAL = auto()  # Categorical measure with *many* categories
    ORDINAL = auto()  # Categorical measure with many *ordered* categories
    NUMERICAL = auto()  # Numbers used to express a quantity
    DISCRETE = auto()  # Numerical measure with *countably infinite* options
    CONTINUOUS = auto()  # Numerical measure w/ *uncountably infinite* options
    INTERVAL = auto()  # Continuous measure *without* an absolute zero
    RATIO = auto()  # Continuous measure *with* an absolute zero

    def __str__(self):
        return str(self.name).lower()

    @classmethod
    def from_name(cls, name: str):
        name = name.lower()
        if name == "float":
            return cls.CONTINUOUS
        elif name == "string":
            return cls.NOMINAL
        elif name == "boolean":
            return cls.BINARY
        elif name == "integer":
            return cls.DISCRETE
        # TODO remove array after updating for2py to use list type
        elif name == "none" or name == "list" or name == "array":
            return cls.NONE
        else:
            raise ValueError(f"DataType unrecognized name: {name}")

    @classmethod
    def from_type_str(cls, type_str: str):
        type_str = type_str.lower()
        if type_str == "catgorical":
            return cls.CATEGORICAL
        elif type_str == "binary":
            return cls.BINARY
        elif type_str == "nominal":
            return cls.NOMINAL
        elif type_str == "ordinal":
            return cls.ORDINAL
        elif type_str == "numerical":
            return cls.NUMERICAL
        elif type_str == "discrete":
            return cls.DISCRETE
        elif type_str == "continuous":
            return cls.CONTINUOUS
        elif type_str == "interval":
            return cls.INTERVAL
        elif type_str == "ratio":
            return cls.RATIO
        elif type_str == "none":
            return cls.NONE
        else:
            raise ValueError(f"DataType unrecognized name: {type_str}")


@unique
class LambdaType(Enum):
    ASSIGN = auto()
    LITERAL = auto()
    CONDITION = auto()
    DECISION = auto()
    INTERFACE = auto()
    EXTRACT = auto()
    PACK = auto()
    OPERATOR = auto()

    def __str__(self):
        return str(self.name)

    def shortname(self):
        return self.__str__()[0]

    @classmethod
    def get_lambda_type(cls, type_str: str, num_inputs: int):
        if type_str == "assign":
            if num_inputs == 0:
                return cls.LITERAL
            return cls.ASSIGN
        elif type_str == "condition":
            return cls.CONDITION
        elif type_str == "decision":
            return cls.DECISION
        elif type_str == "interface":
            return cls.INTERFACE
        else:
            raise ValueError(f"Unrecognized lambda type name: {type_str}")

    @classmethod
    def from_str(cls, name: str):
        if name == "ASSIGN":
            return cls.ASSIGN
        elif name == "CONDITION":
            return cls.CONDITION
        elif name == "DECISION":
            return cls.DECISION
        elif name == "LITERAL":
            return cls.LITERAL
        elif name == "INTERFACE":
            return cls.INTERFACE
        elif name == "PACK":
            return cls.PACK
        elif name == "EXTRACT":
            return cls.EXTRACT
        elif name == "OPERATOR":
            return cls.OPERATOR
        elif name == "PASS":
            raise ValueError(
                f'Using container interface node name {name}. Please update to "INTERFACE" '
            )
        else:
            raise ValueError(f"Unrecognized lambda type name: {name}")


class GenericStmt(ABC):
    def __init__(self, stmt: dict, p: GenericContainer):
        self.container = p
        self.inputs = [
            VariableIdentifier.from_str_and_con(i, self.container.identifier)
            for i in stmt["input"]
        ]
        self.outputs = [
            VariableIdentifier.from_str_and_con(o, self.container.identifier)
            for o in (stmt["output"] + stmt["updated"])
        ]

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    def __str__(self):
        inputs_str = ", ".join(
            [f"{id.var_name} ({id.index})" for id in self.inputs])
        outputs_str = ", ".join(
            [f"{id.var_name} ({id.index})" for id in self.outputs])
        return f"Inputs: {inputs_str}\nOutputs: {outputs_str}"

    @staticmethod
    def create_statement(stmt_data: dict, container: GenericContainer):
        func_type = stmt_data["function"]["type"]
        if func_type == "lambda":
            return LambdaStmt(stmt_data, container)
        elif func_type == "container":
            return CallStmt(stmt_data, container)
        else:
            raise ValueError(f"Undefined statement type: {func_type}")

    # def correct_input_list(
    #     self, alt_inputs: Dict[VariableIdentifier, VariableNode]
    # ) -> List[VariableNode]:
    #     return [v if v.index != -1 else alt_inputs[v] for v in self.inputs]


class CallStmt(GenericStmt):
    def __init__(self, stmt: dict, con: GenericContainer):
        super().__init__(stmt, con)
        self.call_id = GenericIdentifier.from_str(stmt["function"]["name"])

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        generic_str = super().__str__()
        return f"<CallStmt>: {self.call_id}\n{generic_str}"


class LambdaStmt(GenericStmt):
    def __init__(self, stmt: dict, con: GenericContainer):
        super().__init__(stmt, con)
        # NOTE Want to use the form below eventually
        # type_str = stmt["function"]["lambda_type"]

        type_str = self.type_str_from_name(stmt["function"]["name"])

        # NOTE: we shouldn't need this since we will use UUIDs
        # self.lambda_node_name = f"{self.parent.name}::" + self.name
        self.type = LambdaType.get_lambda_type(type_str, len(self.inputs))
        self.func_str = stmt["function"]["code"]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        generic_str = super().__str__()
        return f"<LambdaStmt>: {self.type}\n{generic_str}"

    @staticmethod
    def type_str_from_name(name: str) -> str:
        if re.search(r"__assign__", name) is not None:
            return "assign"
        elif re.search(r"__condition__", name) is not None:
            return "condition"
        elif re.search(r"__decision__", name) is not None:
            return "decision"
        else:
            raise ValueError(
                f"No recognized lambda type found from name string: {name}"
            )


class GrFNExecutionException(Exception):
    pass
