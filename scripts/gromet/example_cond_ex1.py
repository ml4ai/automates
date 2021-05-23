from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def cond_ex1_gromet() -> Gromet:

    variables = [
        Variable(uid=UidVariable("x"), name="x", type=UidType("Float"),
                 states=[UidWire("W:cond_ex1.x"),
                         UidWire("W:c1.x"),
                         UidWire("W:c1_c1exp.x")],
                 metadata=None),
        Variable(uid=UidVariable("y"), name="y", type=UidType("Float"),
                 states=[UidWire("W:cond_ex1.y"),
                         UidWire("W:cond1.y"), UidWire("W:c1.y"),
                         UidWire("W:c2.y"),
                         UidWire("W:c1_c1exp.y"),
                         UidWire("W:c2.y_z")],
                 metadata=None),
        Variable(uid=UidVariable("z"), name="z", type=UidType("Float"),
                 states=[UidWire("W:c1_c1exp.z"),
                         UidWire("W:c1.z"),
                         UidWire("W:c2.z"),
                         UidWire("W:cond_ex1.z")],
                 metadata=None),
    ]

    wires = [

        # Branch 1
        # input
        Wire(uid=UidWire("W:cond1.y"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Integer"),
             name=None, value=None, metadata=None,
             src=UidPort('P:conditional.in.y'),
             tgt=UidPort('P:cond1.in.y')),
        Wire(uid=UidWire("W:c1.x"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort('P:conditional.in.x'),
             tgt=UidPort('P:c1.in.x')),
        Wire(uid=UidWire("W:c1.y"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Integer"),
             name=None, value=None, metadata=None,
             src=UidPort('P:conditional.in.x'),
             tgt=UidPort('P:c1.in.y')),
        # output
        Wire(uid=UidWire("W:c1.z"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort('P:c1.out.z'),
             tgt=UidPort('P:conditional.out.z')),

        # Branch 1 : c1
        Wire(uid=UidWire("W:c1_c1exp.x"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort('P:c1.in.x'),
             tgt=UidPort('P:c1_exp.in.x')),
        Wire(uid=UidWire("W:c1_c1exp.y"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Integer"),
             name=None, value=None, metadata=None,
             src=UidPort('P:c1.in.y'),
             tgt=UidPort('P:c1_exp.in.7')),
        Wire(uid=UidWire("W:c1_c1exp.z"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort('P:c1_exp.out.z'),
             tgt=UidPort('P:c1.out.z')),

        # Branch 2
        # input
        Wire(uid=UidWire("W:c2.y"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Integer"),
             name=None, value=None, metadata=None,
             src=UidPort('P:conditional.in.y'),
             tgt=UidPort('P:c2.in.y')),
        # output
        Wire(uid=UidWire("W:c2.z"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Integer"),
             name=None, value=None, metadata=None,
             src=UidPort('P:c2.out.z'),
             tgt=UidPort('P:conditional.out.z')),

        # Branch 2 : c2
        Wire(uid=UidWire("W:c2.y_z"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Integer"),
             name=None, value=None, metadata=None,
             src=UidPort('P:c2.in.y'),
             tgt=UidPort('P:c2.out.z')),

        # cond_ex1
        # input
        Wire(uid=UidWire("W:cond_ex1.x"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort('P:cond_ex1.in.x'),
             tgt=UidPort('P:conditional.in.x')),
        Wire(uid=UidWire("W:cond_ex1.y"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Integer"),
             name=None, value=None, metadata=None,
             src=UidPort('P:cond_ex1.in.y'),
             tgt=UidPort('P:conditional.in.y')),
        # output
        Wire(uid=UidWire("W:cond_ex1.z"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort('P:conditional.out.z'),
             tgt=UidPort('P:cond_ex1.out.z')),
    ]

    ports = [
        # input for 'cond_ex1'
        Port(uid=UidPort('P:cond_ex1.in.x'), box=UidBox('B:cond_ex1'),
             type=UidType("T:PortInput"),
             value_type=UidType('T:Float'),
             name='x',
             value=None, metadata=None),
        Port(uid=UidPort('P:cond_ex1.in.y'), box=UidBox('B:cond_ex1'),
             type=UidType("T:PortInput"),
             value_type=UidType('T:Integer'),
             name='y',
             value=None, metadata=None),
        # output for 'conditional'
        Port(uid=UidPort('P:cond_ex1.out.z'), box=UidBox('B:cond_ex1'),
             type=UidType("T:PortOutput"),
             value_type=UidType('T:Float'),
             name='z',
             value=None, metadata=None),

        # input for 'conditional'
        Port(uid=UidPort('P:conditional.in.x'), box=UidBox('B:conditional'),
             type=UidType("T:PortInput"),
             value_type=UidType('T:Float'),
             name='x',
             value=None, metadata=None),
        Port(uid=UidPort('P:conditional.in.y'), box=UidBox('B:conditional'),
             type=UidType("T:PortInput"),
             value_type=UidType('T:Integer'),
             name='y',
             value=None, metadata=None),
        # output for 'conditional'
        Port(uid=UidPort('P:conditional.out.z'), box=UidBox('B:conditional'),
             type=UidType("T:PortOutput"),
             value_type=UidType('T:Float'), name='z',
             value=None, metadata=None),

        # input for 'cond1'
        Port(uid=UidPort('P:cond1.in.y'), box=UidBox('B:cond1'),
             type=UidType("T:PortInput"),
             value_type=UidType('T:Integer'),
             name='y',
             value=None, metadata=None),
        # output for 'cond1'
        Port(uid=UidPort('P:cond1.out.c1'), box=UidBox('B:cond1'),
             type=UidType("T:PortOutput"),
             value_type=UidType('T:Boolean'),
             name='c1',
             value=None, metadata=None),

        # input for 'c1'
        Port(uid=UidPort('P:c1.in.x'), box=UidBox('B:c1'),
             type=UidType("T:PortInput"),
             value_type=UidType('T:Float'),
             name='x',
             value=None, metadata=None),
        Port(uid=UidPort('P:c1.in.y'), box=UidBox('B:c1'),
             type=UidType("T:PortInput"),
             value_type=UidType('T:Integer'),
             name='y',
             value=None, metadata=None),
        # output for 'c1'
        Port(uid=UidPort('P:c1.out.z'), box=UidBox('B:c1'),
             type=UidType("T:PortOutput"),
             value_type=UidType('T:Float'),
             name='z',
             value=None, metadata=None),

        # input for 'c1_exp'
        Port(uid=UidPort('P:c1_exp.in.x'), box=UidBox('B:c1_exp'),
             type=UidType("T:PortInput"),
             value_type=UidType('T:Float'),
             name='x',
             value=None, metadata=None),
        Port(uid=UidPort('P:c1_exp.in.y'), box=UidBox('B:c1_exp'),
             type=UidType("T:PortInput"),
             value_type=UidType('T:Integer'),
             name='y',
             value=None, metadata=None),
        # output for 'c1_exp'
        Port(uid=UidPort('P:c1_exp.out.z'), box=UidBox('B:c1_exp'),
             type=UidType("T:PortOutput"),
             value_type=UidType('T:Float'), name='z',
             value=None, metadata=None),

        # input for 'c2'
        Port(uid=UidPort('P:c2.in.y'), box=UidBox('B:c2'),
             type=UidType("T:PortInput"),
             value_type=UidType('T:Integer'),
             name='y',
             value=None, metadata=None),
        # output for 'c2'
        Port(uid=UidPort('P:c2.out.z'), box=UidBox('B:c2'),
             type=UidType("T:PortOutput"),
             value_type=UidType('T:Integer'),
             name='z',
             value=None, metadata=None),
    ]

    # Branch 1 components

    e1 = Expr(call=RefOp(UidOp("<")),
              args=[UidPort('P:cond1.in.y'),
                    Literal(uid=None, type=UidType("T:Integer"), value=Val("10"),
                            name=None, metadata=None)])
    cond1 = Predicate(uid=UidBox('B:cond1'),
                      type=None,
                      name=None,
                      ports=[UidPort('P:cond1.in.y'),
                             UidPort('P:cond1.out.c1')],
                      tree=e1,
                      metadata=None)

    e2 = Expr(call=RefOp(UidOp("*")),
              args=[UidPort('P:c1_exp.in.x'), UidPort('P:c1_exp.in.y')])
    c1_exp = Expression(uid=UidBox('B:c1_exp'),
                        type=None,
                        name=None,
                        ports=[UidPort('P:c1_exp.in.x'), UidPort('P:c1_exp.in.y'),
                               UidPort('P:c1_exp.out.z')],
                        tree=e2,
                        metadata=None)

    c1 = Function(uid=UidBox('B:c1'),
                  type=None,
                  name=None,
                  ports=[UidPort('P:c1.in.x'), UidPort('P:c1.in.y'),
                         UidPort('P:c1.out.z')],

                  # contents
                  wires=[UidWire("W:c1_c1exp.x"), UidWire("W:c1_c1exp.y"),
                         UidWire("W:c1_c1exp.z")],
                  boxes=[UidBox('B:c1_exp')],
                  junctions=None,

                  metadata=None)

    # Branch 2 components

    c2 = Function(uid=UidBox('B:c2'),
                  type=None,
                  name=None,
                  ports=[UidPort('P:c2.in.y'),
                         UidPort('P:c2.out.z')],

                  # contents
                  wires=[UidWire("W:c2.y_z")],
                  boxes=None,
                  junctions=None,

                  metadata=None)

    # branches

    branches = [
        (cond1, c1, [UidWire("W:cond1.y"),
                     UidWire("W:c1.x"), UidWire("W:c1.y"), UidWire("W:c1.z")]),
        (None, c2, [UidWire("W:c2.y"),
                    UidWire("W:c2.z")])
    ]

    # conditional

    conditional = Conditional(uid=UidBox('B:conditional'),
                              type=None,
                              name=None,
                              ports=[UidPort('P:conditional.in.y'),
                                     UidPort('P:conditional.in.y'),
                                     UidPort('P:conditional.out.z')],
                              branches=branches,
                              metadata=None)

    cond_ex1 = Function(uid=UidBox('B:cond_ex1'),
                        type=None,
                        name='cond_ex1',
                        ports=[UidPort('P:cond_ex1.in.x'),
                               UidPort('P:cond_ex1.in.y'),
                               UidPort('P:cond_ex1.out.z')],

                        # contents
                        wires=[UidWire("W:cond_ex1.x"),
                               UidWire("W:cond_ex1.y"),
                               UidWire("W:cond_ex1.z")],
                        boxes=[UidBox('B:conditional')],
                        junctions=None,

                        metadata=None)

    boxes = [cond1, c1, c1_exp,
             c2,
             conditional,
             cond_ex1]

    _g = Gromet(
        uid=UidGromet('cond_ex1'),
        name='cond_ex1',
        type=UidType('FunctionNetwork'),
        root=cond_ex1.uid,
        types=None,
        literals=None,
        junctions=None,
        ports=ports,
        wires=wires,
        boxes=boxes,
        variables=variables,
        metadata=None
    )

    return _g


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    gromet_to_json(cond_ex1_gromet())
