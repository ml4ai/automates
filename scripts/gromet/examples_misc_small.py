from gromet import *  # never do this :)


if __name__ == "__main__":
    __t = TypeDeclaration(name=UidType("myType"),
                          type=Type(),
                          metadata=None)
    print(json.dumps(asdict(__t)))

    __lit = Literal(uid=UidLiteral("myLiteral"), type=UidType("myType"),
                    value=Val("infty"), metadata=None)
    print(json.dumps(asdict(__lit)))

    __p = Port(uid=UidPort("myPort"), box=UidBox("myBox"), type=UidType("Int"),
               name="myPort", metadata=None)
    print(json.dumps(asdict(__p)))

    __w = Wire(uid=UidWire("myWire"), type=UidType("Float"), value=None,
               metadata=None)
    print(json.dumps(asdict(__w)))

    __wd = WireDirected(uid=UidWire("myDirectedWire"), type=UidType("Float"), value=None,
                        input=UidPort("inPort"),
                        output=UidPort("outPort"),
                        metadata=None)
    print(json.dumps(asdict(__wd)))

    __wu = WireUndirected(uid=UidWire("myUndirectedWire"), type=UidType("Float"), value=None,
                          ports=(UidPort("p1"), UidJunction("p2")),
                          metadata=None)
    print(json.dumps(asdict(__wu)))

    __j = Junction(uid=UidJunction("myJunction"), type=UidType("Float"), value=None, metadata=None)
    print(json.dumps(asdict(__j)))

    __b = Box(uid=UidBox("myBox"), name="aBox", wiring=[UidWire("myWire")], type=None, metadata=None)
    print(json.dumps(asdict(__b)))

    __bu = BoxUndirected(uid=UidBox("myBoxUndirected"), name="aBox", wiring=[UidWire("myWire")],
                         ports=[UidPort("myPort")], type=None, metadata=None)
    print(json.dumps(asdict(__bu)))

    __bd = BoxDirected(uid=UidBox("myBoxDirected"), name="aBox",
                       type=None,
                       wiring=[UidWire("myWire")],
                       input_ports=[UidPort("in1"), UidPort("in2")],
                       output_ports=[UidPort("out1"), UidPort("out2")],
                       metadata=None)
    print(json.dumps(asdict(__bd)))

    __r = Relation(uid=UidBox("myRelation"), name="aBox", wiring=[UidWire("myWire")],
                   ports=[UidPort("p1"), UidPort("p2")], type=None, metadata=None)
    print(json.dumps(asdict(__r)))

    __f = Function(uid=UidBox("myFunction"), name=UidOp("aBox"),
                   type=None,
                   wiring=[UidWire("myWire")],
                   input_ports=[UidPort("in1"), UidPort("in2")],
                   output_ports=[UidPort("out1"), UidPort("out2")],
                   metadata=None)
    print(json.dumps(asdict(__f)))

    __exp = Expr(call=RefOp(UidOp("myExp")),
                 args=[UidPort("p1"), UidPort("p2")])
    print(json.dumps(asdict(__exp)))

    __exp2 = Expr(call=RefFn(UidFn("myFn")),
                  args=[UidPort("p1"), UidPort("p2")])
    print(json.dumps(asdict(__exp)))

    __e = Expression(uid=UidBox("myExpression"), name=UidOp("aBox"),
                     type=None,
                     tree=__exp,
                     wiring=None,
                     input_ports=[UidPort("in1"), UidPort("in2")],
                     output_ports=[UidPort("out")],
                     metadata=None)
    print(json.dumps(asdict(__e)))

    __pred = Predicate(uid=UidBox("myPredicate"), name=UidOp("aBox"),
                       type=None,
                       tree=__exp2,
                       wiring=None,
                       input_ports=[UidPort("in1"), UidPort("in2")],
                       output_ports=[UidPort("outBooleanPort")],
                       metadata=None)
    print(json.dumps(asdict(__pred)))

    # loop = Loop(uid=UidBox("myLoop"), name=UidOp("myLoop"),
    #             input_ports=[UidPort("in1"), UidPort("in2")],
    #             output_ports=[UidPort("out1"), UidPort("out2")],
    #             wiring=[UidWire("wire_from_in1_to_out_1"),
    #                     UidWire("wire_from_in2_to_out_2")],
    #             portmap=[(UidPort("out1"), UidPort("in1")),
    #                      (UidPort("out2"), UidPort("in2"))],
    #             exit=pred,
    #             metadata=None)
    # print(json.dumps(asdict(loop), indent=2))

    __v = Variable(uid=UidVariable("myVariable"),
                   name="nameOfMyVar",
                   type=UidType("myType"),
                   wires=[UidWire("wire1"), UidWire("wire2")],
                   metadata=None)
    print(json.dumps(asdict(__v)))

    __g = Gromet(
        uid=UidGromet("myGromet"),
        name="myGromet",
        type=UidType("FunctionNetwork"),
        root=__b.uid,
        types=[__t],
        ports=[__p],
        wires=[__w, __wd, __wu],
        boxes=[__b, __bd, __bu],
        variables=[__v],
        metadata=None
    )
    print(json.dumps(asdict(__g), indent=2))