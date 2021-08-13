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
        # done: k_in, k_out, loop_1.i_init, loop_1.i_out, loop_1.out.k
        Variable(uid=UidVariable('V:loop_ex1.in.k'),
                 name='k',
                 type=UidType('Integer'),
                 proxy_state=UidPort('P:loop_ex1.in.k'),
                 states=[UidPort('P:loop_ex1.in.k'),
                         UidWire('W:loop_ex1.loop_1.k'),
                         UidPort('P:loop_1.in.k')],
                 metadata=None),

        Variable(uid=UidVariable('V:loop_ex1.out.k'),
                 name='k',
                 type=UidType('Integer'),
                 proxy_state=UidPort('P:loop_ex1.out.k'),
                 states=[UidPort('P:loop_ex1.out.k'),
                         UidPort('P:loop_1.out.k'),
                         UidWire('W:loop_1.loop_ex1.k')],
                 metadata=None),

        Variable(uid=UidVariable('V:loop_ex1.loop_1.i_init'),
                 name='i',
                 type=UidType('Integer'),
                 proxy_state=UidJunction('J:loop_ex1.i'),
                 states=[UidJunction('J:loop_ex1.i'),
                         UidWire('W:loop_ex1.i>loop_1.in.i'),
                         UidPort('P:loop_1.in.i')],
                 metadata=None),

        Variable(uid=UidVariable('V:loop_1.in.i'),
                 name='i',
                 type=UidType('Integer'),
                 proxy_state=UidPort('P:loop_1.in.i'),
                 states=[UidPort('P:loop_1.in.i'),
                         UidWire('W:loop_1.loop_1_cond.i'),
                         UidPort('P:loop_1_cond.in.i'),
                         UidWire('W:loop_1.loop_1_i_exp.i'),
                         UidPort('P:loop_1_i_exp.in.i')],
                 metadata=None),

        Variable(uid=UidVariable('V:loop_1.in.k'),
                 name='i',
                 type=UidType('Integer'),
                 proxy_state=UidPort('P:loop_1.in.k'),
                 states=[UidPort('P:loop_1.in.k'),
                         UidWire('W:loop_1.loop_1_k_exp.k'),
                         UidPort('P:loop_1_k_exp.in.k')],
                 metadata=None),

        Variable(uid=UidVariable('V:loop_1.i_out'),
                 name='i',
                 type=UidType('Integer'),
                 proxy_state=UidPort('P:loop_1.out.i'),
                 states=[UidPort('P:loop_1.out.i'),
                         UidPort('P:loop_1_i_exp.out.i'),
                         UidWire('W:loop_1_i_exp.loop_1.i')],
                 metadata=None),

        Variable(uid=UidVariable('V:loop_1.out.k'),
                 name='k',
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

        # wiring loop_1 loop index i initialization Junction
        Wire(uid=UidWire('W:loop_ex1.i>loop_1.in.i'),
             type=None,
             value_type=UidType('Integer'),
             name=None, value=None, metadata=None,
             src=UidJunction('J:loop_ex1.i'),
             tgt=UidPort('P:loop_1.in.i')),

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

    junctions = [
        # loop index initialization:
        Junction(uid=UidJunction('J:loop_ex1.i'),
                 name='i',
                 type=None,
                 value=Literal(uid=None,
                               type=UidType('Integer'),
                               value=Val('0'),
                               name=None, metadata=None),
                 value_type=UidType('Integer'),
                 metadata=None)
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
             value=None,
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

    e0 = Expr(call=RefOp(UidOp('lt')),
              args=[UidPort('P:loop_1_cond.in.i'),
                    Literal(uid=None,
                            type=UidType('Integer'),
                            value=Val('5'),
                            name=None, metadata=None)])
    e0_not = Expr(call=RefOp(UidOp('not')),
                  args=[e0])
    loop_1_cond = \
        Predicate(uid=UidBox('B:loop_1_cond'),
                  type=None,
                  name=None,
                  ports=[UidPort('P:loop_1_cond.in.i'),
                         UidPort('P:loop_1_cond.out.exit')],
                  tree=e0_not,
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
                        UidWire('W:loop_1.loop_ex1.k'),
                        UidWire('W:loop_ex1.i>loop_1.in.i')],
                 junctions=[UidJunction('J:loop_ex1.i')],
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
        junctions=junctions,
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
