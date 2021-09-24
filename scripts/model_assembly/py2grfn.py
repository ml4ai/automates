import os
import ast
import json

import argparse

from automates.program_analysis.PyAST2CAST import py_ast_to_cast
from automates.program_analysis.CAST2GrFN import cast
from automates.program_analysis.CAST2GrFN.model.cast import SourceRef
from automates.model_assembly.networks import (
    GroundedFunctionNetwork,
    CausalAnalysisGraph,
)
from automates.model_assembly.air import AutoMATES_IR


def main(args):
    CAST = convert2CAST(args)
    AIR = CAST2AIR(args, CAST)

    print("Translating AIR to GrFN3")
    GrFN = GroundedFunctionNetwork.from_AIR(AIR)

    if args.gen_grfn_json:
        print("Outputting GrFN3 JSON")
        grfn_file = args.python_filepath.replace(".py", "--GrFN3.json")
        GrFN.to_json_file(grfn_file)

        if args.grfn_json_eq:
            print("Loading from GrFN3 JSON")
            saved_GrFN = GroundedFunctionNetwork.from_json(grfn_file)
            print("Comparing constructed GrFN3 to JSON loaded GrFN3")
            assert GrFN == saved_GrFN
            print("GrFNs are identical!")

    if args.gen_grfn_pdf:
        print("Outputting GrFN3 PDF visualization")
        A = GrFN.to_AGraph(expand_expressions=False)
        grfn_file = args.python_filepath.replace(".py", "--GrFN3.pdf")
        A.draw(grfn_file, prog="dot")

    if args.gen_full_grfn_pdf:
        print("Outputting expanded GrFN3 PDF visualization")
        Ae = GrFN.to_AGraph(expand_expressions=True)
        grfn_file = args.python_filepath.replace(".py", "--GrFN3_expanded.pdf")
        Ae.draw(grfn_file, prog="dot")

    if args.gen_grfn_dotfile:
        print("Outputting GrFN3 dotfile")
        grfn_file = args.python_filepath.replace(".py", "--GrFN3.dot")
        GrFN.to_dotfile(grfn_file)

    if args.gen_full_grfn_dotfile:
        print("Outputting expanded GrFN3 dotfile")
        grfn_file = args.python_filepath.replace(".py", "--GrFN3_expanded.dot")
        GrFN.to_dotfile(grfn_file, expand_expressions=True)

    if args.gen_cag_json:
        print("Outputting CAG JSON")
        CAG = CausalAnalysisGraph.from_GrFN(GrFN)
        cag_file = args.python_filepath.replace(".py", "--CAG.json")
        print("Loading from CAG JSON")
        CAG.to_json_file(cag_file)
        if args.cag_json_eq:
            print("Comparing constructed CAG to JSON loaded CAG")
            saved_CAG = CausalAnalysisGraph.from_json_file(cag_file)
            assert CAG == saved_CAG
            print("CAGs are identical!")

    print("Done.")


def convert2CAST(args):
    print("Translating Python to CAST")
    # Open Python file as a giant string
    file_contents = list()
    with open(args.python_filepath, "r") as infile:
        file_contents = infile.read()

    file_name = args.python_filepath.split("/")[-1]

    # Count the number of lines in the file
    line_count = 0
    with open(args.python_filepath, "r") as infile:
        line_count = infile.readlines()

    # Create a PyASTToCAST Object
    convert = py_ast_to_cast.PyASTToCAST(file_name)

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

    if args.gen_cast_json:
        print("Outputting CAST JSON")
        cast_filename = args.python_filepath.replace(".py", "--CAST.json")
        json.dump(
            out_cast.to_json_object(),
            open(cast_filename, "w"),
            sort_keys=True,
            indent=4,
        )

    return out_cast


def CAST2AIR(args, CAST):
    print("Translating CAST to AIR")
    air_dict = CAST.to_air_dict()
    AIR = AutoMATES_IR.from_CAST(air_dict)

    if args.gen_air_json:
        print("Outputting AIR JSON")
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
        "-cgj",
        dest="gen_cag_json",
        action="store_true",
        help="Setting this flag will generate CAG JSON for the Python input file",
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
        "-gd",
        dest="gen_grfn_dotfile",
        action="store_true",
        help="Setting this flag will generate a GrFN PDF dotfile for the Python input file",
    )
    parser.add_argument(
        "-gdf",
        dest="gen_full_grfn_dotfile",
        action="store_true",
        help="Setting this flag will generate an expanded GrFN PDF dotfile for the Python input file",
    )
    parser.add_argument(
        "-gjeq",
        dest="grfn_json_eq",
        action="store_true",
        help="Setting this flag will check whether the saved and reloaded GrFN from JSON is equivalent to the created GrFN",
    )
    parser.add_argument(
        "-cgjeq",
        dest="cag_json_eq",
        action="store_true",
        help="Setting this flag will check whether the saved and reloaded CAG from JSON is equivalent to the created GrFN",
    )
    parser.add_argument(
        "-astpp",
        dest="ast_pretty_print",
        action="store_true",
        help="Pption to allow us to view the PyAST using the astpp module",
    )

    main(parser.parse_args())
