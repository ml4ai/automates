import pytest
import json
import os
import subprocess
from pathlib import Path
from sys import platform
from types import SimpleNamespace
from typing import List

# All test data is stored in `TEST_DATA_DIR`
# Each test uses two files for test data
#     1. the C source file
#     2. the expected gcc AST json file
# We use pytest's parametrize functionality to dynamically
# generate tests based on a test names.  To make this work correctly,
# the source and gcc AST json files must follow an expected pattern.
# For now, we use the following:
#    - For a test named "name_of_test"
#    - The source file should be named: "name_of_test.c"
#    - The gcc_AST_json file should be named: "name_of_test_gcc_ast.json"
# When adding new tests, you must do the following two things:
#    - Add the C source file and expected gcc AST json to `TEST_DATA_DIR` using the
#      the naming pattern described above

# Below, we use `SimpleNamespace` to automatically convert the gcc AST json to
# an object.  This allows us to access fields with dots instead of dictionary like access.
# I.e. we can write `json.field1.field2` instead of `json["field1"]["field2"]`

TEST_DATA_DIR = "tests/data/program_analysis/GCC2GrFN/gcc_to_cast_pipeline"
GCC_10_BIN_DIRECTORY = "/usr/local/gcc-10.1.0/bin"
GCC_PLUGIN_IMAGE = "automates/program_analysis/gcc_plugin/plugin/ast_dump.so"

# global identifiers such as `stdin`, `stdout`, `stderr`
# can be added to the AST by including system header files
# However, the CI that is run on Github actions includes additional 
# global names which should be skipped.  
# It sounds like these global names are added from errno.h
GLOBAL_NAMES_TO_SKIP = ['_sys_errlist', '_sys_nerr', 'sys_errlist', 'sys_nerr']


def make_gcc_ast_json_file_path(test_name: str) -> str:
    return f"{TEST_DATA_DIR}/{test_name}_gcc_ast.json"


def make_source_file_path(test_name: str) -> str:
    return f"{TEST_DATA_DIR}/{test_name}.c"


# We find the test names to run, by using a glob over the TEST_DATA_DIR directory
def collect_test_names():
    """ "
    Finds all test names in `TEST_DATA_DIR` which have are valid, i.e.
    which have both a C file and associated gcc AST json
    """
    test_data_dir_path = Path(TEST_DATA_DIR)
    c_files = test_data_dir_path.glob("*.c")
    ast_files = test_data_dir_path.glob("*_gcc_ast.json")
    # the stem of the file is the file name without extension
    c_test_names = [f.stem for f in c_files]
    ast_test_names = [f.stem.replace("_gcc_ast", "") for f in ast_files]

    test_names = set(c_test_names).intersection(set(ast_test_names))
    return test_names


class FunctionData:
    """
    This class grabs certain fields of a function from a
    gcc AST json, and is used to check equality between two function.
    This class can be extended with more fields as desired.

    Currently we track:
        - the name of the function
        - the names of parameters to the function
        - the names of variable declaration inside the function
        - the number of loops inside the function
    """
    name: str
    parameters: List[str]
    variable_declarations: List[str]
    number_of_loops: int

    def __init__(self, function: SimpleNamespace):
        self.name = function.name
        # due to single static assignments, some variable declarations
        # in a function do not have a name (only an id)
        named_var_declarations = filter(
            lambda var: hasattr(var, "name"), function.variableDeclarations
        )
        self.variable_declarations = [var.name for var in named_var_declarations]
        self.parameters = []
        if hasattr(function, "parameters"):
            self.parameters = [param.name for param in function.parameters]
        self.number_of_loops = function.numberOfLoops

    def __eq__(self, other):
        
        equal = (
            self.name == other.name
            and self.variable_declarations == other.variable_declarations
            and self.parameters == other.parameters
            and self.number_of_loops == other.number_of_loops
        )

        # We print out the difference, so it can be viewed in Github CI results
        if not equal:
            print(f"{50*'*'}")
            print(f"DEBUGGING: in __eq__ for FunctionData")
            print(f"{5*' '}self.name = {self.name}, other.name = {other.name}")
            print(f"{5*' '}self.var_decls = {self.variable_declarations}, other.var_decls = {other.variable_declarations}")
            print(f"{5*' '}self.params = {self.parameters}, other.params = {other.parameters}")
            print(f"{5*' '}self.num_loops = {self.number_of_loops}, other.num_loops = {other.number_of_loops}")
            print(f"{50*'*'}")

        return equal

def build_gcc_ast_json_from_source(test_name: str) -> SimpleNamespace:
    path_to_source = make_source_file_path(test_name)
    run_gcc_plugin_with_c_file(path_to_source)
    print(f"cwd = {os.getcwd()}")
    path_to_json = f"{test_name}_gcc_ast.json"
    return load_gcc_ast_json(path_to_json)


def load_gcc_ast_json(path_to_json: str) -> SimpleNamespace:
    # Parse JSON into an object with attributes corresponding to dict keys
    return json.load(
        open(path_to_json, "r"), object_hook=lambda d: SimpleNamespace(**d)
    )


def compare_asts(ast1: SimpleNamespace, ast2: SimpleNamespace) -> bool:
    """
    Compares `ast1` and `ast2` to check if they match.
    Currently, we only check specific fields in the AST.  More fields can be added later
    as stability of the produced AST increases.

    Returns True if they match and False otherwise
    """
    same_globals = compare_global_variables(ast1, ast2)
    same_functions = compare_ast_functions(ast1, ast2)
    return same_globals and same_functions


def compare_global_variables(ast1: SimpleNamespace, ast2: SimpleNamespace) -> bool:
    """
    Check that global variables of the same name appear in each AST.  We remove the global
    variables names that appear in `GLOBAL_NAMES_TO_SKIP`.  The names from that list
    appear on Github Actions CI, but not locally.

    Returns True if global variable names match and False otherwise
    """
    ast1_global_names = [gv.name for gv in ast1.globalVariables]
    ast1_global_names = set(ast1_global_names).difference(GLOBAL_NAMES_TO_SKIP)
    ast2_global_names = [gv.name for gv in ast2.globalVariables]
    ast2_global_names = set(ast2_global_names).difference(GLOBAL_NAMES_TO_SKIP)
    
    # We print out the difference, so it can be viewed in Github CI results
    if set(ast1_global_names) != set(ast2_global_names):
        print(f"{50*'*'}")
        print(f"DEBUGGING: in compare_global_variables")
        print(f"{5*' '}ast1_g_names = {ast1_global_names} and ast2_g_names = {ast2_global_names}")
        print(f"{50*'*'}")
        return False

    return True


def compare_ast_functions(ast1: SimpleNamespace, ast2: SimpleNamespace) -> bool:
    """
    Checks that the "functions" list of `ast1` matches the functions list of `ast2`
    For individual functions from the list, we only check equality of fields
    defined in `FunctionData`.

    Returns True is the functions lists match and False otherwise
    """
    ast1_functions = {}
    ast2_functions = {}

    # map functions name to FunctionData to easily grab during comparison
    for func in ast1.functions:
        ast1_functions[func.name] = FunctionData(func)

    for func in ast2.functions:
        ast2_functions[func.name] = FunctionData(func)

    if len(ast1_functions) != len(ast2_functions):
        return False

    # check functions are the same
    for name, func1 in ast1_functions.items():
        if name not in ast2_functions:
            return False
        func2 = ast2_functions[name]
        if func1 != func2:
            return False

    return True


@pytest.fixture(scope="session", autouse=True)
def cleanup_files():
    """
    Pytest fixture which runs after all test to
    remove object files and gcc AST jsons created during test run time
    """
    # don't do anything to start the session
    yield  # run the session
    # clean up after session
    for item in os.listdir("./"):
        if item.endswith(".o") or item.endswith("_gcc_ast.json"):
            os.remove("./" + item)


TEST_NAMES = collect_test_names()


@pytest.mark.parametrize("test_name", TEST_NAMES)
def test_expected_ast(test_name):
    expected_ast_file_path = make_gcc_ast_json_file_path(test_name)

    created_ast = build_gcc_ast_json_from_source(test_name)
    expected_ast = load_gcc_ast_json(expected_ast_file_path)

    assert compare_asts(created_ast, expected_ast)


@pytest.fixture(scope="module", autouse=True)
def run_before_tests(request):
    # Change to the plugin dir and remove the current plugin image
    cur_dir = os.getcwd()
    os.chdir("automates/program_analysis/gcc_plugin/plugin/")
    if os.path.exists("./ast_dump.so"):
        os.remove("./ast_dump.so")

    if platform == "linux" or platform == "linux2":
        # linux, run "make linux"
        subprocess.run(["make", "linux"], stdout=subprocess.DEVNULL)
    elif platform == "darwin":
        # OS X, run "make"
        subprocess.run(["make"], stdout=subprocess.DEVNULL)
    elif platform == "win32":
        raise Exception("Error: Unable to run tests on windows.")

    # Return to working dir
    os.chdir(cur_dir)

    assert os.path.exists(
        "automates/program_analysis/gcc_plugin/plugin/ast_dump.so"
    ), f"Error: GCC AST dump plugin does not exist at expected location: {GCC_PLUGIN_IMAGE}"


def run_gcc_plugin_with_c_file(c_file):
    gpp_command = os.getenv("CUSTOM_GCC_10_PATH")
    if gpp_command is None:
        gpp_command = f"{GCC_10_BIN_DIRECTORY}/g++-10.1"
    plugin_option = f"-fplugin={GCC_PLUGIN_IMAGE}"
    # Runs g++ with the given c file. This creates a file ending with "*_gcc_ast.json"
    # with the programs AST inside of it.
    results = subprocess.run(
        [
            gpp_command,
            plugin_option,
            "-c",
            "-x",
            "c++",
            c_file,
        ],
        stdout=subprocess.DEVNULL,
    )
    # Assert return code is 0 which is success
    assert results.returncode == 0
