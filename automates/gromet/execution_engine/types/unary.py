from typing import Union

from automates.gromet.execution_engine.types.defined_types import Field

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