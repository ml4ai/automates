import pytest
from pathlib import Path

import automates.utils.misc as misc
from automates.program_analysis.CAST2GrFN.cast import CAST
from automates.program_analysis.CAST2GrFN.ann_cast.cast_to_annotated_cast import CastToAnnotatedCastVisitor
from automates.program_analysis.CAST2GrFN.ann_cast.ann_cast_utility import *
from automates.model_assembly.networks import GroundedFunctionNetwork

# All test data is stored in `TEST_DATA_DIR`
# Each test uses two files for test data
#     1. the input CAST json file
#     2. the expected GrFN json file
# We use pytests parameterize functionality to dynamically
# generate tests based on files in `TEST_DATA_DIR`.  To make this work correctly,
# the input CAST json and expected GrFN json must follow an expected pattern.
# For now, we use the following:
#    - For a test named "name_of_test"
#    - The CAST json file should be named: "name_of_test--CAST.json"
#    - The expected GrFN json file should be named: "name_of_test--GrFN.json"
# When adding new tests, you must do the following two things:
#    - Add the input CAST json and expected GrFN json files to `TEST_DATA_DIR` using the
#      the naming pattern described above

TEST_DATA_DIR = "tests/data/program_analysis/CAST2GrFN/ann_cast_pipeline_grfn_2_2"

def make_cast_json_file_path(test_name: str) -> str:
    return f"{TEST_DATA_DIR}/{test_name}--CAST.json"

def make_grfn_json_file_path(test_name: str) -> str:
    return f"{TEST_DATA_DIR}/{test_name}--GrFN.json"

def load_cast_from_json(path_to_cast_json: str) -> CAST:
    return CAST.from_json_file(path_to_cast_json)

def load_grfn_from_json(path_to_grfn_json: str) -> GroundedFunctionNetwork:
    return GroundedFunctionNetwork.from_json(path_to_grfn_json)

def run_ann_cast_pipeline(path_to_cast_json: str) -> GroundedFunctionNetwork:
    cast = load_cast_from_json(path_to_cast_json)
    # Before generating GrFN, set the seed to generate uuids consistently
    # misc.rd = random.Random()
    misc.rd.seed(0)

    cast_visitor = CastToAnnotatedCastVisitor(cast)
    pipeline_state = cast_visitor.generate_annotated_cast(grfn_2_2=True)

    run_all_ann_cast_passes(pipeline_state, verbose=False)

    return pipeline_state.get_grfn()

def check_grfn_equality(grfn1, grfn2) -> bool:
    # FUTURE: we should also check execution results
    # the exectution results should be exported to JSON
    # to capture results at the time the JSON was created
    return grfn1 == grfn2

# We find the test names to run, by using a glob over the TEST_DATA_DIR directory
def collect_test_names():
    """ "
    Finds all test names in `TEST_DATA_DIR` which have are valid, i.e.
    which have both a CAST json file and GrFN json
    """
    test_data_dir_path = Path(TEST_DATA_DIR)
    cast_files = test_data_dir_path.glob("*--CAST.json")
    grfn_files = test_data_dir_path.glob("*--GrFN.json")
    # the stem of the file is the file name without extension
    cast_test_names = [f.stem.replace("--CAST", "") for f in cast_files]
    grfn_test_names = [f.stem.replace("--GrFN", "") for f in grfn_files]

    test_names = set(cast_test_names).intersection(set(grfn_test_names))
    return test_names

TEST_NAMES = collect_test_names()

@pytest.mark.parametrize("test_name", TEST_NAMES)
def test_expected_grfn(test_name):
    cast_file_path = make_cast_json_file_path(test_name)
    grfn_file_path = make_grfn_json_file_path(test_name)

    created_grfn = run_ann_cast_pipeline(cast_file_path)
    expected_grfn = load_grfn_from_json(grfn_file_path)

    assert check_grfn_equality(created_grfn, expected_grfn)
