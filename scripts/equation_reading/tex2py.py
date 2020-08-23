"""
This program translates all tokenized LaTeX equations from an input text file
into syntactically equivalent executable python expressions.


Example execution:
    $ python tex2py.py <path-to-equations.txt> <path/to/py_equations.txt>

Author: Paul D. Hein, Marco Valenzuela
"""

import sys

from automates.equation_reading.decoding import tex2py


def main():
    eqn_filepath = sys.argv[1]
    py_equations = list()
    with open(eqn_filepath, "r") as infile:
        for tex_eqn_line in infile:
            no_ws_tex_eqn_line = tex_eqn_line.strip()
            if no_ws_tex_eqn_line == "None":
                no_ws_tex_eqn_line = None
                sanitized_eqn = None
                py_eqn = None
            else:
                (sanitized_eqn, py_eqn) = tex2py(
                    no_ws_tex_eqn_line, include_sanitized=True
                )

            print(f"ORIGINAL:\t\t{no_ws_tex_eqn_line}")
            print(f"SANITIZED:\t\t{sanitized_eqn}")
            print(f"TRANSLATED:\t\t{py_eqn}")
            print("\n")
            py_equations.append(py_eqn)

    py_eqn_filepath = sys.argv[2]
    with open(py_eqn_filepath, "w") as outfile:
        for py_eqn in py_equations:
            outfile.write(f"{py_eqn}\n")


if __name__ == "__main__":
    main()
