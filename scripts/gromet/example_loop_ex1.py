from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

"""
def loop_ex1(k):
    for i in range(5):
        k = k + 1
    return k


def loop_ex2(y: float):
    p = 5
    for i in range(10):
        x = i + 2
        for j in range(x):
            p = y + p - x
    return p
"""


def generate_gromet() -> Gromet:

    # ----- Metadata -----

    loop_ex1_interface = \
        ModelInterface(uid=UidMetadatum("loop_ex1_model_interface"),
                       provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                             timestamp=get_current_datetime()),
                       variables=[],
                       parameters=[],
                       initial_conditions=[])

    # ----- Model component definitions -----

    variables = [
        Variable(uid=UidVariable('V:k_in'),
                 name='k_in',
                 type=UidType('Integer'),
                 proxy_state=UidPort('P:loop_ex1.in.k'),
                 states=[UidPort('P:loop_ex1.in.k'),
                         UidWire('W:loop_ex1.loop_1.k'),
                         UidPort('P:loop_1.in.k')],
                 metadata=None),
        Variable(uid=UidVariable('V:k_out'),
                 name='k_out',
                 type=UidType('Integer'),
                 proxy_state=UidPort('P:loop_ex1.out.k'),
                 states=[UidPort('P:loop_ex1.out.k'),
                         UidPort('P:loop_1.out.k'),
                         UidWire('W:loop_1.loop_ex1.k')],
                 metadata=None),
        Variable(uid=UidVariable('V:i_loop_idx'),
                 name='i_loop_idx',
                 type=UidType('Integer'),
                 proxy_state=UidPort('P:loop_1.out.i'),
                 states=[UidPort('P:loop_1.out.i'),
                         UidPort('P:loop_1_i_exp.out.i'),
                         UidWire('W:loop_1_i_exp.loop_1.i')],
                 metadata=None),
        Variable(uid=UidVariable('V:k_loop'),
                 name='k_loop',
                 type=UidType('Integer'),
                 proxy_state=UidPort('P:loop_1.out.k'),
                 states=[UidPort('P:loop_1.out.k'),
                         UidPort('P:loop_1_k_exp.out.k'),
                         UidWire('W:loop_1_k_exp.loop_1.k')],
                 metadata=None)
    ]

    wires = [
        Wire(uid=UidWire('W:loop_ex1.loop_1.k'),
             type=None,
             value_type=UidType('Integer'),
             name=None, value=None, metadata=None,
             src=UidPort('P:loop_ex1.in.k'),
             tgt=UidPort('P:loop_1.in.k')),
        Wire(uid=UidWire('W:loop_1.loop_ex1.k'),
             type=None,
             value_type=UidType('Integer'),
             name=None, value=None, metadata=None,
             src=UidPort('P:loop_1.out.k'),
             tgt=UidPort('P:loop_ex1.out.k')),

        Wire(uid=UidWire('W:loop_1.loop_1_k_exp.k'),
             type=None,
             value_type=UidType('Integer'),
             name=None, value=None, metadata=None,
             src=UidPort('P:loop_1.in.k'),
             tgt=UidPort('P:loop_1_k_exp.in.k')),

        Wire(uid=UidWire('W:loop_1.loop_1_cond.i'),
             type=None,
             value_type=UidType('Integer'),
             name=None, value=None, metadata=None,
             src=UidPort('P:loop_1.in.i'),
             tgt=UidPort('P:loop_1_cond.in.i')),
        Wire(uid=UidWire('W:loop_1.loop_1_i_exp.i'),
             type=None,
             value_type=UidType('Integer'),
             name=None, value=None, metadata=None,
             src=UidPort('P:loop_1.in.i'),
             tgt=UidPort('P:loop_1_i_exp.in.i')),

        Wire(uid=UidWire('W:loop_1_i_exp.loop_1.i'),
             type=None,
             value_type=UidType('Integer'),
             name=None, value=None, metadata=None,
             src=UidPort('P:loop_1_i_exp.out.i'),
             tgt=UidPort('P:loop_1.out.i')),

        Wire(uid=UidWire('W:loop_1_k_exp.loop_1.k'),
             type=None,
             value_type=UidType('Integer'),
             name=None, value=None, metadata=None,
             src=UidPort('P:loop_1_k_exp.out.k'),
             tgt=UidPort('P:loop_1.out.k'))
    ]

    ports = [

        # loop_ex1 in
        Port(uid=UidPort('P:loop_ex1.in.k'),
             box=UidBox('B:loop_ex1'),
             type=UidType('PortInput'),
             value_type=UidType('Integer'),
             name='k',
             value=None,
             metadata=None),
        # loop_ex1 out
        Port(uid=UidPort('P:loop_ex1.out.k'),
             box=UidBox('B:loop_ex1'),
             type=UidType('PortOutput'),
             value_type=UidType('Integer'),
             name='k',
             value=None,
             metadata=None),

        # loop_1_cond in
        Port(uid=UidPort('P:loop_1_cond.in.i'),
             box=UidBox('B:loop_1_cond'),
             type=UidType('PortInput'),
             value_type=UidType('Integer'),
             name='i',
             value=None,
             metadata=None),
        # loop_1_cond out
        Port(uid=UidPort('P:loop_1_cond.out.exit'),
             box=UidBox('B:loop_1_cond'),
             type=UidType('PortOutput'),
             value_type=UidType('Boolean'),
             name='exit',
             value=None,
             metadata=None),

        # loop_1_i_exp in
        Port(uid=UidPort('P:loop_1_i_exp.in.i'),
             box=UidBox('B:loop_1_i_exp'),
             type=UidType('PortInput'),
             value_type=UidType('Integer'),
             name='i',
             value=None,
             metadata=None),
        # loop_1_i_exp out
        Port(uid=UidPort('P:loop_1_i_exp.out.i'),
             box=UidBox('B:loop_1_i_exp'),
             type=UidType('PortOutput'),
             value_type=UidType('Integer'),
             name='i',
             value=None,
             metadata=None),

        # loop_1_k_exp in
        Port(uid=UidPort('P:loop_1_k_exp.in.k'),
             box=UidBox('B:loop_1_k_exp'),
             type=UidType('PortInput'),
             value_type=UidType('Integer'),
             name='k',
             value=None,
             metadata=None),
        # loop_1_k_exp out
        Port(uid=UidPort('P:loop_1_k_exp.out.k'),
             box=UidBox('B:loop_1_k_exp'),
             type=UidType('PortOutput'),
             value_type=UidType('Integer'),
             name='k',
             value=None,
             metadata=None),

        # loop_1 in
        Port(uid=UidPort('P:loop_1.in.k'),
             box=UidBox('B:loop_1'),
             type=UidType('PortInput'),
             value_type=UidType('Integer'),
             name='k',
             value=None,
             metadata=None),
        Port(uid=UidPort('P:loop_1.in.i'),
             box=UidBox('B:loop_1'),
             type=UidType('PortInput'),
             value_type=UidType('Integer'),
             name='i',
             # loop index initialization:
             value=Literal(uid=None,
                           type=UidType('Integer'),
                           value=Val('0'),
                           name=None, metadata=None),
             metadata=None),
        # loop_1 out
        PortCall(uid=UidPort('P:loop_1.out.k'),
                 call=UidPort('P:loop_1.in.k'),
                 box=UidBox('B:loop_1'),
                 type=UidType('PortOutput'),
                 value_type=UidType('Integer'),
                 name='k',
                 value=None,
                 metadata=None),
        PortCall(uid=UidPort('P:loop_1.out.i'),
                 call=UidPort('P:loop_1.in.i'),
                 box=UidBox('B:loop_1'),
                 type=UidType('PortOutput'),
                 value_type=UidType('Integer'),
                 name='i',
                 value=None,
                 metadata=None),
    ]

    e0 = Expr(call=RefOp(UidOp('geq')),
              args=[UidPort('P:loop_1_cond.in.i'),
                    Literal(uid=None,
                            type=UidType('Integer'),
                            value=Val('5'),
                            name=None, metadata=None)])
    loop_1_cond = \
        Predicate(uid=UidBox('B:loop_1_cond'),
                  type=None,
                  name=None,
                  ports=[UidPort('P:loop_1_cond.in.i'),
                         UidPort('P:loop_1_cond.out.exit')],
                  tree=e0,
                  metadata=None)

    e1 = Expr(call=RefOp(UidOp('+')),
              args=[UidPort('P:loop_1_i_exp.in.i'),
                    Literal(uid=None,
                            type=UidType('Integer'),
                            value=Val('1'),
                            name=None, metadata=None)])
    loop_1_i_exp = \
        Expression(uid=UidBox('B:loop_1_i_exp'),
                   type=None,
                   name=None,
                   ports=[UidPort('P:loop_1_i_exp.in.i'),
                          UidPort('P:loop_1_i_exp.out.i')],
                   tree=e1,
                   metadata=None)

    e2 = Expr(call=RefOp(UidOp('+')),
              args=[UidPort('P:loop_1_k_exp.in.k'),
                    Literal(uid=None,
                            type=UidType('Integer'),
                            value=Val('1'),
                            name=None, metadata=None)])
    loop_1_k_exp = \
        Expression(uid=UidBox('B:loop_1_k_exp'),
                   type=None,
                   name=None,
                   ports=[UidPort('P:loop_1_k_exp.in.k'),
                          UidPort('P:loop_1_k_exp.out.k')],
                   tree=e2,
                   metadata=None)

    loop_1 = \
        Loop(uid=UidBox('B:loop_1'),
             type=None,
             name=None,
             ports=[UidPort('P:loop_1.in.k'),
                    UidPort('P:loop_1.out.k'),
                    UidPort('P:loop_1.in.i'),
                    UidPort('P:loop_1.out.i')],

             exit_condition=UidBox('B:loop_1_cond'),

             # contents
             wires=[UidWire('W:loop_1.loop_1_k_exp.k'),
                    UidWire('W:loop_1.loop_1_cond.i'),
                    UidWire('W:loop_1.loop_1_i_exp.i'),
                    UidWire('W:loop_1_i_exp.loop_1.i'),
                    UidWire('W:loop_1_k_exp.loop_1.k')],
             junctions=None,
             boxes=[UidBox('B:loop_1_i_exp'),
                    UidBox('B:loop_1_k_exp')],

             metadata=None)

    loop_ex1 = \
        Function(uid=UidBox('B:loop_ex1'),
                 type=None,
                 name='loop_ex1',
                 ports=[UidPort('P:loop_ex1.in.k'),
                        UidPort('P:loop_ex1.out.k')],

                 # contents
                 wires=[UidWire('W:loop_ex1.loop_1.k'),
                        UidWire('W:loop_1.loop_ex1.k')],
                 junctions=None,
                 boxes=[UidBox('B:loop_1')],

                 metadata=None)

    boxes = [loop_1, loop_1_cond, loop_1_i_exp, loop_1_k_exp, loop_ex1]

    _g = Gromet(
        uid=UidGromet("loop_ex1_uid"),
        name="loop_ex1",
        type=UidType("FunctionNetwork"),
        root=loop_ex1.uid,
        types=None,
        literals=None,
        junctions=None,
        ports=ports,
        wires=wires,
        boxes=boxes,
        variables=variables,
        metadata=[loop_ex1_interface]
    )

    return _g


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    gromet_to_json(generate_gromet())
