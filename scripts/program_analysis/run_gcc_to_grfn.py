"""
    Takes a C program name as the first argument, runs it through the gcc plugin,
    gcc ast to cast, and cast to grfn. Given <program_name> it creates 
        ast.json -- AST json dump from gcc plugin
        <program_name>--CAST.json -- CAST json
        <program_name>--GrFN.json -- GrFN json
        <program_name>--GrFN.pdf -- graphviz pdf

    Depends on gcc 10 being installed in /usr/local and the ast_dump.so existing
    in the gcc plugin directory. Follow the directions in the readme found in
    automates/program_analysis/gcc_plugin/ to set this up.


    TODO update to optionally take a fortran file. Need to use different compile
    command in this scenarion (gfortran-10 and no "-x c++")
"""

import sys
import os
import subprocess
import json
import argparse

from automates.program_analysis.GCC2GrFN.gcc_ast_to_cast import GCC2CAST

GCC_10_BIN_DIRECTORY = "/usr/local/gcc-10.1.0/bin/"
GCC_PLUGIN_IMAGE_DIR = "automates/program_analysis/gcc_plugin/plugin/"


def get_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-i", "--inputs", help="Your input file(s).", nargs="*")
    parser.add_argument(
        "-l",
        "--language",
        help="The langugage of the input file. Valid inputs: c, c++, f (for fortran)",
    )
    parser.add_argument(
        "-v", "--verbose", help="Verbose mode, dump output of gcc plugin."
    )
    options = parser.parse_args(args)
    return options


def run_gcc_pipeline():

    assert len(sys.argv) > 1, "Error: No c file name passed in arguments"

    args = get_args()

    if args.inputs is None:
        raise Exception("Error: No input file specified via -i option")
    input_files = args.inputs

    compiler = None
    plugin_name = "ast_dump.so"
    if args.language is None or args.language in {"c", "c++"}:
        compiler = "g++-10.1"
    elif args.language == "f":
        compiler = "gfortran-10.1"
        plugin_name = "ast_dump_for.so"
    else:
        raise Exception(f"Error: Unknown language specified {args.language}")

    capture_output = []
    if args.verbose is None:
        capture_output = [
            "-o",
            "/dev/null",
        ]

    assert os.path.exists(
        GCC_10_BIN_DIRECTORY
    ), f"Error: GCC binaries not installed at expected location: {GCC_10_BIN_DIRECTORY}"

    assert os.path.exists(
        GCC_PLUGIN_IMAGE_DIR + plugin_name
    ), f"Error: GCC AST dump plugin does not exist at expected location: {GCC_PLUGIN_IMAGE_DIR + plugin_name}"

    # Runs g++ with the given c file. This should create the file ast.json
    # with the programs ast inside of it.
    results = subprocess.run(
        [
            f"{GCC_10_BIN_DIRECTORY}/{compiler}",
            f"-fplugin={GCC_PLUGIN_IMAGE_DIR + plugin_name}",
            "-O0",
            "-c",
            # "-x",
            # "c++",
        ]
        + input_files
        + capture_output,
        stdout=subprocess.DEVNULL,
    )

    # Assert return code is 0 which is success
    assert (
        results.returncode == 0
    ), "Error: Received bad return code when executing GCC plugin: {results.returncode}"

    assert os.path.exists(
        "./ast.json"
    ), "Error: ast.json file not created after executing GCC plugin"

    # For now, assume the last input file is the program name. This is because
    # the gcc plugin interprets the last input file listed as the "main input"
    program_name = input_files[-1].rsplit(".")[0].rsplit("/")[-1]
    gcc_ast_obj = json.load(open("./ast.json"))
    cast = GCC2CAST(gcc_ast_obj).to_cast()
    json.dump(cast.to_json_object(), open(f"{program_name}--CAST.json", "w+"))
    grfn = cast.to_GrFN()
    grfn.to_json_file(f"{program_name}--GrFN.json")
    A = grfn.to_AGraph()
    A.draw(program_name + "--GrFN.pdf", prog="dot")

    # STEMP SOILT inputs
    # inputs = {
    #     "albedo": 1,
    #     "b": 1,
    #     "cumdpt": 1,
    #     "doy": 1,
    #     "dp": 1,
    #     "hday": 1,
    #     "nlayr": 1,
    #     "pesw": 1,
    #     "srad": 1,
    #     "tamp": 1,
    #     "tav": 1,
    #     "tavg": 1,
    #     "tmax": 1,
    #     "ww": 1,
    #     "dsmid": [1, 1, 1, 1, 1],
    #     "atot": 1,
    #     "tma": [1, 1, 1, 1, 1],
    #     "srftemp": 1,
    #     "st": [1, 1, 1, 1, 1],
    # }

    # STEMP EPIC SOILT inputs
    # inputs = {
    #     "b": 1,
    #     "bcv": 1,
    #     "cumdpt": 1,
    #     "dp": 1,
    #     "dsmid": [1, 1, 1, 1, 1],
    #     "nlayr": 1,
    #     "pesw": 1,
    #     "tav": 1,
    #     "tavg": 1,
    #     "tmax": 1,
    #     "tmin": 1,
    #     "wetday": 1,
    #     "wft": 20,
    #     "ww": 1,
    #     "tma": [1, 2, 3, 4, 5],
    #     "srftemp": 1,
    #     "st": [1, 1, 1, 1, 1],
    #     "x2_avg": 1,
    # }

    # GE Simple PI controller inputs
    inputs = {"integrator_state": 0, "argv": [], "argc": 0}

    result = grfn(inputs)
    from pprint import pprint

    pprint(result)


if __name__ == "__main__":
    run_gcc_pipeline()