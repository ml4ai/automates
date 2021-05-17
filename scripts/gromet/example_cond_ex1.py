from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def cond_ex1_gromet() -> Gromet:

    variables = [
        Variable(uid=UidVariable("x"), name="x", type=UidType("Float"),
                 wires=[UidWire("W:cond_ex1.x"),
                        UidWire("W:c1.x"),
                        UidWire("W:c1_c1exp.x")],
                 metadata=None),
        Variable(uid=UidVariable("y"), name="y", type=UidType("Float"),
                 wires=[UidWire("W:cond_ex1.y"),
                        UidWire("W:cond1.y"), UidWire("W:c1.y"),
                        UidWire("W:c2.y"),
                        UidWire("W:c1_c1exp.y"),
                        UidWire("W:c2.y_z")],
                 metadata=None),
        Variable(uid=UidVariable("z"), name="z", type=UidType("Float"),
                 wires=[UidWire("W:c1_c1exp.z"),
                        UidWire("W:c1.z"),
                        UidWire("W:c2.z"),
                        UidWire("W:cond_ex1.z")],
                 metadata=None),
    ]

    wires = [

        # Branch 1
        # input
        WireDirected(uid=UidWire("W:cond1.y"), type=UidType("T:Integer"), value=None, metadata=None,
                     input=UidPort('P:conditional.in.y'),
                     output=UidPort('P:cond1.in.y')),
        WireDirected(uid=UidWire("W:c1.x"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort('P:conditional.in.x'),
                     output=UidPort('P:c1.in.x')),
        WireDirected(uid=UidWire("W:c1.y"), type=UidType("T:Integer"), value=None, metadata=None,
                     input=UidPort('P:conditional.in.x'),
                     output=UidPort('P:c1.in.y')),
        # output
        WireDirected(uid=UidWire("W:c1.z"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort('P:c1.out.z'),
                     output=UidPort('P:conditional.out.z')),

        # Branch 1 : c1
        WireDirected(uid=UidWire("W:c1_c1exp.x"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort('P:c1.in.x'),
                     output=UidPort('P:c1_exp.in.x')),
        WireDirected(uid=UidWire("W:c1_c1exp.y"), type=UidType("T:Integer"), value=None, metadata=None,
                     input=UidPort('P:c1.in.y'),
                     output=UidPort('P:c1_exp.in.7')),
        WireDirected(uid=UidWire("W:c1_c1exp.z"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort('P:c1_exp.out.z'),
                     output=UidPort('P:c1.out.z')),

        # Branch 2
        # input
        WireDirected(uid=UidWire("W:c2.y"), type=UidType("T:Integer"), value=None, metadata=None,
                     input=UidPort('P:conditional.in.y'),
                     output=UidPort('P:c2.in.y')),
        # output
        WireDirected(uid=UidWire("W:c2.z"), type=UidType("T:Integer"), value=None, metadata=None,
                     input=UidPort('P:c2.out.z'),
                     output=UidPort('P:conditional.out.z')),

        # Branch 2 : c2
        WireDirected(uid=UidWire("W:c2.y_z"), type=UidType("T:Integer"), value=None, metadata=None,
                     input=UidPort('P:c2.in.y'),
                     output=UidPort('P:c2.out.z')),

        # cond_ex1
        # input
        WireDirected(uid=UidWire("W:cond_ex1.x"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort('P:cond_ex1.in.x'),
                     output=UidPort('P:conditional.in.x')),
        WireDirected(uid=UidWire("W:cond_ex1.y"), type=UidType("T:Integer"), value=None, metadata=None,
                     input=UidPort('P:cond_ex1.in.y'),
                     output=UidPort('P:conditional.in.y')),
        # output
        WireDirected(uid=UidWire("W:cond_ex1.z"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort('P:conditional.out.z'),
                     output=UidPort('P:cond_ex1.out.z')),
    ]

    ports = [
        # input for 'cond_ex1'
        Port(uid=UidPort('P:cond_ex1.in.x'), box=UidBox('B:cond_ex1'), type=UidType('T:Float'), name='x',
             metadata=None),
        Port(uid=UidPort('P:cond_ex1.in.y'), box=UidBox('B:cond_ex1'), type=UidType('T:Integer'), name='x',
             metadata=None),
        # output for 'conditional'
        Port(uid=UidPort('P:cond_ex1.out.z'), box=UidBox('B:cond_ex1'), type=UidType('T:Float'), name='z',
             metadata=None),

        # input for 'conditional'
        Port(uid=UidPort('P:conditional.in.x'), box=UidBox('B:conditional'), type=UidType('T:Float'), name='x',
             metadata=None),
        Port(uid=UidPort('P:conditional.in.y'), box=UidBox('B:conditional'), type=UidType('T:Integer'), name='x',
             metadata=None),
        # output for 'conditional'
        Port(uid=UidPort('P:conditional.out.z'), box=UidBox('B:conditional'), type=UidType('T:Float'), name='z',
             metadata=None),

        # input for 'cond1'
        Port(uid=UidPort('P:cond1.in.y'), box=UidBox('B:cond1'), type=UidType('T:Integer'), name='y', metadata=None),
        # output for 'cond1'
        Port(uid=UidPort('P:cond1.out.c1'), box=UidBox('B:cond1'), type=UidType('T:Boolean'), name='c1', metadata=None),

        # input for 'c1'
        Port(uid=UidPort('P:c1.in.x'), box=UidBox('B:c1'), type=UidType('T:Float'), name='x', metadata=None),
        Port(uid=UidPort('P:c1.in.y'), box=UidBox('B:c1'), type=UidType('T:Integer'), name='y', metadata=None),
        # output for 'c1'
        Port(uid=UidPort('P:c1.out.z'), box=UidBox('B:c1'), type=UidType('T:Float'), name='z', metadata=None),

        # input for 'c1_exp'
        Port(uid=UidPort('P:c1_exp.in.x'), box=UidBox('B:c1_exp'), type=UidType('T:Float'), name='x', metadata=None),
        Port(uid=UidPort('P:c1_exp.in.y'), box=UidBox('B:c1_exp'), type=UidType('T:Integer'), name='y', metadata=None),
        # output for 'c1_exp'
        Port(uid=UidPort('P:c1_exp.out.z'), box=UidBox('B:c1_exp'), type=UidType('T:Float'), name='z', metadata=None),

        # input for 'c2'
        Port(uid=UidPort('P:c2.in.y'), box=UidBox('B:c2'), type=UidType('T:Integer'), name='y', metadata=None),
        # output for 'c2'
        Port(uid=UidPort('P:c2.out.z'), box=UidBox('B:c2'), type=UidType('T:Integer'), name='z', metadata=None),
    ]

    # Branch 1 components

    e1 = Expr(call=RefOp(UidOp("<")),
              args=[UidPort('P:cond1.in.y'),
                    Literal(uid=None, type=UidType("Int"), value=Val("10"), metadata=None)])
    cond1 = Predicate(uid=UidBox('B:cond1'),
                      type=None,
                      name=None,
                      input_ports=[UidPort('P:cond1.in.y')],
                      output_ports=[UidPort('P:cond1.out.c1')],
                      tree=e1,
                      wiring=None,
                      metadata=None)

    e2 = Expr(call=RefOp(UidOp("*")),
              args=[UidPort('P:c1_exp.in.x'), UidPort('P:c1_exp.in.y')])
    c1_exp = Expression(uid=UidBox('B:c1_exp'),
                        type=None,
                        name=None,
                        input_ports=[UidPort('P:c1_exp.in.x'), UidPort('P:c1_exp.in.y')],
                        output_ports=[UidPort('P:c1_exp.out.z')],
                        tree=e2,
                        wiring=None,
                        metadata=None)

    c1 = Function(uid=UidBox('B:c1'),
                  type=None,
                  name=None,
                  input_ports=[UidPort('P:c1.in.x'), UidPort('P:c1.in.y')],
                  output_ports=[UidPort('P:c1.out.z')],
                  wiring=[UidWire("W:c1_c1exp.x"), UidWire("W:c1_c1exp.y"),
                          UidWire("W:c1_c1exp.z")],
                  metadata=None)

    # Branch 2 components

    c2 = Function(uid=UidBox('B:c2'),
                  type=None,
                  name=None,
                  input_ports=[UidPort('P:c2.in.y')],
                  output_ports=[UidPort('P:c2.out.z')],
                  wiring=[UidWire("W:c2.y_z")],
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
                              input_ports=[UidPort('P:conditional.in.y'),
                                           UidPort('P:conditional.in.y')],
                              output_ports=[UidPort('P:conditional.out.z')],
                              branches=branches,
                              wiring=None,
                              metadata=None)

    cond_ex1 = Function(uid=UidBox('B:cond_ex1'),
                        type=None,
                        name='cond_ex1',
                        input_ports=[UidPort('P:cond_ex1.in.x'),
                                     UidPort('P:cond_ex1.in.y')],
                        output_ports=[UidPort('P:cond_ex1.out.z')],
                        wiring=[UidWire("W:cond_ex1.x"),
                                UidWire("W:cond_ex1.y"),
                                UidWire("W:cond_ex1.z")],
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
