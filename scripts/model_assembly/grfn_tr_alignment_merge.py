import argparse
import json
import os

from automates.model_assembly.air import AutoMATES_IR
from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_assembly.text_reading_linker import TextReadingLinker
from automates.model_assembly.interfaces import (
    LocalTextReadingInterface,
)


def main(args):

    air_filepath = args.air_file
    air_json_data = json.load(open(air_filepath, "r"))
    AIR = AutoMATES_IR.from_air_json(air_json_data)
    GrFN = GroundedFunctionNetwork.from_AIR(AIR)

    name = air_filepath.split("/")[-1].rsplit("--AIR", 1)[0]
    tr_interface = LocalTextReadingInterface(name)
    tr_linker = TextReadingLinker(tr_interface)

    GrFN = tr_linker.perform_tr_grfn_linking(
        GrFN,
        {
            "comm_file": args.comm_file,
            "eqn_file": args.eqn_file,
            "doc_file": args.doc_file,
        },
    )

    grfn_file = air_filepath.replace("AIR.json", "GrFN.json")
    GrFN.to_json_file(grfn_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("air_file", help="filepath to a AIR JSON file")
    parser.add_argument("comm_file", help="filepath to a comments JSON file")
    parser.add_argument("doc_file", help="filepath to a source text pdf file")
    parser.add_argument("eqn_file", help="filepath to an equations txt file")

    args = parser.parse_args()
    main(args)
