import ast
import sys
import os

from cast import CAST2GrFN

def py2grfn(file_path):
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
    


def main():
    python_file = sys.argv[1]
    grfn = py2grfn(python_file)

    program_name = os.path.basename(python_file).split(".py")[0]
    grfn.to_json_file(program_name + ".json")
    
    from pprint import pprint
    # print(grfn({"c1" : 1, "c2": 2, "c3": 3, "c4": 4}))
    pprint(grfn({"x": 1, "y":2}))

    A = grfn.to_AGraph()
    A.draw(program_name + ".pdf", prog="dot")

if __name__ == "__main__":
    main()
