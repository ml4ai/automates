import os
import subprocess

GCC_10_BIN_DIRECTORY = "/usr/local/gcc-10.1.0/bin/"

def run_gcc_plugin(language, input_files, plugin_location="./"):
    """
    Runs the GCC ast dump plugin to create an AST file for each individual
    input code file. Then it returns the name of the created AST files.

    Args:
        language (str): The source language we are running through gcc.
        input_files (List[str]): A list of locations for the input source 
            files to run through the plugin.
        plugin_location (str, optional): Location of the .so for the ast dump 
            plugin. Defaults to "./".

    Raises:
        Exception: Raises various exceptions if files do not exist or fail to
            be created.

    Returns:
        List[str]: Returns a list of locations for the GCC ast files.
    """
    compiler = None
    plugin_name = "ast_dump.so"
    if language in {"c", "c++"}:
        compiler = "g++-10.1"
    elif language == "f":
        compiler = "gfortran-10.1"
        plugin_name = "ast_dump_for.so"
    else:
        raise Exception(f"Error: Unknown language specified {language}")

    assert os.path.exists(
        GCC_10_BIN_DIRECTORY
    ), f"Error: GCC binaries not installed at expected location: {GCC_10_BIN_DIRECTORY}"

    full_plugin_path = plugin_location + plugin_name
    assert os.path.exists(
        full_plugin_path
    ), f"Error: GCC AST dump plugin does not exist at expected location: {full_plugin_path}"

    # Runs gcc with the given source file. This should create the file ast.json
    # with the programs ast inside of it.
    results = subprocess.run(
        [
            f"{GCC_10_BIN_DIRECTORY}/{compiler}",
            f"-fplugin={full_plugin_path}",
            "-O0",
            # Need to use -c if only one file in order to make a .o file
            "-c" if len(input_files) == 1 else "",
            # "-x",
            # "c++",
        ]
        + input_files
        + [
            "-o",
            "/dev/null",
        ],
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

    return ast_file_names