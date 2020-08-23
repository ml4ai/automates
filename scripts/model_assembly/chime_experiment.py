import json
import os

from  automates.model_assembly.interfaces import TextReadingInterface

cur_dir = os.getcwd()
DATA = os.environ["AUTOMATES_DATA"]
EQN_PATH = f"{DATA}/COVID-19/CHIME/Equations/2000/2000_equations.txt"
DOC_PATH = f"{DATA}/COVID-19/CHIME/Literature/2000 - The Mathematics of Infectious Diseases.pdf"
AIR_PATH = "../../tests/data/model_analysis/CHIME-SIR_AIR.json"


def main():
    caller = TextReadingInterface("http://localhost:9000")

    mention_path = f"{cur_dir}/CHIME-mentions.json"
    mention_data = caller.extract_mentions(DOC_PATH, mention_path)
    print(mention_data)

    hypothesis_data = caller.get_link_hypotheses(
        mention_path, EQN_PATH, AIR_PATH
    )
    print(hypothesis_data)
    json.dump(hypothesis_data, open(f"{cur_dir}/CHIME-hypotheses.json"))


if __name__ == "__main__":
    main()
