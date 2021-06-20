# %%[markdown]
# Author: Clayton T. Morrison
# Email: [claytonm@arizona.edu](mailto:claytonm@arizona.edu)
# Adapted from initial version by: Nelson Liu
# Email: [nliu@uncharted.software](mailto:nliu@uncharted.software)

import json
from collections import defaultdict
import argparse
import os


def debug(objs):
    """
    Quick-n-dirty helper for summarizing validator 'objects' dictionary contents
    :param objs:
    :return:
    """
    print("=" * 50)
    print('DEBUG:')
    for k in objs:
        print(k)
        if type(objs[k]) is dict:
            for uid in objs[k]:
                print(f'  {uid}: {objs[k][uid]}')
        elif type(objs[k]) is list or type(objs[k]) is set:
            print(f'  {len(objs[k])}: {objs[k]}')
        else:
            print(f'  {objs[k]}')


def validate(gromet):

    print('-' * 50)
    print(f"Validating GroMEt '{gromet['uid']}' ({gromet['type']})...")

    # ---------------------------------------------------------------------
    # Extract gromet components
    # ---------------------------------------------------------------------

    objects = {}
    for k in ('variables', 'boxes', 'wires', 'junctions', 'ports'):
        objects[k] = {}
        if gromet[k] is not None:
            objects[k] = {**objects[k], **{obj['uid']: obj for obj in gromet[k]}}
    objects['nodes'] = {**objects['ports'], **objects["junctions"]}

    # Collect index of Wires by their end-points
    wires_by_src_id = defaultdict(lambda: set())
    wires_by_tgt_id = defaultdict(lambda: set())
    for w_id, wire in objects['wires'].items():
        wires_by_src_id[wire['src']].add(w_id)
        wires_by_tgt_id[wire['tgt']].add(w_id)
    objects['wires_by_src_id'] = wires_by_src_id
    objects['wires_by_tgt_id'] = wires_by_tgt_id

    # Collect box_ids called by a BoxCall)
    #     and box_ids for Expression Boxes
    called_by_boxcall = set()
    expression_boxes = set()
    conditional_boxes = set()
    conditional_branch_boxes = set()
    for b_id, box in objects['boxes'].items():
        if box['syntax'] == 'BoxCall':
            called_by_boxcall.add(box['call'])
        if box['syntax'] == 'Expression':
            expression_boxes.add(b_id)
        if box['syntax'] == 'Conditional':
            conditional_boxes.add(b_id)
            # NOW that branches no longer have in-lined Boxes, this is not necessary...
            # for cond, body in box['branches']:
            #     if cond is not None:
            #         print(f'>>> cond: {cond}')
            #         conditional_boxes.add(cond['uid'])
            #     if body is not None:
            #         conditional_boxes.add(body['uid'])
            for cond_id, body_id in box['branches']:
                if cond_id is not None:
                    conditional_branch_boxes.add(cond_id)
                if body_id is not None:
                    conditional_branch_boxes.add(body_id)
    objects['called_by_boxcall'] = called_by_boxcall
    objects['expression_boxes'] = expression_boxes
    objects['conditional_boxes'] = conditional_boxes
    objects['conditional_branch_boxes'] = conditional_branch_boxes

    # Collect box_ids called by Expression Expr tree calls
    called_by_expr = set()
    for b_id in objects['expression_boxes']:
        box = objects['boxes'][b_id]
        expr = box['tree']
        called_by_expr |= collect_expr_refbox_calls(expr)
    objects['called_by_expr'] = called_by_expr

    # Any Boxes that are called (by either BoxCall or Expr call)
    objects['called_boxes'] = objects['called_by_boxcall'] | objects['called_by_expr']

    # print(f">>>> objects['called_by_boxcall']: {objects['called_by_boxcall']}")
    # print(f">>>> objects['called_by_expr']:    {objects['called_by_expr']}")
    # print(f">>>> objects['called_boxes']:      {objects['called_boxes']}")
    # print(f">>>> objects['expression_boxes']:  {objects['expression_boxes']}")
    # print(f">>>> objects['conditional_boxes']:  {objects['conditional_boxes']}")

    # -- Extract metadata per Metadatum type --

    for k in ('variables', 'boxes', 'wires', 'junctions', 'ports'):
        for elm in objects[k]:
            box = objects[k][elm]
            if box['metadata'] is not None:
                # print('>'*50)
                # print('> FOUND METADATA')
                # print('>'*50)
                for datum in box['metadata']:
                    metadata_type = f"metadata_{k}_{datum['metadata_type']}"
                    if metadata_type not in objects:
                        objects[metadata_type] = [datum]
                    else:
                        objects[metadata_type].append(datum)
    # gromet metadata:
    if gromet['metadata'] is not None:
        for datum in gromet['metadata']:
            metadata_type = f"metadata_gromet_{datum['metadata_type']}"
            if metadata_type not in objects:
                objects[metadata_type] = [datum]
            else:
                objects[metadata_type].append(datum)


    # TODO types: TypeDeclaration
    # TODO literals: Literal

    # tests: (ensure only in <...>)
    # CodeSpanReference
    #   <Any>
    #   file_id exists in gromet.CodeCollectionReference CodeFileReference
    # ModelInterface
    #   <Gromet>
    #   variables, parameters and initial_conditions exist
    #   BL:
    #     variables: All State, Flux, Tangent Junctions
    #     parameters: All Flux Junctions
    #     initial_conditions: All State Junctions
    #   PNC:
    #     variables: All State and Rate Junctions
    #     parameters: All Rate Junctions
    #     initial_conditions: All State Junctions
    #   FN: Inferred or user-defined
    # TextualDocumentReferenceSet
    #   <Gromet>
    # CodeCollectionReference
    #   <Gromet>
    # EquationDefinition
    #   <Box>
    #   has EquationExtraction (see below)
    # TextDefinition
    #   <Variable>
    #   has TextExtraction (see below)
    # TexParameter
    #   <Variable>
    #   has TextExtraction (see below)
    # EquationParameter
    #   <Variable>
    #   has EquationExtraction (see below)

    # TextExtraction
    #   document_reference_uid exists in gromet.TextualDocumentReferenceSet TextualDocumentReference
    # EquationExtraction
    #   document_reference_uid exists in gromet.CodeCollectionReference CodeFileReference

    # ReactionReference
    #   should only be associated with PNC Rate Junction
    # IndraAgentReferenceSet
    #   should only be associated with PNC State Junction

    # -- Extract object uids --

    # Literal
    # Junction
    # Port
    # Wire
    # Box
    # Variable
    # Gromet

    # ---------------------------------------------------------------------
    # General Tests:
    # ---------------------------------------------------------------------

    # Test: Wire src and tgt have corresponding Port/Junction definitions
    for w_id, wire in objects['wires'].items():
        for k in ('src', 'tgt'):
            if wire[k] not in objects['nodes']:
                print(f"Error: Wire'{w_id}'"
                      f" has {k}={wire[k]} not found in node set.")

    # Test: Variable states exist in Nodes (Ports, Junctions) or Wires
    for v_id, variable in objects['variables'].items():
        if set(variable['states']) \
                <= (set(objects['nodes'].keys()) | set(objects['wires'].keys())):
            pass
        else:
            # (make error more targeted)
            node_set = set(objects['nodes'].keys()) | set(objects['wires'].keys())
            for s in variable['states']:
                if s not in node_set:
                    print(f"Error: Variable '{v_id}'"
                          f" has state '{s}' missing from Ports, Junctions and Wires")

    # Test: parent Box of Ports exists
    for p_id, port in objects['ports'].items():
        if port['box'] not in objects['boxes']:
            print(f"Error: Parent Box of Port '{p_id}'"
                  f" is missing from list of Boxes.")

    # Test: Box contents have been defined
    for b_id, box in objects['boxes'].items():
        for k in ('ports', 'wires', 'boxes', 'junctions'):
            if k in box.keys():
                if box[k] is not None:
                    if set(box[k]) <= set(objects[k].keys()):
                        pass
                    else:
                        # (make error more targeted)
                        elems = set(objects[k].keys())
                        for elm_name in box[k]:
                            if elm_name not in elems:
                                print(f"Error: Box '{b_id}'"
                                      f" names '{elm_name}' in {k},"
                                      f" but not found in {k} definitions.")

    # Test: BoxCall must call a defined Box
    for b_id, box in objects['boxes'].items():
        box_ids = set(objects['boxes'].keys())
        if box['syntax'] == 'BoxCall' and box['call'] not in box_ids:
            print(f"Error: BoxCall '{b_id}'"
                  f" calls undefined Box '{box['call']}'.")

    # Test: PortCall must call a defined Port
    for p_id, port in objects['ports'].items():
        port_names = set(objects['ports'].keys())
        if port['syntax'] == 'PortCall' and port['call'] not in port_names:
            print(f"Error: PortCall '{p_id}'"
                  f" calls undefined Port '{port['call']}'.")

    # ---------------------------------------------------------------------
    # Test: Conditional
    # ---------------------------------------------------------------------
    # For each branch
    #    first box (branch condition):
    #    (1) is Predicate or None -- None is only possible in the Last branch
    #    (2) all PortInput ports are
    #           (a) syntax PortCalls
    #           (b) that reference outer condition PortInput port
    #    (3) PortOutput port:
    #           (a) must be exactly 1
    #           (b) syntax Port
    #           (c) value_type Boolean
    #    second box (branch body):
    #    (4) is Expression or Function or None (None is a 'pass')
    #    (5) All ports must be PortCalls
    #    (6) all PortInput ports reference outer condition PortInput ports
    #    (7) all PortOutput ports reference outer condition PortOutput port
    # (8) Every branch body Box PortOutput has a PortCall
    #           that calls the same PortOutput Port as every other Port output
    for c_id in objects['conditional_boxes']:
        conditional_box = objects['boxes'][c_id]
        num_branches = len(conditional_box['branches'])

        body_ids = set()
        called_ports_called_by_branch_body = defaultdict(lambda: set())

        for i, (cond_id, body_id) in enumerate(conditional_box['branches']):
            if cond_id is None:
                if i < num_branches - 1:
                    # (1a) Condition cannot be None unless in the last branch
                    print(f"Error [Cond 1a]: condition of branch {i} in Conditional '{c_id}'"
                          f" is None but is not the last branch.")
            else:
                cond_box = objects['boxes'][cond_id]
                if cond_box['syntax'] != 'Predicate':
                    # (1b) Condition must be a Predicate
                    print(f"Error [Cond 1b]: condition '{cond_id}' in branch {i} of Conditional '{c_id}'"
                          f" is syntax '{cond_box['syntax']}', but should be a Predicate.")
                output_ports = list()  # collect output_ports
                for p_id in cond_box['ports']:
                    if p_id in objects['ports']:
                        cond_port = objects['ports'][p_id]
                        if cond_port['type'] == 'PortInput':
                            if cond_port['syntax'] != 'PortCall':
                                # (2a) Condition's ports must be PortCalls
                                print(f"Error [Cond 2a]: condition '{cond_id}' in branch {i} of Conditional '{c_id}'"
                                      f" is a '{cond_port['syntax']}' but must be a PortCall.")
                            else:
                                if cond_port['call'] not in conditional_box['ports']:
                                    # (2b.1) Condition's PortCall calls a Port not found in Conditional
                                    print(f"Error [Cond 2b.1]: condition '{cond_id}' in branch {i} of Conditional '{c_id}'"
                                          f" calls '{cond_port['call']}' but not found in '{c_id}'s ports")
                                else:
                                    called_port = objects['ports'][cond_port['call']]
                                    if called_port['type'] != 'PortInput':
                                        # (2b.2) Condition's PortCall calls a Port that is not type PortInput
                                        print(f"Error [Cond 2b.2]: condition '{cond_id}' in branch {i} of Conditional '{c_id}'"
                                              f" calls '{cond_port['call']}' that is type '{called_port['type']}'"
                                              f" but should be type PortInput.")
                        elif cond_port['type'] == 'PortOutput':
                            output_ports.append(p_id)
                if len(output_ports) != 1:
                    # (3a) There is just one output port
                    print(f"Error [Cond 3a]: condition '{cond_id}' in branch {i} of Conditional '{c_id}'"
                          f" must have exactly 1 output_port, but has: {output_ports}.")
                else:
                    output_port_id = output_ports[0]
                    if output_port_id in objects['ports'][output_port_id]:
                        output_port = objects['ports'][output_port_id]
                        if output_port['syntax'] != 'Port':
                            # (3b) output port must be syntax Port
                            print(f"Error [Cond 3b]: condition '{cond_id}' in branch {i} of Conditional '{c_id}'"
                                  f" is syntax '{output_port['syntax']}' but must be syntax Port.")
                        if output_port['value_type'] != 'Boolean':
                            # (3c) output port must have value_type Boolean
                            print(f"Error [Cond 3c]: condition '{cond_id}' in branch {i} of Conditional '{c_id}'"
                                  f" is value_type '{output_port['value_type']}' but must be value_type Boolean.")

            if body_id is not None:
                body_ids.add(body_id)
                if body_id in objects['boxes']:
                    body_box = objects['boxes'][body_id]
                    if body_box['syntax'] != 'Expression' and body_box['syntax'] != 'Function':
                        # (4) branch body must be Expression or Function
                        print(f"Error [Cond 4]: condition '{body_id}' in branch {i} of Conditional '{c_id}'"
                              f" is syntax '{body_box['syntax']}' but must be either Expression or Function.")
                    for p_id in body_box['ports']:
                        body_port = objects['ports'][p_id]
                        if body_port['syntax'] != 'PortCall':
                            # (5) branch body ports must be PortCalls
                            print(f"Error [Cond 5]: condition '{body_id}' in branch {i} of Conditional '{c_id}'"
                                  f" has port '{p_id}' that is type '{body_box['syntax']}' but must be PortCall.")
                        else:
                            if body_port['type'] == 'PortInput':
                                if body_port['call'] not in conditional_box['ports']:
                                    # (6a) branch body PortInput PortCall calls an existing Conditional port
                                    print(f"Error [Cond 6a]: condition '{body_id}' in branch {i}"
                                          f" of Conditional '{c_id}'"
                                          f" has PortInput port '{p_id}' that calls port '{body_port['call']}'"
                                          f" but not found in '{c_id}'s ports.")
                                else:
                                    called_port = objects['ports'][body_port['call']]
                                    if called_port['type'] != 'PortInput':
                                        # (6b) the called port must be a PortInput
                                        print(f"Error [Cond 6b]: condition '{body_id}' in branch {i}"
                                              f" of Conditional '{c_id}'"
                                              f" has port '{p_id}' that cals port '{body_port['call']}'"
                                              f" that is type '{called_port['type']}', but it must be type PortInput.")
                            elif body_port['type'] == 'PortOutput':
                                if body_port['call'] not in conditional_box['ports']:
                                    # (7a) branch body PortOutput PortCall calls an existing Conditional port
                                    print(f"Error [Cond 7a]: condition '{body_id}' in branch {i}"
                                          f" of Conditional '{c_id}'"
                                          f" has PortOutput port '{p_id}' that calls port '{body_port['call']}'"
                                          f" but not found in '{c_id}'s ports.")
                                else:
                                    called_port = objects['ports'][body_port['call']]
                                    if called_port['type'] != 'PortOutput':
                                        # (7b) the called port must be a PortOutput
                                        print(f"Error [Cond 7b]: condition '{body_id}' in branch {i}"
                                              f" of Conditional '{c_id}'"
                                              f" has port '{p_id}' that cals port '{body_port['call']}'"
                                              f" that is type '{called_port['type']}', but it must be type PortOutput.")
                                    called_ports_called_by_branch_body[called_port['uid']].add(body_id)
                            else:
                                print(f"Error [Cond x]: condition '{body_id}' in branch {i}"
                                      f" of Conditional '{c_id}'"
                                      f" has port '{p_id}' that cals port '{body_port['call']}'"
                                      f" that is type '{called_port['type']}', but it must be either "
                                      f" type PortInput or PortOutput.")

        # collect all Conditional PortOutputs
        cond_output_ports = set()
        for p_id in conditional_box['ports']:
            if p_id in objects['ports']:
                if objects['ports'][p_id]['type'] == 'PortOutput':
                    cond_output_ports.add(p_id)

        for called_port_id, called_by_branch_body_set in called_ports_called_by_branch_body.items():
            if body_ids != called_by_branch_body_set:
                # (8a) Every Conditional PortOutput is called by a corresponding
                #      PortOutput of *each* (non-None -- i.e., non-pass) branch body
                cond_ports_not_called_by_branch_bodies = body_ids - called_by_branch_body_set
                print(f"Error [Cond 8a]: Conditional '{c_id}'"
                      f" has PortOutput Port '{called_port_id}'...\n"
                      f"    not called by branches: {cond_ports_not_called_by_branch_bodies}\n"
                      f"    (that should be empty)")

        output_ports_not_called_by_any = cond_output_ports - set(called_ports_called_by_branch_body.keys())
        if output_ports_not_called_by_any:
            # (8b) Every Conditional PortOutput must be called
            print(f"Error [Cond 8b]: Conditional '{c_id}'"
                  " has the following PortOutputs that are not"
                  " called by any of the branch PortOutput PortCalls:\n"
                  f"     {output_ports_not_called_by_any}")

    # ---------------------------------------------------------------------
    # Petri Net Classic (PNC) tests:
    # ---------------------------------------------------------------------

    if gromet['type'] == 'PetriNetClassic':
        junction_types = ('State', 'Rate')
        # Test: Junction types are one of State or Rate
        for j_id, junction in objects['junctions'].items():
            if junction['type'] not in junction_types:
                print(f"Error [PNC]: Junction '{j_id}'"
                      f" is type '{junction['type']}' instead of {junction_types}")
        # Test: Wires connect connect Junctions of the same type
        #       (This version safely checks whether src,tgt Junctions were defined;
        #        if either are not, then will produce redundant Error about missing
        #        definition.)
        for w_id, wire in objects['wires'].items():
            src_junction = None
            tgt_junction = None
            if wire['src'] not in objects['junctions']:
                print(f"Error [PNC]: Wire '{w_id}'"
                      f" references src '{wire['src']}' not found in defined junctions.")
            else:
                src_junction = objects['junctions'][wire['src']]
            if wire['tgt'] not in objects['junctions']:
                print(f"Error [PNC]: Wire '{w_id}'"
                      f" references tgt '{wire['tgt']}' not found in defined junctions.")
            else:
                tgt_junction = objects['junctions'][wire['tgt']]
            if src_junction is not None and tgt_junction is not None\
                    and src_junction['type'] == tgt_junction['type']:
                print(f"Error [PNC]: Wire '{w_id}'"
                      f" connects src and tgt Junctions of the same type: '{src_junction['type']}'.")

    # ---------------------------------------------------------------------
    # Bilayer (BL) Tests:
    # ---------------------------------------------------------------------

    if gromet['type'] == 'Bilayer':
        junction_types = ('State', 'Flux', 'Tangent')
        wire_types = ('W_in', 'W_pos', 'W_neg')

        # Test: Junction types are one of State, Flux or Tangent
        for j_id, junction in objects['junctions'].items():
            if junction['type'] not in junction_types:
                print(f"Error [Bilayer]: Junction '{j_id}'"
                      f" is type '{junction['type']}' instead of one of {junction_types}")

        # Test: Wire types connect the right type of Junctions
        for w_id, wire in objects['wires'].items():

            # Test: Wire types are one of W_in, W_pos, W_neg
            if wire['type'] not in wire_types:
                print(f"Error [Bilayer]: Wire '{w_id}'"
                      f" is type '{wire['type']}' instead of {wire_types}")

            src_junction = None
            tgt_junction = None

            # (The following safely checks whether src,tgt Junctions were defined;
            #  if either are not, then will produce redundant Error about missing
            #  definition.)
            if wire['src'] not in objects['junctions']:
                print(f"Error [Bilayer]: Wire '{w_id}'"
                      f" references src '{wire['src']}' not found in defined junctions.")
            else:
                src_junction = objects['junctions'][wire['src']]
            if wire['tgt'] not in objects['junctions']:
                print(f"Error [Bilayer]: Wire '{w_id}'"
                      f" references tgt '{wire['tgt']}' not found in defined junctions.")
            else:
                tgt_junction = objects['junctions'][wire['tgt']]

            if wire['type'] == 'W_in' and src_junction and tgt_junction:

                # Test: W_in Wires only connect from State to Flux Junctions
                if src_junction['type'] == 'State' and tgt_junction['type'] == 'Flux':
                    pass  # OK
                else:
                    print(f"Error [Bilayer]: Wire '{w_id}'"
                          f" is of type '{wire['type']}' and connects"
                          f" src Junction '{src_junction['uid']}' of type '{src_junction['type']}'"
                          f" (must be type State) to"
                          f" tgt Junction '{tgt_junction['uid']}' of type '{tgt_junction['type']}'"
                          f" (must be type Flux).")
            elif wire['type'] == 'W_pos' or wire['type'] == 'W_pos':

                # Test: W_pos and W_neg only connect from Flux to Tangent Junctions
                if src_junction['type'] == 'Flux' and tgt_junction['type'] == 'Tangent':
                    pass  # OK
                else:
                    print(f"Error [Bilayer]: Wire '{w_id}'"
                          f" is of type '{wire['type']}' and connects"
                          f" src Junction '{src_junction['uid']}' of type '{src_junction['type']}'"
                          f" (must be type State) to"
                          f" tgt Junction '{tgt_junction['uid']}' of type '{tgt_junction['type']}'"
                          f" (must be type Flux).")

    # ---------------------------------------------------------------------
    # Function Network (FN) Tests:
    # ---------------------------------------------------------------------

    if gromet['type'] == 'FunctionNetwork':
        port_types = ('PortInput', 'PortOutput')

        # Test: Port and PortCall types are one of PortInput or PortOutput
        for p_id, port in objects['ports'].items():
            if port['type'] not in port_types:
                print(f"Error [FN]: Port '{p_id}'"
                      f" is type '{port['type']}' instead of one of {port_types}")

        # Test: gromet has a defined root Box
        if gromet['root'] is None:
            print(f"Error [FN root 0a]: root Box not specified ('{gromet['root']}')")
        if gromet['root'] not in objects['boxes']:
            print(f"Error [FN root 0b]: undefined root Box '{gromet['root']}'")
        else:
            # Test: root Box
            #   (1) every input Port must have at least one outgoing Wire
            #   (2) every output port must have only one incoming Wire
            # TODO Abstracted Function Network may have emtpy Boxes
            #      But won't have examples of this before August 2021
            root_box = objects['boxes'][gromet['root']]
            for p_id in root_box['ports']:
                if p_id not in objects['ports']:
                    print(f"Error [FN root 0c]: root Box '{root_box['uid']}' references"
                          f" Port '{p_id}' not found in port definitions.")
                else:
                    port = objects['ports'][p_id]
                    if port['type'] == 'PortInput' and \
                            p_id not in objects['wires_by_src_id']:
                        print(f"Error [FN root 1a]: root Box '{root_box['uid']}' has"
                              f" PortInput type Port '{p_id}'"
                              f" that does not have outgoing Wire.")
                    elif port['type'] == 'PortOutput' and \
                            p_id not in objects['wires_by_tgt_id']:
                        print(f"Error [FN root 1b]: root Box '{root_box['uid']}' had"
                              f" PortOutput type Port '{p_id}'"
                              f" that does not have incoming Wire")

        # Tests:
        # For non-root, non-Expression, non-Conditional and non-called Box (`non_recd_boxes`):
        #   (1) every Port or PortInput PortCall must have only one incoming Wire
        #   (2) every Port or PortOutput PortCall must have at least one outgoing Wire
        #   (3) every PortInput PortCall must have no outgoing Wires
        #   (4) every PortOutput PortCall must have no incoming Wires
        # For non-Expression called Box (`non_exp_called_boxes`)
        #   (5) All called Box Ports must be Port syntax (no PortCalls)
        #   (6) every PortInput must have no incoming Wires and at least one outgoing Wire
        #   (7) every PortOutput must have only one incoming Wire and no outgoing Wires
        # For non-called Expressions (`non_called_expressions`)
        #   (8) All Expression Box Ports must be Port syntax (no PortCalls)
        #   (9) every PortInput must have
        #           only one incoming Wire
        #           cannot have any outgoing Wires
        #   (10) every PortOutput must have
        #           at least one outgoing Wire
        #           cannot have any incoming Wires
        # For called Expressions (`called_expressions`)
        #   (11) PortInput and PortOutput should not have any incoming or outgoing Wires.

        # For non-root, non-Expression, non-Conditional and non-called Box (`non_recc_boxes`):
        non_recc_boxes = [box_id for box_id in objects['boxes']
                          if box_id not in objects['called_boxes']
                          and box_id not in objects['expression_boxes']
                          and box_id not in objects['conditional_boxes']
                          and box_id not in objects['conditional_branch_boxes']
                          and box_id != gromet['root']]
        for b_id in non_recc_boxes:
            box = objects['boxes'][b_id]
            for p_id in box['ports']:
                # don't worry about flagging error if p_id is not found in
                #     objects['ports'] as if missing, this will already have
                #     been flagged in test of defined Ports above...
                if p_id in objects['ports']:
                    port_syntax = objects['ports'][p_id]['syntax']
                    port_type = objects['ports'][p_id]['type']
                    # (1) every Port or PortInput PortCall must have only one incoming Wire
                    if port_syntax == 'Port' or \
                            (port_syntax == 'PortCall' and port_type == 'PortInput'):
                        if p_id not in objects['wires_by_tgt_id']:
                            print(f"Error [FN 1a]: Box '{b_id}' has {port_syntax} '{p_id}'"
                                  f" of type '{port_type}' with no incoming Wire.")
                        elif len(objects['wires_by_tgt_id'][p_id]) != 1:
                            print(f"Error [FN 1b]: Box '{b_id}' has {port_syntax} '{p_id}'"
                                  f" of type '{port_type}' with too many incoming Wires:"
                                  f" {objects['wires_by_tgt_id'][p_id]}.")
                    # (2) every Port or PortOutput PortCall must have at least one outgoing Wire
                    if port_syntax == 'Port' or \
                            (port_syntax == 'PortCall' and port_type == 'PortOutput'):
                        if p_id not in objects['wires_by_src_id']:
                            print(f"Error [FN 2]: Box '{b_id}' has {port_syntax} '{p_id}'"
                                  f" of type '{port_type}' with no outgoing Wire.")
                    # (3) every PortInput PortCall must have no outgoing Wires
                    if port_syntax == 'PortCall' and port_type == 'PortInput':
                        outgoing_wires = objects['wires_by_src_id']
                        if p_id in outgoing_wires:
                            print(f"Error [FN 3]: Box '{b_id}' has {port_syntax} '{p_id}'"
                                  f" of type '{port_type}' with some outgoing Wire:"
                                  f" {outgoing_wires[p_id]}.")
                    # (4) every PortOutput PortCall must have no incoming Wires
                    if port_syntax == 'PortCall' and port_type == 'PortOutput':
                        incoming_wire_ids = objects['wires_by_tgt_id']
                        if p_id in incoming_wire_ids:
                            print(f"Error [FN 4]: Box '{b_id}' has {port_syntax} '{p_id}'"
                                  f" of type '{port_type}' with some outgoing Wire:"
                                  f" {incoming_wire_ids[p_id]}.")

        # For non-Expression called Box (`non_exp_called_boxes`)
        non_exp_called_boxes = objects['called_boxes'] - objects['expression_boxes']
        for b_id in non_exp_called_boxes:
            box = objects['boxes'][b_id]
            for p_id in box['ports']:
                port_syntax = objects['ports'][p_id]['syntax']
                port_type = objects['ports'][p_id]['type']
                # (5) All Box Ports must be Port syntax (no PortCalls)
                if port_syntax != 'Port':
                    print(f"Error [FN 5]: called Box '{b_id}' has a '{port_syntax}'"
                          f" but it should be a Port.")
                # (6) every PortInput must have no incoming Wires and at least one outgoing Wire
                if port_type == 'PortInput':
                    if p_id in objects['wires_by_tgt_id']:
                        print(f"Error [FN 6a]: called Box '{b_id}' has '{port_syntax}'"
                              f" of type '{port_type}' with incoming Wires:"
                              f" {objects['wires_by_tgt_id'][p_id]}"
                              f" -- must have no incoming.")
                    if p_id not in objects['wires_by_src_id']:
                        print(f"Error [FN 6b]: called Box '{b_id}' has '{port_syntax}'"
                              f" of type '{port_type}' with no outgoing Wires"
                              f" -- must have at least one.")
                # (7) every PortOutput must have only one incoming Wire and no outgoing Wires
                if port_type == 'PortOutput':
                    if p_id not in objects['wires_by_tgt_id']:
                        print(f"Error [FN 7a]: called Box '{b_id}' has '{port_syntax}'"
                              f" of type '{port_type}' with no incoming Wires"
                              f" -- must have at just one.")
                    incoming_wire_ids = objects['wires_by_tgt_id'][p_id]
                    if len(incoming_wire_ids) != 1:
                        print(f"Error [FN 7b]: called Box '{b_id}' has '{port_syntax}'"
                              f" of type '{port_type}' with too many incoming Wires:"
                              f" {incoming_wire_ids}"
                              f" -- must have at just one.")

        # For non-called Expressions (`non_called_expressions`)
        non_called_expressions = objects['expression_boxes'] - objects['called_boxes']
        for b_id in non_called_expressions:
            box = objects['boxes'][b_id]
        # TODO
        # (8) All Expression Box Ports must be Port syntax (no PortCalls)
        # (9) every PortInput must have only one incoming Wire
        # (10) every PortOutput must have at least one outgoing Wire

        # TODO This does not currently happen in a FN
        #  Would require PA to recognize that Function is just a wrapper
        #  around an Expression and then "collapse" to a callable Expression
        #  But this provides reuse, e.g., in PrTNets
        # For called Expressions (`called_expressions`)
        called_expressions = objects['expression_boxes'] & objects['called_by_boxcall']
        # (11) PortInput and PortOutput should not have any incoming or outgoing Wires.

        # TODO Test Conditionals

        # TODO Test Loops

        # Test FN Expression structure
        #   (1) all references to Ports in the Expr refer to Expression PortInput Ports
        #   (2) there is just one output Port for the output of the Expression
        for b_id, box in objects['boxes'].items():
            if box['syntax'] == 'Expression':
                port_references = collect_expr_port_references(box['tree'])
                input_ports = set()
                output_ports = set()
                for p_id in box['ports']:
                    if p_id in objects['ports']:
                        p_type = objects['ports'][p_id]['type']
                        if p_type == 'PortInput':
                            input_ports.add(p_id)
                        elif p_type == 'PortOutput':
                            output_ports.add(p_id)
                        else:
                            print(f"Error [FN]: Expression '{b_id}'"
                                  f" has Port '{p_id}' of type {p_type},"
                                  f" but was expecting type 'PortInput' or 'PortOutput'.")
                    else:
                        # this will be redundant to Box contents test...
                        print(f"Error [FN]: Expression '{b_id}'"
                              f" claims Port '{p_id}' that is not defined.")
                if len(output_ports) != 1:
                    print(f"Error [FN]: Expression '{b_id}'"
                          f" has {len(output_ports)} output Ports ({output_ports}),"
                          f" but was expecting only 1.")
                if port_references == input_ports:
                    pass  # OK
                else:
                    inputs_not_referenced = input_ports - port_references
                    if inputs_not_referenced:
                        print(f"Error [FN]: Expression '{b_id}'"
                              f" has the following input Ports that are not referenced: "
                              f" {inputs_not_referenced}.")
                    references_not_in_inputs = port_references - input_ports
                    if references_not_in_inputs:
                        print(f"Error [FN]: Expression '{b_id}'"
                              f" has an Expr tree that makes the following Port reference"
                              f" without matching input Ports: {references_not_in_inputs}.")

    # ---------------------------------------------------------------------
    # Predicate/Transition Network (PrTNet) tests:
    # ---------------------------------------------------------------------
    # TODO

    # debug(objects)

    print('DONE.')


def collect_expr_refbox_calls(expr) -> set:
    box_calls = set()
    if expr['call']['syntax'] == 'RefBox':
        box_calls.add(expr['call']['name'])
    for arg in expr['args']:
        if isinstance(arg, dict) and 'syntax' in arg and arg['syntax'] == 'Expr':
            box_calls |= collect_expr_refbox_calls(arg)
    return box_calls


def test_collect_expr_refbox_calls():
    t = {'syntax': 'Expr',
         'call': {'syntax': 'RefBox', 'name': 'B:Box1'},
         'args': [{'syntax': 'Expr',
                   'call': {'syntax': 'RefOp', 'name': '/'},
                   'args': [{'syntax': 'Expr',
                             'call': {'syntax': 'RefOp', 'name': '*'},
                             'args': [{'syntax': 'Expr',
                                       'call': {'syntax': 'RefBox', 'name': 'B:Box2'},
                                       'args': ['P:infected_exp.in.beta', 'P:infected_exp.in.S', 'P:infected_exp.in.I']},
                                      {'syntax': 'Literal', 'type': 'Int', 'name': None, 'metadata': None, 'uid': None, 'value': {'syntax': 'Val', 'val': '-1'}}]},
                            {'syntax': 'Expr',
                             'call': {'syntax': 'RefBox', 'name': 'B:Box3'},
                             'args': ['P:infected_exp.in.S', 'P:infected_exp.in.I', 'P:infected_exp.in.R']}]},
                  'P:infected_exp.in.dt']}
    bc = collect_expr_refbox_calls(t)
    assert bc == {'B:Box2', 'B:Box1', 'B:Box3'}


test_collect_expr_refbox_calls()


def collect_expr_port_references(expr) -> set:
    port_refs = set()
    for arg in expr['args']:
        if isinstance(arg, str):
            port_refs.add(arg)
        else:
            if isinstance(arg, dict) and 'syntax' in arg and arg['syntax'] == 'Expr':
                port_refs |= collect_expr_port_references(arg)
    return port_refs


def test_collect_expr_port_references():
    t = {'syntax': 'Expr',
         'call': {'syntax': 'RefOp', 'name': '*'},
         'args': [{'syntax': 'Expr',
                   'call': {'syntax': 'RefOp', 'name': '/'},
                   'args': [{'syntax': 'Expr',
                             'call': {'syntax': 'RefOp', 'name': '*'},
                             'args': [{'syntax': 'Expr',
                                       'call': {'syntax': 'RefOp', 'name': '*'},
                                       'args': ['P:infected_exp.in.beta', 'P:infected_exp.in.S', 'P:infected_exp.in.I']},
                                      {'syntax': 'Literal', 'type': 'Int', 'name': None, 'metadata': None, 'uid': None, 'value': {'syntax': 'Val', 'val': '-1'}}]},
                            {'syntax': 'Expr',
                             'call': {'syntax': 'RefOp', 'name': '+'},
                             'args': ['P:infected_exp.in.S', 'P:infected_exp.in.I', 'P:infected_exp.in.R']}]},
                  'P:infected_exp.in.dt']}
    p = collect_expr_port_references(t)
    assert p == {'P:infected_exp.in.dt', 'P:infected_exp.in.R', 'P:infected_exp.in.S',
                 'P:infected_exp.in.beta', 'P:infected_exp.in.I'}


test_collect_expr_port_references()


# '/Users/claytonm/Google Drive/ASKE-AutoMATES/ASKE-E/GroMEt-model-representation-WG/gromet/examples/Simple_SIR/SimpleSIR_gromet_FunctionNetwork.json'
# '/Users/claytonm/Google Drive/ASKE-AutoMATES/ASKE-E/GroMEt-model-representation-WG/gromet/examples/call_ex1/call_ex1_gromet_FunctionNetwork.json'
DEFAULT_ROOT = 'examples'
# DEFAULT_PATH = 'examples/call_ex1_gromet_FunctionNetwork.json'
# DEFAULT_PATH = 'examples/SimpleSIR_metadata_gromet_FunctionNetwork.json'
DEFAULT_PATH = 'examples/cond_ex1_gromet_FunctionNetwork.json'
FORCE_BATCH = True  # True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, default='',
                        help="Path to a target GroMEt file or root dir for batch processing")
    parser.add_argument("-b", "--batch", action="store_true",
                        help="Process batch, interpret path as root dir")
    args = parser.parse_args()
    path = args.path
    if args.batch or FORCE_BATCH:
        print("Processing batch")
        if path == '':
            path = DEFAULT_ROOT
        for filename in os.listdir(path=path):
            if filename.split(".")[1] == "json":
                filename = os.path.join(path, filename)
            validate(json.load(open(filename)))
    else:
        print("Processing individual")
        if path == '':
            path = DEFAULT_PATH
        validate(json.load(open(path)))


if __name__ == '__main__':
    main()


# -----------------------------------------------------------------------------
# CHANGE LOG
# -----------------------------------------------------------------------------

"""
Changes 2021-06-16:
() Added test that all object Uids are unique
() Start support for metadata
"""
