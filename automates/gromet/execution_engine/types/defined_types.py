import numpy
from typing import Union, List, Tuple, Dict, Set, Any
from dataclasses import dataclass

@dataclass(frozen=True)
class Field:
    name: str
    type: str
    variatic: bool = False
    default_val: Any = None

@dataclass
class RecordField:
    name: str
    value_type: type
    value: Any

@dataclass
class Record(object):
    name: str
    fields: "list[RecordField]"

Sequence = Union[range, List, numpy.ndarray, Tuple]
Iterable = Union[Set, Sequence, Dict]
Indexable = Union[Sequence, Dict, Record]


