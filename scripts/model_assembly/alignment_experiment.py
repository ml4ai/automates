import json
import os

from automates.model_assembly.interfaces import TextReadingInterface

cur_dir = os.getcwd()
DATA = os.environ["AUTOMATES_DATA"]
MODEL_NAME = "PETPNO"
EQN_PATH = f"{DATA}/Mini-SPAM/eqns/SPAM/PET/PETPNO/PETPNO_equations.txt"
DOC_PATH = f"{DATA}/ASKE-E/integration-wg/DSSAT-evapotranspiration-models/PNO-model/PNO-2006-Simplified Versions for the Penman Evap Equation Using Routine Weather Data-petpno_Penman.pdf"
GrFN_PATH = f"{cur_dir}/{MODEL_NAME}--GrFN.json"
COMM_PATH = f"{cur_dir}/{MODEL_NAME}--documentation.json"
MENTIONS_PATH = f"{cur_dir}/{MODEL_NAME}-mentions.json"
ALIGNMENT_PATH = f"{cur_dir}/{MODEL_NAME}-alignment.json"


def main():
    caller = TextReadingInterface("http://localhost:9000")
    caller.extract_mentions(DOC_PATH, MENTIONS_PATH)
    hypothesis_data = caller.get_link_hypotheses(
        MENTIONS_PATH, EQN_PATH, GrFN_PATH, COMM_PATH
    )
    json.dump({"grounding": hypothesis_data}, open(ALIGNMENT_PATH, "w"))


if __name__ == "__main__":
    main()
