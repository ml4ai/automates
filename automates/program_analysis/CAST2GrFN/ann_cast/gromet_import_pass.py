import json
from automates.model_assembly.gromet.model import (
    FunctionType,    
    GrometBoxConditional,
    GrometBoxFunction,
    GrometBoxLoop,
    GrometBox,
    GrometFNModule,
    GrometFN,
    GrometPort,
    GrometWire,
    LiteralValue,
)
from automates.utils.fold import dictionary_to_gromet_json, del_nulls
from automates.model_assembly.gromet.model.gromet_type import GrometType
from automates.model_assembly.gromet.model.typed_value import TypedValue

class GrometImportPass:
    def __init__(self, path):
        self.path = path
        self.json_string = None
        self.json_object = None

        self.box_functions = ["b", "bf"]
        self.ports = ["opi", "opo", "pil", "pol", "pif", "pof", "pic", "poc"]
        self.wires = ["wopio", "wlopi", "wll", "wlf", "wlc", "wlopo", "wfopi", "wfl", "wff", "wfc", "wfopo", "wcopi", "wcl", "wcf", "wcc", "wcopo"]
       
        self.gromet_module = None

        self.load_file()
        
        self.import_module()
        self.import_attributes()
        
        self.export()

    def import_module(self):
        # Create module 
        name = self.json_object["name"]
        self.gromet_module = GrometFNModule(name)
        
        # Create the function networt
        self.gromet_module.fn = self.parse_function_network(self.json_object["fn"])
        
    def import_attributes(self):
        for fn in self.json_object["attributes"]:
             # TODO: Add support for types other than FN
            type = fn["type"]
            value = TypedValue(type="FN", value=self.parse_function_network(fn["value"]))
            
            if not self.gromet_module.attributes:
                self.gromet_module.attributes = [value]
            else:
                self.gromet_module.attributes.append(value)

    def parse_function_network(self, obj):
        # Create function_network object
        function_network = GrometFN()

        for table,contents in obj.items():
            # Move to next table if this one is empty
            table_size = len(table)
            if table_size == 0:
                continue
            if table in self.box_functions:
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
                    
                    # TODO: Value field is a little more complex to import
                    #if "value" in entry:
                        #gromet_box_funciton_value =
                    
                    # We use getattr/setattr to set attribute, since we only have the attribute as a string
                    try:
                        current_attribute = getattr(function_network, table)
                    except:
                        current_attribute = None
                    if current_attribute:
                        current_attribute.append(gromet_box_function)
                    else:
                        setattr(function_network, table, [gromet_box_function])
                
            elif table in self.ports:
                for entry in contents:
                    gromet_port = GrometPort()
                    if "id" in entry:
                        gromet_port.id = entry["id"]
                    if "name" in entry:
                        gromet_port.name = entry["name"]
                    if "box" in entry:
                        gromet_port.box = entry["box"]
                    
                    try:
                        current_attribute = getattr(function_network, table)
                    except:
                        current_attribute = None
                    if current_attribute:
                        current_attribute.append(gromet_port)
                    else:
                        setattr(function_network, table, [gromet_port])

            elif table in self.wires:
                for entry in contents:
                    gromet_wire = GrometWire()
                    
                    if "src" in entry:
                        gromet_wire.src = entry["src"]
                    if "tgt" in entry:
                        gromet_wire.tgt = entry["tgt"]
                    
                    try:
                        current_attribute = getattr(function_network, table)
                    except:
                        current_attribute = None
                    if current_attribute:
                        current_attribute.append(gromet_wire)
                    else:
                        setattr(function_network, table, [gromet_wire])
        return function_network

    def load_file(self):
        with open(self.path) as f:
            self.json_string = f.read()
        self.json_object = json.loads(self.json_string)
    def export(self):
        print(dictionary_to_gromet_json(del_nulls(self.gromet_module.to_dict())))

p = GrometImportPass("CHIME_SIR_get_growth_rate--Gromet-FN-auto.json")