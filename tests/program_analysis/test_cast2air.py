import pytest
import json
import os


from automates.model_assembly.air import AutoMATES_IR


def air_json_comparison(dir_path: str, air: AutoMATES_IR):
    air_filename = "temp_model--AIR.json"
    air.to_json(air_filename)
    dumped_data = json.load(open(air_filename, "r"))
    dumped_air = AutoMATES_IR.from_air_json(dumped_data)
    assert air == dumped_air
    os.remove(air_filename)

    test_name = dir_path[dir_path.rfind("/") + 1 :]
    prev_air_json_file = os.path.join(dir_path, f"{test_name}--AIR.json")
    prev_data = json.load(open(prev_air_json_file, "r"))
    prev_air = AutoMATES_IR.from_air_json(prev_data)
    assert air == prev_air


@pytest.mark.literal_tests
def test_literal_direct_assg(
    literal_direct_assg_path, literal_direct_assg_air
):
    assert isinstance(literal_direct_assg_air, AutoMATES_IR)
    air_json_comparison(literal_direct_assg_path, literal_direct_assg_air)


@pytest.mark.literal_tests
def test_literal_in_stmt(literal_in_stmt_path, literal_in_stmt_air):
    assert isinstance(literal_in_stmt_air, AutoMATES_IR)
    air_json_comparison(literal_in_stmt_path, literal_in_stmt_air)


@pytest.mark.model_tests
def test_Simple_SIR(Simple_SIR_path, Simple_SIR_air):
    assert isinstance(Simple_SIR_air, AutoMATES_IR)
    air_json_comparison(Simple_SIR_path, Simple_SIR_air)
