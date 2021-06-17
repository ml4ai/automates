from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def generate_gromet() -> Gromet:

    # ----- Metadata -----

    # -- model interface metadata

    simple_sir_model_BL_interface = \
        ModelInterface(uid=UidMetadatum("simple_sir_BL_model_interface"),
                       provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                             timestamp=get_current_datetime()),
                       variables=[UidJunction("J:S"), UidJunction("J:I"), UidJunction("J:R"),      # State
                                  UidJunction("J:beta"), UidJunction("J:gamma"),                   # Flux
                                  UidJunction("J:S'"), UidJunction("J:I'"), UidJunction("J:R'")],  # Tangent
                       parameters=[UidJunction("J:beta"), UidJunction("J:gamma")],  # Flux
                       initial_conditions=[UidJunction("J:S"), UidJunction("J:I"), UidJunction("J:R")])  # States

    # ----- Model component definitions -----

    wires = [
        Wire(uid=UidWire("W:S.beta"),
             type=UidType("W_in"),
             value_type=UidType("Integer"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:S"),
             tgt=UidJunction("J:beta")),
        Wire(uid=UidWire("W:I.beta"),
             type=UidType("W_in"),
             value_type=UidType("Integer"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:I"),
             tgt=UidJunction("J:beta")),
        Wire(uid=UidWire("W:I.gamma"),
             type=UidType("W_in"),
             value_type=UidType("Integer"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:I"),
             tgt=UidJunction("J:gamma")),

        Wire(uid=UidWire("W:beta.S'"),
             type=UidType("W_neg"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:beta"),
             tgt=UidJunction("J:S'")),
        Wire(uid=UidWire("W:beta.I'"),
             type=UidType("W_pos"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:beta"),
             tgt=UidJunction("J:I'")),
        Wire(uid=UidWire("W:gamma.I'"),
             type=UidType("W_neg"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:gamma"),
             tgt=UidJunction("J:I'")),
        Wire(uid=UidWire("W:gamma.R'"),
             type=UidType("W_pos"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:gamma"),
             tgt=UidJunction("J:R'"))
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
                 type=UidType("Flux"),
                 name="beta",
                 value=Literal(uid=None, name=None,
                               value=Val("0.1"),
                               type=UidType("Real"),
                               metadata=None),
                 value_type=UidType("Real"),
                 metadata=None),
        Junction(uid=UidJunction("J:gamma"),
                 type=UidType("Flux"),
                 name="gamma",
                 value=Literal(uid=None, name=None,
                               value=Val("0.2"),
                               type=UidType("Real"),
                               metadata=None),
                 value_type=UidType("Real"),
                 metadata=None),

        Junction(uid=UidJunction("J:S'"),
                 type=UidType("Tangent"),
                 name="S'",
                 value=None,
                 value_type=UidType("Integer"),
                 metadata=None),
        Junction(uid=UidJunction("J:I'"),
                 type=UidType("Tangent"),
                 name="I'",
                 value=None,
                 value_type=UidType("Integer"),
                 metadata=None),
        Junction(uid=UidJunction("J:R'"),
                 type=UidType("Tangent"),
                 name="R'",
                 value=None,
                 value_type=UidType("Integer"),
                 metadata=None)
    ]

    sir = Relation(uid=UidBox("B:sir"),
                   type=None,
                   name="sir",
                   junctions=[UidJunction("J:S"), UidJunction("J:I"), UidJunction("J:R"),
                              UidJunction("J:beta"), UidJunction("J:gamma"),
                              UidJunction("J:S'"), UidJunction("J:R'"), UidJunction("J:R'")],
                   wires=[UidWire("W:S.beta"), UidWire("W:I.beta"), UidWire("W:I.gamma"),
                          UidWire("W:beta.S'"), UidWire("W:beta.I'"),
                          UidWire("W:gamma.I'"), UidWire("W:gamma.R'")],
                   boxes=None,
                   ports=None,
                   metadata=None)

    boxes = [sir]

    g = Gromet(
        uid=UidGromet("SimpleSIR_Bilayer"),
        name="SimpleSIR_metadata",
        type=UidType("Bilayer"),
        root=sir.uid,
        types=None,
        literals=None,
        junctions=junctions,
        ports=None,
        wires=wires,
        boxes=boxes,
        variables=None,
        metadata=[simple_sir_model_BL_interface]
    )
    return g


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    gromet_to_json(generate_gromet())
