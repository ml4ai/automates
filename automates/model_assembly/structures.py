from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import re

from .code_types import CodeType
from .metadata import LambdaType, TypedMetadata, CodeSpanReference


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
        split = data.split("::")
        name = ""
        idx = -1
        if len(split) == 3:
            # Identifier is depricated <id type>::<name>::<version> style
            (_, name, idx) = split
            return cls(con.namespace, con.con_name, name, int(idx))
        elif len(split) == 5:
            # Identifier is <id type>::<module>::<scope>::<name>::<version>
            (_, ns, sc, name, idx) = split
            return cls(ns, sc, name, int(idx))
        else:
            raise ValueError(f"Unrecognized variable identifier: {data}")

    @classmethod
    def from_str(cls, var_id: str):
        split = var_id.split("::")
        # We introduced a change where we now append "::<uid>" onto variable
        # ids to create unique variable nodes for multiple calls to the same
        # function. We should probably only have the else case, but to be safe
        # for now, keep both around.
        if len(split) == 4:
            (ns, sc, vn, ix) = split
        else:
            (_, ns, sc, vn, ix) = split
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
                list(data["source_refs"]),
            )
        else:
            return TypeDefinition.from_data(data)


@dataclass(frozen=True)
class VariableDefinition(GenericDefinition):
    is_mutable: bool
    domain_name: str
    domain_constraint: str
    metadata: List[TypedMetadata]

    @classmethod
    def from_identifier(cls, id: VariableIdentifier):
        return cls(
            id,
            "type",
            False,
            "None",
            "(and (> v -infty) (< v infty))",
            [],
        )

    @classmethod
    def from_data(cls, data: dict) -> VariableDefinition:
        var_id = VariableIdentifier.from_str(data["name"])
        type_str = "type"
        file_ref = data["file_uid"] if "file_uid" in data else ""
        src_ref = data["source_refs"][0] if "source_refs" in data else ""
        code_span_data = {
            "source_ref": src_ref,
            "file_uid": file_ref,
            "code_type": "identifier",
        }
        code_span_metadata = [CodeSpanReference.from_air_data(code_span_data)]
        metadata = (
            []
            if "metadata" not in data
            else [TypedMetadata.from_data(mdict) for mdict in data["metadata"]]
            + code_span_metadata
        )
        return cls(
            var_id,
            type_str,
            data["domain"]["mutable"],
            data["domain"]["name"],
            data["domain_constraint"],
            metadata,
        )


@dataclass(frozen=True)
class TypeFieldDefinition:
    name: str
    type: str
    metadata: List[TypedMetadata]

    @classmethod
    def from_air_data(cls, data: dict, file_uid: str) -> TypeFieldDefinition:
        code_span_data = {
            "source_ref": data["source_ref"],
            "file_uid": file_uid,
            "code_type": "identifier",
        }
        return cls(
            data["name"],
            data["type"],
            [CodeSpanReference.from_air_data(code_span_data)],
        )

    @classmethod
    def from_data(cls, data: dict) -> TypeFieldDefinition:
        return cls(
            data["name"],
            data["type"],
            [TypedMetadata.from_data(d) for d in data["metadata"]]
            if "metadata" in data
            else [],
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "metadata": [d.to_dict() for d in self.metadata],
        }


@dataclass(frozen=True)
class TypeDefinition(GenericDefinition):
    name: str
    metatype: str
    fields: List[TypeFieldDefinition]
    metadata: List[TypedMetadata]

    @classmethod
    def from_air_data(cls, data: dict) -> TypeDefinition:
        file_ref = data["file_uid"] if "file_uid" in data else ""
        src_ref = data["source_ref"] if "source_ref" in data else ""
        code_span_data = {
            "source_ref": src_ref,
            "file_uid": file_ref,
            "code_type": "block",
        }
        metadata = [CodeSpanReference.from_air_data(code_span_data)]
        return cls(
            "",
            "",
            data["name"],
            data["metatype"],
            [
                TypeFieldDefinition.from_air_data(d, data["file_uid"])
                for d in data["fields"]
            ],
            metadata,
        )

    @classmethod
    def from_data(cls, data: dict) -> TypeDefinition:
        metadata = [TypedMetadata.from_data(d) for d in data["metadata"]]
        return cls(
            data["name"],
            "",
            data["name"],
            data["metatype"],
            [TypeFieldDefinition.from_data(d) for d in data["fields"]],
            metadata,
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "metatype": self.metatype,
            "fields": [fdef.to_dict() for fdef in self.fields],
            "metadata": [d.to_dict() for d in self.metadata],
        }


@dataclass(frozen=True)
class ObjectDefinition(GenericDefinition):
    pass


class GenericContainer(ABC):
    def __init__(self, data: dict):
        self.identifier = GenericIdentifier.from_str(data["name"])
        file_reference = data["file_uid"] if "file_uid" in data else ""
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
            GenericStmt.create_statement(stmt, self, file_reference)
            for stmt in data["body"]
        ]
        src_ref = data["body_source_ref"] if "body_source_ref" in data else ""
        file_ref = data["file_uid"] if "file_uid" in data else ""
        code_span_data = {
            "source_ref": src_ref,
            "file_uid": file_ref,
            "code_type": "block",
        }
        self.metadata = [CodeSpanReference.from_air_data(code_span_data)]

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
        outputs_str = "\n".join([f"\t{var}" for var in self.returns + self.updated])
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
        inputs_str = ", ".join([f"{id.var_name} ({id.index})" for id in self.inputs])
        outputs_str = ", ".join([f"{id.var_name} ({id.index})" for id in self.outputs])
        return f"Inputs: {inputs_str}\nOutputs: {outputs_str}"

    @staticmethod
    def create_statement(stmt_data: dict, container: GenericContainer, file_ref: str):
        func_type = stmt_data["function"]["type"]
        if func_type == "lambda":
            return LambdaStmt(stmt_data, container, file_ref)
        elif func_type == "container":
            return CallStmt(stmt_data, container, file_ref)
        elif func_type == "operator":
            return OperatorStmt(stmt_data, container, file_ref)
        else:
            raise ValueError(f"Undefined statement type: {func_type}")

    # def correct_input_list(
    #     self, alt_inputs: Dict[VariableIdentifier, VariableNode]
    # ) -> List[VariableNode]:
    #     return [v if v.index != -1 else alt_inputs[v] for v in self.inputs]


class CallStmt(GenericStmt):
    def __init__(self, stmt: dict, con: GenericContainer, file_ref: str):
        super().__init__(stmt, con)
        self.call_id = GenericIdentifier.from_str(stmt["function"]["name"])
        src_ref = stmt["source_ref"] if "source_ref" in stmt else ""
        code_span_data = {
            "source_ref": src_ref,
            "file_uid": file_ref,
            "code_type": "block",
        }
        self.metadata = [CodeSpanReference.from_air_data(code_span_data)]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        generic_str = super().__str__()
        return f"<CallStmt>: {self.call_id}\n{generic_str}"


class OperatorStmt(GenericStmt):
    def __init__(self, stmt: dict, con: GenericContainer):
        super().__init__(stmt, con)
        self.call_id = GenericIdentifier.from_str(stmt["function"]["name"])

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        generic_str = super().__str__()
        return f"<OperatorStmt>: {self.call_id}\n{generic_str}"


class LambdaStmt(GenericStmt):
    def __init__(self, stmt: dict, con: GenericContainer, file_ref: str):
        super().__init__(stmt, con)
        # NOTE Want to use the form below eventually
        # type_str = stmt["function"]["lambda_type"]

        type_str = self.type_str_from_name(stmt["function"]["name"])

        # NOTE: we shouldn't need this since we will use UUIDs
        # self.lambda_node_name = f"{self.parent.name}::" + self.name
        self.type = LambdaType.get_lambda_type(type_str, len(self.inputs))
        self.func_str = stmt["function"]["code"]
        src_ref = stmt["source_ref"] if "source_ref" in stmt else ""
        code_span_data = {
            "source_ref": src_ref,
            "file_uid": file_ref,
            "code_type": "block",
        }
        self.metadata = [CodeSpanReference.from_air_data(code_span_data)]

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
        elif re.search(r"__pack__", name) is not None:
            return "pack"
        elif re.search(r"__extract__", name) is not None:
            return "extract"
        else:
            raise ValueError(
                f"No recognized lambda type found from name string: {name}"
            )


class GrFNExecutionException(Exception):
    pass
