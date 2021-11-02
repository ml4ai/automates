import os
import subprocess

GCC_10_BIN_DIRECTORY = "/usr/local/gcc-10.1.0/bin/"


def run_gcc(
    compiler_name,
    full_plugin_path,
    input_files,
    compile_binary,
    no_optimize,
):
    command = [
        f"{GCC_10_BIN_DIRECTORY}/{compiler_name}",
        f"-fplugin={full_plugin_path}",
    ]

    if no_optimize:
        command.append("-O0")

    if not compile_binary and len(input_files) == 1:
        command.append("-c")

    command.extend(input_files)

    if not compile_binary:
        command.extend(["-o", "/dev/null"])

    # Runs gcc with the given source file. This should create the file ast.json
    # with the programs ast inside of it.
    results = subprocess.run(
        command,
        errors=True,
        # capture_output=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if results.returncode == 0:
        return (True, results)
    else:
        return (False, results)


def gather_ast_files(input_files):
    ast_file_names = [
        f"./{i.split('/')[-1].rsplit('.')[0]}_gcc_ast.json" for i in input_files
    ]

    # Assert an ast was made for each input file
    for a in ast_file_names:
        assert os.path.exists(
            a
        ), f"Error: {a} file not created after executing GCC plugin"

    return ast_file_names


def run_gcc_plugin(
    language,
    input_files,
    plugin_location="./",
    compile_binary=False,
    no_optimize=True,
):
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
        # compiler = "gcc-10.1"
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

    results = run_gcc(
        compiler,
        full_plugin_path,
        input_files,
        compile_binary,
        no_optimize,
    )
    # Assert return code is 0 which is success
    assert results[
        0
    ], f"Error: Received bad return code when executing GCC plugin: {results[1].returncode}\n"

    return gather_ast_files(input_files)
