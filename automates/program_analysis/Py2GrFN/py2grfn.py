import ast
import sys
import os
import json

from .cast import CAST2GrFN


def python_file_to_grfn(file_path):
    """
    This function takes one input argument and assumes it is a python 3.7
    file name. It attempts to open, parse the AST, and tranlaste it to GrFN.
    """
    code = ""
    with open(file_path, "r") as infile:
        code = "".join(infile.readlines())

    tree = ast.parse(code)
    c2g = CAST2GrFN(tree)
    # Returns FN in first position and source comments in seconds
    result = c2g.to_grfn()

    basename = os.path.basename(file_path).split(".py")[0]
    with open(f"{basename}-documentation.json", "w") as f:
        json.dump(result[1], f, indent=4)

    return result[0]
