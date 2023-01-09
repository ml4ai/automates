from typing import Dict, Any
from defined_types import Hashable
def new_Map() -> Dict:
    return {}

def Map_get(map_input: Dict, index: Hashable) -> Any:
    return map_input[index]

def Map_set(map_input: Dict, index: Hashable, element: Any):
    map_input[index] = element
    return map_input
