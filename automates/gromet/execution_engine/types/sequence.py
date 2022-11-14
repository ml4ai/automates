import numpy
from typing import Union, List, Tuple, Any
import itertools

from automates.gromet.execution_engine.types.defined_types import Field, Sequence

#TODO: Check the correctness for numpy arrays - How do n>1d arrays work in this case
class Sequence_concatenate(object):
    source_language_name = {"CAST":"concatenate"}
    inputs = [Field("sequence_inputs", "Sequence", True)]
    outputs = [Field("sequence_output", "Sequence")]
    shorthand = ""
    documentation = ""

    def exec(*sequence_inputs : Sequence) -> Sequence:
        # TODO: How do we handle type checking, whose responsibility should it be?
        assert type(sequence_inputs[0] != range) # Range type doesn't support concatenation 
        assert all(isinstance(sequence, type(sequence_inputs[0])) for sequence in sequence_inputs) # Cannot concatenate sequences of different types

        if isinstance(sequence_inputs[0], numpy.ndarray):
            Sequence_concatenate.Array_concatenate(sequence_inputs)
        else:
            return type(sequence_inputs[0])(itertools.chain.from_iterable(sequence_inputs))

    def Array_concatenate(array_inputs: Tuple[numpy.ndarray, ...]) -> numpy.ndarray:
        return numpy.concatenate(array_inputs)

        

class Sequence_replicate(object):
    source_language_name = {"CAST":"replicate"}
    inputs = [Field("sequence_input", "Sequence"), Field("count", "Integer") ]
    outputs = [Field("sequence_output", "Sequence")]
    shorthand = ""
    documentation = ""

    def exec(sequence_input: Sequence, count: int) -> Sequence:
        assert type(sequence_input != range)
        if isinstance(sequence_input, numpy.ndarray):
            return Sequence_replicate.Array_replicate(sequence_input, count)
        else:
            return sequence_input*count
    
    def Array_replicate(array_input: numpy.ndarray, count: int) -> numpy.ndarray:
        return numpy.tile(array_input, count)

   
class Sequence_length(object):
    source_language_name = {"CAST": "length"}
    inputs = [Field("sequence_input", "Sequence")]
    outputs = [Field("length", "Integer")]
    shorthand = ""
    documentation = ""

    def exec(sequence_input: Sequence) -> int:
        return len(sequence_input)

class Sequence_min(object):
    source_language_name = {"CAST": "min"}
    inputs = [Field("sequence_input", "Sequence")]
    outputs = [Field("minimum", "Any")]
    shorthand = ""
    documentation = ""

    def exec(sequence_input: Sequence) -> Any:
        return min(list(sequence_input))

class Sequence_max(object):
    source_language_name = {"CAST": "max"}
    inputs = [Field("sequence_input", "Sequence")]
    outputs = [Field("maximum", "Any")]
    shorthand = ""
    documentation = ""

    def exec(sequence_input: Sequence) -> Any:
        return max(list(sequence_input))

class Sequence_count(object):
    source_language_name = {"CAST": "count"}
    inputs = [Field("sequence_input", "Sequence"), Field("element", "Any")]
    outputs = [Field("count", "Integer")]
    shorthand = ""
    documentation = ""

    def exec(sequence_input: Sequence, element: Any) -> Any:
        return list(sequence_input).count(element)

class Sequence_index(object):
    source_language_name = {"CAST": "index"}
    inputs = [Field("list_input", "List"), Field("element", "Any")]
    outputs = [Field("index", "Integer")]
    shorthand = ""
    documentation = ""

    def exec(list_input: List, element: Any) -> Any:
        return list(list_input).index(element)
