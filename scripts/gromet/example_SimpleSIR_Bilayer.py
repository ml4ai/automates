from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def simple_sir_Bilayer_gromet() -> Gromet:

    wires = [
        Wire(uid=UidWire("W:S.beta"),
             type=UidType("T:W_in"),
             value_type=UidType("T:Integer"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:S"),
             tgt=UidJunction("J:beta")),
        Wire(uid=UidWire("W:I.beta"),
             type=UidType("T:W_in"),
             value_type=UidType("T:Integer"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:I"),
             tgt=UidJunction("J:beta")),
        Wire(uid=UidWire("W:I.gamma"),
             type=UidType("T:W_in"),
             value_type=UidType("T:Integer"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:I"),
             tgt=UidJunction("J:gamma")),

        Wire(uid=UidWire("W:beta.S'"),
             type=UidType("T:W_neg"),
             value_type=UidType("T:Real"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:beta"),
             tgt=UidJunction("J:S'")),
        Wire(uid=UidWire("W:beta.I'"),
             type=UidType("T:W_pos"),
             value_type=UidType("T:Real"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:beta"),
             tgt=UidJunction("J:I'")),
        Wire(uid=UidWire("W:gamma.I'"),
             type=UidType("T:W_neg"),
             value_type=UidType("T:Real"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:gamma"),
             tgt=UidJunction("J:I'")),
        Wire(uid=UidWire("W:gamma.R'"),
             type=UidType("T:W_pos"),
             value_type=UidType("T:Real"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:gamma"),
             tgt=UidJunction("J:R'"))
    ]

    junctions = [
        Junction(uid=UidJunction("J:S"),
                 type=UidType("State"),
                 name="S",
                 value=None,
                 value_type=UidType("T:Integer"),
                 metadata=None),
        Junction(uid=UidJunction("J:I"),
                 type=UidType("State"),
                 name="I",
                 value=None,
                 value_type=UidType("T:Integer"),
                 metadata=None),
        Junction(uid=UidJunction("J:R"),
                 type=UidType("State"),
                 name="R",
                 value=None,
                 value_type=UidType("T:Integer"),
                 metadata=None),

        Junction(uid=UidJunction("J:beta"),
                 type=UidType("Flux"),
                 name="beta",
                 value=Literal(uid=None, name=None,
                               value=Val("0.1"),
                               type=UidType("T:Real"),
                               metadata=None),
                 value_type=UidType("T:Real"),
                 metadata=None),
        Junction(uid=UidJunction("J:gamma"),
                 type=UidType("Flux"),
                 name="gamma",
                 value=Literal(uid=None, name=None,
                               value=Val("0.2"),
                               type=UidType("T:Real"),
                               metadata=None),
                 value_type=UidType("T:Real"),
                 metadata=None),

        Junction(uid=UidJunction("J:S'"),
                 type=UidType("Tangent"),
                 name="S'",
                 value=None,
                 value_type=UidType("T:Integer"),
                 metadata=None),
        Junction(uid=UidJunction("J:I'"),
                 type=UidType("Tangent"),
                 name="I'",
                 value=None,
                 value_type=UidType("T:Integer"),
                 metadata=None),
        Junction(uid=UidJunction("J:R'"),
                 type=UidType("Tangent"),
                 name="R'",
                 value=None,
                 value_type=UidType("T:Integer"),
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
        name="SimpleSIR",
        type=UidType("Bilayer"),
        root=sir.uid,
        types=None,
        literals=None,
        junctions=junctions,
        ports=None,
        wires=wires,
        boxes=boxes,
        variables=None,
        metadata=None
    )
    return g


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    gromet_to_json(simple_sir_Bilayer_gromet())
