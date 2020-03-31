import sys
import re
import os

from sympy.parsing.latex import parse_latex


RESERVED_WORDS = {
    "max",
    "min",
    "frac",
    "exp",
    "sin",
    "cos",
    "tan",
    "arctan",
    "arccos",
    "arcsin",
    "ln",
}


def latex2python(symbols_str):
    try:
        return repr(parse_latex(symbols_str))
    except Exception as e:
        print(e)
        return None


def sanitize_token_tex(tokenized_tex):
    # only using the right-most expr for now
    tokenized_tex = tokenized_tex.split("=")[-1]
    tokenized_tex = re.sub(
        r"\\left|\\right|\\mathrm\{Int\}", "", tokenized_tex
    )
    tokenized_tex = re.sub(r"~", " ", tokenized_tex)
    words = re.findall(
        r"[A-Za-z]+\^[A-Za-z]|[A-Za-z]+_[A-Za-z0-9]|[A-Za-z]+_\{[A-Za-z0-9]+\}|[A-Za-z]+",
        tokenized_tex,
    )
    # print(words)
    unique_words = set(words)
    vars = list(unique_words - RESERVED_WORDS)
    # print(vars)
    return tokenized_tex


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
            # print(no_ws_eqn_tex)
            sanitized_eqn_tex = sanitize_token_tex(no_ws_eqn_tex)
            python_eqn = latex2python(sanitized_eqn_tex)
            equations.append(
                {
                    "original": no_ws_eqn_tex,
                    "sanitized": sanitized_eqn_tex,
                    "translated": python_eqn,
                }
            )

    for eqns in equations:
        print(f"ORIGINAL:\t\t{eqns['original']}")
        print(f"SANITIZED:\t\t{eqns['sanitized']}")
        print(f"TRANSLATED:\t\t{eqns['translated']}")
        print("\n")
