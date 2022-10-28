from typing import Dict

from automates.gromet.execution_engine.types.defined_types import Field

class new_Map(object): # TODO: Should we have inputs for this?
    source_language_name = {"Python":"new_Map"} 
    inputs = []
    outputs =  [Field("map_output", "Map")]
    shorthand = "new_Map"
    documentation = ""

    def exec() -> Dict:
        return {}