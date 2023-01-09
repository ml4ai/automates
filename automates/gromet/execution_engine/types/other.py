from typing import Any

from automates.gromet.execution_engine.types.defined_types import Field 

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
    inputs = [Field("operand", "Any"), Field("type_name", "String")] # TODO: Get confirmation on adding Type field
    outputs =  [Field("result", "Boolean")]
    shorthand = "type"
    documentation = ""
    
    def exec(operand: Any, type_name: str) -> bool: # TODO: Fix name of right argument
        return isinstance(operand, type)

class Type(object):
    source_language_name = {"Python": "type"}
    inputs = [Field("operand", "Any")]
    outputs =  [Field("result", "String")]
    shorthand = "type"
    documentation = ""
    
    def exec(operand: Any) -> str:
        return str(type(operand))

class Cast(object):
    source_language_name = { "CAST": "cast"}
    inputs = [Field("operand", "Any")]
    outputs =  [Field("type_name", "String")]
    shorthand = "cast"
    documentation = ""

class Slice(object):
    source_language_name = { "CAST": "slice"}
    inputs = [Field("lower", "Integer"), Field("upper", "Integer"), Field("step", "Integer")]
    outputs =  [Field("output_slice", "Slice")]
    shorthand = "slice"
    documentation = ""

class ExtSlice(object):
    source_language_name = { "CAST": "ext_slice"}
    inputs = [Field("dims", "List")]
    outputs =  [Field("output_slice", "ExtSlice")]
    shorthand = "ext_slice"

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
    inputs = [Field("stop", "integer"), Field("start", "integer", default_val=0), Field("step", "integer", default_val=1)] #TODO: What is the input to range?
    outputs =  [Field("range_output", "Range")]
    shorthand = "range"
    documentation = ""

    def exec(input: int) -> range:
        return range(input)
