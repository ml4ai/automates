from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path
import json

from .identifiers import (
    BaseIdentifier,
    AIRIdentifier,
    VariableIdentifier,
    TypeIdentifier,
    ObjectIdentifier,
    ContainerIdentifier,
    LambdaStmtIdentifier,
    CallStmtIdentifier,
)
from automates.model_assembly.metadata import (
    TypedMetadata,
    GrFNCreation,
    CodeCollectionReference,
    CodeSpanReference,
)


@dataclass
class AutoMATES_IR:
    identifier: AIRIdentifier
    entrypoint: ContainerIdentifier
    containers: Dict[ContainerIdentifier, ContainerDef]
    variables: Dict[VariableIdentifier, VariableDef]
    type_definitions: Dict[TypeIdentifier, TypeDef]
    objects: Dict[ObjectIdentifier, ObjectDef]
    documentation: Dict[str, dict]
    metadata: List[TypedMetadata]

    def to_json(self, filepath: str):
        json_dict = {
            "entrypoint": self.entrypoint,
            "containers": self.containers,
            "variables": self.variables,
            "types": self.type_definitions,
            "objects": self.objects,
            "documentation": self.documentation,
            "metadata": self.metadata,
        }

        with open(filepath, "w") as f:
            json.dump(json_dict, f)

    @classmethod
    def from_air_json(cls, data: dict) -> AutoMATES_IR:
        C, V, O, D = dict(), dict(), dict(), dict()

        code_refs = CodeCollectionReference.from_sources(data["sources"])
        code_file_uid = code_refs.files[0].uid
        first_file_name = code_refs.files[0].name
        name_ending_idx = first_file_name.rfind(".")
        M = [
            GrFNCreation.from_name(first_file_name[:name_ending_idx]),
            code_refs,
        ]
        if "sources" in data:
            code_refs = CodeCollectionReference.from_sources(data["sources"])
            code_file_uid = code_refs.files[0].uid
            M.append(code_refs)

        T = dict()
        for type_data in data["types"]:
            type_data.update({"file_uid": code_file_uid})
            tdef = TypeDef.from_air_json(type_data)
            T[tdef.identifier] = tdef

        for var_dict in data["variables"]:
            var_def = VariableDef.from_air_json(var_dict)
            var_id = var_def.identifier
            V[var_id] = var_def

        for con_data in data["containers"]:
            con_data.update({"file_uid": code_file_uid})
            new_container = ContainerDef.from_air_json(con_data)
            C[new_container.identifier] = new_container

        filename = data["sources"][0]
        idt = AIRIdentifier.from_filename(filename)
        container_name = Path(filename).stem.lower()
        D.update(
            {
                (n if not n.startswith("$") else container_name + n): data
                for n, data in data["source_comments"].items()
            }
        )

        e = ContainerIdentifier.from_name_str(data["entrypoint"])

        return cls(idt, e, C, V, T, O, D, M)


# @dataclass(frozen=True)
# class SourceRef:
#     line_number: int
#     column_start: int
#     column_end: int
#     file_path: str

#     def __hash__(self):
#         return hash(astuple(self))

#     def __str__(self):
#         line_begin = self.line_number
#         col_begin = self.column_start
#         col_end = self.column_end
#         filepath = self.file_path
#         return f"({line_begin=}, {col_begin=}, {col_end=})\t({filepath=})"

#     @classmethod
#     def from_air_json(cls, data: dict) -> SourceRef:
#         return cls(**data)

#     def to_json_data(self) -> dict:
#         return asdict(self)


@dataclass(frozen=True)
class BaseDef(ABC):
    identifier: BaseIdentifier
    metadata: List[TypedMetadata]

    def __hash__(self):
        return hash(self.identifier)

    @abstractmethod
    def __str__(self):
        return f"{self.identifier}"

    @staticmethod
    def from_dict(data: dict):
        if "domain" in data:
            if "dimensions" in data["domain"]:
                type_str = "type"
                name_str = "list"
            else:
                name_str = data["domain"]["name"]
                type_str = data["domain"]["type"]
            return VariableDef(
                BaseIdentifier.from_str(data["name"]),
                type_str,
                data["domain"]["mutable"],
                name_str,
                data["domain_constraint"],
                list(data["source_refs"]),
            )
        else:
            return TypeDef.from_data(data)


@dataclass(frozen=True)
class VariableDef(BaseDef):
    domain_name: str
    domain_constraint: str

    def __str__(self):
        base_str = super().__str__()
        return f"(Variable Def)\n{base_str}\n"

    @classmethod
    def from_identifier(cls, var_id: VariableIdentifier):
        return cls(
            var_id,
            [],
            "None",
            "(and (> v -infty) (< v infty))",
        )

    @classmethod
    def from_air_json(cls, data: dict) -> VariableDef:
        var_id = VariableIdentifier.from_name_str(data["name"])
        file_ref = data["file_uid"] if "file_uid" in data else ""
        src_ref = data["source_refs"][0] if "source_refs" in data else ""
        code_span_data = {
            "source_ref": src_ref,
            "file_uid": file_ref,
            "code_type": "identifier",
        }
        metadata = [CodeSpanReference.from_air_json(code_span_data)]
        return cls(
            var_id,
            metadata,
            data["domain"]["name"],
            data["domain_constraint"],
        )


@dataclass(frozen=True)
class TypeFieldDef:
    name: str
    type: TypeIdentifier
    metadata: List[TypedMetadata]

    def __str__(self):
        return (
            f"(TypeField Def)\n{self.name}, {self.type}\n{self.source_ref}\n"
        )

    @classmethod
    def from_air_json(cls, data: dict, file_uid: str) -> TypeFieldDef:
        code_span_data = {
            "source_ref": data["source_ref"],
            "file_uid": file_uid,
            "code_type": "identifier",
        }
        return cls(
            data["name"],
            data["type"],
            [CodeSpanReference.from_air_json(code_span_data)],
        )

    @classmethod
    def from_data(cls, data: dict) -> TypeFieldDef:
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
class TypeDef(BaseDef):
    metatype: str
    fields: List[TypeFieldDef]

    def __str__(self):
        base_str = super().__str__()
        metatype = self.metatype
        num_fields = len(self.fields)
        return f"(Type Def)\n{metatype=}, {num_fields=}\n{base_str}\n"

    @classmethod
    def from_air_json(cls, data: dict) -> TypeDef:
        file_ref = data["file_uid"] if "file_uid" in data else ""
        src_ref = data["source_ref"] if "source_ref" in data else ""
        code_span_data = {
            "source_ref": src_ref,
            "file_uid": file_ref,
            "code_type": "block",
        }
        metadata = [CodeSpanReference.from_air_json(code_span_data)]
        return cls(
            TypeIdentifier.from_air_json(data),
            metadata,
            data["metatype"],
            [
                TypeFieldDef.from_air_json(d, data["file_uid"])
                for d in data["fields"]
            ],
        )

    @classmethod
    def from_data(cls, data: dict) -> TypeDef:
        metadata = [TypedMetadata.from_data(d) for d in data["metadata"]]
        return cls(
            "",
            "",
            data["name"],
            data["metatype"],
            [TypeFieldDef.from_data(d) for d in data["fields"]],
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
class FieldValue:
    name: str
    value: str


@dataclass(frozen=True)
class ObjectDef(BaseDef):
    type: TypeIdentifier
    field_values: List[FieldValue]

    def __str__(self):
        base_str = super().__str__()
        type_id = self.type
        num_values = len(self.field_values)
        return f"(Object Def)\n{type_id=}, {num_values=}\n{base_str}\n"


@dataclass(frozen=True)
class ContainerDef(BaseDef):
    arguments: List[VariableIdentifier]
    updated: List[VariableIdentifier]
    return_value: List[VariableIdentifier]
    variables: List[VariableDef]
    statements: List[StmtDef]

    @staticmethod
    def from_air_json(data: dict) -> ContainerDef:
        identifier = ContainerIdentifier.from_name_str(data["name"])
        file_reference = data["file_uid"] if "file_uid" in data else ""
        arguments = [
            VariableIdentifier.from_name_str(var_str)
            for var_str in data["arguments"]
        ]
        updated = [
            VariableIdentifier.from_name_str(var_str)
            for var_str in data["updated"]
        ]
        returns = [
            VariableIdentifier.from_name_str(var_str)
            for var_str in data["return_value"]
        ]
        statements = [
            StmtDef.from_air_json(
                {"file_uid": file_reference, "p_con_id": identifier, **stmt}
            )
            for stmt in data["body"]
        ]

        metadata = [
            CodeSpanReference.from_air_json(
                {
                    "source_ref": data["body_source_ref"]
                    if "body_source_ref" in data
                    else "",
                    "file_uid": file_reference,
                    "code_type": "block",
                }
            )
        ]

        variables = arguments + updated + returns
        for stmt in statements:
            variables.extend(stmt.inputs)
            variables.extend(stmt.outputs)
        variables = list(set(variables))

        if identifier.name.startswith("LOOP"):
            con_cls = LoopContainerDef
        else:
            con_cls = FuncContainerDef

        return con_cls(
            identifier,
            metadata,
            arguments,
            updated,
            returns,
            variables,
            statements,
        )

        # TODO: these should be moved to code role analysis
        # self.code_type = CodeType.UNKNOWN
        # code_stats = {
        #     "num_calls": 0,
        #     "max_call_depth": 0,
        #     "num_math_assgs": 0,
        #     "num_data_changes": 0,
        #     "num_var_access": 0,
        #     "num_assgs": 0,
        #     "num_switches": 0,
        #     "num_loops": 0,
        #     "max_loop_depth": 0,
        #     "num_conditionals": 0,
        #     "max_conditional_depth": 0,
        # }

    def __str__(self):
        base_str = super().__str__()
        num_args = len(self.arguments)
        num_updated = len(self.updated)
        num_returns = len(self.return_value)
        body_size = len(self.body)

        return (
            f"{num_args=}, {num_updated=}, {num_returns=}, {body_size=}",
            f"\n{base_str}\n",
        )

    # @abstractmethod
    # def __str__(self):
    #     args_str = "\n".join([f"\t{arg}" for arg in self.arguments])
    #     outputs_str = "\n".join(
    #         [f"\t{var}" for var in self.returns + self.updated]
    #     )
    #     return f"Inputs:\n{args_str}\nVariables:\n{outputs_str}"

    @staticmethod
    def from_dict(data: dict):
        if "type" not in data:
            con_type = "function"
        else:
            con_type = data["type"]
        if con_type == "function":
            return FuncContainerDef(data)
        elif con_type == "loop":
            return LoopContainerDef(data)
        elif con_type == "if-block":
            return CondContainerDef(data)
        elif con_type == "select-block":
            return CondContainerDef(data)
        else:
            raise ValueError(f"Unrecognized container type value: {con_type}")


@dataclass(frozen=True)
class CondContainerDef(ContainerDef):
    repeat: bool = False

    def __str__(self):
        base_str = super().__str__()
        return f"(COND Con Def)\n{base_str}\n"


@dataclass(frozen=True)
class FuncContainerDef(ContainerDef):
    repeat: bool = False

    def __str__(self):
        base_str = super().__str__()
        return f"(FUNC Con Def)\n{base_str}\n"


@dataclass(frozen=True)
class LoopContainerDef(ContainerDef):
    repeat: bool = True

    def __str__(self):
        base_str = super().__str__()
        return f"(Loop Con Def)\t{self.identifier.con_name}\n{base_str}\n"


@dataclass(frozen=True)
class StmtDef(BaseDef):
    container_id: ContainerIdentifier
    inputs: List[VariableIdentifier]
    outputs: List[VariableIdentifier]

    @staticmethod
    def from_air_json(data: dict) -> StmtDef:
        metadata = [
            CodeSpanReference.from_air_json(
                {
                    "source_ref": data.get("source_ref", ""),
                    "file_uid": data["file_uid"],
                    "code_type": "block",
                }
            )
        ]
        con_id = data["p_con_id"]
        inputs = [
            VariableIdentifier.from_name_str(iname) for iname in data["input"]
        ]
        outputs = [
            VariableIdentifier.from_name_str(oname)
            for oname in (data["output"] + data["updated"])
        ]
        func_data = data["function"]
        func_type = func_data["type"]

        if func_type == "lambda":
            identifier = LambdaStmtIdentifier.from_air_json(func_data)
            expression = func_data["code"]
            expr_type = LambdaStmtDef.get_type_str(func_data["name"])
            return LambdaStmtDef(
                identifier,
                metadata,
                con_id,
                inputs,
                outputs,
                expression,
                expr_type,
            )
        elif func_type == "container":
            identifier = CallStmtIdentifier.from_air_json(func_data)
            callee_id = ContainerIdentifier.from_name_str(func_data["name"])
            return CallStmtDef(
                identifier, metadata, con_id, inputs, outputs, callee_id
            )
        else:
            raise ValueError(f"Unrecognized statement type: {func_type}")

    def __str__(self):
        base_str = super().__str__()
        con_id = self.container_id
        num_inputs = len(self.inputs)
        num_outputs = len(self.outputs)
        return f"{con_id=}, {num_inputs=}, {num_outputs=}\n{base_str}"


@dataclass(frozen=True)
class CallStmtDef(StmtDef):
    callee_container_id: ContainerIdentifier
    # def __init__(self, stmt: dict, con: ContainerDef, file_ref: str):
    #     super().__init__(stmt, con)
    #     self.call_id = BaseIdentifier.from_str(stmt["function"]["name"])
    #     src_ref = stmt["source_ref"] if "source_ref" in stmt else ""
    #     code_span_data = {
    #         "source_ref": src_ref,
    #         "file_uid": file_ref,
    #         "code_type": "block",
    #     }
    #     self.metadata = [CodeSpanReference.from_air_json(code_span_data)]

    def __str__(self):
        base_str = super().__str__()
        return f"(Call Stmt Def)\n{base_str}\n"


@dataclass(frozen=True)
class LambdaStmtDef(StmtDef):
    expression: str
    expr_type: str

    # def __init__(self, stmt: dict, con: ContainerDef, file_ref: str):
    #     super().__init__(stmt, con)
    #     # NOTE Want to use the form below eventually
    #     # type_str = stmt["function"]["lambda_type"]

    #     type_str = self.type_str_from_name(stmt["function"]["name"])

    #     # NOTE: we shouldn't need this since we will use UUIDs
    #     # self.lambda_node_name = f"{self.parent.name}::" + self.name
    #     self.type = LambdaType.get_lambda_type(type_str, len(self.inputs))
    #     self.func_str = stmt["function"]["code"]
    #     src_ref = stmt["source_ref"] if "source_ref" in stmt else ""
    #     code_span_data = {
    #         "source_ref": src_ref,
    #         "file_uid": file_ref,
    #         "code_type": "block",
    #     }
    #     self.metadata = [CodeSpanReference.from_air_json(code_span_data)]

    def __str__(self):
        base_str = super().__str__()
        return f"(Lambda Stmt Def)\n{base_str}\n"

    @staticmethod
    def get_type_str(name: str) -> str:
        (_, _, type_str, _, _) = name.split("__")
        return type_str
        # if re.search(r"__assign__", name) is not None:
        #     return "assign"
        # elif re.search(r"__condition__", name) is not None:
        #     return "condition"
        # elif re.search(r"__decision__", name) is not None:
        #     return "decision"
        # elif re.search(r"__pack__", name) is not None:
        #     return "pack"
        # elif re.search(r"__extract__", name) is not None:
        #     return "extract"
        # else:
        #     raise ValueError(
        #         f"No recognized lambda type found from name string: {name}"
        #     )
