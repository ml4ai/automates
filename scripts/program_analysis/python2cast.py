import re
import sys
import ast
import astpp
from automates.program_analysis.PyAST2CAST import py_ast_to_cast
from automates.program_analysis.CAST2GrFN import cast 


if(len(sys.argv) != 2):
    print("USAGE: python3 python2cast.py [PYTHON_FILE_NAME]")
    print("Requires a Python file on the command line to run")
    sys.exit()

# Open Python file as a giant string
pyfile_path = sys.argv[1]
file_contents = open(pyfile_path).read()

# Create a PyASTToCAST Object
convert = py_ast_to_cast.PyASTToCAST()

# Use ast.parse to get a PyAST
# ../../tests/data/program_analysis/PyAST2CAST/
# Use it to convert PyAST To CAST
print(ast.parse(file_contents))
print(astpp.parseprint(file_contents))
C = convert.visit(ast.parse(file_contents))
print(type(cast.CAST([C])))

Cast = cast.CAST([C])
# Then, print CAST as JSON
print(Cast.to_json_str())

G = Cast.to_GrFN()

A = G.to_AGraph()
A.draw("test-grfn.pdf", prog="dot") 
