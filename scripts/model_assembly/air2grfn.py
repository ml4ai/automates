import json
import argparse

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_assembly.air import AutoMATES_IR


def main(args):

    air_filepath = args.air_filepath
    air_json_data = json.load(open(air_filepath, "r"))
    AIR = AutoMATES_IR.from_air_json(air_json_data)

    GrFN = GroundedFunctionNetwork.from_AIR(AIR)
    grfn_file = air_filepath.replace("AIR.json", "GrFN3.json")
    # GrFN.to_json_file(grfn_file)

    A = GrFN.to_AGraph(expand_expressions=False)
    grfn_pdf_name = air_filepath.replace("AIR.json", "GrFN3.pdf")
    # grfn_pdf_name = air_filepath.replace("AIR.json", "GrFN3_expanded.pdf")
    A.draw(grfn_pdf_name, prog="dot")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("air_filepath", help="Path to AIR file")

    main(parser.parse_args())
