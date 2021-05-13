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

    print("Dumping GCC AST...")

    # Runs g++ with the given c file. This should create the file ast.json
    # with the programs ast inside of it.
    results = subprocess.run(
        [
            f"{GCC_10_BIN_DIRECTORY}/{compiler}",
            f"-fplugin={GCC_PLUGIN_IMAGE_DIR + plugin_name}",
            "-O0",
            # Need to use -c if only one file in order to make a .o file
            "-c" if len(input_files) == 1 else "",
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

    ast_file_names = [
        f"./{i.split('/')[-1].rsplit('.')[0]}_gcc_ast.json" for i in input_files
    ]

    # Assert an ast was made for each input file
    for a in ast_file_names:
        assert os.path.exists(
            a
        ), f"Error: {a} file not created after executing GCC plugin"

    # For now, assume the last input file is the overall program name.
    program_name = input_files[-1].rsplit(".")[0].rsplit("/")[-1]
    # Load json of each files ast
    ast_jsons = [json.load(open(a)) for a in ast_file_names]

    print("Turning GCC AST into CAST...")
    cast = GCC2CAST(ast_jsons).to_cast()
    json.dump(cast.to_json_object(), open(f"{program_name}--CAST.json", "w+"))

    print("Transforminf CAST into GrFN...")
    grfn = cast.to_GrFN()
    grfn.to_json_file(f"{program_name}--GrFN.json")

    print("Transforminf GrFN into AGraph...")
    A = grfn.to_AGraph()
    A.draw(program_name + "--GrFN.pdf", prog="dot")

    # STEMP SOILT inputs
    # inputs = {
    #     "stemp_soilt::stemp_soilt.soilt::albedo::-1": 1,
    #     "stemp_soilt::stemp_soilt.soilt::b::-1": 1,
    #     "stemp_soilt::stemp_soilt.soilt::cumdpt::-1": 1,
    #     "stemp_soilt::stemp_soilt.soilt::doy::-1": 1,
    #     "stemp_soilt::stemp_soilt.soilt::dp::-1": 1,
    #     "stemp_soilt::stemp_soilt.soilt::hday::-1": 1,
    #     "stemp_soilt::stemp_soilt.soilt::nlayr::-1": 1,
    #     "stemp_soilt::stemp_soilt.soilt::pesw::-1": 1,
    #     "stemp_soilt::stemp_soilt.soilt::srad::-1": 1,
    #     "stemp_soilt::stemp_soilt.soilt::tamp::-1": 1,
    #     "stemp_soilt::stemp_soilt.soilt::tav::-1": 1,
    #     "stemp_soilt::stemp_soilt.soilt::tavg::-1": 1,
    #     "stemp_soilt::stemp_soilt.soilt::tmax::-1": 1,
    #     "stemp_soilt::stemp_soilt.soilt::ww::-1": 1,
    #     "stemp_soilt::stemp_soilt.soilt::dsmid::-1": [1, 1, 1, 1, 1],
    #     "stemp_soilt::stemp_soilt.soilt::atot::-1": 1,
    #     "stemp_soilt::stemp_soilt.soilt::tma::-1": [1, 1, 1, 1, 1],
    #     "stemp_soilt::stemp_soilt.soilt::st::-1": [1, 1, 1, 1, 1],
    # }

    # STEMP EPIC SOILT inputs
    inputs = {
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::b::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::bcv::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::cumdpt::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::dp::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::dsmid::-1": [1, 1, 1, 1, 1],
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::nlayr::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::pesw::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::tav::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::tavg::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::tmax::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::tmin::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::wetday::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::wft::-1": 20,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::ww::-1": 1,
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::tma::-1": [1, 2, 3, 4, 5],
        "stemp_epic_soilt::stemp_epic_soilt.soilt_epic::st::-1": [1, 1, 1, 1, 1],
    }

    # GE Simple PI controller dynamics inputs
    # inputs = {
    #     "GE_simple_PI_controller_dynamics::GE_simple_PI_controller_dynamics.main::integrator_state::-1": 0
    #     # "GE_simple_PI_controller::GE_simple_PI_controller.main::integrator_state::-1": 0
    # }

    print("Executing GrFN...")
    result = grfn(inputs)
    from pprint import pprint

    print("GrFn execution results:")
    pprint(result)


if __name__ == "__main__":
    run_gcc_pipeline()