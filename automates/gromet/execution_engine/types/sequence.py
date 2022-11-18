import numpy
from typing import Union, List, Tuple, Any
import itertools

from automates.gromet.execution_engine.types.defined_types import Field, Sequence

class Sequence_concatenate(object): #TODO: Check implementation of *args
    source_language_name = {}
    inputs = [Field("sequence_inputs", "Sequence", True)]
    outputs = [Field("sequence_output", "Sequence")]
    shorthand = ""
    documentation = ""

    def exec(*sequence_inputs : Sequence) -> Sequence:
        if isinstance(list(sequence_inputs)[0], numpy.ndarray):
            return Sequence_concatenate.Array_concatenate()
        elif isinstance(list(sequence_inputs)[0], List):
            return Sequence_concatenate.List_concatenate()
        elif isinstance(list(sequence_inputs)[0], Tuple):
            return Sequence_concatenate.Tuple_concatenate()
        else:
            # Range does not support concatenate, so this is a placeholde
            pass

    def List_concatenate(*list_inputs: List) -> List:
        return sum(list_inputs, [])
    def Array_concatenate(*array_inputs: numpy.ndarray) -> numpy.ndarray:
        return numpy.concatenate(array_inputs)
    def Tuple_concatenate(*tuple_inputs: Tuple) -> Tuple:
        return sum(tuple_inputs, ())
        

class Sequence_replicate(object):
    source_language_name = {}
    inputs = [Field("sequence_input", "Sequence"), Field("count", "Integer") ]
    outputs = [Field("sequence_output", "Sequence")]
    shorthand = ""
    documentation = ""

    def exec(sequence_input: Sequence, count: int) -> Sequence:
        if isinstance(sequence_input, List):
            return Sequence_replicate.List_replicate(sequence_input, count)
        elif isinstance(sequence_input, numpy.ndarray):
            return Sequence_replicate.Array_replicate(sequence_input, count)
    
    def Array_replicate(array_input: numpy.ndarray, count: int) -> numpy.ndarray:
        return numpy.tile(array_input, count)



class List_replicate(object):
    source_language_name = {}
    inputs = [Field("list_input", "List"), Field("count", "Integer") ]
    outputs = [Field("list_output", "List")]
    shorthand = ""
    documentation = ""

    def exec(list_input: List, count: int) -> List:
        return [list_input]*count
   
class List_length(object):
    source_language_name = {}
    inputs = [Field("list_input", "List")]
    outputs = [Field("length", "Integer")]
    shorthand = ""
    documentation = ""

    def exec(list_input: List) -> int:
        return len(list_input)

class List_min(object):
    source_language_name = {}
    inputs = [Field("list_input", "List")]
    outputs = [Field("minimum", "Any")]
    shorthand = ""
    documentation = ""

    def exec(list_input: List) -> Any:
        return min(list_input)

class List_max(object):
    source_language_name = {}
    inputs = [Field("list_input", "List")]
    outputs = [Field("maximum", "Any")]
    shorthand = ""
    documentation = ""

    def exec(list_input: List) -> Any:
        return max(list_input)

class List_count(object):
    source_language_name = {}
    inputs = [Field("list_input", "List"), Field("element", "Any")]
    outputs = [Field("count", "Integer")]
    shorthand = ""
    documentation = ""

    def exec(list_input: List, element: Any) -> Any:
        return list_input.count(element)

class List_index(object):
    source_language_name = {}
    inputs = [Field("list_input", "List"), Field("element", "Any")]
    outputs = [Field("index", "Integer")]
    shorthand = ""
    documentation = ""

    def exec(list_input: List, element: Any) -> Any:
        return list_input.index(element)
