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

class GrometImportPass:
    def __init__(self, path):
        self.path = path
        self.json_string = None
        self.json_object = None

        self.box_functions = ["b", "bf"]
        self.ports = ["pof", "pif", "opo", "opi"]
        self.wires = ["wfopo"]
       
        self.gromet_module_fn = None

        self.load_file()
        self.import_module()
        self.export()
    def import_module(self):
        # Create module 
        name = self.json_object["name"]
        self.gromet_module_fn = GrometFNModule(name)
        
        # Create function network for module
        self.gromet_module_fn.fn = GrometFN()
        for table,contents in self.json_object["fn"].items():
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
                        current_attribute = getattr(self.gromet_module_fn.fn, table)
                    except:
                        current_attribute = None
                    if current_attribute:
                        current_attribute.append(gromet_box_function)
                    else:
                        setattr(self.gromet_module_fn.fn, table, [gromet_box_function])
                
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
                        current_attribute = getattr(self.gromet_module_fn.fn, table)
                    except:
                        current_attribute = None
                    if current_attribute:
                        current_attribute.append(gromet_port)
                    else:
                        setattr(self.gromet_module_fn.fn, table, [gromet_port])

            elif table in self.wires:
                for entry in contents:
                    gromet_wire = GrometWire()

                    if "tgt" in entry:
                        gromet_port.src = entry["src"]
                    if "src" in entry:
                        gromet_port.tgt = entry["tgt"]
                    
                    try:
                        current_attribute = getattr(self.gromet_module_fn.fn, table)
                    except:
                        current_attribute = None
                    if current_attribute:
                        current_attribute.append(gromet_wire)
                    else:
                        setattr(self.gromet_module_fn.fn, table, [gromet_wire])
           
    def load_file(self):
        with open(self.path) as f:
            self.json_string = f.read()
        self.json_object = json.loads(self.json_string)
    def export(self):
        print(dictionary_to_gromet_json(del_nulls(self.gromet_module_fn.to_dict())))

p = GrometImportPass("exp0--Gromet-FN-auto.json")