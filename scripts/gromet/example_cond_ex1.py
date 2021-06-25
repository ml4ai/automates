from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def generate_gromet() -> Gromet:

    # ----- Metadata -----

    # ----- Model component definitions -----

    variables = [
        Variable(uid=UidVariable('V:x'),
                 name='x',
                 type=UidType('Float'),
                 proxy_state=UidPort('P:cond_ex1.in.x'),
                 states=[UidPort('P:cond_ex1.in.x')],
                 metadata=None),
        Variable(uid=UidVariable('V:y'),
                 name='y',
                 type=UidType('Integer'),
                 proxy_state=UidPort('P:cond_ex1.in.y'),
                 states=[UidPort('P:cond_ex1.in.y')],
                 metadata=None),
        Variable(uid=UidVariable('V:z'),
                 name='z',
                 type=UidType('Float'),
                 proxy_state=UidPort('P:cond_ex1.out.z'),
                 states=[UidPort('P:cond_ex1.out.z')],
                 metadata=None),
    ]

    wires = [
        Wire(uid=UidWire('W:cond_ex1.conditional.x'),
             type=None,
             value_type=UidType('Float'),
             name=None, value=None, metadata=None,
             src=UidPort('P:cond_ex1.in.x'),
             tgt=UidPort('P:conditional.in.x')),
        Wire(uid=UidWire('W:cond_ex1.conditional.y'),
             type=None,
             value_type=UidType('Integer'),
             name=None, value=None, metadata=None,
             src=UidPort('P:cond_ex1.in.y'),
             tgt=UidPort('P:conditional.in.y')),
        Wire(uid=UidWire('W:conditional.cond_ex1.z'),
             type=None,
             value_type=UidType('Float'),  # assumes the "cast" happens here
             name=None, value=None, metadata=None,
             src=UidPort('P:conditional.out.z'),
             tgt=UidPort('P:cond_ex1.out.z'))
    ]

    ports = [
        # cond_ex1 in
        Port(uid=UidPort('P:cond_ex1.in.x'),
             box=UidBox('B:cond_ex1'),
             type=UidType('PortInput'),
             name='x',
             value=None,
             value_type=UidType('Float'),
             metadata=None),
        Port(uid=UidPort('P:cond_ex1.in.y'),
             box=UidBox('B:cond_ex1'),
             type=UidType('PortInput'),
             name='y',
             value=None,
             value_type=UidType('Integer'),
             metadata=None),
        # cond_ex1 out
        Port(uid=UidPort('P:cond_ex1.out.z'),
             box=UidBox('B:cond_ex1'),
             type=UidType('PortOutput'),
             name='z',
             value=None,
             value_type=UidType('Float'),
             metadata=None),

        # conditional in
        Port(uid=UidPort('P:conditional.in.x'),
             box=UidBox('B:conditional'),
             type=UidType('PortInput'),
             name='x',
             value=None,
             value_type=UidType('Float'),
             metadata=None),
        Port(uid=UidPort('P:conditional.in.y'),
             box=UidBox('B:conditional'),
             type=UidType('PortInput'),
             name='y',
             value=None,
             value_type=UidType('Integer'),
             metadata=None),
        # conditional out
        Port(uid=UidPort('P:conditional.out.z'),
             box=UidBox('B:conditional'),
             type=UidType('PortOutput'),
             name='z',
             value=None,
             value_type=UidType('Float'),
             metadata=None),

        # cond0 in
        PortCall(uid=UidPort('PC:cond0.in.y'),
                 box=UidBox('B:cond0'),
                 type=UidType('PortInput'),
                 name='y',
                 value=None,
                 value_type=UidType('Integer'),
                 call=UidPort('P:conditional.in.y'),
                 metadata=None),
        # cond0 out
        Port(uid=UidPort('P:cond0.out.c0'),
             box=UidBox('B:cond0'),
             type=UidType('PortOutput'),
             name='c0',
             value=None,
             value_type=UidType('Boolean'),
             metadata=None),

        # c0_exp in
        PortCall(uid=UidPort('PC:c0_exp.in.x'),
                 box=UidBox('B:c0_exp'),
                 type=UidType('PortInput'),
                 name='x',
                 value=None,
                 value_type=UidType('Float'),
                 call=UidPort('P:conditional.in.x'),
                 metadata=None),
        PortCall(uid=UidPort('PC:c0_exp.in.y'),
                 box=UidBox('B:c0_exp'),
                 type=UidType('PortInput'),
                 name='y',
                 value=None,
                 value_type=UidType('Integer'),
                 call=UidPort('P:conditional.in.y'),
                 metadata=None),
        # c0_exp out
        PortCall(uid=UidPort('PC:c0_exp.out.z'),
                 box=UidBox('B:c0_exp'),
                 type=UidType('PortOutput'),
                 name='z',
                 value=None,
                 value_type=UidType('Float'),
                 call=UidPort('P:conditional.out.z'),
                 metadata=None),

        # c1 in
        PortCall(uid=UidPort('PC:c1.in.y'),
                 box=UidBox('B:c1_exp'),
                 type=UidType('PortInput'),
                 name='y',
                 value=None,
                 value_type=UidType('Integer'),
                 call=UidPort('P:conditional.in.y'),
                 metadata=None),
        # c1 out
        PortCall(uid=UidPort('PC:c1.out.z'),
                 box=UidBox('B:c1_exp'),
                 type=UidType('PortOutput'),
                 name='z',
                 value=None,
                 value_type=UidType('Integer'),
                 call=UidPort('P:conditional.out.z'),
                 metadata=None)
    ]

    # branch 0
    # branch 0 condition
    e0 = Expr(call=RefOp(UidOp('>')),
              args=[UidPort('PC:cond0.in.y'),
                    Literal(uid=None, name=None, metadata=None,
                            type=UidType('Integer'), value=Val("10"))])
    cond0 = Predicate(uid=UidBox('B:cond0'),
                      type=None, name=None,
                      ports=[UidPort('PC:cond0.in.y'),
                             UidPort('P:cond0.out.c0')],
                      tree=e0,
                      metadata=None)
    # branch 0 body
    e1 = Expr(call=RefOp(UidOp('*')),
              args=[UidPort('PC:c0_exp.in.x'),
                    UidPort('PC:c0_exp.in.y')])
    c0_exp = Expression(uid=UidBox('B:c0_exp'),
                        type=None, name=None,
                        ports=[UidPort('PC:c0_exp.in.x'),
                               UidPort('PC:c0_exp.in.y'),
                               UidPort('PC:c0_exp.out.z')],
                        tree=e1,
                        metadata=None)

    # branch 1 body
    e2 = Expr(call=RefOp(UidOp('id')),
              args=[UidPort('PC:c1.in.y')])
    c1_exp = Expression(uid=UidBox('B:c1_exp'),
                        type=None, name=None,
                        ports=[UidPort('PC:c1.in.y'),
                               UidPort('PC:c1.out.z')],
                        tree=e2,
                        metadata=None)

    # conditional
    conditional = \
        Conditional(uid=UidBox('B:conditional'),
                    type=None, name=None,
                    ports=[UidPort('P:conditional.in.x'),
                           UidPort('P:conditional.in.y'),
                           UidPort('P:conditional.out.z')],
                    branches=[
                        (UidBox('B:cond0'), UidBox('B:c0_exp')),
                        (None, UidBox('B:c1_exp'))
                    ],
                    metadata=None)

    # cond_ex1
    cond_ex1 = \
        Function(uid=UidBox('B:cond_ex1'),
                 type=None,
                 name='cond_ex1',
                 ports=[UidPort('P:cond_ex1.in.x'),
                        UidPort('P:cond_ex1.in.y'),
                        UidPort('P:cond_ex1.out.z')],

                 # contents
                 junctions=None,
                 wires=[UidWire('W:cond_ex1.conditional.x'),
                        UidWire('W:cond_ex1.conditional.y'),
                        UidWire('W:conditional.cond_ex1.z')],
                 boxes=[UidBox('B:conditional')],

                 metadata=None)

    boxes = [cond0, c0_exp, c1_exp, conditional, cond_ex1]

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
    gromet_to_json(generate_gromet())
