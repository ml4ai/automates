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

Sequence = Union[range, List, numpy.ndarray, Tuple]
Iterable = Union[Set, Sequence, Dict]
Indexable = Union[Sequence, Dict, Record]
DimensionalIndex = Union[slice, int]
Hashable = Union[Tuple, str, int, bool]

