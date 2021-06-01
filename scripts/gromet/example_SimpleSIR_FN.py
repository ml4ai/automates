from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def simple_sir_FN_gromet() -> Gromet:

    variables = [
        Variable(uid=UidVariable("S"), name="S", type=UidType("Float"),
                 states=[UidWire("W:S1.1"), UidWire("W:S1.2"),
                         UidWire("W:S2")],
                 metadata=None),
        Variable(uid=UidVariable("I"), name="I", type=UidType("Float"),
                 states=[UidWire("W:I1.1"), UidWire("W:I1.2"), UidWire("W:I1.3"),
                         UidWire("W:I2")],
                 metadata=None),
        Variable(uid=UidVariable("R"), name="R", type=UidType("Float"),
                 states=[UidWire("W:R1.1"), UidWire("W:R1.2"),
                         UidWire("W:R2")],
                 metadata=None),
        Variable(uid=UidVariable("beta"), name="beta", type=UidType("Float"),
                 states=[UidWire("W:beta")],
                 metadata=None),
        Variable(uid=UidVariable("gamma"), name="gamma", type=UidType("Float"),
                 states=[UidWire("W:gamma")],
                 metadata=None),
        Variable(uid=UidVariable("dt"), name="dt", type=UidType("Float"),
                 states=[UidWire("W:dt.1"), UidWire("W:dt.2")],
                 metadata=None),
        Variable(uid=UidVariable("infected"), name="infected", type=UidType("Float"),
                 states=[UidWire("W:infected.1"), UidWire("W:infected.2")],
                 metadata=None),
        Variable(uid=UidVariable("recovered"), name="recovered", type=UidType("Float"),
                 states=[UidWire("W:recovered.1"), UidWire("W:recovered.2")],
                 metadata=None),
    ]

    wires = [
        # Var "S"
        Wire(uid=UidWire("W:S1.1"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.S"),
             tgt=UidPort("P:infected_exp.in.S")),
        Wire(uid=UidWire("W:S1.2"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.S"),
             tgt=UidPort("P:S_update_exp.in.S")),

        # Var "I"
        Wire(uid=UidWire("W:I1.1"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.I"),
             tgt=UidPort("P:infected_exp.in.I")),
        Wire(uid=UidWire("W:I1.2"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.I"),
             tgt=UidPort("P:recovered_exp.in.I")),
        Wire(uid=UidWire("W:I1.3"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.I"),
             tgt=UidPort("P:I_update_exp.in.I")),
        # Var "R"
        Wire(uid=UidWire("W:R1.1"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.R"),
             tgt=UidPort("P:infected_exp.in.R")),
        Wire(uid=UidWire("W:R1.2"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.R"),
             tgt=UidPort("P:R_update_exp.in.R")),
        # Var "beta"
        Wire(uid=UidWire("W:beta"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.beta"),
             tgt=UidPort("P:infected_exp.in.beta")),
        # Var "gamma"
        Wire(uid=UidWire("W:gamma"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.gamma"),
             tgt=UidPort("P:recovered_exp.in.gamma")),
        # Var "dt"
        Wire(uid=UidWire("W:dt.1"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.dt"),
             tgt=UidPort("P:infected_exp.in.dt")),
        Wire(uid=UidWire("W:dt.2"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.dt"),
             tgt=UidPort("P:recovered_exp.in.dt")),

        # Wire for Var "infected"
        Wire(uid=UidWire("W:infected.1"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:infected_exp.out.infected"),
             tgt=UidPort("P:S_update_exp.in.infected")),
        Wire(uid=UidWire("W:infected.2"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:infected_exp.out.infected"),
             tgt=UidPort("P:I_update_exp.in.infected")),

        # Wire for Var "recovered"
        Wire(uid=UidWire("W:recovered.1"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:recovered_exp.out.recovered"),
             tgt=UidPort("P:I_update_exp.in.recovered")),
        Wire(uid=UidWire("W:recovered.2"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:recovered_exp.out.recovered"),
             tgt=UidPort("P:R_update_exp.in.recovered")),

        # part of Var "S"
        Wire(uid=UidWire("W:S2"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:S_update_exp.out.S"),
             tgt=UidPort("P:sir.out.S")),

        # part of Var "I"
        Wire(uid=UidWire("W:I2"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:I_update_exp.out.I"),
             tgt=UidPort("P:sir.out.I")),

        # part of Var "R"
        Wire(uid=UidWire("W:R2"),
             type=UidType("T:WireDirected"),
             value_type=UidType("T:Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:R_update_exp.out.R"),
             tgt=UidPort("P:sir.out.R")),
    ]

    ports = [
        # The input ports to the 'sir' outer/parent Function
        Port(uid=UidPort("P:sir.in.S"), box=UidBox("B:sir"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"),
             name="S", value=None, metadata=None),
        Port(uid=UidPort("P:sir.in.I"), box=UidBox("B:sir"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"),
             name="I", value=None, metadata=None),
        Port(uid=UidPort("P:sir.in.R"), box=UidBox("B:sir"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"),
             name="R", value=None, metadata=None),
        Port(uid=UidPort("P:sir.in.beta"), box=UidBox("B:sir"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"),
             name="beta", value=None, metadata=None),
        Port(uid=UidPort("P:sir.in.gamma"), box=UidBox("B:sir"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"),
             name="gamma", value=None, metadata=None),
        Port(uid=UidPort("P:sir.in.dt"), box=UidBox("B:sir"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"),
             name="dt", value=None, metadata=None),
        # The output ports to the 'sir' outer/parent Function
        Port(uid=UidPort("P:sir.out.S"), box=UidBox("B:sir"),
             type=UidType("T:PortOutput"),
             value_type=UidType("T:Float"),
             name="S", value=None, metadata=None),
        Port(uid=UidPort("P:sir.out.I"), box=UidBox("B:sir"),
             type=UidType("T:PortOutput"),
             value_type=UidType("T:Float"),
             name="I", value=None, metadata=None),
        Port(uid=UidPort("P:sir.out.R"), box=UidBox("B:sir"),
             type=UidType("T:PortOutput"),
             value_type=UidType("T:Float"),
             name="R", value=None, metadata=None),

        # The input ports to the 'infected_exp' anonymous assignment Expression
        Port(uid=UidPort("P:infected_exp.in.S"), box=UidBox("B:infected_exp"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"), name="S", value=None, metadata=None),
        Port(uid=UidPort("P:infected_exp.in.I"), box=UidBox("B:infected_exp"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"), name="I", value=None, metadata=None),
        Port(uid=UidPort("P:infected_exp.in.R"), box=UidBox("B:infected_exp"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"), name="R", value=None, metadata=None),
        Port(uid=UidPort("P:infected_exp.in.beta"), box=UidBox("B:infected_exp"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"), name="beta", value=None, metadata=None),
        Port(uid=UidPort("P:infected_exp.in.dt"), box=UidBox("B:infected_exp"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"), name="dt", value=None, metadata=None),
        # The output ports to the 'infected_exp' anonymous assignment Expression
        Port(uid=UidPort("P:infected_exp.out.infected"), box=UidBox("B:infected_exp"),
             type=UidType("T:PortOutput"),
             value_type=UidType("T:Float"), name="infected", value=None, metadata=None),

        # The input ports to the 'recovered_exp' anonymous assignment Expression
        Port(uid=UidPort("P:recovered_exp.in.I"), box=UidBox("B:recovered_exp"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"), name="I", value=None, metadata=None),
        Port(uid=UidPort("P:recovered_exp.in.gamma"), box=UidBox("B:recovered_exp"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"), name="gamma", value=None, metadata=None),
        Port(uid=UidPort("P:recovered_exp.in.dt"), box=UidBox("B:recovered_exp"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"), name="dt", value=None, metadata=None),
        # The output ports to the 'recovered_exp' anonymous assignment Expression
        Port(uid=UidPort("P:recovered_exp.out.recovered"), box=UidBox("B:recovered_exp"),
             type=UidType("T:PortOutput"),
             value_type=UidType("T:Float"), name="recovered", value=None, metadata=None),

        # The input ports to the 'S_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:S_update_exp.in.S"), box=UidBox("B:S_update_exp"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"), name="S", value=None, metadata=None),
        Port(uid=UidPort("P:S_update_exp.in.infected"), box=UidBox("B:S_update_exp"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"), name="infected", value=None, metadata=None),
        # The output ports to the 'S_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:S_update_exp.out.S"), box=UidBox("B:S_update_exp"),
             type=UidType("T:PortOutput"),
             value_type=UidType("T:Float"), name="S", value=None, metadata=None),

        # The input ports to the 'I_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:I_update_exp.in.I"), box=UidBox("B:I_update_exp"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"), name="I", value=None, metadata=None),
        Port(uid=UidPort("P:I_update_exp.in.infected"), box=UidBox("B:I_update_exp"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"), name="infected", value=None, metadata=None),
        Port(uid=UidPort("P:I_update_exp.in.recovered"), box=UidBox("B:I_update_exp"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"), name="recovered", value=None, metadata=None),
        # The output ports to the 'I_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:I_update_exp.out.I"), box=UidBox("B:I_update_exp"),
             type=UidType("T:PortOutput"),
             value_type=UidType("T:Float"), name="I", value=None, metadata=None),

        # The input ports to the 'R_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:R_update_exp.in.R"), box=UidBox("B:R_update_exp"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"), name="R", value=None, metadata=None),
        Port(uid=UidPort("P:R_update_exp.in.recovered"), box=UidBox("B:R_update_exp"),
             type=UidType("T:PortInput"),
             value_type=UidType("T:Float"), name="recovered", value=None, metadata=None),
        # The output ports to the 'R_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:R_update_exp.out.R"), box=UidBox("B:R_update_exp"),
             type=UidType("T:PortOutput"),
             value_type=UidType("T:Float"), name="R", value=None, metadata=None)
    ]

    # Expression 'infected_exp' (SIR-simple line 46) -- input: (S I R beta dt)
    # Expr's:
    # e1 : (* beta S I) -> e1
    e1 = Expr(call=RefOp(UidOp("*")),
              args=[UidPort("P:infected_exp.in.beta"),
                    UidPort("P:infected_exp.in.S"),
                    UidPort("P:infected_exp.in.I")])
    # e2 : (* e1 Literal(-1)) -> e2
    e2 = Expr(call=RefOp(UidOp("*")),
              args=[e1, Literal(uid=None, type=UidType("Int"), value=Val("-1"),
                                name=None, metadata=None)])
    # e3 : (+ S I R) -> e3
    e3 = Expr(call=RefOp(UidOp("+")),
              args=[UidPort("P:infected_exp.in.S"),
                    UidPort("P:infected_exp.in.I"),
                    UidPort("P:infected_exp.in.R")])
    # e4 : (/ e2 e3) -> e4
    e4 = Expr(call=RefOp(UidOp("/")), args=[e2, e3])
    # e5 : (* e4 dt) -> e5
    e5 = Expr(call=RefOp(UidOp("*")), args=[e4, UidPort("P:infected_exp.in.dt")])
    # The anonymous Expression
    infected_exp = Expression(uid=UidBox("B:infected_exp"),
                              type=None,
                              name=None,
                              ports=[UidPort("P:infected_exp.in.S"),
                                     UidPort("P:infected_exp.in.I"),
                                     UidPort("P:infected_exp.in.R"),
                                     UidPort("P:infected_exp.in.beta"),
                                     UidPort("P:infected_exp.in.dt"),
                                     UidPort("P:infected_exp.out.infected")],
                              tree=e5,
                              metadata=None)

    # Expression 'recovered_exp' (SIR-simple line 47) -- input: (gamma I dt)
    # Expr's:
    # e6 : (* gamma I) -> e6
    e6 = Expr(call=RefOp(UidOp("*")), args=[UidPort("P:recovered_exp.in.gamma"), UidPort("P:recovered_exp.in.I")])
    # e7 : (* e6 dt) -> e7
    e7 = Expr(call=RefOp(UidOp("*")), args=[e6, UidPort("P:recovered_exp.in.dt")])
    # The anonymous Expression
    recovered_exp = Expression(uid=UidBox("B:recovered_exp"),
                               type=None,
                               name=None,
                               ports=[UidPort("P:recovered_exp.in.I"),
                                      UidPort("P:recovered_exp.in.gamma"),
                                      UidPort("P:recovered_exp.in.dt"),
                                      UidPort("P:recovered_exp.out.recovered")],
                               tree=e7,
                               metadata=None)

    # Expression 'S_update_exp' (SIR-simple line 49) -- input: (S infected)
    # Expr's:
    # e8 : (- S infected) -> e8
    e8 = Expr(call=RefOp(UidOp("-")),
              args=[UidPort("P:S_update_exp.in.S"), UidPort("P:S_update_exp.in.infected")])
    # The anonymous Expression
    s_update_exp = Expression(uid=UidBox("B:S_update_exp"),
                              type=None,
                              name=None,
                              ports=[UidPort("P:S_update_exp.in.S"),
                                     UidPort("P:S_update_exp.in.infected"),
                                     UidPort("P:S_update_exp.out.S")],
                              tree=e8,
                              metadata=None)

    # Expression 'I_update_exp' (SIR-simple line 50) -- input: (I infected recovered)
    # Expr's
    # e9 : (+ I infected) -> e9
    e9 = Expr(call=RefOp(UidOp("+")),
              args=[UidPort("P:I_update_exp.in.I"), UidPort("P:I_update_exp.in.infected")])
    # e10 : (- e9 recovered) -> e10
    e10 = Expr(call=RefOp(UidOp("-")),
               args=[e9, UidPort("P:I_update_exp.in.recovered")])
    # The anonymous Expression
    i_update_exp = Expression(uid=UidBox("B:I_update_exp"),
                              type=None,
                              name=None,
                              ports=[UidPort("P:I_update_exp.in.I"),
                                     UidPort("P:I_update_exp.in.infected"),
                                     UidPort("P:I_update_exp.in.recovered"),
                                     UidPort("P:I_update_exp.out.I")],
                              tree=e10,
                              metadata=None)

    # Expression 'R_update_exp' (SIR-simple line 50) -- input: (R recovered)
    # Expr's
    # e11 : (+ R recovered) -> e11
    e11 = Expr(call=RefOp(UidOp("+")),
               args=[UidPort("P:R_update_exp.in.R"), UidPort("P:R_update_exp.in.recovered")])
    # The anonymous Expression
    r_update_exp = Expression(uid=UidBox("B:R_update_exp"),
                              type=None,
                              name=None,
                              ports=[UidPort("P:R_update_exp.in.R"),
                                     UidPort("P:R_update_exp.in.recovered"),
                                     UidPort("P:R_update_exp.out.R")],
                              tree=e11,
                              metadata=None)

    sir = Function(uid=UidBox("B:sir"),
                   type=None,
                   name=UidOp("sir"),
                   ports=[UidPort("P:sir.in.S"),
                          UidPort("P:sir.in.I"),
                          UidPort("P:sir.in.R"),
                          UidPort("P:sir.in.beta"),
                          UidPort("P:sir.in.gamma"),
                          UidPort("P:sir.in.dt"),
                          UidPort("P:sir.out.S"),
                          UidPort("P:sir.out.I"),
                          UidPort("P:sir.out.R")],

                   # contents
                   wires=[UidWire("W:S1.1"), UidWire("W:S1.2"),
                          UidWire("W:I1.1"), UidWire("W:I1.2"), UidWire("W:I1.3"),
                          UidWire("W:R1.1"), UidWire("W:R1.2"),
                          UidWire("W:beta"), UidWire("W:gamma"),
                          UidWire("W:dt.1"), UidWire("W:dt.2"),
                          UidWire("W:infected.1"), UidWire("W:infected.2"),
                          UidWire("W:recovered.1"), UidWire("W:recovered.2"),
                          UidWire("W:S2"), UidWire("W:I2"), UidWire("W:R2")],
                   boxes=[UidBox("B:infected_exp"),
                          UidBox("B:recovered_exp"),
                          UidBox("B:S_update_exp"),
                          UidBox("B:I_update_exp"),
                          UidBox("B:R_update_exp")],
                   junctions=None,

                   metadata=None)

    boxes = [sir, infected_exp, recovered_exp,
             s_update_exp, i_update_exp, r_update_exp]

    _g = Gromet(
        uid=UidGromet("SimpleSIR_FN"),
        name="SimpleSIR",
        type=UidType("FunctionNetwork"),
        root=sir.uid,
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
    gromet_to_json(simple_sir_FN_gromet())
