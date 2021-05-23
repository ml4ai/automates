from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def simple_sir_GRPnet_gromet() -> Gromet:
    ports = [
        Port(uid=UidPort("P:sir_model:S"), box=UidBox("B:sir"),type=UidType("T:Float"), name="S", metadata=None),
        Port(uid=UidPort("P:sir_model:I"), box=UidBox("B:sir"),type=UidType("T:Float"), name="I", metadata=None),
        Port(uid=UidPort("P:sir_model:R"), box=UidBox("B:sir"),type=UidType("T:Float"), name="R", metadata=None)
    ]
    wires = []
    boxes = []
    variables = []
    sir_model = Relation(uid=UidBox("B:sir"),
                    name=UidOp("sir"),
                    ports=[],
                    wiring=[],
                    metadata=None)
    infect_enabling = Relation(uid=UidBox("B:infect_enabling"),
                               name=UidOp("infect_enabling"),
                               ports=[],
                               wiring=[],
                               metadata=None
    )
    infect_rate = Relation(uid=UidBox("B:infect_rate"),
                           name=UidOp("infect_rate"),
                           ports=[],
                           wiring=[],
                           metadata=None
    )
    infect_effect = Relation(uid=UidBox("B:infect_effect"),
                             name=UidOp("infect_effect"),
                             ports=[],
                             wiring=[],
                             metadata=None
    )
    infect_event = PetriEvent(uid=UidBox("B:infect_event"),
                              name=UidOp("infect_event"),
                              enabling_condition = infect_enabling,
                              rate = infect_rate,
                              effect = infect_effect,
                              ports=[],
                              wiring=[],
                              metadata=None
    )
    recover_enabling = Relation(uid=UidBox("B:recover_enabling"),
                                name=UidOp("recover_enabling"),
                                ports=[],
                                wiring=[],
                                metadata=None
    )
    recover_rate = Relation(uid=UidBox("B:recover_rate"),
                            name=UidOp("recover_rate"),
                            ports=[],
                            wiring=[],
                            metadata=None
    )
    recover_effect = Relation(uid=UidBox("B:recover_effect"),
                              name=UidOp("recover_effect"),
                              ports=[],
                              wiring=[],
                              metadata=None
    )
    recover_event = PetriEvent(uid=UidBox("B:recover_event"),
                               name=UidOp("recover_event"),
                               enabling_condition = recover_enabling,
                               rate = recover_rate,
                               effect = recover_effect,
                               ports=[],
                               wiring=[],
                               metadata=None
    )
    g = Gromet(
        uid=UidGromet("sir"),
        name="sir",
        framework_type="FunctionNetwork",
        root=sir_model.name,
        types=None,
        ports=ports,
        wires=wires,
        boxes=boxes,
        variables=variables,
        metadata=None
    )
    return g


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    gromet_to_json(simple_sir_GRPnet_gromet())