import argparse
import json
import os

from automates.model_assembly.interfaces import TextReadingInterface


def main(args):
    CUR_DIR = os.getcwd()
    MODEL_NAME = os.path.basename(args.grfn_file).replace("--GrFN.json", "")

    MENTIONS_PATH = f"{CUR_DIR}/{MODEL_NAME}--mentions.json"
    ALIGNMENT_PATH = f"{CUR_DIR}/{MODEL_NAME}--alignment.json"

    caller = TextReadingInterface(f"http://{args.address}:{args.port}")
    if not os.path.isfile(MENTIONS_PATH):
        caller.extract_mentions(args.doc_file, MENTIONS_PATH)
    else:
        print(f"Mentions have been previously extracted and are stored in {MENTIONS_PATH}")


    hypothesis_data = caller.get_link_hypotheses(
        MENTIONS_PATH, args.eqn_file, args.grfn_file, args.comm_file, args.wikidata_file,
    )
    json.dump({"grounding": hypothesis_data}, open(ALIGNMENT_PATH, "w", encoding='utf8'), ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("grfn_file", help="filepath to a GrFN JSON file")
    parser.add_argument("comm_file", help="filepath to a comments JSON file")
    parser.add_argument("doc_file", help="filepath to a source paper file (COSMOS or Science Parse)")
    parser.add_argument("eqn_file", help="filepath to an equations txt file")
    parser.add_argument("--wikidata_file", help="filepath to a wikidata grounding json file", type=str, default="None")
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
