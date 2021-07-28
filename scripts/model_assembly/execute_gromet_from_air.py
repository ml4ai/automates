import json
import argparse

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_assembly.air import AutoMATES_IR
from automates.model_assembly.gromet import Gromet
from automates.model_assembly.gromet_execution import execute_gromet


def main(args):

    air_filepath = args.air_filepath
    air_json_data = json.load(open(air_filepath, "r"))
    AIR = AutoMATES_IR.from_air_json(air_json_data)
    GrFN = GroundedFunctionNetwork.from_AIR(AIR)

    GroMEt = Gromet.from_GrFN(GrFN)

    inputs = {
        "SIR-simple::SIR-simple::sir::0::--::s::-1": [1],
        "SIR-simple::SIR-simple::sir::0::--::i::-1": [1],
        "SIR-simple::SIR-simple::sir::0::--::r::-1": [1],
        "SIR-simple::SIR-simple::sir::0::--::beta::-1": [1],
        "SIR-simple::SIR-simple::sir::0::--::gamma::-1": [1],
    }
    results = execute_gromet(GroMEt, inputs)
    print(f"Results: {results}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("air_filepath", help="Path to AIR file")
    main(parser.parse_args())
