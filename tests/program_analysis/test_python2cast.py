import pytest
import json
import os


from automates.program_analysis.CAST2GrFN.cast import CAST


def cast_json_comparison(dir_path: str, C: CAST):
    cast_filename = "temp_model--CAST.json"
    json.dump(C.to_json_object(), open(cast_filename, "w"))
    dumped_data = json.load(open(cast_filename, "r"))
    dumped_C = CAST.from_json_data(dumped_data, cast_source_language="python")
    assert C == dumped_C
    os.remove(cast_filename)

    test_name = dir_path[dir_path.rfind("/") + 1 :]
    prev_cast_json_file = os.path.join(dir_path, f"{test_name}--CAST.json")
    prev_data = json.load(open(prev_cast_json_file, "r"))
    prev_C = CAST.from_json_data(prev_data, cast_source_language="python")
    assert C == prev_C


@pytest.mark.literal_tests
def test_literal_direct_assg(
    literal_direct_assg_path, literal_direct_assg_cast
):
    assert isinstance(literal_direct_assg_cast, CAST)
    cast_json_comparison(literal_direct_assg_path, literal_direct_assg_cast)


@pytest.mark.literal_tests
def test_literal_in_stmt(literal_in_stmt_path, literal_in_stmt_cast):
    assert isinstance(literal_in_stmt_cast, CAST)
    cast_json_comparison(literal_in_stmt_path, literal_in_stmt_cast)


@pytest.mark.model_tests
def test_Simple_SIR(Simple_SIR_path, Simple_SIR_cast):
    assert isinstance(Simple_SIR_cast, CAST)
    cast_json_comparison(Simple_SIR_path, Simple_SIR_cast)
