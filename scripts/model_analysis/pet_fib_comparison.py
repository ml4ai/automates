from model_analysis.networks import (
    GroundedFunctionNetwork,
    ForwardInfluenceBlanket,
)

G_pt = GroundedFunctionNetwork.from_fortran_file(
    "../../tests/data/program_analysis/PETPT.for"
)

G_asce = GroundedFunctionNetwork.from_fortran_file(
    "../../tests/data/program_analysis/PETASCE_simple.for"
)

G_pno = GroundedFunctionNetwork.from_fortran_file(
    "../../tests/data/program_analysis/PETPNO.for"
)
G_pen = GroundedFunctionNetwork.from_fortran_file(
    "../../tests/data/program_analysis/PETPEN.for"
)

G_dyn = GroundedFunctionNetwork.from_fortran_file(
    "../../tests/data/program_analysis/PETDYN.for"
)

grfns = [G_pt, G_asce, G_pno, G_pen, G_dyn]
names = ["PT", "ASCE", "PNO", "PEN", "DYN"]

for i, g1 in enumerate(grfns):
    for j, g2 in list(enumerate(grfns)):
        if i != j:
            f1 = ForwardInfluenceBlanket.from_GrFN(g1, g2)
            CAG = f1.CAG_to_AGraph()
            CAG.draw(
                f"FIB_{names[i]}--{names[i]}_vs_{names[j]}.pdf", prog="dot"
            )
