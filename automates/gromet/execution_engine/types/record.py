from typing import Any
from automates.gromet.execution_engine.types.defined_types import Record, RecordField

def new_Record(record_name: str) -> Record:
    return Record(record_name)

def new_Field(record_input: Record, field_name: str, value_type: type) -> Record:
    return record_input.fields.append(RecordField(field_name, value_type, None)) # #TODO: Do we need to set a default value?

def Record_get(record_input: Record, index: str) -> Any:
   for field in record_input.fields:
        if field.name == index:
            return field

def Record_set(record_input: Record, index: str, element: Any):
    for field in record_input.fields:
        if field.name == index:
            field.value = element # TODO: Do we need type checking here?
    return record_input
