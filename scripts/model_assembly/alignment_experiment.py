import json
import sys
import os

from automates.model_assembly.interfaces import TextReadingInterface

CUR_DIR = os.getcwd()

GrFN_PATH = sys.argv[1]
EQN_PATH = sys.argv[2]
DOC_PATH = sys.argv[3]
COMM_PATH = sys.argv[4]

MODEL_NAME = GrFN_PATH[
    GrFN_PATH.rfind("/") + 1 : GrFN_PATH.rfind("--GrFN.json")
]


MENTIONS_PATH = f"{CUR_DIR}/{MODEL_NAME}-mentions.json"
ALIGNMENT_PATH = f"{CUR_DIR}/{MODEL_NAME}-alignment.json"


def main():
    caller = TextReadingInterface("http://localhost:9000")
    caller.extract_mentions(DOC_PATH, MENTIONS_PATH)
    hypothesis_data = caller.get_link_hypotheses(
        MENTIONS_PATH, EQN_PATH, GrFN_PATH, COMM_PATH
    )
    json.dump({"grounding": hypothesis_data}, open(ALIGNMENT_PATH, "w"))


if __name__ == "__main__":
    main()
