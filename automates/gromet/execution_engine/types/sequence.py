import numpy
from typing import Union, List, Tuple, Any
import itertools

from automates.gromet.execution_engine.types.defined_types import Sequence, DimensionalIndex, Slice, ExtendedSlice

#TODO: Check the correctness for numpy arrays - How do n>1d arrays work in this case
def Sequence_get(sequence_input: Sequence, index: DimensionalIndex) -> Any: # Returns sequence if index=slice and Any otherwise
    return sequence_input[index] # Works for both int and slice

def Sequence_set(sequence_input: Sequence, index: DimensionalIndex, element: Any) -> Sequence:
    sequence_input[index] = element
    return sequence_input
    
def Sequence_concatenate(*sequence_inputs : Sequence) -> Sequence:
    # TODO: How do we handle type checking, whose responsibility should it be?
    assert type(sequence_inputs[0] != range) # Range type doesn't support concatenation 
    assert all(isinstance(sequence, type(sequence_inputs[0])) for sequence in sequence_inputs) # Cannot concatenate sequences of different types

    if isinstance(sequence_inputs[0], numpy.ndarray):
        return numpy.concatenate(sequence_inputs)
    else:
        return type(sequence_inputs[0])(itertools.chain.from_iterable(sequence_inputs))

def Sequence_replicate(sequence_input: Sequence, count: int) -> Sequence:
    assert type(sequence_input != range)
    if isinstance(sequence_input, numpy.ndarray):
        return numpy.tile(sequence_input, count)
    else:
        return sequence_input*count
    
def Sequence_length(sequence_input: Sequence) -> int:
    return len(sequence_input)

def Sequence_min(sequence_input: Sequence) -> Any:
    return min(list(sequence_input))

def Sequence_max(sequence_input: Sequence) -> Any:
    return max(list(sequence_input))

def Sequence_count(sequence_input: Sequence, element: Any) -> Any:
    return list(sequence_input).count(element)

def Sequence_index(list_input: List, element: Any) -> Any:
    return list(list_input).index(element)

