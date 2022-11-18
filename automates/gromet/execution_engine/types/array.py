import numpy
from typing import Any

from automates.gromet.execution_engine.types.defined_types import Field

class new_Array(object):
    source_language_name = {"Python":"new_Array"} 
    inputs = [Field("elements", "Any", True)]
    outputs =  [Field("array_output", "Array")]
    shorthand = "new_Array"
    documentation = ""

    def exec(*elements: Any) -> numpy.ndarray:
        return numpy.array(list(elements))