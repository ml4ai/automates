import sys
import re

from sympy.parsing.latex import parse_latex

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
    vars = re.findall(r"[a-z]+\^[a-z]|(?!\\)[a-z]+_\{[a-z]+\}", tokenized_tex)
    print(vars)
    return tokenized_tex


if __name__ == "__main__":
    eqn_filepath = sys.argv[1]
    equations = list()
    with open(eqn_filepath, "r") as infile:
        for eqn_tex in infile:
            no_ws_eqn_tex = eqn_tex.strip()
            if no_ws_eqn_tex == "None":
                continue
            sanitized_eqn_tex = sanitize_token_tex(no_ws_eqn_tex)
            python_eqn = latex2python(sanitized_eqn_tex)
            equations.append(
                {
                    "original": no_ws_eqn_tex,
                    "sanitized": sanitized_eqn_tex,
                    "translated": python_eqn,
                }
            )

    # for eqns in equations:
    #     print(f"ORIGINAL:\t\t{eqns['original']}")
    #     print(f"SANITIZED:\t\t{eqns['sanitized']}")
    #     print(f"TRANSLATED:\t\t{eqns['translated']}")
    #     print("\n")
