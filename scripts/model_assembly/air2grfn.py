import sys

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_assembly.air import AutoMATES_IR


def main():
    air_filepath = sys.argv[1]
    AIR = AutoMATES_IR.from_json(air_filepath)
    G = GroundedFunctionNetwork.from_AIR(AIR)

    grfn_file = air_filepath.replace("AIR.json", "GrFN.json")
    G.to_json_file(grfn_file)

    A = G.to_AGraph()
    grfn_pdf_name = air_filepath.replace("AIR.json", "GrFN.pdf")
    A.draw(grfn_pdf_name, prog="dot")

    G2 = GroundedFunctionNetwork.from_json(grfn_file)
    assert G == G2


if __name__ == "__main__":
    main()
