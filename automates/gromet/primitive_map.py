from typing import Iterator, Union, Tuple, Dict, List, Set, Any
from dataclasses import dataclass
import numpy

import sys
import inspect


@dataclass(frozen=True) 
class Field:
    name: str
    type: str
    variatic: bool = False

@dataclass
class RecordField:
    name: str
    value_type: type
    value: Any

@dataclass
class Record(object):
    name: str
    fields: "list[RecordField]"

class UAdd(object):
    source_language_name = {"Python": "UAdd", "CAST": "UAdd"}
    inputs = [Field("operand", "Number")]
    outputs =  [Field("result", "Number")]
    shorthand = "u+"
    documentation = ""
    
    def exec(operand: Union[int, float, complex]) -> Union[int, float, complex]:
        return +operand

class USub(object):
    source_language_name = {"Python": "USub", "CAST": "USub"}
    inputs = [Field("operand", "Number")]
    outputs =  [Field("result", "Number")]
    shorthand = "u-"
    documentation = ""
    
    def exec(operand: Union[int, float, complex]) -> Union[int, float, complex]:
        return -operand

class Not(object):
    source_language_name = {"Python": "Not", "CAST": "Not"}
    inputs = [Field("operand", "Boolean")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "not"
    documentation = ""
    
    def exec(operand: bool) -> bool:
        return not operand

class Invert(object):
    source_language_name = {"Python": "Invert", "CAST": "Invert"}
    inputs = [Field("operand", "Number")]
    outputs =  [Field("result", "Number")]
    shorthand = "~"
    documentation = ""
    
    def exec(operand: Union[int, float, complex]) -> Union[int, float, complex]:
        return ~operand

class Add(object):
    source_language_name = {"Python":"Add", "GCC":"plus_expr", "CAST": "Add"}
    inputs = [Field("augend", "Number"), Field("addend", "Number")]
    outputs =  [Field("sum", "Number")]
    shorthand = "+"
    documentation = "Add is the numerical addition operator. For a general addition operation (For example, the case of concatanation with +) see GenAdd."
    
    @staticmethod # TODO: Look into if this is required. Only need @staticmethod if you intend to call the method from an instance of class
    def exec(augend: Union[int, float, complex], addend: Union[int, float, complex] ) -> Union[int, float, complex]:
        return augend + addend

class GenAdd(object):
    source_language_name = {"Python":"Add"} 
    inputs = [Field("operand1", "Any"), Field("operand2", "Any")]
    outputs =  [Field("result", "Any")]
    shorthand = "g+"
    documentation = ""
    
    def exec(operand1: Any, operand2: Any) -> Any:
        return operand1 + operand2

class Sub(object):
    source_language_name = {"Python":"Sub", "GCC":"minus_expr", "CAST": "Sub"}
    inputs = [Field("minuend", "Number"), Field("subtrahend", "Number")]
    outputs =  [Field("difference", "Number")]
    shorthand = "-"
    documentation = "Sub is the numerical subtraction operator. For a general subtraction operation () see GenSub."
    
    def exec(minuend: Union[int, float, complex], subtahend: Union[int, float, complex] ) -> Union[int, float, complex]:
        return minuend - subtahend

class GenSub(object):
    source_language_name = {"Python":"Sub"} 
    inputs = [Field("operand1", "Any"), Field("operand2", "Any")]
    outputs =  [Field("result", "Any")]
    shorthand = "g-"
    documentation = ""
    
    def exec(operand1: Any, operand2: Any) -> Any:
        return operand1 - operand2

class Mult(object):
    source_language_name = {"Python":"Mult", "GCC":"mult_expr", "CAST": "Mult"}
    inputs = [Field("multiplier", "Number"), Field("multiplicand", "Number")]
    outputs =  [Field("product", "Number")] 
    shorthand = "*"
    documentation = ""

    def exec(multiplier: Union[int, float, complex], multiplicand: Union[int, float, complex]) -> Union[int, float, complex]:
        return multiplier * multiplicand

# TODO: Do we need a general operator for all overloadable operators in Python (https://www.programiz.com/python-programming/operator-overloading)? 

class Div(object):
    source_language_name = {"Python":"Div", "GCC":"rdiv_expr", "CAST": "Div"}
    inputs = [Field("dividend", "Number"), Field("divisor", "Number")]
    outputs =  [Field("quotient", "Number")]
    shorthand = "/"
    documentation = ""

    def exec(dividend: Union[int, float, complex], divisor: Union[int, float, complex]) -> Union[int, float, complex]:
        return dividend / divisor

class FloorDiv(object):
    source_language_name = {"Python":"FloorDiv", "CAST": "FloorDiv"}
    inputs = [Field("dividend", "Number"), Field("divisor", "Number")]
    outputs =  [Field("quotient", "Number")]
    shorthand = "//"
    documentation = ""

    def exec(dividend: Union[int, float, complex], divisor: Union[int, float, complex]) -> Union[int, float, complex]:
        return dividend // divisor

class Mod(object):
    source_language_name = {"Python":"Mod", "GCC":"trunc_mod_expr", "CAST": "Mod"}
    inputs = [Field("dividend", "Number"), Field("divisor", "Number")]
    outputs =  [Field("remainder", "Number")]
    shorthand = "%"
    documentation = ""

    def exec(dividend: Union[int, float, complex], divisor: Union[int, float, complex]) -> Union[int, float, complex]:
        return dividend % divisor

class Pow(object):
    source_language_name = {"Python":"Pow", "CAST": "Pow"}
    inputs = [Field("base", "Number"), Field("exponent", "Number")]
    outputs =  [Field("power", "Number")]
    shorthand = "**"
    documentation = ""

    def exec(base: Union[int, float, complex], power: Union[int, float, complex]) -> Union[int, float, complex]:
        return base ** power

class LShift(object):
    source_language_name = {"Python":"LShift", "GCC":"lshift_expr", "CAST": "LShift"}
    inputs = [Field("operand1", "Number"), Field("operand2", "Number")]
    outputs =  [Field("result", "Number")]
    shorthand = "<<"
    documentation = ""

    def exec(operand1: Union[int, float, complex], operand2: Union[int, float, complex]) -> Union[int, float, complex]:
        return operand1 << operand2

class RShift(object):
    source_language_name = {"Python":"RShift", "GCC":"rshift_expr", "CAST": "RShift"}
    inputs = [Field("operand1", "Number"), Field("operand2", "Number")]
    outputs =  [Field("result", "Number")]
    shorthand = ">>"
    documentation = ""

    def exec(operand1: Union[int, float, complex], operand2: Union[int, float, complex]) -> Union[int, float, complex]:
        return operand1 >> operand2

class BitOr(object):
    source_language_name = {"Python":"BitOr", "GCC":"bit_ior_expr", "CAST": "BitOr"}
    inputs = [Field("binary1", "Number"), Field("binary2", "Number")]
    outputs =  [Field("result", "Number")]
    shorthand = "|"
    documentation = ""

    def exec(binary1: Union[int, float, complex], binary2: Union[int, float, complex]) -> Union[int, float, complex]:
        return binary1 | binary2

class BitXor(object):
    source_language_name = {"Python":"BitXor", "GCC":"bit_xor_expr", "CAST": "BitXor"}
    inputs = [Field("binary1", "Number"), Field("binary2", "Number")]
    outputs =  [Field("result", "Number")]
    shorthand = "^"
    documentation = ""

    def exec(binary1: Union[int, float, complex], binary2: Union[int, float, complex]) -> Union[int, float, complex]:
        return binary1 ^ binary2

class BitAnd(object):
    source_language_name = {"Python":"BitAnd", "GCC":"bit_and_expr", "CAST": "BitAnd"}
    inputs = [Field("binary1", "Number"), Field("binary2", "Number")]
    outputs =  [Field("result", "Number")]
    shorthand = "&"
    documentation = ""

    def exec(binary1: Union[int, float, complex], binary2: Union[int, float, complex]) -> Union[int, float, complex]:
        return binary1 & binary2
    
class And(object):
    source_language_name = {"Python":"And", "GCC":"logical_and", "CAST": "And"}
    inputs = [Field("logical1", "Boolean"), Field("logical2", "Boolean")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "and"
    documentation = ""

    def exec(logical1: bool, logical2:bool) -> bool:
        return logical1 and logical2

class Or(object):
    source_language_name = {"Python":"Or", "GCC":"logical_or", "CAST": "Or"}
    inputs = [Field("logical1", "Boolean"), Field("logical2", "Boolean")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "or"
    documentation = ""

    def exec(logical1: bool, logical2:bool) -> bool:
        return logical1 or logical2

class Eq(object): 
    source_language_name = {"Python":"Eq", "GCC":"eq_expr", "CAST":"Eq"}
    inputs = [Field("operand1", "Any"), Field("operand2", "Any")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "=="
    documentation = ""

    def exec(operand1: Any, operand2: Any) -> bool:
        return operand1 == operand2

class NotEq(object): 
    source_language_name = {"Python":"NotEq", "GCC":"ne_expr", "CAST":"NotEq"}
    inputs = [Field("operand1", "Any"), Field("operand2", "Any")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "!="
    documentation = ""

    def exec(operand1: Any, operand2: Any) -> bool:
        return operand1 != operand2

class Lt(object): 
    source_language_name = {"Python":"Lt", "GCC":"lt_expr", "CAST":"Lt"}
    inputs = [Field("number1", "Number"), Field("number2", "Number")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "<"
    documentation = ""

    def exec(number1: Union[int, float, complex], number2: Union[int, float, complex]) -> bool:
        return number1 < number2

class Lte(object): 
    source_language_name = {"Python":"Lte", "GCC":"le_expr", "CAST":"Lte"} #TODO: Is it LtE or Lte for Python and CAST
    inputs = [Field("number1", "Number"), Field("number2", "Number")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "<="
    documentation = ""

    def exec(number1: Union[int, float, complex], number2: Union[int, float, complex]) -> bool:
        return number1 <= number2

class Gt(object): 
    source_language_name = {"Python":"Gt", "GCC":"gt_expr", "CAST":"Gt"}
    inputs = [Field("number1", "Number"), Field("number2", "Number")]
    outputs =  [Field("result", "Boolean")]
    shorthand = ">"
    documentation = ""

    def exec(number1: Union[int, float, complex], number2: Union[int, float, complex]) -> bool:
        return number1 > number2

class Gte(object): 
    source_language_name = {"Python":"GtE", "GCC":"ge_expr", "CAST":"Gte"}
    inputs = [Field("number1", "Number"), Field("number2", "Number")]
    outputs =  [Field("result", "Boolean")]
    shorthand = ">="
    documentation = ""

    def exec(number1: Union[int, float, complex], number2: Union[int, float, complex]) -> bool:
        return number1 >= number2
   
class In(object): #TODO: How should In and NotIn work? What is the difference between in, member, List_in?
    source_language_name = {"Python":"In", "CAST":"In"}
    inputs = [Field("container_input", "Any"), Field("value", "Any")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "in"
    documentation = ""

    def exec(container_input: Any, value: Any) -> bool:
        return value in container_input

class NotIn(object): #TODO: How should In and NotIn work? What is the difference between in, member, List_in?
    source_language_name = {"Python":"NotIn", "CAST":"NotIn"}
    inputs = [Field("container_input", "Any"), Field("value", "Any")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "not in"
    documentation = ""

    def exec(container_input: Any, value: Any) -> bool:
        return value not in container_input
       
class Set_new_Iterator(object):
    source_language_name = {"Python":"Set_new_Iterator"} 
    inputs = [Field("set_input", "Set")]
    outputs =  [Field("set_iterator", "IteratorSet")]
    shorthand = "Set_new_Iterator"
    documentation = ""

    def exec(set_input: set) -> Iterator[set]:
        return iter(set_input)

class Set_in(object):
    source_language_name = {"Python":"Set_in"} 
    inputs = [Field("set_input", "set"), Field("value", "Any")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "Set_in"
    documentation = ""

    def exec(set_input: set, value: Any) -> bool:
        return value in set_input
  
class new_Set(object):
    source_language_name = {"Python":"new_set"} 
    inputs = [Field("elements", "Any", True)]
    outputs =  [Field("set_output", "Set")]
    shorthand = "new_Set"
    documentation = ""

    def exec(*elements: Any) -> set:
        return set(elements) 
   
class member(object): #TODO: Still unsure the difference between this and in
    source_language_name = {"Python":"member"} 
    inputs = [Field("set_input", "Set", True), Field("value", "Any")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "member"
    documentation = ""

    def exec(set_input: set, value: Any) -> set:
        return value in set_input

class add_elm(object):
    source_language_name = {"Python":"add_elm"} 
    inputs = [Field("input_set", "Set"), Field("element", "Any")]
    outputs =  [Field("set_output", "Set")]
    shorthand = "add_elm"
    documentation = ""

    def exec(input_set: set, element: Any) -> set:
        return input_set.add(element)

class del_elm(object):
    source_language_name = {"Python":"del_elm"} 
    inputs = [Field("input_set", "Set"), Field("element", "Any")]
    outputs =  [Field("set_output", "Set")]
    shorthand = "del_elm"
    documentation = ""

    def exec(input_set: set, element: Any) -> set:
        return input_set.remove(element) # TODO: Do we need to check if this exists first? Will throw KeyError if it does not

class List_get(object):
    source_language_name = {"Python":"List_get"} #TODO: What should this be?
    inputs = [Field("list_input", "List"), Field("index", "Integer")]
    outputs =  [Field("item", "Any")]
    shorthand = "List_get"
    documentation = ""

    def exec(list_input: list, index: int) -> Any:
        return list_input[index]

class List_set(object):
    source_language_name = {"Python":"List_set"} 
    inputs = [Field("list_input", "List"), Field("index", "Integer"), Field("value", "Any")]
    outputs =  [Field("list_output", "List")]
    shorthand = "List_set"
    documentation = ""

    def exec(list_input: list, index: int, value: Any) -> list:
       list_input[index] = value
       return list_input

class List_in(object):
    source_language_name = {"Python":"List_in"} 
    inputs = [Field("list_input", "List"), Field("value", "Any")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "List_in"
    documentation = ""

    def exec(list_input: list, value: Any) -> bool:
        return value in list_input
  
class List_new_Iterator(object):
    source_language_name = {"Python":"List_new_Iterator"} 
    inputs = [Field("list_input", "List")]
    outputs =  [Field("list_iterator", "IteratorList")]
    shorthand = "List_new_Iterator"
    documentation = ""

    def exec(list_input: list) -> Iterator[list]:
        return iter(list_input)

class new_List(object):
    source_language_name = {"Python":"new_List"} 
    inputs = [Field("elements", "Any", True)]
    outputs =  [Field("list_output", "List")]
    shorthand = "new_List"
    documentation = ""

    def exec(*elements: Any) -> list:
        return list(elements) # Interestingly when passing variable sized arguments, it is passeed as a tuple
   
class new_List_num(object):
    source_language_name = {"Python":"new_List_num"} 
    inputs = [Field("element", "Any", True), Field("count", "Integer")]
    outputs =  [Field("list_output", "List")]
    shorthand = "new_List_num"
    documentation = ""

    def exec(element: Any, count: int) -> list:
        return [element] * count 
   
class Array_get(object): # TODO: Should this do type checking for each element?
    source_language_name = {"Python":"Array_get"} 
    inputs = [Field("array_input", "Array"), Field("index", "Integer")]
    outputs =  [Field("item", "Any")]
    shorthand = "Array_get"
    documentation = ""

    def exec(array_input: numpy.ndarray, index: int) -> Any: 
        return array_input[index]

class Array_set(object):
    source_language_name = {"Python":"Array_set"} 
    inputs = [Field("array_input", "Array"), Field("index", "Integer"), Field("value", "Any")]
    outputs =  [Field("array_output", "Array")]
    shorthand = "Array_set"
    documentation = ""

    def exec(array_input: numpy.ndarray, index: int, value: Any) -> numpy.ndarray:
       array_input[index] = value
       return array_input

class Array_in(object):
    source_language_name = {"Python":"Array_in"} 
    inputs = [Field("array_input", "Array"), Field("value", "Any")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "Array_in"
    documentation = ""

    def exec(array_input: numpy.ndarray, value: Any) -> bool:
        return value in array_input
  
class Array_new_Iterator(object):
    source_language_name = {"Python":"Array_new_Iterator"} 
    inputs = [Field("array_input", "Array")]
    outputs =  [Field("array_iterator", "IteratorArray")]
    shorthand = "Array_new_Iterator"
    documentation = ""

    def exec(array_input: numpy.ndarray) -> Iterator: # TODO: Numpy array is not built in type, can we still customize type hints
        return iter(array_input)

class new_Array(object):
    source_language_name = {"Python":"new_Array"} 
    inputs = [Field("elements", "Any", True)]
    outputs =  [Field("array_output", "Array")]
    shorthand = "new_Array"
    documentation = ""

    def exec(*elements: Any) -> numpy.ndarray:
        return numpy.array(list(elements))
   
class new_Array_num(object):
    source_language_name = {"Python":"new_Array_num"} 
    inputs = [Field("element", "Any", True), Field("count", "Integer")]
    outputs =  [Field("array_output", "Array")]
    shorthand = "new_Array_num"
    documentation = ""

    def exec(element: Any, count: int) -> numpy.ndarray:
        return numpy.array([element] * count) 

class Tuple_get(object):
    source_language_name = {"Python":"Tuple_get"} #TODO: What should this be?
    inputs = [Field("tuple_input", "Tuple"), Field("index", "Integer")]
    outputs =  [Field("item", "Any")]
    shorthand = "Tuple_get"
    documentation = ""

    def exec(tuple_input: tuple, index: int) -> Any:
        return tuple_input[index]

class Tuple_set(object): #TODO: Should this exist?
    source_language_name = {"Python":"Tuple_set"} 
    inputs = [Field("tuple_input", "Tuple"), Field("index", "Integer"), Field("value", "Any")]
    outputs =  [Field("tuple_output", "Tuple")]
    shorthand = "Tuple_set"
    documentation = ""

    def exec(tuple_input: tuple, index: int, value: Any) -> tuple:
       placeholder_list = list(tuple_input) #tuples are immutable, so conversions must be made
       placeholder_list[index] = value
       return tuple(placeholder_list) #Convert back to tuple for output 
       

class Tuple_in(object):
    source_language_name = {"Python":"Tuple_in"} 
    inputs = [Field("tuple_input", "Tuple"), Field("value", "Any")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "Tuple_in"
    documentation = ""

    def exec(tuple_input: list, value: Any) -> bool:
        return value in tuple_input
  
class Tuple_new_Iterator(object):
    source_language_name = {"Python":"Tuple_new_Iterator"} 
    inputs = [Field("tuple_input", "Tuple")]
    outputs =  [Field("tuple_iterator", "IteratorTuple")]
    shorthand = "Tuple_new_Iterator"
    documentation = ""

    def exec(tuple_input: list) -> Iterator[tuple]:
        return iter(tuple_input)

class new_Tuple(object):
    source_language_name = {"Python":"new_Tuple"} 
    inputs = [Field("elements", "Any", True)]
    outputs =  [Field("tuple_output", "Tuple")]
    shorthand = "new_Tuple"
    documentation = ""

    def exec(*elements: Any) -> tuple:
        return elements # Interestingly when passing variable sized arguments, it is passeed as a tuple
   
class new_Tuple_num(object):
    source_language_name = {"Python":"new_Tuple_num"} 
    inputs = [Field("element", "Any", True), Field("count", "Integer")]
    outputs =  [Field("tuple_output", "Tuple")]
    shorthand = "new_Tuple_num"
    documentation = ""

    def exec(element: Any, count: int) -> tuple:
        return tuple([element] * count) 

class Map_get(object):
    source_language_name = {"Python":"Map_get"} #TODO: What should this be?
    inputs = [Field("map_input", "Map"), Field("index", "Any")]
    outputs =  [Field("item", "Any")]
    shorthand = "Map_get"
    documentation = ""

    def exec(map_input: dict, index: Any) -> Any: #TODO: Should index really be Any for dict?
        return map_input[index]

class Map_set(object):
    source_language_name = {"Python":"Map_set"} 
    inputs = [Field("map_input", "List"), Field("index", "Any"), Field("value", "Any")]
    outputs =  [Field("map_output", "Map")]
    shorthand = "Map_set"
    documentation = ""

    def exec(map_input: dict, index: Any, value: Any) -> dict:
       map_input[index] = value
       return map_input

class Map_in(object):
    source_language_name = {"Python":"Map_in"} 
    inputs = [Field("map_input", "List"), Field("value", "Any")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "Map_in"
    documentation = ""

    def exec(map_input: dict, value: Any) -> bool:
        return value in map_input
  
class Map_new_Iterator(object): 
    source_language_name = {"Python":"Map_new_Iterator"} 
    inputs = [Field("map_input", "Map")]
    outputs =  [Field("map_iterator", "IteratorMap")]
    shorthand = "Map_new_Iterator"
    documentation = ""

    def exec(map_input: dict) -> Iterator[dict]:
        return iter(map_input)

class new_Map(object): # TODO: Should we have inputs for this?
    source_language_name = {"Python":"new_Map"} 
    inputs = []
    outputs =  [Field("map_output", "Map")]
    shorthand = "new_Map"
    documentation = ""

    def exec() -> dict:
        return {}
   
class new_List_num(object):
    source_language_name = {"Python":"new_List_num"} 
    inputs = [Field("element", "Any", True), Field("count", "Integer")]
    outputs =  [Field("list_output", "List")]
    shorthand = "new_List_num"
    documentation = ""

    def exec(element: Any, count: int) -> list:
        return [element] * count

class Record_get(object):
    source_language_name = {"Python":"Record_get"}
    inputs = [Field("record_input", "Record"), Field("field_name", "String")]
    outputs =  [Field("field", "Field")]
    shorthand = "Record_get"
    documentation = ""

    def exec(record_input: Record, field_name: str) -> RecordField:
        for field in record_input.fields:
            if field.name == field_name:
                return field
        return None

class Record_set(object):
    source_language_name = {"Python":"Record_set"}
    inputs = [Field("record_input", "Record"), Field("field_name", "String"), Field("value", "Any")]
    outputs =  [Field("record_output", "Record")]
    shorthand = "Record_set"
    documentation = ""

    def exec(record_input: Record, field_name: str, value: Any) -> Record:
        for field in record_input.fields:
            if field.name == field_name:
                field.value = value # TODO: Do we need type checking here?

class new_Record(object):
    source_language_name = {"Python":"new_Record"}
    inputs = [Field("record_name", "String")]
    outputs =  [Field("record_output", "Record")]
    shorthand = "new_Record"
    documentation = ""

    def exec(record_name: str) -> Record:
        return Record(record_name)

class new_Field(object):
    source_language_name = {"Python":"new_Field"}
    inputs = [Field("record_input", "Record"), Field("field_name", "String"), Field("value_type", "Type")]
    outputs =  [Field("record_output", "Record")]
    shorthand = "new_Field"
    documentation = ""

    def exec(record_input: Record, field_name: str, value_type: type) -> Record:
        return record_input.fields.append(RecordField(field_name, value_type, None)) # #TODO: Do we need to set a default value?

class IteratorSet_next(object):
    source_language_name = {"Python":"IteratorSet_next"} 
    inputs = [Field("iterator_input", "IteratorSet")]
    outputs =  [Field("element", "Any"), Field("iterator_output", "IteratorSet"), Field("stop_condition", "Boolean")]
    shorthand = "IteratorSet_next"
    documentation = ""

    def exec(iterator_input: Iterator[set]) -> Tuple[Any, Iterator[Set], bool]:
        current_element = None
        # We have to wrap this code in a try except block because of the call to next()
        # next() will throw an error if you've reached the end of the iterator
        # You can specify a default value for it to return instead of an exception, 
        # but we can't use this since there is no way to differentiate between a regular value and the default value
        
        try:
            current_element = next(iterator_input)
            return(current_element, iterator_input, False)
        except: 
            return(None, iterator_input, True)

class IteratorTuple_next(object):
    source_language_name = {"Python":"IteratorTuple_next"} 
    inputs = [Field("iterator_input", "IteratorTuple")]
    outputs =  [Field("element", "Any"), Field("iterator_output", "IteratorTuple"), Field("stop_condition", "Boolean")]
    shorthand = "IteratorTuple_next"
    documentation = ""

    def exec(iterator_input: Iterator[tuple]) -> Tuple[Any, Iterator[Tuple], bool]:
        current_element = None
        # We have to wrap this code in a try except block because of the call to next()
        # next() will throw an error if you've reached the end of the iterator
        # You can specify a default value for it to return instead of an exception, 
        # but we can't use this since there is no way to differentiate between a regular value and the default value
        
        try:
            current_element = next(iterator_input)
            return(current_element, iterator_input, False)
        except: 
            return(None, iterator_input, True)

class IteratorArray_next(object):
    source_language_name = {"Python":"IteratorArray_next"} 
    inputs = [Field("iterator_input", "IteratorArray")]
    outputs =  [Field("element", "Any"), Field("iterator_output", "IteratorArray"), Field("stop_condition", "Boolean")]
    shorthand = "IteratorArray_next"
    documentation = ""

    def exec(iterator_input: Iterator) -> Tuple[Any, Iterator, bool]: # TODO: Can we say Iterator[numpy.ndarray]
        current_element = None
        # We have to wrap this code in a try except block because of the call to next()
        # next() will throw an error if you've reached the end of the iterator
        # You can specify a default value for it to return instead of an exception, 
        # but we can't use this since there is no way to differentiate between a regular value and the default value
        
        try:
            current_element = next(iterator_input)
            return(current_element, iterator_input, False)
        except: 
            return(None, iterator_input, True)

class IteratorList_next(object):
    source_language_name = {"Python":"IteratorList_next"} 
    inputs = [Field("iterator_input", "IteratorList")]
    outputs =  [Field("element", "Any"), Field("iterator_output", "IteratorList"), Field("stop_condition", "Boolean")]
    shorthand = "IteratorList_next"
    documentation = ""

    def exec(iterator_input: Iterator[List]) -> Tuple[Any, Iterator[List], bool]:
        current_element = None
        # We have to wrap this code in a try except block because of the call to next()
        # next() will throw an error if you've reached the end of the iterator
        # You can specify a default value for it to return instead of an exception, 
        # but we can't use this since there is no way to differentiate between a regular value and the default value
        
        try:
            current_element = next(iterator_input)
            return(current_element, iterator_input, False)
        except: 
            return(None, iterator_input, True)

class IteratorMap_next(object):
    source_language_name = {"Python":"IteratorMap_next"} 
    inputs = [Field("iterator_input", "IteratorMap")]
    outputs =  [Field("element", "Any"), Field("iterator_output", "IteratorMap"), Field("stop_condition", "Boolean")]
    shorthand = "IteratorMap_next"
    documentation = ""

    def exec(iterator_input: Iterator[dict]) -> Tuple[Any, Iterator[Dict], bool]:
        current_element = None
        # We have to wrap this code in a try except block because of the call to next()
        # next() will throw an error if you've reached the end of the iterator
        # You can specify a default value for it to return instead of an exception, 
        # but we can't use this since there is no way to differentiate between a regular value and the default value
        
        try:
            current_element = next(iterator_input)
            return(current_element, iterator_input, False)
        except: 
            return(None, iterator_input, True)
      
class CASTGenericGet:
    source_language_name = {"CAST":"_get"} 
    inputs = [Field("indexible_input", "Indexable"), Field("index", "Any")]
    outputs =  [Field("element", "Any")]
    shorthand = "_get"
    documentation = "The cast currently uses generic primitive operators (_get, _set, iter, next) while the  Gromet uses specific operators (IteratorMap_next). These primitive ops are a tempory fix for that mismatch"
class CASTGenericSet:
    source_language_name = {"CAST":"_set"} 
    inputs = [Field("indexible_input", "Indexable"), Field("index", "Any"), Field("value", "Any")]
    outputs =  [Field("indexible_output", "Indexable")]
    shorthand = "_set"
    documentation = "The cast currently uses generic primitive operators (_get, _set, iter, next) while the  Gromet uses specific operators (IteratorMap_next). These primitive ops are a tempory fix for that mismatch"

class CASTGenericIter:
    source_language_name = {"CAST":"iter"} 
    inputs = [Field("iterable_input", "Iterable")]
    outputs =  [Field("iterator_output", "Iterator")]
    shorthand = "iter"
    documentation = "The cast currently uses generic primitive operators (_get, _set, iter, next) while the  Gromet uses specific operators (IteratorMap_next). These primitive ops are a tempory fix for that mismatch"
class CASTGenericNext:
    source_language_name = {"CAST":"next"} 
    inputs = [Field("iterator_input", "Iterator")]
    outputs =  [Field("element", "Any"), Field("iterator_output", "Iterator"), Field("stop_condition", "Boolean")]
    shorthand = "next"
    documentation = "The cast currently uses generic primitive operators (_get, _set, iter, next) while the  Gromet uses specific operators (IteratorMap_next). These primitive ops are a tempory fix for that mismatch"

class Is(object):
    source_language_name = {"Python": "is", "CAST":"Is"} #TODO: Should Python/CAST be Is or is?
    inputs = [Field("operand1", "Any"), Field("operand2", "Any")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "is"
    documentation = ""
    
    def exec(operand1: Any, operand2: Any) -> bool:
        return operand1 is operand2

class NotIs(object):
    source_language_name = {"Python": "is not", "CAST":"NotIs"} #TODO: What should Python name be here?
    inputs = [Field("operand1", "Any"), Field("operand2", "Any")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "not is"
    documentation = ""
    
    def exec(operand1: Any, operand2: Any) -> bool:
        return operand1 is not operand2

class IsInstance(object):
    source_language_name = {"Python": "isinstance"}
    inputs = [Field("operand", "Any"), Field("type", "Type")] # TODO: Get confirmation on adding Type field
    outputs =  [Field("result", "Boolean")]
    shorthand = "type"
    documentation = ""
    
    def exec(operand: Any, type: type) -> bool: # TODO: Fix name of right argument
        return isinstance(operand, type)

class Type(object):
    source_language_name = {"Python": "type"}
    inputs = [Field("operand", "Any")]
    outputs =  [Field("result", "Type")]
    shorthand = "type"
    documentation = ""
    
    def exec(operand: Any) ->type:
        return type(operand)


class Print: #TODO: How should print work? Will likely not be a CASTGeneric function
    source_language_name = {"CAST":"print"} 
    inputs = [Field("input", "Any")]
    outputs =  []
    shorthand = "print"
    documentation = "The cast currently uses generic primitive operators (_get, _set, iter, next) while the  Gromet uses specific operators (IteratorMap_next). These primitive ops are a tempory fix for that mismatch"

    def exec(input: Any) -> None:
        print(input)

class Range:
    source_language_name = {"CAST":"range"} 
    inputs = [Field("input", "Integer")] #TODO: What is the input to range?
    outputs =  [Field("range_output", "Range")]
    shorthand = "range"
    documentation = ""

    def exec(input: int) -> range:
        return range(input)

#### Interface for accessing fields of classes
def get_class_obj(op: str, language: str, debug=False) -> Any: #TODO: Update the type hints for this
    global primitive_map

    try:
        return primitive_map[language][op]
    except:
        if(debug):
            print(f"Operation not supported: {op} for language {language} ... Returning None")
        return None

def get_shorthand(op: str, language: str) -> str:
    class_obj = get_class_obj(op, language, debug=True)
    
    if class_obj:
        try:
            return class_obj.shorthand
        except:
            print(f"Operation has no shorthand: {op} for language {language} ... Returning None")
            
    return None
        
def get_inputs(op: str, language: str) -> str:
    class_obj = get_class_obj(op, language, debug=True)
    
    if class_obj:
        try:
            return class_obj.inputs
        except:
            print(f"Operation has no inputs: {op} for language {language} ... Returning None")
    
    return None

def get_outputs(op: str, language: str, debug=True) -> str:
    class_obj = get_class_obj(op, language)
    
    if class_obj:
        try:
            return class_obj.outputs
        except:
            print(f"Operation has no outputs: {op} for language {language} ... Returning None")
    
    return None

def is_primitive(op: str, language: str):
    return get_class_obj(op, language) is not None

# Create table ob primitive op classes
primitive_ops = inspect.getmembers(sys.modules[__name__], predicate=inspect.isclass)

# Create map between langauge names and python class objects
python_primitive_dict = {}
gcc_primitive_dict = {}
cast_primitive_dict = {}
for class_name, class_obj in primitive_ops:
        if hasattr(class_obj, "source_language_name"):
            if "Python" in class_obj.source_language_name:
                python_primitive_dict[class_obj.source_language_name["Python"]] = class_obj
            if "GCC" in class_obj.source_language_name:
                gcc_primitive_dict[class_obj.source_language_name["GCC"]] = class_obj
            if "CAST" in class_obj.source_language_name:
                cast_primitive_dict[class_obj.source_language_name["CAST"]] = class_obj
  
primitive_map = {"Python": python_primitive_dict, "GCC": gcc_primitive_dict, "CAST": cast_primitive_dict}


