graph = \
    {"V": [{}, {}, {}],
     "E": [{"src": 1, "tgt": 2},
           {"src": 2, "tgt": 3},
           {"src": 1, "tgt": 3}]}

uwd = \
    {"Box": [{}, {}],
     "Port": [{"box": 1, "junction": 1},
              {"box": 1, "junction": 2},
              {"box": 2, "junction": 2},
              {"box": 2, "junction": 3}],
     "OuterPort": [],
     "Junction": [{}, {}, {}]}

tuwd = \
    {"Box": [{}, {}],
     "Port": [{"box": 1, "junction": 1, "port_type": "A"},
              {"box": 1, "junction": 2, "port_type": "B"},
              {"box": 2, "junction": 2, "port_type": "B"},
              {"box": 2, "junction": 3, "port_type": "C"}],
     "OuterPort": [],
     "Junction": [{"junction_type": "A"},
                  {"junction_type": "B"},
                  {"junction_type": "C"}]}

dwd = \
    {"Box": [{"value": "f", "box_type": "X"},
             {"value": "g", "box_type": "X"},
             {"value": "h", "box_type": "X"}],
     "InPort": [{"in_port_box": 2, "in_port_type": "X"},
                {"in_port_box": 2, "in_port_type": "X"},
                {"in_port_box": 3, "in_port_type": "X"}],
     "OutPort": [{"out_port_box": 1, "out_port_type": "X"},
                 {"out_port_box": 2, "out_port_type": "X"},
                 {"out_port_box": 3, "out_port_type": "X"}],
     "OuterInPort": [],
     "OuterOutPort": [],
     "Wire": [{"src": 1, "tgt": 1, "wire_value": "x"},
              {"src": 1, "tgt": 3, "wire_value": "y"},
              {"src": 2, "tgt": 2, "wire_value": "z"},
              {"src": 3, "tgt": 1, "wire_value": "ω"}],
     "InWire": [], "OutWire": [], "PassWire": []}

bg = \
    {"V₁": [{}, {}],
     "V₂": [{}, {}, {}],
     "E₁₂": [{"src₁": 1, "tgt₂": 1},
             {"src₁": 1, "tgt₂": 2},
             {"src₁": 2, "tgt₂": 2},
             {"src₁": 2, "tgt₂": 3}],
     "E₂₁": [{"src₂": 3, "tgt₁": 1}]}
