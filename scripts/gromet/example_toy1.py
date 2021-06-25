from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance: toy1
# -----------------------------------------------------------------------------

def generate_gromet() -> Gromet:

    ports = [
        # input ports to 'toy1'
        Port(uid=UidPort("P:toy1.in.x"), box=UidBox("B:toy1"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="x", value=None, metadata=None),
        Port(uid=UidPort("P:toy1.in.y"), box=UidBox("B:toy1"),
             type=UidType("PortInput"),
             value_type=UidType("Integer"),
             name="y", value=None, metadata=None),
        # output ports to 'toy1'
        Port(uid=UidPort("P:toy1.out.x"), box=UidBox("B:toy1"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="x", value=None, metadata=None),
        Port(uid=UidPort("P:toy1.out.z"), box=UidBox("B:toy1"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="z", value=None, metadata=None),

        # input ports to 'toy1_set_z_exp'
        Port(uid=UidPort("P:toy1_set_z_exp.in.x"), box=UidBox("B:toy1_set_z_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="x", value=None, metadata=None),
        Port(uid=UidPort("P:toy1_set_z_exp.in.y"), box=UidBox("B:toy1_set_z_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="y", value=None, metadata=None),
        # output ports to 'toy1_set_z_exp'
        Port(uid=UidPort("P:toy1_set_z_exp.out.z"), box=UidBox("B:toy1_set_z_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="z", value=None, metadata=None),

        # input ports to 'toy1_reset_x_exp'
        Port(uid=UidPort("P:toy1_reset_x_exp.in.z"), box=UidBox("B:toy1_reset_x_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="z", value=None, metadata=None),
        # output ports to 'toy1_reset_x_exp'
        Port(uid=UidPort("P:toy1_reset_x_exp.out.x"), box=UidBox("B:toy1_reset_x_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"), name="x", value=None, metadata=None),

        # input ports to 'add1'
        Port(uid=UidPort("P:add1.in.x"), box=UidBox("B:add1"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="x", value=None, metadata=None),
        # output ports to 'add1'
        Port(uid=UidPort("P:add1.out.result"), box=UidBox("B:add1"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name=None, value=None, metadata=None),

        # input ports to 'add1'
        Port(uid=UidPort("P:add1_exp.in.x"), box=UidBox("B:add1_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="x", value=None, metadata=None),
        # output ports to 'add1'
        Port(uid=UidPort("P:add1_exp.out.result"), box=UidBox("B:add1_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name=None, value=None, metadata=None),
    ]

    wires = [
        Wire(uid=UidWire("W:add1_x"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:add1.in.x"),
             tgt=UidPort("P:add1_exp.in.x")),
        Wire(uid=UidWire("W:add1_result"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:add1_exp.out.result"),
             tgt=UidPort("P:add1.out.result")),
        Wire(uid=UidWire("W:toy1_x"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:toy1.in.x"),
             tgt=UidPort("P:toy1_set_z_exp.in.x")),
        Wire(uid=UidWire("W:toy1_y"),
             type=None,
             value_type=UidType("Integer"),
             name=None, value=None, metadata=None,
             src=UidPort("P:toy1.in.y"),
             tgt=UidPort("P:toy1_set_z_exp.in.y")),
        Wire(uid=UidWire("W:toy1_set_z1"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:toy1_set_z_exp.out.z"),
             tgt=UidPort("P:toy1_reset_x_exp.in.z")),
        Wire(uid=UidWire("W:toy1_set_z2"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:toy1_set_z_exp.out.z"),
             tgt=UidPort("P:toy1.out.z")),
        Wire(uid=UidWire("W:toy1_reset_x"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:toy1_reset_x_exp.out.x"),
             tgt=UidPort("P:toy1.out.x")),
    ]

    # ====================
    # Boxes

    # ----------
    # add1

    # Expression add1_exp
    # Expr's
    e3 = Expr(call=RefOp(UidOp("+")),
              args=[UidPort("P:add1_exp.in.x"),
                    Literal(uid=None, type=UidType("Integer"), value=Val("1"), name=None, metadata=None)])
    # the anonymous Expression
    add1_exp = Expression(uid=UidBox("B:add1_exp"),
                          type=None,
                          name=None,
                          ports=[UidPort("P:add1_exp.in.x"),
                                 UidPort("P:add1_exp.out.result")],
                          tree=e3,
                          metadata=None)

    add1 = Function(uid=UidBox("B:add1"),
                    type=None,
                    name="add1",
                    ports=[UidPort("P:add1.in.x"),
                           UidPort("P:add1.out.result")],

                    # contents
                    wires=[UidWire("W:add1_x"), UidWire("W:add1_result")],
                    boxes=[UidBox("B:add1_exp")],
                    junctions=None,

                    metadata=None)

    # ----------
    # toy1

    # Expression toy1_set_z
    # Expr's
    e1 = Expr(call=RefOp(UidOp("*")),
              args=[UidPort("P:toy1_set_z_exp.in.x"),
                    UidPort("P:toy1_set_z_exp.in.y")])
    # the anonymous (no name) Expression
    toy1_set_z_exp = \
        Expression(uid=UidBox("B:toy1_set_z_exp"),
                   type=None,
                   name=None,
                   ports=[UidPort("P:toy1_set_z_exp.in.x"),
                          UidPort("P:toy1_set_z_exp.in.y"),
                          UidPort("P:toy1_set_z_exp.out.z")],
                   tree=e1,
                   metadata=None)

    # Expression reset_x
    # Expr's
    e2 = Expr(call=RefBox(UidBox("B:add1")),
              args=[UidPort("P:toy1_reset_x_exp.in.z")])
    # the anonymous (no name) Expression
    toy1_reset_x_exp = \
        Expression(uid=UidBox("B:toy1_reset_x_exp"),
                   type=None,
                   name=None,
                   ports=[UidPort("P:toy1_reset_x_exp.in.z"),
                          UidPort("P:toy1_reset_x_exp.out.x")],
                   tree=e2,
                   metadata=None)

    toy1 = Function(uid=UidBox("B:toy1"),
                    type=None,
                    name="toy1",
                    ports=[UidPort("P:toy1.in.x"), UidPort("P:toy1.in.y"),
                           UidPort("P:toy1.out.x"), UidPort("P:toy1.out.z")],

                    # contents
                    wires=[UidWire("W:toy1_x"), UidWire("W:toy1_y"),
                           UidWire("W:toy1_set_z1"), UidWire("W:toy1_set_z2"),
                           UidWire("W:toy1_reset_x")],
                    boxes=[UidBox("B:toy1_set_z_exp"),
                           UidBox("B:toy1_reset_x_exp")],
                    junctions=None,

                    metadata=None)

    boxes = [toy1, toy1_set_z_exp, toy1_reset_x_exp,
             add1, add1_exp]

    variables = [
        Variable(uid=UidVariable("var1"), name="x_in", type=UidType("Float"),
                 proxy_state=UidPort("P:toy1.in.x"),
                 states=[UidPort("P:toy1.in.x"),
                         UidWire("W:toy1_x")],
                 metadata=None),
        Variable(uid=UidVariable("var2"), name="y_in", type=UidType("Float"),
                 proxy_state=UidPort("P:toy1.in.y"),
                 states=[UidPort("P:toy1.in.y"),
                         UidWire("W:toy1_y")],
                 metadata=None),
        Variable(uid=UidVariable("var3"), name="z_out", type=UidType("Float"),
                 proxy_state=UidPort("P:toy1.out.z"),
                 states=[UidPort("P:toy1.out.z"),
                         UidWire("W:toy1_set_z1"),
                         UidWire("W:toy1_set_z2")],
                 metadata=None),
        Variable(uid=UidVariable("var4"), name="x_out", type=UidType("Float"),
                 proxy_state=UidPort("P:toy1.out.x"),
                 states=[UidPort("P:toy1.out.x"),
                         UidWire("W:toy1_reset_x")],
                 metadata=None)
    ]

    g = Gromet(
        uid=UidGromet("toy1"),
        name="toy1",
        type=UidType("FunctionNetwork"),
        root=toy1.uid,
        types=None,
        literals=None,
        junctions=None,
        ports=ports,
        wires=wires,
        boxes=boxes,
        variables=variables,
        metadata=None
    )

    return g


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    gromet_to_json(generate_gromet())
