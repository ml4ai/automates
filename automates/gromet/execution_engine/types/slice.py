from typing import Tuple, List
from defined_types import Slice, ExtendedSlice

def slice(lower: int, upper: int, step: int) -> slice:
    return slice(lower, upper, step)

def ext_slice(dims: List[Tuple, int]) -> slice:
    pass #TODO