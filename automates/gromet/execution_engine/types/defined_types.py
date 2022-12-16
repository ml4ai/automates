import numpy
from typing import Union, List, Tuple, Dict, Set, Any
from dataclasses import dataclass

@dataclass
class RecordField:
    name: str
    value_type: type
    value: Any

@dataclass
class Record(object):
    name: str
    fields: "list[RecordField]"

@dataclass
class Slice(object):
    lower: int
    upper: int
    step: int
@dataclass
class ExtendedSlice(object):
    dims: List[Slice, int]


Sequence = Union[range, List, numpy.ndarray, Tuple]
Iterable = Union[Set, Sequence, Dict]
Indexable = Union[Sequence, Dict, Record]
DimensionalIndex = Union[Slice, ExtendedSlice]

