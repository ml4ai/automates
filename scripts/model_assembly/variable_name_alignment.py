"""
Code is taken from "alignment_experiment.py". The difference in this file 
is that we will read in a list of var names for the alignment that is not
grounded in an actual GrFN.
"""

import argparse
import json
import os

from automates.model_assembly.interfaces import TextReadingAppInterface


def main(args):
    CUR_DIR = os.getcwd()
    MODEL_NAME = os.path.basename(args.names).replace("--vars.json", "")

    MENTIONS_PATH = f"{CUR_DIR}/{MODEL_NAME}--mentions.json"
    ALIGNMENT_PATH = f"{CUR_DIR}/{MODEL_NAME}--alignment.json"

    caller = TextReadingAppInterface(f"http://{args.address}:{args.port}")
    if not os.path.isfile(MENTIONS_PATH):
        caller.extract_mentions(args.doc_file, MENTIONS_PATH)
    else:
        print(f"Mentions have been previously extracted and are stored in {MENTIONS_PATH}")

    variable_names_json = json.load(open(args.names, "r"))
    variable_names = [{"name": name} for name in variable_names_json["variables"]]

    hypothesis_data = caller.get_link_hypotheses(
        MENTIONS_PATH, args.eqn_file, args.comm_file, variable_names
    )
    json.dump({"grounding": hypothesis_data}, open(ALIGNMENT_PATH, "w"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("names", help="filepath to a json file with variable names")
    parser.add_argument("comm_file", help="filepath to a comments JSON file")
    parser.add_argument("doc_file", help="filepath to a source text pdf file")
    parser.add_argument("eqn_file", help="filepath to an equations txt file")
    parser.add_argument(
        "-a",
        "--address",
        type=str,
        default="localhost",
        help="Address to reach the TextReading webapp",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=9000,
        help="Port to reach the TextReading webapp",
    )
    args = parser.parse_args()
    main(args)
