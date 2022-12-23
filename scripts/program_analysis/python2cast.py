import os 
import sys
import ast
import astpp
import json 
import argparse
from automates.program_analysis.PyAST2CAST import py_ast_to_cast
from automates.program_analysis.CAST2GrFN import cast 
from automates.program_analysis.CAST2GrFN.model.cast import SourceRef
from automates.program_analysis.CAST2GrFN.visitors.cast_to_agraph_visitor import (
    CASTToAGraphVisitor,
)
from automates.utils.script_functions import python_to_cast

def get_args():
    parser = argparse.ArgumentParser("Runs Python to CAST pipeline on input Python source file.")
    parser.add_argument("--astpp", 
            help="Dumps Python AST to stdout",
            action="store_true")
    parser.add_argument("--rawjson", 
            help="Dumps out raw JSON contents to stdout",
            action="store_true")
    parser.add_argument("--stdout", 
            help="Dumps CAST JSON to stdout instead of a file",
            action="store_true")
    parser.add_argument("--agraph", 
            help="Generates visualization of CAST as a PDF file",
            action="store_true")
    parser.add_argument("--legacy", 
            help="Generate CAST for GrFN 2.2 pipeline",
            action="store_true")
    parser.add_argument("pyfile_path",
            help="input Python source file")
    options = parser.parse_args()
    return options

"""
def python_to_cast(pyfile_path, agraph=False, astprint=False, std_out=False, rawjson=False, legacy=False, cast_obj=False):
    # Open Python file as a giant string
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
    if legacy:
        convert = py_ast_to_cast.PyASTToCAST(file_name, legacy=True)
    else:
        convert = py_ast_to_cast.PyASTToCAST(file_name)

    # Additional option to allow us to view the PyAST 
    # using the astpp module 
    if astprint:
        astpp.parseprint(file_contents)

    # 'Root' the current working directory so that it's where the 
    # Source file we're generating CAST for is (for Import statements)
    old_path = os.getcwd()
    idx = pyfile_path.rfind("/")

    if idx > -1:
        curr_path = pyfile_path[0:idx]
        os.chdir(curr_path)
    else:
        curr_path = "./"+pyfile_path

    #os.chdir(curr_path)

    # Parse the python program's AST and create the CAST
    contents = ast.parse(file_contents)
    C = convert.visit(contents, {}, {})
    C.source_refs = [SourceRef(file_name, None, None, 1, line_count)]

    os.chdir(old_path)
    out_cast = cast.CAST([C], "python")

    if agraph:
        V = CASTToAGraphVisitor(out_cast)
        last_slash_idx = file_name.rfind("/")
        file_ending_idx = file_name.rfind(".")
        pdf_file_name = f"{file_name[last_slash_idx + 1 : file_ending_idx]}.pdf"
        V.to_pdf(pdf_file_name)

    # Then, print CAST as JSON
    if cast_obj:
        return out_cast
    else:
        if rawjson:
            print(json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None))
        else:
            if std_out:
                print(out_cast.to_json_str())
            else:
                out_name = file_name.split(".")[0]
                print("Writing CAST to "+out_name+"--CAST.json")
                out_handle = open(out_name+"--CAST.json","w")
                out_handle.write(out_cast.to_json_str())
"""        

def main():
    """main
    """
    args = get_args()
    python_to_cast(args.pyfile_path, args.agraph, args.astpp, args.stdout, args.rawjson, args.legacy)

if __name__ == "__main__":
    main()