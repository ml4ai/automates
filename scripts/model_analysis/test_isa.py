import networkx as nx

from model_analysis.sensitivity import ISA, SensitivityAnalyzer
from model_analysis.networks import GroundedFunctionNetwork


G = GroundedFunctionNetwork.from_fortran_file(
    "tests/data/program_analysis/PETPT.for"
)
B = {
    "tmax": [-30.0, 60.0],
    "tmin": [-30.0, 60.0],
    "srad": [0.0, 30.0],
    "msalb": [0.0, 1.0],
    "xhlai": [0.0, 20.0],
}
N = 1000
analyzer = SensitivityAnalyzer.Si_from_RBD_FAST
V = ISA(G, B, N, analyzer, max_iterations=7)
V.graph["graph"] = {"rankdir": "LR"}
V.graph["edges"] = {"arrowsize": "4.0"}
A = nx.nx_agraph.to_agraph(V)
A.draw("isa-graph.pdf", prog="dot")
