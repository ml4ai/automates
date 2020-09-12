import json
import os

from automates.model_assembly.interfaces import TextReadingInterface

cur_dir = os.getcwd()
DATA = os.environ["AUTOMATES_DATA"]
EQN_PATH = f"{DATA}/COVID-19/CHIME/eqns/2000/2000_equations.txt"
DOC_PATH = f"{DATA}/COVID-19/CHIME/docs/2000 - The Mathematics of Infectious Diseases.pdf"
AIR_PATH = "../../tests/data/model_analysis/CHIME-SIR_AIR.json"
COMM_PATH = ""


def main():
    caller = TextReadingInterface("http://localhost:9000")

    mention_path = f"{cur_dir}/CHIME-mentions.json"
    mention_data = caller.extract_mentions(DOC_PATH, mention_path)

    hypothesis_data = caller.get_link_hypotheses(
        mention_path, EQN_PATH, AIR_PATH, COMM_PATH
    )
    print(hypothesis_data)
    json.dump(hypothesis_data, open(f"{cur_dir}/CHIME-hypotheses.json"))


if __name__ == "__main__":
    main()
