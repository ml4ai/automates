from gromet import *  # never do this :)

if __name__ == "__main__":
    __t = TypeDeclaration(name=UidType("myType"),
                          type=Type(),
                          metadata=None)
    print(json.dumps(asdict(__t)))

    __lit = Literal(uid=UidLiteral("myLiteral"),
                    name=None,
                    type=UidType("myType"),
                    value=Val("infty"), metadata=None)
    print(json.dumps(asdict(__lit)))

    __p = Port(uid=UidPort("myPort"), box=UidBox("myBox"),
               type=UidType("PortInput"),
               value_type=UidType("Integer"),
               name="myPort", value=None, metadata=None)
    print(json.dumps(asdict(__p)))

    __w = Wire(uid=UidWire("myWire"), type=UidType("Float"),
               value=None,
               value_type=None,
               src=UidPort("P:some_port"),
               tgt=UidPort("P:another_port"),
               name=None, metadata=None)
    print(json.dumps(asdict(__w)))

    __wd = Wire(uid=UidWire("myDirectedWire"), type=UidType("Float"),
                value=None,
                value_type=None,
                src=UidPort("inPort"),
                tgt=UidPort("outPort"),
                name=None, metadata=None)
    print(json.dumps(asdict(__wd)))

    __wu = Wire(uid=UidWire("myUndirectedWire"), type=UidType("Float"),
                value=None,
                value_type=None,
                src=UidPort("p1"),
                tgt=UidJunction("p2"),
                name=None, metadata=None)
    print(json.dumps(asdict(__wu)))

    __j = Junction(uid=UidJunction("myJunction"), type=UidType("Float"),
                   value=None,
                   value_type=UidType("Real"),
                   name=None, metadata=None)
    print(json.dumps(asdict(__j)))

    __b = Box(uid=UidBox("myBox"), name="B:box", type=None,
              ports=[UidPort("P:my_first_port"), UidPort("P:my_second_port")],
              metadata=None)
    print(json.dumps(asdict(__b)))

    __r = Relation(uid=UidBox("myRelation"), name="aBox",
                   ports=[UidPort("p1"), UidPort("p2")],

                   # contents:
                   wires=[UidWire("myWire")],
                   boxes=[UidBox("someBox")],
                   junctions=[UidJunction("myJunction")],

                   type=None, metadata=None)
    print(json.dumps(asdict(__r)))

    __f = Function(uid=UidBox("myFunction"), name=UidOp("aBox"),
                   type=None,
                   ports=[UidPort("in1"), UidPort("in2"),
                          UidPort("out1"), UidPort("out2")],

                   # contents
                   wires=[UidWire("myWire")],
                   boxes=[UidBox("myBox")],
                   junctions=None,

                   metadata=None)
    print(json.dumps(asdict(__f)))

    __exp = Expr(call=RefOp(UidOp("myExp")),
                 args=[UidPort("p1"), UidPort("p2")])
    print(json.dumps(asdict(__exp)))

    __exp2 = Expr(call=RefBox(UidBox("myFn")),
                  args=[UidPort("p1"), UidPort("p2")])
    print(json.dumps(asdict(__exp)))

    __e = Expression(uid=UidBox("myExpression"), name=UidOp("aBox"),
                     type=None,
                     tree=__exp,
                     ports=[UidPort("in1"), UidPort("in2"),
                            UidPort("out")],
                     metadata=None)
    print(json.dumps(asdict(__e)))

    __pred = Predicate(uid=UidBox("myPredicate"), name=UidOp("aBox"),
                       type=None,
                       tree=__exp2,
                       ports=[UidPort("in1"), UidPort("in2"),
                              UidPort("outBooleanPort")],
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
                   proxy_state=UidWire("wire1"),
                   states=[UidWire("wire1"), UidWire("wire2")],
                   metadata=None)
    print(json.dumps(asdict(__v)))

    __g = Gromet(
        uid=UidGromet("myGromet"),
        name="myGromet",
        type=UidType("FunctionNetwork"),
        root=__b.uid,
        types=[__t],
        literals=None,
        ports=[__p],
        wires=[__w, __wd, __wu],
        junctions=None,
        boxes=[__b],
        variables=[__v],
        metadata=None
    )
    print(json.dumps(asdict(__g), indent=2))
