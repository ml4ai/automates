from __future__ import annotations
from pathlib import Path
import json

from .metadata import GrFNCreation, CodeCollectionReference
from .structures import (
    GenericDefinition,
    VariableDefinition,
    GenericContainer,
    GenericIdentifier,
    TypeDefinition,
)


class AutoMATES_IR:
    def __init__(self, e, C, V, T, O, D, M):
        self.entrypoint = e
        self.containers = C
        self.variables = V
        self.type_definitions = T
        self.objects = O
        self.documentation = D
        self.metadata = M

    def to_json(self):
        json_dict = {
            "entrypoint": self.entrypoint,
            "containers": self.containers,
            "variables": self.variables,
            "types": self.type_definitions,
            "objects": self.objects,
            "documentation": self.documentation,
            "metadata": self.metadata,
        }

        with open("test.json", "w") as f:
            json.dump(json_dict, f)

    @classmethod
    def from_json(cls, filepath: str) -> AutoMATES_IR:
        data = json.load(open(filepath, "r"))

        C, V, O, D = dict(), dict(), dict(), dict()

        M = [
            GrFNCreation.from_name(filepath.replace("--AIR.json", "")),
        ]
        if "sources" in data:
            code_refs = CodeCollectionReference.from_sources(data["sources"])
            code_file_uid = code_refs.files[0].uid
            M.append(code_refs)

        for var_data in data["variables"]:
            # new_var = GenericDefinition.from_dict(var_data)
            var_data.update({"file_uid": code_file_uid})
            new_var = VariableDefinition.from_data(var_data)
            V[new_var.identifier] = new_var

        T = list()
        for type_data in data["types"]:
            type_data.update({"file_uid": code_file_uid})
            T.append(TypeDefinition.from_air_data(type_data))

        for con_data in data["containers"]:
            con_data.update({"file_uid": code_file_uid})
            new_container = GenericContainer.from_dict(con_data)
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
