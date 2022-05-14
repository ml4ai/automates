import pytest
import dill
from pathlib import Path

import automates.utils.misc as misc
from automates.program_analysis.CAST2GrFN.cast import CAST
from automates.program_analysis.CAST2GrFN.ann_cast.cast_to_annotated_cast import CastToAnnotatedCastVisitor
from automates.program_analysis.CAST2GrFN.ann_cast.annotated_cast import PipelineState
from automates.program_analysis.CAST2GrFN.ann_cast.ann_cast_utility import run_all_ann_cast_passes
from automates.model_assembly.networks import GroundedFunctionNetwork

# All test data is stored in `TEST_DATA_DIR`
# Each test uses two files for test data
#     1. the input CAST json file
#     2. the expected pickled AnnCast object
# We use pytests parameterize functionality to dynamically
# generate tests based on files in `TEST_DATA_DIR`.  To make this work correctly,
# the input CAST json and pickled AnnCast object must follow an expected pattern.
# For now, we use the following:
#    - For a test named "name_of_test"
#    - The CAST json file should be named: "name_of_test--CAST.json"
#    - The expected pickled AnnCast object should be named: "name_of_test--AnnCast.pickled"
# When adding new tests, you must do the following two things:
#    - Add the input CAST json and expected pickled AnnCast object to `TEST_DATA_DIR` using the
#      the naming pattern described above

TEST_DATA_DIR = "tests/data/program_analysis/CAST2GrFN/ann_cast_pipeline_grfn_2_2"

def make_cast_json_file_path(test_name: str) -> str:
    return f"{TEST_DATA_DIR}/{test_name}--CAST.json"

def make_pickled_ann_cast_file_path(test_name: str) -> str:
    return f"{TEST_DATA_DIR}/{test_name}--AnnCast.pickled"

def load_cast_from_json(path_to_cast_json: str) -> CAST:
    return CAST.from_json_file(path_to_cast_json)

def load_pickled_ann_cast_obj(path_to_pickled_obj: str) -> PipelineState:
    with open(path_to_pickled_obj, "rb") as obj:
        return dill.load(obj)

def run_ann_cast_pipeline(path_to_cast_json: str) -> GroundedFunctionNetwork:
    cast = load_cast_from_json(path_to_cast_json)
    # Before generating GrFN, set the seed to generate uuids consistently
    misc.rd.seed(0)

    cast_visitor = CastToAnnotatedCastVisitor(cast)
    pipeline_state = cast_visitor.generate_annotated_cast(grfn_2_2=True)

    run_all_ann_cast_passes(pipeline_state, verbose=False)

    return pipeline_state

def check_ann_cast_equality(pipeline_state1, pipeline_state2) -> bool:
    # FUTURE: extend AnnCast nodes `equiv()` method as needed
    return pipeline_state1.equiv(pipeline_state2)

# We find the test names to run, by using a glob over the TEST_DATA_DIR directory
def collect_test_names():
    """ "
    Finds all test names in `TEST_DATA_DIR` which have are valid, i.e.
    which have both a CAST json file and GrFN json
    """
    test_data_dir_path = Path(TEST_DATA_DIR)
    cast_files = test_data_dir_path.glob("*--CAST.json")
    ann_cast_files = test_data_dir_path.glob("*--AnnCast.pickled")
    # the stem of the file is the file name without extension
    cast_test_names = [f.stem.replace("--CAST", "") for f in cast_files]
    ann_cast_test_names = [f.stem.replace("--AnnCast", "") for f in ann_cast_files]

    test_names = set(cast_test_names).intersection(set(ann_cast_test_names))
    return test_names

TEST_NAMES = collect_test_names()

@pytest.mark.parametrize("test_name", TEST_NAMES)
def test_expected_grfn(test_name):
    cast_file_path = make_cast_json_file_path(test_name)
    ann_cast_file_path = make_pickled_ann_cast_file_path(test_name)

    created_ann_cast = run_ann_cast_pipeline(cast_file_path)
    expected_ann_cast = load_pickled_ann_cast_obj(ann_cast_file_path)

    assert check_ann_cast_equality(created_ann_cast, expected_ann_cast)
