from typing import Any, Iterator, Tuple

from automates.gromet.execution_engine.types.defined_types import Field

class Iterator_next(object):
    source_language_name = {"Python":"_next"} 
    inputs = [Field("iterator_input", "Iterator")]
    outputs =  [Field("element", "Any"), Field("iterator_output", "Iterator"), Field("stop_condition", "Boolean")]
    shorthand = "_next"
    documentation = ""

    def exec(iterator_input: Iterator) -> Tuple[Any, Iterator, bool]:
        current_element = None
        # We have to wrap this code in a try except block because of the call to next()
        # next() will throw an error if you've reached the end of the iterator
        # You can specify a default value for it to return instead of an exception, 
        # but we can't use this since there is no way to differentiate between a regular value and the default value
        
        try:
            current_element = next(iterator_input)
            return(current_element, iterator_input, False)
        except: 
            return(None, iterator_input, True)