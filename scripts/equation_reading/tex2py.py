import re
import os
import sys

# insert path to decoding.py
sys.path.insert(0, os.path.abspath("src/equation_reading"))

from decoding import tex2py



if __name__ == "__main__":

    automates_data = os.environ["AUTOMATES_DATA"]
    mini_spam_eqns = f"{automates_data}/Mini-SPAM/eqns/SPAM/PET"
    eqn_filepath = f"{mini_spam_eqns}/PETASCE/PETASCE_equations.txt"
    equations = list()
    with open(eqn_filepath, "r") as infile:
        for l, eqn_tex in enumerate(infile):
            no_ws_eqn_tex = eqn_tex.strip()
            if no_ws_eqn_tex == "None":
                continue
            if l == 5:
                break
            equations.append(tex2py(no_ws_eqn_tex))

    for eqns in equations:
        print(f"ORIGINAL:\t\t{eqns['original']}")
        print(f"SANITIZED:\t\t{eqns['sanitized']}")
        print(f"TRANSLATED:\t\t{eqns['translated']}")
        print("\n")
