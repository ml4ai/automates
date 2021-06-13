from gromet import *  # never do this :)


"""
def bar(y: float) -> float:
    return y + 2  # bar_exp

def foo(x: float) -> float:
    return bar(x)  # bar_call

def main(a: float, b: float) -> float:
    a = foo(a)  # foo_call_1
    b = foo(b)  # foo_call_2
    return a + b
"""


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def generate_gromet() -> Gromet:

    variables = []

    wires = [

        # main
        Wire(uid=UidWire("W:main_a.foo_call_1_x_1"),
             type=None,
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:main.in.a"),
             tgt=UidPort("P:foo_call_1.in.x_1")),
        Wire(uid=UidWire("W:main_b.foo_call_2_x_2"),
             type=None,
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:main.in.b"),
             tgt=UidPort("P:foo_call_2.in.x_2")),
        Wire(uid=UidWire("W:main_foo_call_1_fo_1.main_exp_a"),
             type=None,
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:foo_call_1.out.fo_1"),
             tgt=UidPort("P:main_exp.in.a")),
        Wire(uid=UidWire("W:main_foo_call_2_fo_2.main_exp_b"),
             type=None,
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:foo_call_2.out.fo_2"),
             tgt=UidPort("P:main_exp.in.b")),
        Wire(uid=UidWire("W:main_exp_result.main_result"),
             type=None,
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:main_exp.out.result"),
             tgt=UidPort("P:main.out.result")),

        # foo
        Wire(uid=UidWire("W:foo_x.bar_call_y_1"),
             type=None,
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:foo.in.x"),
             tgt=UidPort("P:bar_call.in.y_1")),
        Wire(uid=UidWire("W:foo_bar_call_bo_1.fo"),
             type=None,
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:bar_call.out.bo_1"),
             tgt=UidPort("P:foo.out.fo")),

        # bar
        Wire(uid=UidWire("W:bar_y.exp_y"),
             type=None,
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:bar.in.y"),
             tgt=UidPort("P:bar_exp.in.y")),
        Wire(uid=UidWire("W:bar_exp_res.bo"),
             type=None,
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:bar_exp.out.result"),
             tgt=UidPort("P:bar.out.bo")),
    ]

    ports = [

        # main input
        Port(uid=UidPort("P:main.in.a"),
             box=UidBox("B:main"),
             type=UidType("PortInput"),
             value_type=UidType("T:Float"),
             name="a", value=None, metadata=None),
        Port(uid=UidPort("P:main.in.b"),
             box=UidBox("B:main"),
             type=UidType("PortInput"),
             value_type=UidType("T:Float"),
             name="b", value=None, metadata=None),
        # main output
        Port(uid=UidPort("P:main.out.result"),
             box=UidBox("B:main"),
             type=UidType("PortOutput"),
             value_type=UidType("T:Float"),
             name="result", value=None, metadata=None),

        # foo_call_1 input
        PortCall(uid=UidPort("P:foo_call_1.in.x_1"),
                 box=UidBox("B:foo_call_1"),
                 call=UidPort("P:foo.in.x"),
                 type=UidType("PortInput"),
                 value_type=UidType("T:Float"),
                 name=None, value=None, metadata=None),
        # foo_call_1 output
        PortCall(uid=UidPort("P:foo_call_1.out.fo_1"),
                 box=UidBox("B:foo_call_1"),
                 call=UidPort("P:foo.out.fo"),
                 type=UidType("PortOutput"),
                 value_type=UidType("T:Float"),
                 name=None, value=None, metadata=None),

        # foo_call_2 input
        PortCall(uid=UidPort("P:foo_call_2.in.x_2"),
                 box=UidBox("B:foo_call_2"),
                 call=UidPort("P:foo.in.x"),
                 type=UidType("PortInput"),
                 value_type=UidType("T:Float"),
                 name=None, value=None, metadata=None),
        # foo_call_2 output
        PortCall(uid=UidPort("P:foo_call_2.out.fo_2"),
                 box=UidBox("B:foo_call_2"),
                 call=UidPort("P:foo.out.fo"),
                 type=UidType("PortOutput"),
                 value_type=UidType("T:Float"),
                 name=None, value=None, metadata=None),

        # main_exp input
        Port(uid=UidPort("P:main_exp.in.a"),
             box=UidBox("B:main_exp"),
             type=UidType("PortInput"),
             value_type=UidType("T:Float"),
             name="a", value=None, metadata=None),
        Port(uid=UidPort("P:main_exp.in.b"),
             box=UidBox("B:main_exp"),
             type=UidType("PortInput"),
             value_type=UidType("T:Float"),
             name="b", value=None, metadata=None),
        # main_exp output
        Port(uid=UidPort("P:main_exp.out.result"),
             box=UidBox("B:main_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("T:Float"),
             name="result", value=None, metadata=None),


        # foo input
        Port(uid=UidPort("P:foo.in.x"),
             box=UidBox("B:foo"),
             type=UidType("PortInput"),
             value_type=UidType("T:Float"),
             name="x", value=None, metadata=None),
        # foo output
        Port(uid=UidPort("P:foo.out.fo"),
             box=UidBox("B:foo"),
             type=UidType("PortOutput"),
             value_type=UidType("T:Float"),
             name="fo", value=None, metadata=None),

        # bar_call input
        PortCall(uid=UidPort("P:bar_call.in.y_1"),
                 box=UidBox("B:bar_call"),
                 call=UidPort("P:bar.in.y"),
                 type=UidType("PortInput"),
                 value_type=UidType("T:Float"),
                 name=None, value=None, metadata=None),
        # bar_call output
        PortCall(uid=UidPort("P:bar_call.out.bo_1"),
                 box=UidBox("B:bar_call"),
                 call=UidPort("P:bar.out.bo"),
                 type=UidType("PortOutput"),
                 value_type=UidType("T:Float"),
                 name=None, value=None, metadata=None),

        # bar input
        Port(uid=UidPort("P:bar.in.y"),
             box=UidBox("B:bar"),
             type=UidType("PortInput"),
             value_type=UidType("T:Float"),
             name="y", value=None, metadata=None),
        # bar output
        Port(uid=UidPort("P:bar.out.bo"),
             box=UidBox("B:bar"),
             type=UidType("PortOutput"),
             value_type=UidType("T:Float"),
             name="bo", value=None, metadata=None),

        # bar_exp input
        Port(uid=UidPort("P:bar_exp.in.y"),
             box=UidBox("B:bar_exp"),
             type=UidType("PortInput"),
             value_type=UidType("T:Float"),
             name="y", value=None, metadata=None),
        # bar_exp output
        Port(uid=UidPort("P:bar_exp.out.result"),
             box=UidBox("B:bar_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("T:Float"),
             name="result", value=None, metadata=None),
    ]

    # -- main --

    foo_call_1 = BoxCall(uid=UidBox("B:foo_call_1"),
                         type=None,
                         name=None,
                         call=UidBox("B:foo"),
                         ports=[UidPort("P:foo_call_1.in.x_1"),
                                UidPort("P:foo_call_1.out.fo_1")],
                         metadata=None)

    foo_call_2 = BoxCall(uid=UidBox("B:foo_call_2"),
                         type=None,
                         name=None,
                         call=UidBox("B:foo"),
                         ports=[UidPort("P:foo_call_2.in.x_2"),
                                UidPort("P:foo_call_2.out.fo_2")],
                         metadata=None)

    e1 = Expr(call=RefOp(UidOp("+")),
              args=[UidPort("P:main_exp.in.a"),
                    UidPort("P:main_exp.in.b")])
    main_exp = Expression(uid=UidBox("B:main_exp"),
                          type=None,
                          name=None,
                          ports=[UidPort("P:main_exp.in.a"),
                                 UidPort("P:main_exp.in.b"),
                                 UidPort("P:main_exp.out.result")],
                          tree=e1,
                          metadata=None)

    main = Function(uid=UidBox("B:main"),
                    type=None,
                    name="main",
                    ports=[UidPort("P:main.in.a"),
                           UidPort("P:main.in.b"),
                           UidPort("P:main.out.result")],

                    # contents
                    wires=[UidWire("W:main_a.foo_call_1_x_1"),
                           UidWire("W:main_b.foo_call_2_x_2"),
                           UidWire("W:main_foo_call_1_fo_1.main_exp_a"),
                           UidWire("W:main_foo_call_2_fo_2.main_exp_b"),
                           UidWire("W:main_exp_result.main_result")],
                    boxes=[UidBox("B:foo_call_1"),
                           UidBox("B:foo_call_2"),
                           UidBox("B:main_exp")],
                    junctions=None,

                    metadata=None)

    # -- foo --

    bar_call = BoxCall(uid=UidBox("B:bar_call"),
                       type=None,
                       name=None,
                       call=UidBox("B:bar"),
                       ports=[UidPort("P:bar_call.in.y_1"),
                              UidPort("P:bar_call.out.bo_1")],
                       metadata=None)

    foo = Function(uid=UidBox("B:foo"),
                   type=None,
                   name="foo",
                   ports=[UidPort("P:foo.in.x"),
                          UidPort("P:foo.out.fo")],

                   # contents
                   wires=[UidWire("W:foo_x.bar_call_y_1"),
                          UidWire("W:foo_bar_call_bo_1.fo")],
                   boxes=[UidBox("B:bar_call")],
                   junctions=None,

                   metadata=None)

    # -- bar --

    e2 = Expr(call=RefOp(UidOp("+")),
              args=[UidPort("P:bar_exp.in.y"),
                    Literal(uid=None, type=UidType("T:Float"), value=Val("2"), name=None, metadata=None)])
    bar_exp = Expression(uid=UidBox("B:bar_exp"),
                         type=None,
                         name=None,
                         ports=[UidPort("P:bar_exp.in.y"),
                                UidPort("P:bar_exp.out.result")],
                         tree=e2,
                         metadata=None)

    bar = Function(uid=UidBox("B:bar"),
                   type=None,
                   name="bar",
                   ports=[UidPort("P:bar.in.y"),
                          UidPort("P:bar.out.bo")],

                   # contents
                   wires=[UidWire("W:bar_y.exp_y"),
                          UidWire("W:bar_exp_res.bo")],
                   boxes=[UidBox("B:bar_exp")],
                   junctions=None,

                   metadata=None)

    boxes = [main, foo_call_1, foo_call_2, main_exp,
             foo, bar_call,
             bar, bar_exp]

    _g = Gromet(
        uid=UidGromet("call_ex1"),
        name="call_ex1",
        type=UidType("FunctionNetwork"),
        root=main.uid,
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