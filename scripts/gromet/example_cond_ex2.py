from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def generate_gromet() -> Gromet:

    # ----- Metadata -----

    # ----- Model component definitions -----

    variables = []

    wires = []

    ports = []

    cond_ex2 = \
        Function()

    boxes = []

    _g = Gromet(
        uid=UidGromet('cond_ex2'),
        name='cond_ex2',
        type=UidType('FunctionNetwork'),
        root=cond_ex2.uid,
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
