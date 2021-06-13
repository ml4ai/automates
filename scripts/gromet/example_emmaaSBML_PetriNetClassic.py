from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def generate_gromet() -> Gromet:

    wires = [
        Wire(uid=UidWire("W:__s3-kf_vb_bind_1"),
             type=None, value_type=None,
             name=None, value=None, metadata=None,
             src=UidJunction("__s3"),
             tgt=UidJunction("kf_vb_bind_1")),
        Wire(uid=UidWire("W:__s4-kf_vb_bind_1"),
             type=None, value_type=None,
             name=None, value=None, metadata=None,
             src=UidJunction("__s4"),
             tgt=UidJunction("kf_vb_bind_1")),
        Wire(uid=UidWire("W:kf_vb_bind_1-__s12"),
             type=None, value_type=None,
             name=None, value=None, metadata=None,
             src=UidJunction("kf_vb_bind_1"),
             tgt=UidJunction("__s12")),
        Wire(uid=UidWire("W:__s12-kr_vb_bind_1"),
             type=None, value_type=None,
             name=None, value=None, metadata=None,
             src=UidJunction("__s12"),
             tgt=UidJunction("kr_vb_bind_1")),
        Wire(uid=UidWire("kr_vb_bind_1-__s3"),
             type=None, value_type=None,
             name=None, value=None, metadata=None,
             src=UidJunction("kr_vb_bind_1"),
             tgt=UidJunction("__s3")),
        Wire(uid=UidWire("kr_vb_bind_1-__s4"),
             type=None, value_type=None,
             name=None, value=None, metadata=None,
             src=UidJunction("kr_vb_bind_1"),
             tgt=UidJunction("__s4"))
    ]

    junctions = [
        Junction(uid=UidJunction("__s3"),
                 type=UidType("State"),
                 name="BRAF(vemurafenib=None, V600=&apos;WT&apos;, map3k=None, ras=None)",
                 value=Literal(uid=None, type=UidType("Integer"), value=Val("10000"), name=None, metadata=None),
                 value_type=UidType("Integer"),
                 metadata=None),
        Junction(uid=UidJunction("__s4"),
                 type=UidType("State"),
                 name="vemurafenib(map3k=None)",
                 value=Literal(uid=None, type=UidType("Integer"), value=Val("10000"), name=None, metadata=None),
                 value_type=UidType("Integer"),
                 metadata=None),
        Junction(uid=UidJunction("__s12"),
                 type=UidType("State"),
                 name="BRAF(vemurafenib=1, V600=&apos;WT&apos;, map3k=None, ras=None) ._br_vemurafenib(map3k=1)",
                 value=None,  # b/c no initial condition assignment
                 value_type=UidType("Integer"),
                 metadata=None),
        Junction(uid=UidJunction("kf_vb_bind_1"),
                 type=UidType("Rate"),
                 name="kf_vb_bind_1",
                 value=Literal(uid=None, type=UidType("Float"), value=Val("0.0000001"), name=None, metadata=None),
                 value_type=UidType("Float"),
                 metadata=None),
        Junction(uid=UidJunction("kr_vb_bind_1"),
                 type=UidType("Rate"),
                 name="kr_vb_bind_1",
                 value=Literal(uid=None, type=UidType("Float"), value=Val("0.0000001"), name=None, metadata=None),
                 value_type=UidType("Float"),
                 metadata=None)
    ]

    pnc = Relation(uid=UidBox("indra_model"),
                   type=UidType("PetriNetClassic"),
                   name="indra_model",
                   ports=None,

                   # contents
                   junctions=[UidJunction("__s3"),
                              UidJunction("__s4"),
                              UidJunction("__s12"),
                              UidJunction("kf_vb_bind_1"),
                              UidJunction("kr_vb_bind_1")],
                   wires=[UidWire("W:__s3-kf_vb_bind_1"),
                          UidWire("W:__s4-kf_vb_bind_1"),
                          UidWire("W:kf_vb_bind_1-__s12"),
                          UidWire("W:__s12-kr_vb_bind_1"),
                          UidWire("kr_vb_bind_1-__s3"),
                          UidWire("kr_vb_bind_1-__s4")],
                   boxes=None,

                   metadata=None)

    boxes = [pnc]

    g = Gromet(
        uid=UidGromet("indra_model_pnc"),
        name="indra_model",
        type=UidType("PetriNetClassic"),
        root=pnc.uid,
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
    gromet_to_json(generate_gromet())
