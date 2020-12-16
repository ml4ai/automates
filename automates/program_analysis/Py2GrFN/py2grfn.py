import ast
import sys
import os

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
    return c2g.to_grfn()
