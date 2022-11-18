
from typing import Iterator, Union, Any, List, Dict, Set, Tuple
import sys
import inspect
 
import automates.gromet.execution_engine.types
from automates.gromet.execution_engine.types import (
    array,
    binary,
    indexable,
    iterable,
    list,
    map,
    other,
    record,
    sequence,
    set,
    tuple,
    unary
)

#### Interface for accessing fields of classes
def get_class_obj(op: str, language: str, debug=False) -> Any: #TODO: Update the type hints for this
    global primitive_map

    try:
        return primitive_map[language][op]
    except:
        if(debug):
            print(f"Operation not supported: {op} for language {language} ... Returning None")
        return None

def get_shorthand(op: str, language: str) -> str:
    class_obj = get_class_obj(op, language, debug=True)
    
    if class_obj:
        try:
            return class_obj.shorthand
        except:
            print(f"Operation has no shorthand: {op} for language {language} ... Returning None")
            
    return None
        
def get_inputs(op: str, language: str) -> str:
    class_obj = get_class_obj(op, language, debug=True)
    
    if class_obj:
        try:
            return class_obj.inputs
        except:
            print(f"Operation has no inputs: {op} for language {language} ... Returning None")
    
    return None

def get_outputs(op: str, language: str, debug=True) -> str:
    class_obj = get_class_obj(op, language)
    
    if class_obj:
        try:
            return class_obj.outputs
        except:
            print(f"Operation has no outputs: {op} for language {language} ... Returning None")
    
    return None

def is_primitive(op: str, language: str):
    return get_class_obj(op, language) is not None

# Create table ob primitive op classes
submodules = inspect.getmembers(automates.gromet.execution_engine.types, predicate=inspect.ismodule)
primitive_ops = []
for module_name, module in submodules:
    primitive_ops += inspect.getmembers(module, predicate=inspect.isclass)
#primitive_ops = inspect.getmembers(sys.modules[__name__], predicate=inspect.isclass)

# Create map between langauge names and python class objects
python_primitive_dict = {}
gcc_primitive_dict = {}
cast_primitive_dict = {}
for class_name, class_obj in primitive_ops:
        if hasattr(class_obj, "source_language_name"):
            if "Python" in class_obj.source_language_name:
                python_primitive_dict[class_obj.source_language_name["Python"]] = class_obj
            if "GCC" in class_obj.source_language_name:
                gcc_primitive_dict[class_obj.source_language_name["GCC"]] = class_obj
            if "CAST" in class_obj.source_language_name:
                cast_primitive_dict[class_obj.source_language_name["CAST"]] = class_obj
  
primitive_map = {"Python": python_primitive_dict, "GCC": gcc_primitive_dict, "CAST": cast_primitive_dict}
print(primitive_map["CAST"])

