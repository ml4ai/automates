from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def simple_sir_gromet() -> Gromet:

    variables = [
        Variable(name="S", type=UidType("Float"),
                 wires=[UidWire("W:S1"), UidWire("W:S2")],
                 metadata=None),
        Variable(name="I", type=UidType("Float"),
                 wires=[UidWire("W:I1"), UidWire("W:I2")],
                 metadata=None),
        Variable(name="R", type=UidType("Float"),
                 wires=[UidWire("W:R1"), UidWire("W:R2")],
                 metadata=None),
        Variable(name="beta", type=UidType("Float"),
                 wires=[UidWire("W:beta")],
                 metadata=None),
        Variable(name="gamma", type=UidType("Float"),
                 wires=[UidWire("W:gamma")],
                 metadata=None),
        Variable(name="dt", type=UidType("Float"),
                 wires=[UidWire("W:dt")],
                 metadata=None),
        Variable(name="recovered", type=UidType("Float"),
                 wires=[UidWire("W:recovered")],
                 metadata=None),
        Variable(name="infected", type=UidType("Float"),
                 wires=[UidWire("W:infected")],
                 metadata=None),
    ]

    wires = [
        # Var "S"
        WireDirected(uid=UidWire("W:S1"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:sir.in.S"),
                     output=[UidPort("P:infected_exp.in.S"),
                             UidPort("P:S_exp.in.S")]),
        # Var "I"
        WireDirected(uid=UidWire("W:I1"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:sir.in.I"),
                     output=[UidPort("P:infected_exp.in.I"),
                             UidPort("P:recovered_exp.in.I"),
                             UidPort("P:I_update_exp.in.I")]),
        # Var "R"
        WireDirected(uid=UidWire("W:R1"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:sir.in.R"),
                     output=[UidPort("P:infected_exp.in.R"),
                             UidPort("P:I_update_exp.in.R")]),
        # Var "beta"
        WireDirected(uid=UidWire("W:beta"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:sir.in.beta"),
                     output=[UidPort("P:infected_exp.in.beta")]),
        # Var "gamma"
        WireDirected(uid=UidWire("W:gamma"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:sir.in.gamma"),
                     output=[UidPort("P:recovered_exp.in.gamma")]),
        # Var "dt"
        WireDirected(uid=UidWire("W:dt"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:sir.in.dt"),
                     output=[UidPort("P:infected_exp.in.dt"),
                             UidPort("P:recovered_exp.in.dt")]),

        # Wire for Var "infected"
        WireDirected(uid=UidWire("W:infected"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:infected_exp.out.infected"),
                     output=[UidPort("P:S_update_exp.in.infected"),
                             UidPort("P:I_update_exp.in.infected")]),

        # Wire for Var "recovered"
        WireDirected(uid=UidWire("W:recovered"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:recovered_exp.out.recovered"),
                     output=[UidPort("P:I_update_exp.in.recovered"),
                             UidPort("P:R_update_exp.in.recovered")]),

        # part of Var "S"
        WireDirected(uid=UidWire("W:S2"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:S_update_exp.out.S"),
                     output=[UidPort("P:sir.out.S")]),

        # part of Var "I"
        WireDirected(uid=UidWire("W:I2"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:I_update_exp.out.I"),
                     output=[UidPort("P:sir.out.I")]),

        # part of Var "R"
        WireDirected(uid=UidWire("W:R2"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:R_update_exp.out.R"),
                     output=[UidPort("P:sir.out.R")]),
    ]

    ports = [
        # The input ports to the 'sir' outer/parent Function
        Port(uid=UidPort("P:sir.in.S"), type=UidType("T:Float"), name="S", metadata=None),
        Port(uid=UidPort("P:sir.in.I"), type=UidType("T:Float"), name="I", metadata=None),
        Port(uid=UidPort("P:sir.in.R"), type=UidType("T:Float"), name="R", metadata=None),
        Port(uid=UidPort("P:sir.in.beta"), type=UidType("T:Float"), name="beta", metadata=None),
        Port(uid=UidPort("P:sir.in.gamma"), type=UidType("T:Float"), name="gamma", metadata=None),
        Port(uid=UidPort("P:sir.in.dt"), type=UidType("T:Float"), name="dt", metadata=None),
        # The output ports to the 'sir' outer/parent Function
        Port(uid=UidPort("P:sir.out.S"), type=UidType("T:Float"), name="S", metadata=None),
        Port(uid=UidPort("P:sir.out.I"), type=UidType("T:Float"), name="I", metadata=None),
        Port(uid=UidPort("P:sir.out.R"), type=UidType("T:Float"), name="R", metadata=None),

        # The input ports to the 'infected_exp' anonymous assignment Expression
        Port(uid=UidPort("P:infected_exp.in.S"), type=UidType("T:Float"), name="S", metadata=None),
        Port(uid=UidPort("P:infected_exp.in.I"), type=UidType("T:Float"), name="I", metadata=None),
        Port(uid=UidPort("P:infected_exp.in.R"), type=UidType("T:Float"), name="R", metadata=None),
        Port(uid=UidPort("P:infected_exp.in.beta"), type=UidType("T:Float"), name="beta", metadata=None),
        Port(uid=UidPort("P:infected_exp.in.dt"), type=UidType("T:Float"), name="dt", metadata=None),
        # The output ports to the 'infected_exp' anonymous assignment Expression
        Port(uid=UidPort("P:infected_exp.out.infected"), type=UidType("T:Float"), name="infected", metadata=None),

        # The input ports to the 'recovered_exp' anonymous assignment Expression
        Port(uid=UidPort("P:recovered_exp.in.I"), type=UidType("T:Float"), name="I", metadata=None),
        Port(uid=UidPort("P:recovered_exp.in.gamma"), type=UidType("T:Float"), name="gamma", metadata=None),
        Port(uid=UidPort("P:recovered_exp.in.dt"), type=UidType("T:Float"), name="dt", metadata=None),
        # The output ports to the 'recovered_exp' anonymous assignment Expression
        Port(uid=UidPort("P:recovered_exp.out.recovered"), type=UidType("T:Float"), name="recovered", metadata=None),

        # The input ports to the 'S_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:S_update_exp.in.S"), type=UidType("T:Float"), name="S", metadata=None),
        Port(uid=UidPort("P:S_update_exp.in.infected"), type=UidType("T:Float"), name="infected", metadata=None),
        # The output ports to the 'S_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:S_update_exp.out.S"), type=UidType("T:Float"), name="S", metadata=None),

        # The input ports to the 'I_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:I_update_exp.in.I"), type=UidType("T:Float"), name="I", metadata=None),
        Port(uid=UidPort("P:I_update_exp.in.infected"), type=UidType("T:Float"), name="infected", metadata=None),
        Port(uid=UidPort("P:I_update_exp.in.recovered"), type=UidType("T:Float"), name="recovered", metadata=None),
        # The output ports to the 'I_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:I_update_exp.out.I"), type=UidType("T:Float"), name="I", metadata=None),

        # The input ports to the 'R_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:R_update_exp.in.R"), type=UidType("T:Float"), name="R", metadata=None),
        Port(uid=UidPort("P:R_update_exp.in.recovered"), type=UidType("T:Float"), name="recovered", metadata=None),
        # The output ports to the 'R_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:R_update_exp.out.R"), type=UidType("T:Float"), name="R", metadata=None)
    ]

    # Expression 'infected_exp' (SIR-simple line 46) -- input: (S I R beta dt)
    # Exp's:
    # e1 : (* beta S I) -> e1
    e1 = Exp(operator=UidOp("*"),
             args=[UidPort("P:infected_exp.in.beta"),
                   UidPort("P:infected_exp.in.S"),
                   UidPort("P:infected_exp.in.I")])
    # e2 : (* e1 Literal(-1)) -> e2
    e2 = Exp(operator=UidOp("*"),
             args=[e1, Literal(uid=None, type=UidType("Int"), value="-1", metadata=None)])
    # e3 : (+ S I R) -> e3
    e3 = Exp(operator=UidOp("+"),
             args=[UidPort("P:infected_exp.in.S"),
                   UidPort("P:infected_exp.in.I"),
                   UidPort("P:infected_exp.in.R")])
    # e4 : (/ e2 e3) -> e4
    e4 = Exp(operator=UidOp("/"), args=[e2, e3])
    # e5 : (* e4 dt) -> e5
    e5 = Exp(operator=UidOp("*"), args=[e4, UidPort("P:infected_exp.in.dt")])
    # The anonymous Expression
    infected_exp = Expression(uid=UidBox("B:infected_exp"),
                              name=None,
                              input_ports=[UidPort("P:infected_exp.in.S"),
                                           UidPort("P:infected_exp.in.I"),
                                           UidPort("P:infected_exp.in.R"),
                                           UidPort("P:infected_exp.in.beta"),
                                           UidPort("P:infected_exp.in.dt")],
                              output_ports=[UidPort("P:infected_exp.out.infected")],
                              wiring=e5,
                              metadata=None)

    # Expression 'recovered_exp' (SIR-simple line 47) -- input: (gamma I dt)
    # Exp's:
    # e6 : (* gamma I) -> e6
    e6 = Exp(operator=UidOp("*"), args=[UidPort("P:sir.in.gamma"), UidPort("P:sir.in.I")])
    # e7 : (* e6 dt) -> e7
    e7 = Exp(operator=UidOp("*"), args=[e6, UidPort("P:sir.in.dt")])
    # The anonymous Expression
    recovered_exp = Expression(uid=UidBox("B:recovered_exp"),
                               name=None,
                               input_ports=[UidPort("P:recovered_exp.in.I"),
                                            UidPort("P:recovered_exp.in.gamma"),
                                            UidPort("P:recovered_exp.in.dt")],
                               output_ports=[UidPort("P:recovered_exp.out.infected")],
                               wiring=e7,
                               metadata=None)

    # Expression 'S_update_exp' (SIR-simple line 49) -- input: (S infected)
    # Exp's:
    # e8 : (- S infected) -> e8
    e8 = Exp(operator=UidOp("-"),
             args=[UidPort("P:S_update_exp.in.S"), UidPort("P:S_update_exp.in.infected")])
    # The anonymous Expression
    s_update_exp = Expression(uid=UidBox("B:S_update_exp"),
                              name=None,
                              input_ports=[UidPort("P:S_update_exp.in.S"),
                                           UidPort("P:S_update_exp.in.infected")],
                              output_ports=[UidPort("P:S_update_exp.out.S")],
                              wiring=e8,
                              metadata=None)

    # Expression 'I_update_exp' (SIR-simple line 50) -- input: (I infected recovered)
    # Exp's
    # e9 : (+ I infected) -> e9
    e9 = Exp(operator=UidOp("+"),
             args=[UidPort("P:I_update_exp.in.I"), UidPort("P:I_update_exp.in.infected")])
    # e10 : (- e9 recovered) -> e10
    e10 = Exp(operator=UidOp("-"),
              args=[e9, UidPort("P:I_update_exp.in.recovered")])
    # The anonymous Expression
    i_update_exp = Expression(uid=UidBox("B:I_update_exp"),
                              name=None,
                              input_ports=[UidPort("P:I_update_exp.in.I"),
                                           UidPort("P:I_update_exp.in.infected"),
                                           UidPort("P:I_update_exp.in.recovered")],
                              output_ports=[UidPort("P:I_update_exp.out.I")],
                              wiring=e10,
                              metadata=None)

    # Expression 'R_update_exp' (SIR-simple line 50) -- input: (R recovered)
    # Exp's
    # e11 : (+ R recovered) -> e11
    e11 = Exp(operator=UidOp("+"),
              args=[UidPort("P:R_update_exp.in.R"), UidPort("P:R_update_exp.in.recovered")])
    # The anonymous Expression
    r_update_exp = Expression(uid=UidBox("B:R_update_exp"),
                              name=None,
                              input_ports=[UidPort("P:R_update_exp.in.R"),
                                           UidPort("P:R_update_exp.in.recovered")],
                              output_ports=[UidPort("P:R_update_exp.out.R")],
                              wiring=e11,
                              metadata=None)

    sir = Function(uid=UidBox("B:sir"),
                   name=UidOp("sir"),
                   input_ports=[UidPort("P:sir.in.S"),
                                UidPort("P:sir.in.I"),
                                UidPort("P:sir.in.R"),
                                UidPort("P:sir.in.beta"),
                                UidPort("P:sir.in.gamma"),
                                UidPort("P:sir.in.dt")],
                   output_ports=[UidPort("P:sir.out.S"),
                                 UidPort("P:sir.out.I"),
                                 UidPort("P:sir.out.R")],
                   # this is redundant with having explicit top-level wires list
                   wiring=[UidWire("W:S1"), UidWire("W:I1"), UidWire("W:R1"),
                           UidWire("W:beta"), UidWire("W:gamma"), UidWire("W:dt"),
                           UidWire("W:infected"), UidWire("W:recovered"),
                           UidWire("W:S2"), UidWire("W:I2"), UidWire("W:R2")],
                   metadata=None)

    g = Gromet(
        uid=UidGromet("SimpleSIR"),
        name="SimpleSIR",
        framework_type="FunctionNetwork",
        root=sir.uid,
        types=None,
        ports=ports,
        wires=wires,
        boxes=[sir, infected_exp, recovered_exp,
               s_update_exp, i_update_exp, r_update_exp],
        variables=variables,
        metadata=None
    )

    return g


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    gromet_to_json(simple_sir_gromet())

