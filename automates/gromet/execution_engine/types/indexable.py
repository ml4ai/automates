import numpy
from typing import Union, Dict, Any, Tuple, List

from automates.gromet.execution_engine.types.defined_types import Field, Sequence, Indexable, Record, RecordField



class Indexable_get(object):
    source_language_name = {"CAST":"_get"}
    inputs = [Field("indexable_input", "Indexable"), Field("index", "Any")]
    outputs =  [Field("element", "Any")]
    shorthand = "_get"
    documentation = ""

    def exec(indexable_input: Indexable, index: Any) -> Any:
        if isinstance(indexable_input, Record):
            return Indexable_get.Record_get(indexable_input, index)
        else:
            return indexable_input[index]
    
    def Record_get(record_input: Record, field_name: str) -> RecordField:
        for field in record_input.fields:
            if field.name == field_name:
                return field

class Indexable_set(object):
    source_language_name = {"CAST":"_set"}
    inputs = [Field("indexable_input", "Indexable"), Field("index", "Any"), Field("value", "Any")]
    outputs =  [Field("indexable_output", "Indexable")]
    shorthand = "_set"
    documentation = ""

    def exec(indexable_input: Indexable, index: Any, value: Any) -> Indexable:
        if isinstance(indexable_input, Sequence):
            return Indexable_set.Sequence_set(indexable_input, index, value)
        elif isinstance(indexable_input, Dict):
            return Indexable_set.Map_set(indexable_input, index, value)
        elif isinstance(indexable_input, Record):
            return Indexable_set.Record_set(indexable_input, index, value)
        
    def Sequence_set(sequence_input: Sequence, index: int, value: Any) -> Any:
        if isinstance(sequence_input, range):
            #TODO: You cannot assign to a range object
            pass
        elif isinstance(sequence_input, List):
            return Indexable_set.List_set(sequence_input, index, value)
        elif isinstance(sequence_input, numpy.ndarray):
            return Indexable_set.Array_set(sequence_input, index, value)
        elif isinstance(sequence_input, Tuple):
            return Indexable_set.Tuple_set(sequence_input, index, value)
    def List_set(list_input: List, index: int, value: Any) -> List:
        list_input[index] = value
        return list_input
    def Array_set(array_input: numpy.ndarray, index: int, value: Any) -> numpy.ndarray:
        array_input[index] = value
        return array_input
    def Tuple_set(tuple_input: Tuple, index: int, value: Any) -> Tuple:
        converted_tuple = list(tuple_input)
        converted_tuple[index] = value
        return tuple(converted_tuple)
    def Map_set(map_input: Dict, index: Any, value: Any) -> Dict:
        map_input[index] = value
        return map_input
    def Record_set(record_input: Record, field_name: str, value: Any) -> Record: #TODO: Double check this implementation, how to copy Record type
        for field in record_input.fields:
            if field.name == field_name:
                field.value = value # TODO: Do we need type checking here?
        return record_input