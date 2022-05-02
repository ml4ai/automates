import os 
import re
import sys
import ast
import astpp
import json 
from automates.program_analysis.PyAST2CAST import py_ast_to_cast
from automates.program_analysis.CAST2GrFN import cast 
from automates.program_analysis.CAST2GrFN.model.cast import SourceRef

if len(sys.argv) < 2:
    print("USAGE: python3 python2cast.py PYTHON_FILE_NAME [--astpp] [--legacy] [--rawjson] [--stdout]")
    print("Requires a Python file on the command line to run")
    sys.exit()

# Open Python file as a giant string
pyfile_path = sys.argv[1]
file_handle = open(pyfile_path)
file_contents = file_handle.read()
file_handle.close()
file_name = pyfile_path.split("/")[-1]

# Count the number of lines in the file
file_handle = open(pyfile_path)
file_list = file_handle.readlines()
line_count = 0
for l in file_list:
    line_count += 1
file_handle.close()

# Create a PyASTToCAST Object
if '--legacy' in sys.argv:
    convert = py_ast_to_cast.PyASTToCAST(file_name, legacy=True)
else:
    convert = py_ast_to_cast.PyASTToCAST(file_name)

# Additional option to allow us to view the PyAST 
# using the astpp module 
if '--astpp' in sys.argv:
    astpp.parseprint(file_contents)

# 'Root' the current working directory so that it's where the 
# Source file we're generating CAST for is (for Import statements)
idx = pyfile_path.rfind("/")
curr_path = pyfile_path[0:idx]
old_path = os.getcwd()
os.chdir(curr_path)

# Parse the python program's AST and create the CAST
contents = ast.parse(file_contents)
C = convert.visit(contents, {}, {})
C.source_refs = [SourceRef(file_name, None, None, 1, line_count)]

os.chdir(old_path)
out_cast = cast.CAST([C], "python")
# Then, print CAST as JSON
if '--rawjson' in sys.argv:
    print(json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None))
else:
    if '--stdout' in sys.argv:
        print(out_cast.to_json_str())
    else:
        out_name = file_name.split(".")[0]
        print("Writing CAST to "+out_name+"--CAST.json")
        out_handle = open(out_name+"--CAST.json","w")
        out_handle.write(out_cast.to_json_str())
    
