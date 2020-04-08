from model_analysis.sensitivity import ISA, SensitivityAnalyzer
from model_analysis.networks import GroundedFunctionNetwork


G = GroundedFunctionNetwork.from_fortran_file(
    f"../../tests/data/program_analysis/PETPT.for"
)
B = {
    "tmax": [-30.0, 60.0],
    "tmin": [-30.0, 60.0],
    "srad": [0.0, 30.0],
    "msalb": [0.0, 1.0],
    "xhlai": [0.0, 20.0],
}
N = 10000
analyzer = SensitivityAnalyzer.Si_from_Sobol
res = ISA(G, B, N, analyzer)
print(res)
