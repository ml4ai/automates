from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def generate_gromet() -> Gromet:

    # ----- Metadata -----

    chime_model_interface = \
        ModelInterface(uid=UidMetadatum("chime_model_interface"),
                       provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                             timestamp=get_current_datetime()),
                       variables=[],
                       parameters=[],
                       initial_conditions=[])

    # ----- Model component definitions -----

    variables = []
    wires = []
    ports = []
    boxes = []

    _g = Gromet(
        uid=UidGromet("CHIME_FN"),
        name="CHIME",
        type=UidType("FunctionNetwork"),
        root=None,  # TODO
        types=None,
        literals=None,
        junctions=None,
        ports=ports,
        wires=wires,
        boxes=boxes,
        variables=variables,
        metadata=[chime_model_interface]  # TODO document and code ref sets
    )

    return _g


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    gromet_to_json(generate_gromet())
