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

class Map_get(object):
    source_language_name = {"CAST":"map_get"}
    inputs = [Field("map_input", "Map"), Field("index", "Hashable")]
    outputs = [Field("element", "Any")]
    shorthand = "map_get"
    documentation = ""

class Map_set(object):
    source_language_name = {"CAST":"map_set"}
    inputs = [Field("map_set", "Map"), Field("index", "Hashable"), Field("element", "Any")]
    outputs = [Field("map_output", "Map")]
    shorthand = "map_set"
    documentation = ""