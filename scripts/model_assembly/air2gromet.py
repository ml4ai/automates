import sys
import json
import argparse

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_assembly.air import AutoMATES_IR
from automates.model_assembly.gromet import Gromet, gromet_to_json
from automates.model_assembly.text_reading_linker import TextReadingLinker
from automates.model_assembly.interfaces import (
    TextReadingAppInterface, 
    LocalTextReadingInterface
)

def main(args):

    air_filepath = args.air_filepath
    air_json_data = json.load(open(air_filepath, "r"))
    AIR = AutoMATES_IR.from_air_json(air_json_data)
    GrFN = GroundedFunctionNetwork.from_AIR(AIR)

    if (args.tr_comm_file != None
        and args.tr_doc_file != None
        and args.tr_eqn_file != None):
    
        name = air_filepath.split("/")[-1].rsplit("--AIR", 1)[0]
        tr_interface = LocalTextReadingInterface(name)
        if args.tr_address != None:
            tr_interface = TextReadingAppInterface(
                f"http://{args.tr_address}:{args.tr_port}"
            )

        tr_linker = TextReadingLinker(tr_interface)
        GrFN = tr_linker.perform_tr_grfn_linking(GrFN, {
            "comm_file": args.tr_comm_file,
            "eqn_file": args.tr_eqn_file,
            "doc_file": args.tr_doc_file
        })

    GroMEt = Gromet.from_GrFN(GrFN)

    gromet_file = air_filepath.replace("AIR.json", "GroMEt.json")
    gromet_to_json(GroMEt, gromet_file)

    # A = G.to_AGraph()
    # grfn_pdf_name = air_filepath.replace("AIR.json", "GrFN.pdf")
    # A.draw(grfn_pdf_name, prog="dot")

    # G2 = GroundedFunctionNetwork.from_json(grfn_file)
    # assert G == G2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("air_filepath", help="Path to AIR file")
    parser.add_argument("--tr_comm_file", 
        type=str,
        default=None,
        help="filepath to a comments JSON file"
    )
    parser.add_argument("--tr_doc_file",
        type=str,
        default=None,
        help="filepath to a source text pdf file"
    )
    parser.add_argument("--tr_eqn_file", 
        type=str,
        default=None,
        help="filepath to an equations txt file"
    )
    parser.add_argument(
        "--tr_address",
        type=str,
        default=None,
        help="Address to reach the TextReading webapp",
    )
    parser.add_argument(
        "--tr_port",
        type=int,
        default=9000,
        help="Port to reach the TextReading webapp",
    )

    main(parser.parse_args())
