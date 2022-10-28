from typing import Any, Set

from automates.gromet.execution_engine.types.defined_types import Field

class new_Set(object):
    source_language_name = {"Python":"new_set"} 
    inputs = [Field("elements", "Any", True)]
    outputs =  [Field("set_output", "Set")]
    shorthand = "new_Set"
    documentation = ""

    def exec(*elements: Any) -> Set:
        return set(elements) 
   
class member(object): #TODO: Still unsure the difference between this and in
    source_language_name = {"Python":"member"} 
    inputs = [Field("set_input", "Set", True), Field("value", "Any")]
    outputs =  [Field("result", "Boolean")]
    shorthand = "member"
    documentation = ""

    def exec(set_input: Set, value: Any) -> Set:
        return value in set_input

class add_elm(object):
    source_language_name = {"Python":"add_elm"} 
    inputs = [Field("input_set", "Set"), Field("element", "Any")]
    outputs =  [Field("set_output", "Set")]
    shorthand = "add_elm"
    documentation = ""

    def exec(input_set: Set, element: Any) -> Set:
        return input_set.add(element)

class del_elm(object):
    source_language_name = {"Python":"del_elm"} 
    inputs = [Field("input_set", "Set"), Field("element", "Any")]
    outputs =  [Field("set_output", "Set")]
    shorthand = "del_elm"
    documentation = ""

    def exec(input_set: Set, element: Any) -> Set:
        return input_set.remove(element) # TODO: Do we need to check if this exists first? Will throw KeyError if it does not