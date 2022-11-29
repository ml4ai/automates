from automates.gromet.execution_engine.types.defined_types import Field, Record, RecordField

class new_Record(object):
    source_language_name = {"Python":"new_Record"}
    inputs = [Field("record_name", "String")]
    outputs =  [Field("record_output", "Record")]
    shorthand = "new_Record"
    documentation = ""

    def exec(record_name: str) -> Record:
        return Record(record_name)

class new_Field(object):
    source_language_name = {"Python":"new_Field"}
    inputs = [Field("record_input", "Record"), Field("field_name", "String"), Field("value_type", "Type")]
    outputs =  [Field("record_output", "Record")]
    shorthand = "new_Field"
    documentation = ""

    def exec(record_input: Record, field_name: str, value_type: type) -> Record:
        return record_input.fields.append(RecordField(field_name, value_type, None)) # #TODO: Do we need to set a default value?


class Record_get(object):
    source_language_name = {"CAST":"record_get"}
    inputs = [Field("record_input", "Record"), Field("index", "String")]
    outputs = [Field("field_output", "Field")]
    shorthand = "record_get"
    documentation = ""

class Record_set(object):
    source_language_name = {"CAST":"record_set"}
    inputs = [Field("record_input", "Record"), Field("index", "String"), Field("element", "Any")]
    outputs = [Field("record_output", "Record")]
    shorthand = "record_set"
    documentation = ""