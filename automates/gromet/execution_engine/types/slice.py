from typing import Tuple, List
from defined_types import Slice, ExtendedSlice

def slice(lower: int, upper: int, step: int) -> Tuple:
    return Slice(lower, upper, step)

def ext_slice(dims: List[Tuple, int]) -> List[Tuple, int]:
    return ExtendedSlice(dims)