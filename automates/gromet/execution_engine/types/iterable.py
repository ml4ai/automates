from typing import Iterator, Union, Any, List, Dict, Set, Tuple
from automates.gromet.execution_engine.types.defined_types import Field, Iterable


class Iterable_new_Iterator(object):
    source_language_name = {"CAST":"_iter"} #TODO: What should this be (iter, next, etc)
    inputs = [Field("iterable_input", "Iterable")]
    outputs =  [Field("iterator_output", "Iterator")]
    shorthand = "_iter"
    documentation = ""

    def exec(iterable_input: Iterable) -> Iterator:
        return iter(iterable_input)

class Iterable_in(object):
    source_language_name = {"CAST":"_in"} #TODO: What should this be 
    inputs = [Field("iterable_input", "Iterable"), Field("element", "Any")]
    outputs =  [Field("iterator_output", "Iterator")]
    shorthand = "_in"
    documentation = ""

    def exec(iterable_input: Iterable, element: Any) -> bool:
        return element in iterable_input