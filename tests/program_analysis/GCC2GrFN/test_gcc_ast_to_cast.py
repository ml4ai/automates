import pytest
import json
from pathlib import Path

from automates.program_analysis.CAST2GrFN.cast import CAST
from automates.program_analysis.GCC2GrFN.gcc_ast_to_cast import GCC2CAST

# All test data is stored in `TEST_DATA_DIR`
# Each test uses two files for test data
#     1. the gcc AST json file
#     2. the expected CAST json file
# We use pytests parameterize functionality to dynamically
# generate tests based on a test names.  To make this work correctly,
# the gcc AST json and expected CAST json must follow an expected pattern.
# For now, we use the following:
#    - For a test named "name_of_test"
#    - The gcc_AST_json file should be named: "name_of_test_gcc_ast.json"
#    - The expected CAST json file should be named: "name_of_test--CAST.json"
# When adding new tests, you must do the following two things:
#    - Add the gcc AST json and expected CAST json files to `TEST_DATA_DIR` using the
#      the naming pattern described above

TEST_DATA_DIR = "tests/data/program_analysis/GCC2GrFN/gcc_to_cast_pipeline"

def make_gcc_ast_json_file_path(test_name: str) -> str:
    return f"{TEST_DATA_DIR}/{test_name}_gcc_ast.json"


def make_expected_cast_file_path(test_name: str) -> str:
    return f"{TEST_DATA_DIR}/{test_name}--CAST.json"


def build_cast_from_gcc_json(path_to_json: str) -> CAST:
    gcc_ast_json = json.load(open(path_to_json, "r"))
    return GCC2CAST([gcc_ast_json]).to_cast()


def load_cast_from_json(path_to_json: str) -> CAST:
    return CAST.from_json_file(path_to_json)


# For now, we use the `__eq__` method on CAST objects.  It 
# may be necessary to use a more fine-grained check in the
# future.
def check_cast_equality(cast1: CAST, cast2: CAST) -> bool:
    return cast1 == cast2


# We find the test names to run, by using a glob over the TEST_DATA_DIR directory
def collect_test_names():
    """ "
    Finds all test names in `TEST_DATA_DIR` which have are valid, i.e.
    which have both a C file and associated gcc AST json
    """
    test_data_dir_path = Path(TEST_DATA_DIR)
    cast_files = test_data_dir_path.glob("*--CAST.json")
    ast_files = test_data_dir_path.glob("*_gcc_ast.json")
    # the stem of the file is the file name without extension
    cast_test_names = [f.stem.replace("--CAST", "") for f in cast_files]
    ast_test_names = [f.stem.replace("_gcc_ast", "") for f in ast_files]

    test_names = set(cast_test_names).intersection(set(ast_test_names))
    return test_names


TEST_NAMES = collect_test_names()


@pytest.mark.parametrize("test_name", TEST_NAMES)
def test_expected_cast(test_name):
    gcc_json_file_path = make_gcc_ast_json_file_path(test_name)
    expected_cast_file_path = make_expected_cast_file_path(test_name)

    created_cast = build_cast_from_gcc_json(gcc_json_file_path)
    expected_cast = load_cast_from_json(expected_cast_file_path)

    assert check_cast_equality(created_cast, expected_cast)
