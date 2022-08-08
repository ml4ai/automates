import json

from pyparsing import col
from automates.model_assembly.gromet.model import (  
    GrometBoxConditional,
    GrometBoxFunction,
    GrometBoxLoop,
    GrometFNModule,
    GrometFN,
    GrometPort,
    GrometWire,
    LiteralValue,
)
from automates.model_assembly.gromet.metadata import (
    Metadata,
    Provenance,
    SourceCodeReference,
    SourceCodeDataType,
    SourceCodeLoopInit,
    SourceCodeLoopUpdate,
    TextualDocumentCollection,
    TextualDocumentReference,
    TextDefinition,
    TextParameter,
    EquationDefinition,
    EquationExtraction,
    EquationParameter,
    TextExtraction,
    GrometCreation,
    SourceCodeCollection,
    CodeFileReference

)
from automates.model_assembly.gromet.model.gromet_type import GrometType
from automates.model_assembly.gromet.model.typed_value import TypedValue


def json_to_gromet(path):
    # Read JSON from file
    with open(path) as f:
        json_string = f.read()
    json_object = json.loads(json_string)

    # Import Module 
    name = json_object["name"]
    gromet_module = GrometFNModule(name)
        
    # Create the function networt
    gromet_module.fn = parse_function_network(json_object["fn"])

    # Import Attributes
    for fn in json_object["attributes"]:
             # TODO: Add support for types other than FN
            type = fn["type"]
            value = TypedValue(type="FN", value=parse_function_network(fn["value"]))
            
            if not gromet_module.attributes:
                gromet_module.attributes = [value]
            else:
                gromet_module.attributes.append(value)

    # Import top level module metadata
    if "metadata" in json_object:
        gromet_module.metadata = []
        for metadata in json_object["metadata"]:
            gromet_module.metadata.append(parse_metadata(metadata))
    
    return gromet_module


def parse_function_network(obj):
        # Create function_network object
        function_network = GrometFN()

        for table,contents in obj.items():
            # Move to next table if this one is empty
            table_size = len(table)
            if table_size == 0:
                continue
            if table == "b" or table == "bf":
                for entry in contents:
                    # We create a blank box function first and fill out fields later,
                    # since not all box functions will have all fields 
                    gromet_box_function = GrometBoxFunction()
                    if "function_type" in entry:
                        gromet_box_function.function_type = entry["function_type"]
                    if "contents" in entry:
                        gromet_box_function.contents = entry["contents"]
                    if "name" in entry:
                        gromet_box_function.name = entry["name"]
                    if "value" in entry:
                        gromet_box_function.value = LiteralValue(value_type=entry["value"]["value_type"], value=entry["value"]["value"])
                    
                    # Check for existence of metadata in each entry.
                    if "metadata" in entry:
                        gromet_box_function.metadata = []
                        for metadata in entry["metadata"]:
                            gromet_box_function.metadata.append(parse_metadata(metadata))
                    
                    # We use getattr/setattr to set attribute, since we only have the attribute as a string
                    try:
                        current_attribute = getattr(function_network, table)
                        current_attribute.append(gromet_box_function)
                    except:
                        setattr(function_network, table, [gromet_box_function])
            elif table == "bc":
                for entry in contents:
                    gromet_conditional = GrometBoxConditional()
        
                    # bc has three different components: condition, body_if, and body_else
                    if "condition" in entry:
                        gromet_conditional.condition = entry["condition"]
                    if "body_if" in entry:
                        gromet_conditional.body_if = entry["body_if"]
                    if "body_else" in entry:
                        gromet_conditional.body_else = entry["body_else"]

                    # Check for existence of metadata in each entry.
                    if "metadata" in entry:
                        gromet_conditional.metadata = []
                        for metadata in entry["metadata"]:
                            gromet_conditional.metadata.append(parse_metadata(metadata))

                    if function_network.bc:
                        function_network.bc.append(gromet_conditional)
                    else:
                        function_network.bc = [gromet_conditional]
            elif table == "bl":
                for entry in contents:
                    gromet_loop = GrometBoxLoop()
                    #bl has two components: condition and body
                    if "condition" in entry:
                        gromet_loop.condition = entry["condition"]
                    if "body" in entry:
                        gromet_loop.body = entry["body"]

                    # Check for existence of metadata in each entry.
                    if "metadata" in entry:
                        gromet_loop.metadata = []
                        for metadata in entry["metadata"]:
                            gromet_loop.metadata.append(parse_metadata(metadata))

                    if function_network.bl:
                        function_network.bl.append(gromet_loop)
                    else:
                        function_network.bl = [gromet_loop]  
            elif table.startswith("p") or table.startswith("o"):
                for entry in contents:
                    gromet_port = GrometPort()
                    if "id" in entry:
                        gromet_port.id = entry["id"]
                    if "name" in entry:
                        gromet_port.name = entry["name"]
                    if "box" in entry:
                        gromet_port.box = entry["box"]
                    
                    # Check for existence of metadata in each entry.
                    if "metadata" in entry:
                        gromet_port.metadata = []
                        for metadata in entry["metadata"]:
                            gromet_port.metadata.append(parse_metadata(metadata))

                    try:
                        current_attribute = getattr(function_network, table)
                        current_attribute.append(gromet_port)
                    except:
                        setattr(function_network, table, [gromet_port])
            elif table.startswith("w"):
                for entry in contents:
                    gromet_wire = GrometWire()
                    
                    if "src" in entry:
                        gromet_wire.src = entry["src"]
                    if "tgt" in entry:
                        gromet_wire.tgt = entry["tgt"]
                    
                    # Check for existence of metadata in each entry.
                    if "metadata" in entry:
                        gromet_wire.metadata = []
                        for metadata in entry["metadata"]:
                            gromet_wire.metadata.append(parse_metadata(metadata))

                    try:
                        current_attribute = getattr(function_network, table)
                        current_attribute.append(gromet_wire)
                    except:
                        setattr(function_network, table, [gromet_wire])
        
        # Import function network level metadata
        if "metadata" in obj:
            function_network.metadata = []
            for metadata in obj["metadata"]:
                function_network.metadata.append(parse_metadata(metadata))
        
        return function_network
def parse_metadata(obj):
    # All metadata have a provenance and metadata_type
    provenance = Provenance(method=obj["provenance"]["method"], timestamp=obj["provenance"]["timestamp"])
    metadata_type = obj["metadata_type"]

    # Load type specific data
    if metadata_type == "source_code_reference":
        # Due to Swagger auto generated schema, all fields marked required must be non-None in the constructor
        # TODO: Update required fields. For now all fields will be optional
        source_code_reference = SourceCodeReference(metadata_type=metadata_type, provenance=provenance)
        
        # We check for the existence of optional fields, and then add them to the object if they exist
        if "code_file_reference_uid" in obj:
            source_code_reference.code_file_reference_uid = obj["code_file_reference_uid"]
        if "line_begin" in obj:
            source_code_reference.line_begin = obj["line_begin"]
        if "line_end" in obj:
            source_code_reference.line_end=obj["line_end"]
        if "col_begin" in obj:
            source_code_reference.col_begin=obj["col_begin"]
        if "col_end" in obj:   
            source_code_reference.col_end=obj["col_end"]
            
        return source_code_reference
    elif metadata_type == "source_code_data_type":
        source_code_data_type = SourceCodeDataType(metadata_type=metadata_type, provenance=provenance) 

        if "source_language" in obj:
            source_code_data_type.source_language = obj["source_language"]
        if "source_language_version" in obj:
            source_code_data_type.source_language_version = obj["source_language_version"]
        if "data_type" in obj:
            source_code_data_type.data_type = obj["data_type"]

        return source_code_data_type
    elif metadata_type == "source_code_loop_init":
        source_code_loop_init = SourceCodeLoopInit(metadata_type=metadata_type, provenance=provenance)

        if "source_language" in obj:
            source_code_loop_init.source_language=obj["source_language"]
        if "source_language_version" in obj:
            source_code_loop_init.source_language = obj["source_language_version"]
        if "loop_name" in obj:
            source_code_loop_init.loop_name = obj["loop_name"]

        return source_code_loop_init
    elif metadata_type == "source_code_loop_update":
        source_code_loop_update = SourceCodeLoopUpdate(metadata_type=metadata_type, provenance=provenance)
    
        if "source_language" in obj:
            source_code_loop_update.source_language=obj["source_language"]
        if "source_language_version" in obj:
            source_code_loop_update.source_language = obj["source_language_version"]
        if "loop_name" in obj:
            source_code_loop_update.loop_name = obj["loop_name"]

        return source_code_loop_update
    elif metadata_type == "gromet_creation":
        gromet_creation = GrometCreation(metadata_type=metadata_type, provenance=provenance)
        return gromet_creation
    elif metadata_type == "source_code_collection":
        source_code_collection = SourceCodeCollection(metadata_type=metadata_type, provenance=provenance)

        if "global_reference_id" in obj:
            source_code_collection.global_reference_id = obj["global_reference_id"]
        if "files" in obj: 
            #SourceCodeCollection.files is a list of CodeFileReference objects
            source_code_collection.files = []
            for file in obj["files"]:
                code_file_reference = CodeFileReference()
                if "uid" in file:
                    code_file_reference.uid = file["uid"]
                if "name" in file:
                    code_file_reference.name = file["name"]
                if "path" in file:
                    code_file_reference.path = file["path"]
                source_code_collection.files.append(code_file_reference) 
        if "name" in obj:
            source_code_collection.name = obj["name"]

        return source_code_collection
    elif metadata_type == "textual_document_collection":
        textual_document_collection = TextualDocumentCollection(metadata_type=metadata_type, provenance=provenance)
        
        if "documents" in obj:
            # TextualDocumentCollection.documents is a list of TextualDocumentReference objects
            textual_document_collection.documents = []
            for document in obj["documents"]:
                textual_document_reference = TextualDocumentReference()

                if "uid" in document:
                    textual_document_reference.uid = document["uid"]
                if "global_reference_id" in document:
                    textual_document_reference.global_reference_id = document["global_reference_id"]
                if "cosmos_id" in document:
                    textual_document_reference.cosmos_id = document["cosmos_id"]
                if "cosmos_version_number" in document:
                    textual_document_reference.cosmos_version_number = document["cosmos_version_number"]
                if "skema_id" in document:
                    textual_document_reference._skema_id = document["skema_id"]
                if "skema_version_number" in document:
                    textual_document_reference._skema_version_number = document["skema_version_number"]
                
                # TODO: ADD BIBJSON field
                # bibjson field is a bibjson object
                #if "bibjson" in d:
                #    textual_document_reference._skema_id = d["skema_id"]
                textual_document_collection.documents.append(textual_document_reference)
        return textual_document_collection
    elif metadata_type == "equation_definition":
        equation_definition = EquationDefinition(metadata_type=metadata_type, provenance=provenance)

        # EquationDefinition.equation_extraction is an EquationExtraction object 
        if "equation_extraction" in obj:
            equation_extraction = EquationExtraction()
            if "source_type" in obj["equation_extraction"]:
                equation_extraction.source_type = obj["equation_extraction"]["source_type"]
            if "document_reference_uid" in obj["equation_extraction"]:
                equation_extraction.document_reference_uid = obj["equation_extraction"]["document_reference_uid"]
            if "equation_number" in obj["equation_extraction"]:
                equation_extraction.equation_number = obj["equation_extraction"]["equation_number"]
            equation_definition.equation_extraction = equation_extraction
        if "equation_mathml_source" in obj:
            equation_definition.equation_mathml_source = obj["equation_mathml_source"]
        if "equation_latex_source" in obj:
            equation_definition.equation_latex_source = obj["equation_latex_source"]

        return equation_definition
    elif metadata_type == "equation_parameter":
        equation_parameter = EquationParameter(metadata_type=metadata_type, provenance=provenance)
        
        if "equation_extraction" in obj:
            equation_extraction = EquationExtraction()
            if "source_type" in obj["equation_extraction"]:
                equation_extraction.source_type = obj["equation_extraction"]["source_type"]
            if "document_reference_uid" in obj["equation_extraction"]:
                equation_extraction.document_reference_uid = obj["equation_extraction"]["document_reference_uid"]
            if "equation_number" in obj["equation_extraction"]:
                equation_extraction.equation_number = obj["equation_extraction"]["equation_number"]
            equation_parameter.equation_extraction = equation_extraction
        if "value" in obj:
            value = LiteralValue()
            value.value_type = obj["value"]["value_type"]
            value.value = obj["value"]["value"]
            equation_parameter.value = value
        if "variable_identifier" in obj:
            equation_parameter.variable_identifier = obj["variable_identifier"]

        return equation_parameter
    elif metadata_type == "text_definition":
        text_definition = TextDefinition(metadata_type=metadata_type, provenance=provenance)

        if "text_extraction" in obj:
            text_extraction = TextExtraction()
            text_extraction.document_reference_uid = obj["text_extraction"]["document_reference_uid"]
            text_extraction.page = obj["text_extraction"]["page"]
            text_extraction.block = obj["text_extraction"]["block"]
            text_extraction.char_begin = obj["text_extraction"]["char_begin"]
            text_extraction.char_end = obj["text_extraction"]["char_end"]
            text_definition.text_extraction = text_extraction
        if "variable_identifier" in obj:
            text_definition.variable_identifier = obj["variable_identifier"]
        if "variable_definition" in obj:
            text_definition.variable_definition = obj["variable_definition"]
        
        return text_definition
    elif metadata_type == "text_parameter":
        text_parameter = TextParameter(metadata_type=metadata_type, provenance=provenance)

        if "text_extraction" in obj:
            text_extraction = TextExtraction()
            text_extraction.document_reference_uid = obj["text_extraction"]["document_reference_uid"]
            text_extraction.page = obj["text_extraction"]["page"]
            text_extraction.block = obj["text_extraction"]["block"]
            text_extraction.char_begin = obj["text_extraction"]["char_begin"]
            text_extraction.char_end = obj["text_extraction"]["char_end"]
            text_parameter.text_extraction = text_extraction
        if "value" in obj:
            value = LiteralValue()
            value.value_type = obj["value"]["value_type"]
            value.value = obj["value"]["value"]
            text_parameter.value = value
        if "variable_identifier" in obj:
            text_parameter.variable_identifier = obj["variable_identifier"]

        return text_parameter
    return None