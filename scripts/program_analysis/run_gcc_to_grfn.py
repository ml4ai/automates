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

from automates.program_analysis.GCC2GrFN.gcc_ast_to_cast import GCC2CAST

GCC_10_BIN_DIRECTORY = "/usr/local/gcc-10.1.0/bin/"
GCC_PLUGIN_IMAGE = "automates/program_analysis/gcc_plugin/plugin/ast_dump.so"

if __name__ == "__main__":

    assert len(sys.argv) > 1, "Error: No c file name passed in arguments"

    c_file = sys.argv[1]

    assert os.path.exists(
        GCC_10_BIN_DIRECTORY
    ), f"Error: GCC binaries not installed at expected location: {GCC_10_BIN_DIRECTORY}"

    assert os.path.exists(
        GCC_PLUGIN_IMAGE
    ), f"Error: GCC AST dump plugin does not exist at expected location: {GCC_PLUGIN_IMAGE}"

    # Runs g++ with the given c file. This should create the file ast.json
    # with the programs ast inside of it.
    results = subprocess.run(
        [
            f"{GCC_10_BIN_DIRECTORY}/g++-10.1",
            f"-fplugin={GCC_PLUGIN_IMAGE}",
            "-o0",
            "-c",
            "-x",
            "c++",
            c_file,
            "-o",
            "/dev/null",
        ]
    )

    # Assert return code is 0 which is success
    assert (
        results.returncode == 0
    ), "Error: Received bad return code when executing GCC plugin: {results.returncode}"

    assert os.path.exists(
        "./ast.json"
    ), "Error: ast.json file not created after executing GCC plugin"

    program_name = c_file.rsplit(".")[0].rsplit("/")[-1]
    gcc_ast_obj = json.load(open("./ast.json"))
    cast = GCC2CAST(gcc_ast_obj).to_cast()
    json.dump(cast.to_json_object(), open(f"{program_name}--CAST.json", "w+"))
    grfn = cast.to_GrFN()
    grfn.to_json_file(f"{program_name}--GrFN.json")
    A = grfn.to_AGraph()
    A.draw(program_name + "--GrFN.pdf", prog="dot")