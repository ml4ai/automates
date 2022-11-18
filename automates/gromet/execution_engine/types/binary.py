from typing import Union, Any

from automates.gromet.execution_engine.types.defined_types import Field

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
