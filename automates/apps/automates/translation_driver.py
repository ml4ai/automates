import base64
import json

from automates.program_analysis.GCC2GrFN.gcc_plugin_driver import run_gcc_plugin
from automates.program_analysis.GCC2GrFN.gcc_ast_to_cast import GCC2CAST

# Util functions
def write_out_files(files):
    for f in files:
        file_name = f["file_name"]
        file_str = base64.b64decode(f["base64_encoding"])
        with open(file_name, "wb") as source_file:
            source_file.write(file_str)

def gather_file_names(files):
    return [f["file_name"] for f in files]

def generate_cast_from_gcc_ast_files(gcc_ast_files):
    # Load json of each files ast
    gcc_asts = [json.load(open(a)) for a in gcc_ast_files]
    return GCC2CAST(gcc_asts).to_cast()

# Functions for translating from specific languages
def gcc_translate(body, language):
    source_code_files = body["source_code_files"]
    write_out_files(source_code_files)
    file_names = gather_file_names(source_code_files)

    # TODO get this value from an app config file
    GCC_PLUGIN_IMAGE_DIR = "automates/program_analysis/gcc_plugin/plugin/"
    gcc_ast_files = run_gcc_plugin(language, file_names, plugin_location=GCC_PLUGIN_IMAGE_DIR)
    cast = generate_cast_from_gcc_ast_files(gcc_ast_files)

    # TODO check some config or payload value to see if we should set the 
    # random seed to 0 so UUIDs in GrFN are consistent for testing.
    # if False:
    #     misc.rd.seed(0)

    with open("test.json", "w") as f:
        f.write(cast.to_json_str())

    return cast.to_GrFN()


def translate_c(body):
    return gcc_translate(body, "c")

def translate_fortran(body):
    return gcc_translate(body, "fortran")

def translate_python(body):
    pass