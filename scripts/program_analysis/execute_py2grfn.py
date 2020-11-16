import os
import sys

from automates.program_analysis.Py2GrFN.py2grfn import python_file_to_grfn

def main():
    python_file = sys.argv[1]
    grfn = python_file_to_grfn(python_file)

    program_name = os.path.basename(python_file).split(".py")[0]
    grfn.to_json_file(program_name + ".json")
    
    from pprint import pprint
    # print(grfn({"c1" : 1, "c2": 2, "c3": 3, "c4": 4}))
    # pprint(grfn({"x": 1, "y":5}))

    A = grfn.to_AGraph()
    A.draw(program_name + ".pdf", prog="dot")

if __name__ == "__main__":
    main()


