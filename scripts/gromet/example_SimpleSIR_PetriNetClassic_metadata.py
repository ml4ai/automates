from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def generate_gromet() -> Gromet:

    # ----- Metadata -----

    # -- model interface metadata

    simple_sir_model_PNC_interface = \
        ModelInterface(uid=UidMetadatum("simple_sir_PNC_model_interface"),
                       provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                             timestamp=get_current_datetime()),
                       variables=[UidJunction("J:S"), UidJunction("J:I"), UidJunction("J:R"),  # State
                                  UidJunction("J:beta"), UidJunction("J:gamma")],              # Rate
                       parameters=[UidJunction("J:beta"), UidJunction("J:gamma")],
                       initial_conditions=[UidJunction("J:S"), UidJunction("J:I"), UidJunction("J:R")])

    # ----- Model component definitions -----

    wires = [
        Wire(uid=UidWire("W:S.beta"),
             type=None, value_type=None,
             name=None, value=None, metadata=None,
             src=UidJunction("J:S"),
             tgt=UidJunction("J:beta")),
        Wire(uid=UidWire("W:beta.I1"),
             type=None, value_type=None,
             name=None, value=None, metadata=None,
             src=UidJunction("J:beta"),
             tgt=UidJunction("J:I")),
        Wire(uid=UidWire("W:beta.I2"),
             type=None, value_type=None,
             name=None, value=None, metadata=None,
             src=UidJunction("J:beta"),
             tgt=UidJunction("J:I")),
        Wire(uid=UidWire("W:I.beta"),
             type=None, value_type=None,
             name=None, value=None, metadata=None,
             src=UidJunction("J:I"),
             tgt=UidJunction("J:beta")),
        Wire(uid=UidWire("W:I.gamma"),
             type=None, value_type=None,
             name=None, value=None, metadata=None,
             src=UidJunction("J:I"),
             tgt=UidJunction("J:gamma")),
        Wire(uid=UidWire("W:gamma.R"),
             type=None, value_type=None,
             name=None, value=None, metadata=None,
             src=UidJunction("J:gamma"),
             tgt=UidJunction("J:R")),
    ]

    junctions = [
        Junction(uid=UidJunction("J:S"),
                 type=UidType("State"),
                 name="S",
                 value=None,
                 value_type=UidType("Integer"),
                 metadata=None),
        Junction(uid=UidJunction("J:I"),
                 type=UidType("State"),
                 name="I",
                 value=None,
                 value_type=UidType("Integer"),
                 metadata=None),
        Junction(uid=UidJunction("J:R"),
                 type=UidType("State"),
                 name="R",
                 value=None,
                 value_type=UidType("Integer"),
                 metadata=None),
        Junction(uid=UidJunction("J:beta"),
                 type=UidType("Rate"),
                 name="beta",
                 value=None,
                 value_type=UidType("Real"),
                 metadata=None),
        Junction(uid=UidJunction("J:gamma"),
                 type=UidType("Rate"),
                 name="gamma",
                 value=None,
                 value_type=UidType("Real"),
                 metadata=None),
    ]

    sir = Relation(uid=UidBox("B:sir"),
                   type=None,
                   name="sir",
                   junctions=[UidJunction("J:S"), UidJunction("J:I"), UidJunction("J:R"),
                              UidJunction("J:beta"), UidJunction("J:gamma")],
                   wires=[UidWire("W:S.beta"), UidWire("W:beta.I1"), UidWire("W:beta.I2"),
                          UidWire("W:I.beta"), UidWire("W:I.gamma"), UidWire("W:gamma.R")],
                   boxes=None,
                   ports=None,
                   metadata=None)

    boxes = [sir]

    g = Gromet(
        uid=UidGromet("SimpleSIR_PetriNetClassic"),
        name="SimpleSIR_metadata",
        type=UidType("PetriNetClassic"),
        root=sir.uid,
        types=None,
        literals=None,
        junctions=junctions,
        ports=None,
        wires=wires,
        boxes=boxes,
        variables=None,
        metadata=[simple_sir_model_PNC_interface]
    )

    return g


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    gromet_to_json(generate_gromet())
