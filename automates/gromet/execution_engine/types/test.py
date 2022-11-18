import numpy
from typing import Union, List, Tuple, Any
import itertools

from defined_types import Field, Sequence


class Sequence_concatenate(object): #TODO: Check implementation of *args
    source_language_name = {}
    inputs = [Field("sequence_inputs", "Sequence", True)]
    outputs = [Field("sequence_output", "Sequence")]
    shorthand = ""
    documentation = ""

    def exec(*sequence_inputs : Sequence) -> Sequence:
        if isinstance(list(sequence_inputs)[0], numpy.ndarray):
            return Sequence_concatenate.Array_concatenate(sequence_inputs)
        elif isinstance(sequence_inputs[0], List):
            return Sequence_concatenate.List_concatenate(sequence_inputs)
        elif isinstance(sequence_inputs[0], Tuple):
            return Sequence_concatenate.Tuple_concatenate(sequence_inputs)
        else:
            # Range does not support concatenate, so this is a placeholde
            pass

    def List_concatenate(*list_inputs: List) -> List:
        return sum(list_inputs, [])
    def Array_concatenate(*array_inputs: numpy.ndarray) -> numpy.ndarray:
        return numpy.concatenate(array_inputs)
    def Tuple_concatenate(*tuple_inputs: Tuple) -> Tuple:
        return sum(tuple_inputs, ())

a = [1,2,3]
b = [2,3,4]
print(Sequence_concatenate.exec(a,b))