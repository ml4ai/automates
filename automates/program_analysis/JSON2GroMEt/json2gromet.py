import json
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

from automates.model_assembly.gromet.model.gromet_type import GrometType
from automates.model_assembly.gromet.model.typed_value import TypedValue
 
def JsonToGromet(path):
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
                    condition = entry["condition"][0]
                    gromet_conditional.condition = [GrometBoxFunction(function_type=condition["function_type"], contents=condition["contents"])]

                    body_if = entry["body_if"][0]
                    gromet_conditional.body_if = [GrometBoxFunction(function_type=body_if["function_type"], contents=body_if["contents"])]

                    body_else = entry["body_else"][0]
                    gromet_conditional.body_else = [GrometBoxFunction(function_type=body_else["function_type"], contents=body_else["contents"])]

                    if function_network.bc:
                        function_network.bc.append(gromet_conditional)
                    else:
                        function_network.bc = [gromet_conditional]
            elif table == "bl":
                for entry in contents:
                    gromet_loop = GrometBoxLoop()
                    #bl has two components: condition and body
                    condition = entry["condition"]
                    gromet_loop.condition = [GrometBoxFunction(function_type=condition["function_type"], contents=condition["contents"])]

                    body = entry["body"]
                    gromet_loop.body = [GrometBoxFunction(function_type=body["function_type"], body=condition["contents"])]

                    if function_network.bc:
                        function_network.bc.append(gromet_conditional)
                    else:
                        function_network.bc = [gromet_conditional]  
            elif table.startswith("p") or table.startswith("o"):
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
                    
                    try:
                        current_attribute = getattr(function_network, table)
                        current_attribute.append(gromet_wire)
                    except:
                        setattr(function_network, table, [gromet_wire])
        return function_network