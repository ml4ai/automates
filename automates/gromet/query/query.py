from typing import List
import os

from automates.program_analysis.JSON2GroMEt.json2gromet import json_to_gromet


from automates.gromet.fn import (
    GrometFNModule
)

from automates.gromet.metadata import (
    Metadata,
    SourceCodeReference
)


def get_module_metadata(module: GrometFNModule, idx: int) -> List[Metadata]:
    """
    Helper to access metadata index of a GrometFNModule.
    :param module: The GrometFNModule
    :param idx: index into the module metadata_collection
    :return: List of Metadata objects
    """
    if idx < len(module.metadata_collection):
        return module.metadata_collection[idx]
    else:
        raise Exception(f"GrometFNModule {module.name} as metadata_collection size {len(module.metadata_collection)}, "
                        f"but asked for index {idx}")


def find_source_code_reference(module: GrometFNModule, idx: int) -> SourceCodeReference:
    """
    Helper to find source_code_reference metadatum given an
    index into the metadata_collection of a GrometFNModule.
    :param module: The GrometFNModule
    :param idx: index into the module metadata_collection
    :return: A SourceCodeReference Metadata object (if it is in the Metadata list)
    """
    metadata = get_module_metadata(module, idx)
    scr = None
    for metadatum in metadata:
        if isinstance(metadatum, SourceCodeReference):
            scr = metadatum
    return scr


def collect_named_output_ports(module: GrometFNModule):
    named_output_ports = list()

    def collect_for_fn(fn):
        """
        Helper fn to collected all of the named output ports of a FN
        :param fn:
        :return:
        """
        if fn.pof:
            for output_port in fn.pof:
                if output_port.name:
                    # output_port has a name
                    name = output_port.name
                    value = None
                    source_code_reference = None

                    box = fn.bf[output_port.box - 1]  # the box (call) the output_port is attached to

                    # see if we can find source_code_reference for the output_port
                    if box.metadata:
                        # box has metadata, see if it has a source_code_reference (otherwise will return None)
                        source_code_reference = find_source_code_reference(module, box.metadata - 1)

                    # Now see if there is a LiteralValue assigned directly to this output_port
                    if box.contents:
                        attribute_contents = module.attributes[box.contents - 1]  # the contents of the box-call
                        if attribute_contents.type == 'FN':
                            # the contents are a FN (not an import)
                            fn_contents = attribute_contents.value  # The FN itself
                            if fn_contents.b[0].function_type == 'EXPRESSION':
                                # The FN is an expression, so it has a single return port (value)
                                if fn_contents.wfopo:
                                    expr_box_idx = fn_contents.wfopo[0].tgt  # identify the value source of the output port
                                    expr_box = fn_contents.bf[expr_box_idx - 1]
                                    if expr_box.function_type == 'LITERAL':
                                        # we have a literal!
                                        value = expr_box.value  # The literal value

                    named_output_ports.append((name, value, source_code_reference))

    if module.fn:
        collect_for_fn(module.fn)
    for attr in module.attributes:
        if attr.type == "FN":
            collect_for_fn(attr.value)

    return named_output_ports


# -----------------------------------------------------------------------------
# Development Script
#   NOTE: this has been replicated in <automates_root>/notebooks/gromet/gromet_query.ipynb
# -----------------------------------------------------------------------------

LOCAL_SKEMA_GOOGLE_DRIVE_ROOT = "/Users/claytonm/My Drive/"
ROOT = os.path.join(LOCAL_SKEMA_GOOGLE_DRIVE_ROOT, "ASKEM-SKEMA/data/")
EXP0_GROMET_JSON = os.path.join(ROOT, "gromet/examples/exp0/FN_0.1.4/exp0--Gromet-FN-auto.json")
EXP1_GROMET_JSON = os.path.join(ROOT, "gromet/examples/exp1/FN_0.1.4/exp1--Gromet-FN-auto.json")
EXP2_GROMET_JSON = os.path.join(ROOT, "gromet/examples/exp2/FN_0.1.4/exp2--Gromet-FN-auto.json")
CHIME_SIR_GROMET_JSON = \
    os.path.join(ROOT, "epidemiology/CHIME/CHIME_SIR_model/gromet/FN_0.1.4/CHIME_SIR--Gromet-FN-auto.json")
EXAMPLE_GROMET_JSON_FILE = "../../../notebooks/gromet/CHIME_SIR_while_loop--Gromet-FN-auto.json"


def script():
    # module = json_to_gromet(EXP0_GROMET_JSON)
    # module = json_to_gromet(EXP1_GROMET_JSON)
    # module = json_to_gromet(EXP2_GROMET_JSON)
    module = json_to_gromet(CHIME_SIR_GROMET_JSON)
    # module = json_to_gromet(EXAMPLE_GROMET_JSON_FILE)
    # print(module)
    # print(len(module.metadata_collection))
    # print(find_source_code_reference(module, 0))
    # print(find_source_code_reference(module, 2))

    nops = collect_named_output_ports(module)
    for nop in nops:
        print(nop)


if __name__ == "__main__":
    script()
