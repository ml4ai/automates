import json
from typing import List
from dataclasses import dataclass
from dataclasses_json import dataclass_json


# class Serializable:
#     def toJson(self):
#         return json.dumps(self, default=lambda o: o.__dict__)


@dataclass_json
@dataclass
class Type:
    name: str


@dataclass_json
@dataclass
class Variable:
    name: str


@dataclass_json
@dataclass
class Box:
    name: str


@dataclass_json
@dataclass
class Gromet:
    root: Box
    types: List[Type]
    variables: List[Variable]


def example():
    g = Gromet(
        root=Box(name="my_Function"),
        types=[Type(name="type1"), Type(name="type2")],
        variables=[Variable(name="var1"), Variable(name="var2")]
    )
    return g


if __name__ == "__main__":
    json.dump(example().to_json(), open("example.json", "w"))

