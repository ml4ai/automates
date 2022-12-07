import json

from automates.gromet.fn import (
    GrometBoxConditional,
    GrometBoxFunction,
    GrometBoxLoop,
    GrometFNModule,
    GrometFN,
    GrometPort,
    GrometWire,
    GrometFNModuleCollection,
    LiteralValue,
)
from automates.gromet.metadata import (
    Provenance,
    SourceCodeReference,
    SourceCodeDataType,
    SourceCodeLoopInit,
    SourceCodeLoopUpdate,
    SourceCodeComment,
    TextualDocumentCollection,
    TextualDocumentReference,
    TextDescription,
    TextGrounding,
    TextUnits,
    TextLiteralValue,
    EquationDefinition,
    EquationExtraction,
    EquationLiteralValue,
    TextExtraction,
    GrometCreation,
    SourceCodeCollection,
    CodeFileReference,
    SourceCodePortDefaultVal,
    SourceCodePortKeywordArg,
    ProgramAnalysisRecordBookkeeping

)
from automates.gromet.fn import TypedValue, ImportReference

def json_to_gromet(path):
    # Read JSON from file
    with open(path) as f:
        json_string = f.read()
    json_object = json.loads(json_string)

    # Create top level module collectio
    gromet_collection = GrometFNModuleCollection()
    import_basic_datatypes(json_object, gromet_collection)
    
    # Since module_index and executables are lists, they are not imported automatically
    # and need to be imported manually at this point
    gromet_collection.module_index = json_object["module_index"]
    gromet_collection.executables = json_object["executables"] 

    for module in json_object["modules"]:
        # Creat Module object
        gromet_module = GrometFNModule()
            
        # Create the function network for top level module
        gromet_module.fn = parse_function_network(module["fn"])

        # Import Attributes
        for fn in module["attributes"]:
            type = fn["type"]
            if type == "FN":
                value = TypedValue(type=type, value=parse_function_network(fn["value"]))
            elif type == "IMPORT":
                value = TypedValue(type=type, value=parse_import_reference(fn["value"]))

            if not gromet_module.attributes:
                gromet_module.attributes = [value]
            else:
                gromet_module.attributes.append(value)

        # Import Metadata
        for collection in module["metadata_collection"]:
            gromet_metadata_collection = []
            for metadata in collection:
                gromet_metadata_collection.append(parse_metadata(metadata))
            
            if not gromet_module.metadata_collection:
                gromet_module.metadata_collection = [gromet_metadata_collection]
            else:
                gromet_module.metadata_collection.append(gromet_metadata_collection)
        
        # Import basic data type fields
        import_basic_datatypes(module, gromet_module)
        
        # Add module to collection
        if not gromet_collection.modules:
            gromet_collection.modules = [gromet_module]
        else:
            gromet_collection.modules.append(gromet_module)

    return gromet_collection


def parse_function_network(obj):
        # Create function_network object
        function_network = GrometFN()

        for table,contents in obj.items():
            # Move to next table if this one is empty
            table_size = len(table)
            if table_size == 0:
                continue
            
            gromet_object = None
            for entry in contents:
                if table == "b" or table == "bf":
                    # We create a blank box function first and fill out fields later,
                    # since not all box functions will have all fields 
                    gromet_object = GrometBoxFunction()

                    # Some objects will have to be manually imported still
                    if "value" in entry:
                        try:
                            gromet_object.value = LiteralValue(value_type=entry["value"]["value_type"], value=entry["value"]["value"])
                        except:
                            print("HERE", entry)
                elif table == "bc":
                    gromet_object = GrometBoxConditional()
                elif table == "bl":
                    gromet_object = GrometBoxLoop()
                elif table.startswith("p") or table.startswith("o"):
                    gromet_object = GrometPort()
                elif table.startswith("w"):
                    gromet_object = GrometWire()

                # To generalize some of the import, basic data type fields are imported automatically.
                # So even if the schema changes, we won't have to update the importer
                import_basic_datatypes(entry, gromet_object)
                
                # We use getattr/setattr to set attribute, since we only have the attribute as a string
                try:
                    current_attribute = getattr(function_network, table)
                    current_attribute.append(gromet_object)
                except:
                    setattr(function_network, table, [gromet_object])

        return function_network


def parse_metadata(obj):
    metadata_type_map = {
        "source_code_reference": SourceCodeReference,
        "source_code_data_type": SourceCodeDataType,
        "source_code_loop_init": SourceCodeLoopInit,
        "source_code_loop_update": SourceCodeLoopUpdate,
        "source_code_port_keyword_arg": SourceCodePortKeywordArg,
        "source_code_port_default_val": SourceCodePortDefaultVal,
        "program_analysis_record_bookkeeping": ProgramAnalysisRecordBookkeeping,
        "source_code_comment": SourceCodeComment,
        "gromet_creation": GrometCreation,
        "source_code_collection": SourceCodeCollection,
        "textual_document_collection": TextualDocumentCollection,
        "equation_definition": EquationDefinition,
        "equation_parameter": EquationLiteralValue,
        "text_definition": TextDescription,
        "text_literal_value": TextLiteralValue,
        "text_units": TextUnits
    }

    # All metadata have a provenance and metadata_type
    provenance = Provenance(method=obj["provenance"]["method"], timestamp=obj["provenance"]["timestamp"])
    metadata_type = obj["metadata_type"]

    # Create metadata object using metadata type map
    metadata_object = metadata_type_map[metadata_type](metadata_type=metadata_type, provenance=provenance)

    # Load type specific data for types that have object fields. 
    # Types that only contain basic data type fields will be created automatically
    if metadata_type == "source_code_collection":
        
        if "files" in obj: 
            #SourceCodeCollection.files is a list of CodeFileReference objects
            metadata_object.files = []
            for file in obj["files"]:
                code_file_reference = CodeFileReference()
                import_basic_datatypes(file, code_file_reference)
                metadata_object.files.append(code_file_reference) 
       
    elif metadata_type == "program_analysis_record_bookkeeping":
        if "field_declarations" in obj:
            metadata_object.field_declarations = obj["field_declarations"]
        if "method_declarations" in obj:
            metadata_object.method_declarations = obj["method_declarations"]
            
    elif metadata_type == "textual_document_collection":
        
        if "documents" in obj:
            # TextualDocumentCollection.documents is a list of TextualDocumentReference objects
            metadata_object.documents = []
            for document in obj["documents"]:
                textual_document_reference = TextualDocumentReference()
                import_basic_datatypes(document, textual_document_reference)
                
                # TODO: ADD BIBJSON field
                # bibjson field is a bibjson object
                #if "bibjson" in d:
                #    textual_document_reference._skema_id = d["skema_id"]
                metadata_object.documents.append(textual_document_reference)
        
    elif metadata_type == "equation_definition":

        if "equation_extraction" in obj:
            metadata_object.equation_extraction = EquationExtraction()
            import_basic_datatypes(obj["equation_extraction"], metadata_object.equation_extraction)

    elif metadata_type == "equation_literal_value":
        
        if "equation_extraction" in obj:
            metadata_object.equation_extraction = EquationExtraction()
            import_basic_datatypes(obj["equation_extraction"], metadata_object.equation_extraction)
        if "value" in obj:
            metadata_object.value = LiteralValue()
            import_basic_datatypes(obj["value"], metadata_object.value)

    elif metadata_type == "text_description":

        if "text_extraction" in obj:
            metadata_object.text_extraction = TextExtraction()
            import_basic_datatypes(obj["text_extraction"], metadata_object.text_extraction)
        if "grounding" in obj:
            metadata_object.grounding = []
            for entry in obj["grounding"]:
                grounding = TextGrounding()
                import_basic_datatypes(entry, grounding)
                metadata_object.grounding.append(grounding)
    
    elif metadata_type == "text_literal_value":
        if "text_extraction" in obj:
            metadata_object.text_extraction = TextExtraction()
            import_basic_datatypes(obj["text_extraction"], metadata_object.text_extraction)
        if "grounding" in obj:
            metadata_object.grounding = []
            for entry in obj["grounding"]:
                grounding = TextGrounding()
                import_basic_datatypes(entry, grounding)
                metadata_object.grounding.append(grounding)
        if "value" in obj:
            metadata_object.value = LiteralValue()
            import_basic_datatypes(obj["value"], metadata_object.value)
    
    elif metadata_type == "text_units":
        if "text_extraction" in obj:
            metadata_object.text_extraction = TextExtraction()
            import_basic_datatypes(obj["text_extraction"], metadata_object.text_extraction)
        if "grounding" in obj:
            metadata_object.grounding = []
            for entry in obj["grounding"]:
                grounding = TextGrounding()
                import_basic_datatypes(entry, grounding)
                metadata_object.grounding.append(grounding)

    # Import remaining metadata fields of basic type
    import_basic_datatypes(obj, metadata_object)
    
    return metadata_object


def parse_import_reference(obj):
    import_object = ImportReference()
    
    import_basic_datatypes(obj, import_object)
    
    if "uri" in obj:
        import_object.uri = TypedValue()
        import_basic_datatypes(obj["uri", import_object.uri]) 
        # TODO: Potentially fill out uri.value type for typed value

    return import_object

def import_basic_datatypes(obj, gromet_obj):
    for field, value in obj.items():
        if type(value) != list and type(value) != dict:                         
            setattr(gromet_obj, field, value)

        # TODO: Make this only print when there is an unhandled case
        #else:
        #    print(f"Could not automatically import field: {field}. Make sure it is being manually imported")
