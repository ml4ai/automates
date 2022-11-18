from typing import Any, List

from automates.gromet.execution_engine.types.defined_types import Field

class new_List(object):
    source_language_name = {"Python":"new_List"} 
    inputs = [Field("elements", "Any", True)]
    outputs =  [Field("list_output", "List")]
    shorthand = "new_List"
    documentation = ""

    def exec(*elements: Any) -> list:
        return list(elements) # Interestingly when passing variable sized arguments, it is passeed as a tuple
   
