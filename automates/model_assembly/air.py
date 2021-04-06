from __future__ import annotations
from pathlib import Path
import json

from .metadata import GrFNCreation, CodeCollectionReference
from .structures import (
    GenericDefinition,
    VariableDefinition,
    GenericContainer,
    GenericIdentifier,
)


class AutoMATES_IR:
    def __init__(self, e, C, V, T, O, D, M):
        self.entrypoint = e
        self.containers = C
        self.variables = V
        self.types = T
        self.objects = O
        self.documentation = D
        self.metadata = M

    @classmethod
    def from_json(cls, filepath: str) -> AutoMATES_IR:
        data = json.load(open(filepath, "r"))

        C, V, T, O, D = dict(), dict(), dict(), dict(), dict()

        code_refs = CodeCollectionReference.from_sources(data["sources"])
        code_file_uid = code_refs.files[0].uid
        M = [
            GrFNCreation.from_name(filepath.replace("--AIR.json", "")),
            code_refs,
        ]

        for var_data in data["variables"]:
            # new_var = GenericDefinition.from_dict(var_data)
            var_data.update({"file_uid": code_file_uid})
            new_var = VariableDefinition.from_data(var_data)
            V[new_var.identifier] = new_var

        for type_data in data["types"]:
            new_type = GenericDefinition.from_dict(type_data)
            T[new_type.identifier] = new_type

        for con_data in data["containers"]:
            con_data.update({"file_uid": code_file_uid})
            new_container = GenericContainer.from_dict(con_data)
            # for in_var in new_container.arguments:
            #     if in_var not in V:
            #         V[in_var] = VariableDefinition.from_identifier(in_var)
            C[new_container.identifier] = new_container

        # TODO Paul - is it fine to switch from keying by filename to keying by
        # container name? Also, lowercasing? - Adarsh
        filename = data["sources"][0]
        container_name = Path(filename).stem.lower()
        D.update(
            {
                n if not n.startswith("$") else container_name + n: data
                for n, data in data["source_comments"].items()
            }
        )

        e = GenericIdentifier.from_str(data["entrypoint"])

        return cls(e, C, V, T, O, D, M)