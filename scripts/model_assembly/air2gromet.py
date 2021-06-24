import sys
import json

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_assembly.air import AutoMATES_IR
from automates.model_assembly.gromet import Gromet, gromet_to_json


def main():
    air_filepath = sys.argv[1]
    air_json_data = json.load(open(air_filepath, "r"))
    AIR = AutoMATES_IR.from_air_json(air_json_data)
    GrFN = GroundedFunctionNetwork.from_AIR(AIR)
    # TODO: @Daniel enrich GrFN with metadata here
    GroMEt = Gromet.from_GrFN(GrFN)

    gromet_file = air_filepath.replace("AIR.json", "GroMEt.json")
    gromet_to_json(GroMEt, gromet_file)

    # A = G.to_AGraph()
    # grfn_pdf_name = air_filepath.replace("AIR.json", "GrFN.pdf")
    # A.draw(grfn_pdf_name, prog="dot")

    # G2 = GroundedFunctionNetwork.from_json(grfn_file)
    # assert G == G2


if __name__ == "__main__":
    main()
