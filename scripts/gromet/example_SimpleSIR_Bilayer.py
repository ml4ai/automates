from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def simple_sir_PrTNet_gromet() -> Gromet:

    variables = []

    wires = []

    ports = [
    ]

    junctions = []

    boxes = []

    g = Gromet(
        uid=UidGromet("sir"),
        name="sir PrTNet",
        type=UidType("PrTNet"),
        root=sir.uid,
        types=None,
        literals=None,
        junctions=junctions,
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
    gromet_to_json(simple_sir_PrTNet_gromet())
