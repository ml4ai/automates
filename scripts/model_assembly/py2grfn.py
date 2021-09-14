import os
import re
import sys
import ast
import json

# import astpp
import argparse

from automates.program_analysis.PyAST2CAST import py_ast_to_cast
from automates.program_analysis.CAST2GrFN import cast
from automates.program_analysis.CAST2GrFN.model.cast import SourceRef
from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_assembly.air import AutoMATES_IR


def main(args):
    CAST = convert2CAST(args)
    AIR = CAST2AIR(args, CAST)

    GrFN = GroundedFunctionNetwork.from_AIR(AIR)

    if args.gen_grfn_json:
        grfn_file = args.python_filepath.replace(".py", "--GrFN3.json")
        GrFN.to_json_file(grfn_file)

    if args.gen_grfn_pdf:
        A = GrFN.to_AGraph(expand_expressions=False)
        grfn_file = args.python_filepath.replace(".py", "--GrFN3.pdf")
        A.draw(grfn_file, prog="dot")

    if args.gen_full_grfn_pdf:
        Ae = GrFN.to_AGraph(expand_expressions=True)
        grfn_file = args.python_filepath.replace(".py", "--GrFN3_expanded.pdf")
        Ae.draw(grfn_file, prog="dot")


def convert2CAST(args):
    # Open Python file as a giant string
    # pyfile_path = args.python_filepath
    file_contents = list()
    with open(args.python_filepath, "r") as infile:
        file_contents = infile.read()
    # file_handle = open(pyfile_path)
    # file_contents = file_handle.read()
    # file_handle.close()
    file_name = args.python_filepath.split("/")[-1]

    # Count the number of lines in the file
    line_count = 0
    with open(args.python_filepath, "r") as infile:
        line_count = infile.readlines()

    # Create a PyASTToCAST Object
    convert = py_ast_to_cast.PyASTToCAST(file_name)

    # Additional option to allow us to view the PyAST
    # using the astpp module
    # if args.ast_pretty_print:
    #     astpp.parseprint(file_contents)

    # 'Root' the current working directory so that it's where the
    # Source file we're generating CAST for is (for Import statements)
    old_path = os.getcwd()
    os.chdir(args.python_filepath[: args.python_filepath.rfind("/")])

    # Parse the python program's AST and create the CAST
    contents = ast.parse(file_contents)
    C = convert.visit(contents)
    C.source_refs = [SourceRef(file_name, None, None, 1, line_count)]
    out_cast = cast.CAST([C], "python")
    os.chdir(old_path)

    # Then, print CAST as JSON
    if args.gen_cast_json:
        cast_filename = args.python_filepath.replace(".py", "--CAST.json")
        json.dump(
            out_cast.to_json_object(),
            open(cast_filename, "w"),
            sort_keys=True,
            indent=4,
        )
    return out_cast


def CAST2AIR(args, CAST):
    air_dict = CAST.to_air_dict()
    AIR = AutoMATES_IR.from_air_json(air_dict)

    if args.gen_air_json:
        air_json_file = args.python_filepath.replace(".py", "--AIR.json")
        AIR.to_json(air_json_file)
    return AIR


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "python_filepath",
        help="Path to a python file to be translated to GrFN",
    )
    parser.add_argument(
        "-cj",
        dest="gen_cast_json",
        action="store_true",
        help="Setting this flag will generate CAST JSON for the Python input file",
    )
    parser.add_argument(
        "-aj",
        dest="gen_air_json",
        action="store_true",
        help="Setting this flag will generate AIR JSON for the Python input file",
    )
    parser.add_argument(
        "-gj",
        dest="gen_grfn_json",
        action="store_true",
        help="Setting this flag will generate GrFN JSON for the Python input file",
    )
    parser.add_argument(
        "-gp",
        dest="gen_grfn_pdf",
        action="store_true",
        help="Setting this flag will generate a GrFN PDF visualization for the Python input file",
    )
    parser.add_argument(
        "-gpf",
        dest="gen_full_grfn_pdf",
        action="store_true",
        help="Setting this flag will generate an expanded GrFN PDF visualization for the Python input file",
    )
    parser.add_argument(
        "-astpp",
        dest="ast_pretty_print",
        action="store_true",
        help="Pption to allow us to view the PyAST using the astpp module",
    )

    main(parser.parse_args())
