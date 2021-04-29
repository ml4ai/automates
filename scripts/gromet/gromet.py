import json
from typing import List
from dataclasses import dataclass


# class Serializable:
#     def toJson(self):
#         return json.dumps(self, default=lambda o: o.__dict__)


@dataclass
class Type(dict):
    name: str


@dataclass
class Variable(dict):
    name: str


@dataclass
class Box(dict):
    name: str


@dataclass
class Gromet(dict):
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
    json.dump(example().__dict__, open("example.json", "w"))

