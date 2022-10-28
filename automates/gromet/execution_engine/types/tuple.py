from typing import Any, Tuple

from automates.gromet.execution_engine.types.defined_types import Field

class new_Tuple(object):
    source_language_name = {"Python":"new_Tuple"} 
    inputs = [Field("elements", "Any", True)]
    outputs =  [Field("tuple_output", "Tuple")]
    shorthand = "new_Tuple"
    documentation = ""

    def exec(*elements: Any) -> Tuple:
        return elements # Interestingly when passing variable sized arguments, it is passeed as a tuple