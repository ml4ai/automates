from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


LITERALS = dict()
ANON_VARS = dict()
OP_NAMES = dict()
CONTAINER_IDS = dict()


@dataclass(frozen=True)
class BaseIdentifier(ABC):
    namespace: str
    scope: str

    @staticmethod
    def from_str(data: str):
        # TODO: this is outdated and needs to be changed/removed
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

    @abstractmethod
    def __str__(self):
        return f"{self.namespace}::{self.scope}"


@dataclass(frozen=True)
class NamedIdentifier(BaseIdentifier):
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> NamedIdentifier:
        pass

    def __str__(self):
        return f"{super().__str__()}::{self.name}"

    @staticmethod
    def from_str(data: str):
        (_, ns, sc, nm) = data.split("::")
        return (ns, sc, nm)


@dataclass(frozen=True)
class IndexedIdentifier(NamedIdentifier):
    index: int

    @classmethod
    def from_dict(cls, data: dict) -> IndexedIdentifier:
        pass

    def __str__(self):
        return f"{super().__str__()}::{self.index}"

    @staticmethod
    def from_str(data: str):
        (_, ns, sc, nm, idx) = data.split("::")
        return (ns, sc, nm, int(idx))


@dataclass(frozen=True)
class AIRIdentifier(NamedIdentifier):
    def __str__(self):
        return f"AIR::{super().__str__()}"

    @classmethod
    def from_filename(cls, filename: str):
        return cls("@global", "@global", filename)

    @classmethod
    def from_str(cls, data: str):
        return cls(*(super().from_str(data)))


@dataclass(frozen=True)
class CAGIdentifier(NamedIdentifier):
    def __str__(self):
        return f"CAG::{super().__str__()}"

    @classmethod
    def from_GrFN_id(cls, grfn_id: GrFNIdentifier):
        return cls(grfn_id.namespace, grfn_id.scope, grfn_id.name)

    @classmethod
    def from_filename(cls, filename: str):
        return cls("", "", filename)

    @classmethod
    def from_str(cls, data: str):
        return cls(*(super().from_str(data)))


@dataclass(frozen=True)
class GrFNIdentifier(NamedIdentifier):
    def __str__(self):
        return f"GrFN::{super().__str__()}"

    @classmethod
    def from_air_id(cls, air_id: AIRIdentifier):
        return cls(air_id.namespace, air_id.scope, air_id.name)

    @classmethod
    def from_str(cls, data: str):
        return cls(*(super().from_str(data)))


@dataclass(frozen=True)
class GroMEtIdentifier(NamedIdentifier):
    def __str__(self):
        return f"GroMEt::{super().__str__()}"

    @classmethod
    def from_grfn_id(cls, grfn_id: GrFNIdentifier):
        return cls(grfn_id.namespace, grfn_id.scope, grfn_id.name)

    @classmethod
    def from_str(cls, data: str):
        return cls(*(super().from_str(data)))


@dataclass(frozen=True)
class ContainerIdentifier(NamedIdentifier):
    def __str__(self):
        return f"Container::{super().__str__()}"

    @classmethod
    def from_name_str(cls, name: str) -> ContainerIdentifier:
        (_, ns, sc, name) = name.split("::")
        return cls(ns, sc, name)

    @classmethod
    def from_str(cls, data: str):
        return cls(*(super().from_str(data)))


@dataclass(frozen=True)
class CAGContainerIdentifier(IndexedIdentifier):
    def __str__(self):
        return f"CAGContainer::{super().__str__()}"

    @classmethod
    def from_function_id(cls, func_id: FunctionIdentifier):
        return cls(
            func_id.namespace, func_id.scope, func_id.name, func_id.index
        )

    @classmethod
    def from_name_str(cls, name: str) -> ContainerIdentifier:
        (_, ns, sc, name, idx) = name.split("::")
        return cls(ns, sc, name, int(idx))


@dataclass(frozen=True)
class FunctionIdentifier(IndexedIdentifier):
    def __str__(self):
        return f"Function::{super().__str__()}"

    @classmethod
    def from_container_id(cls, con_id: ContainerIdentifier):
        global CONTAINER_IDS
        if con_id in CONTAINER_IDS:
            CONTAINER_IDS[con_id] += 1
        else:
            CONTAINER_IDS[con_id] = 0

        new_idx = CONTAINER_IDS[con_id]
        return cls(con_id.namespace, con_id.scope, con_id.name, new_idx)

    @classmethod
    def from_lambda_stmt_id(cls, stmt_id: LambdaStmtIdentifier):
        return cls(
            stmt_id.namespace, stmt_id.scope, stmt_id.name, stmt_id.index
        )

    @classmethod
    def from_literal_def(cls, ns: str, sc: str) -> FunctionIdentifier:
        global LITERALS
        ns_sc = (ns, sc)
        if ns_sc in LITERALS:
            LITERALS[ns_sc] += 1
        else:
            LITERALS[ns_sc] = 0

        new_idx = LITERALS[ns_sc]
        return cls(ns, sc, "@literal", new_idx)

    @classmethod
    def from_operator_func(cls, ns: str, sc: str, operation: str):
        global OP_NAMES
        nso = (ns, sc, operation)
        if nso in OP_NAMES:
            OP_NAMES[nso] += 1
        else:
            OP_NAMES[nso] = 0

        new_idx = OP_NAMES[nso]
        return cls(ns, sc, operation, new_idx)

    @classmethod
    def from_str(cls, data: str):
        return cls(*(super().from_str(data)))


@dataclass(frozen=True)
class TypeIdentifier(NamedIdentifier):
    def __str__(self):
        return f"Type::{super().__str__()}"

    @classmethod
    def from_air_json(cls, data: dict):
        ns = data["namespace"] if "namespace" in data else "@global"
        sc = data["scope"] if "scope" in data else "@global"
        return cls(ns, sc, data["name"])

    @classmethod
    def from_str(cls, data: str):
        return cls(*(super().from_str(data)))


@dataclass(frozen=True)
class ObjectIdentifier(NamedIdentifier):
    def __str__(self):
        return f"Object::{super().__str__()}"

    @classmethod
    def from_air_json(cls, data: dict):
        ns = data["namespace"] if "namespace" in data else "@global"
        sc = data["scope"] if "scope" in data else "@global"
        return cls(ns, sc, data["name"])

    @classmethod
    def from_str(cls, data: str):
        return cls(*(super().from_str(data)))


@dataclass(frozen=True)
class StmtIdentifier(NamedIdentifier):
    def __str__(self):
        return f"Stmt::{super().__str__()}"

    @classmethod
    def from_str(cls, data: str):
        return cls(*(super().from_str(data)))


@dataclass(frozen=True)
class CallStmtIdentifier(NamedIdentifier):
    def __str__(self):
        return f"CallStmt::{super().__str__()}"

    @classmethod
    def from_air_json(cls, data: dict) -> CallStmtIdentifier:
        (_, ns, sc, con_name) = data["name"].split("::")
        return cls(ns, sc, con_name)

    @classmethod
    def from_str(cls, data: str):
        return cls(*(super().from_str(data)))


@dataclass(frozen=True)
class LambdaStmtIdentifier(IndexedIdentifier):
    def __str__(self):
        return f"LambdaStmt::{super().__str__()}"

    @classmethod
    def from_air_json(cls, data: dict) -> LambdaStmtIdentifier:
        (ns, sc, exp_type, name, idx) = data["name"].split("__")
        return cls(ns, sc, f"{exp_type}.{name}", int(idx))

    @classmethod
    def from_str(cls, data: str):
        return cls(*(super().from_str(data)))


@dataclass(frozen=True)
class VariableIdentifier(IndexedIdentifier):
    def __str__(self):
        return f"Variable::{super().__str__()}"

    @classmethod
    def from_anonymous(cls, namespace: str, scope: str):
        global ANON_VARS
        ns_sc = (namespace, scope)
        if ns_sc in ANON_VARS:
            ANON_VARS[ns_sc] += 1
        else:
            ANON_VARS[ns_sc] = 0

        new_idx = ANON_VARS[ns_sc]
        return cls(namespace, scope, "@anonymous", new_idx)

    @classmethod
    def from_str_and_con(cls, data: str, con: ContainerIdentifier):
        split = data.split("::")
        name = ""
        idx = -1
        if len(split) == 3:
            # Identifier is deprecated <var_id type>::<name>::<version> style
            (_, name, idx) = split
            return cls(con.namespace, con.con_name, name, int(idx))
        elif len(split) == 5:
            # Identifier is <var_id type>::<module>::<scope>::<name>::<version>
            (_, ns, sc, name, idx) = split
            return cls(ns, sc, name, int(idx))
        else:
            raise ValueError(f"Unrecognized variable identifier: {data}")

    @classmethod
    def from_name_str(cls, name: str):
        elements = name.split("::")
        if len(elements) == 4:
            (ns, sc, vn, ix) = elements
        elif len(elements) == 5:
            (_, ns, sc, vn, ix) = elements
        else:
            raise ValueError(
                f"Unrecognized variable identifier formation for: {name}"
            )
        return cls(ns, sc, vn, int(ix))

    @classmethod
    def from_air_json(cls, data: dict):
        return cls.from_name_str(data["name"])

    @classmethod
    def from_str(cls, data: str):
        return cls(*(super().from_str(data)))
