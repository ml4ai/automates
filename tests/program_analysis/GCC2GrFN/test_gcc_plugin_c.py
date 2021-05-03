import pytest
import subprocess
import os
import random
import json
import numpy as np

# import automates.model_assembly.networks as networks
import automates.utils.misc as misc
from automates.program_analysis.CAST2GrFN.cast import CAST
from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.program_analysis.GCC2GrFN.gcc_ast_to_cast import GCC2CAST

GCC_10_BIN_DIRECTORY = "/usr/local/gcc-10.1.0/bin/"
GCC_PLUGIN_IMAGE = "automates/program_analysis/gcc_plugin/plugin/ast_dump.so"
GCC_TEST_DATA_DIRECTORY = "tests/data/program_analysis/GCC2GrFN"


def cleanup():
    if os.path.exists("./ast.json"):
        os.remove("ast.json")
    # TODO remove object files too
    # os.remove("*.o")


@pytest.fixture(scope="module", autouse=True)
def run_before_tests(request):
    # TODO ensure gcc plugin is compiled
    # prepare something ahead of all tests
    # results = subprocess.run(
    #     [
    #         gpp_command,
    #         plugin_option,
    #         "-c",
    #         c_file,
    #         "-o",
    #         "/dev/null",
    #     ]
    # )
    assert os.path.exists(
        "automates/program_analysis/gcc_plugin/plugin/ast_dump.so"
    ), f"Error: GCC AST dump plugin does not exist at expected location: {GCC_PLUGIN_IMAGE}"


@pytest.fixture(autouse=True)
def run_around_tests():
    # Before each test, set the seed for generating uuids to 0 for consistency
    # between tests and expected output
    misc.rd = random.Random()
    misc.rd.seed(0)

    # Run the test function
    yield

    cleanup()


def run_gcc_plugin_with_c_file(c_file):
    gpp_command = GCC_10_BIN_DIRECTORY + "g++-10.1"
    plugin_option = f"-fplugin={GCC_PLUGIN_IMAGE}"
    # Runs g++ with the given c file. This should create the file ast.json
    # with the programs ast inside of it.
    results = subprocess.run(
        [
            gpp_command,
            plugin_option,
            "-c",
            "-x",
            "c++",
            c_file,
            # "-o",
            # "/dev/null",
        ],
        stdout=subprocess.DEVNULL,
    )

    # Assert return code is 0 which is success
    assert results.returncode == 0


def test_c_simple_function_and_assignments():
    run_gcc_plugin_with_c_file(
        f"{GCC_TEST_DATA_DIRECTORY}/simple_function_and_assignments/simple_function_and_assignments.c"
    )

    gcc_ast_obj = json.load(open("./ast.json"))
    cast = GCC2CAST(gcc_ast_obj).to_cast()

    assert os.path.exists("./ast.json")


def test_all_binary_ops():
    test_name = "all_binary_ops"
    test_dir = f"{GCC_TEST_DATA_DIRECTORY}/{test_name}"
    run_gcc_plugin_with_c_file(f"{test_dir}/{test_name}.c")

    assert os.path.exists("./ast.json")

    gcc_ast_obj = json.load(open("./ast.json"))

    expected_cast_json = json.load(open(f"{test_dir}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json, cast_source_language="c")
    cast = GCC2CAST(gcc_ast_obj).to_cast()
    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{test_dir}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()
    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    assert result == {
        "add": np.array([3]),
        "bitwise_and": np.array([0]),
        "bitwise_l_shift": np.array([2]),
        "bitwise_or": np.array([3]),
        "bitwise_r_shift": np.array([1]),
        "bitwise_xor": np.array([3]),
        "div": np.array([2]),
        "eq": np.array([False]),
        "gt": np.array([False]),
        "gte": np.array([False]),
        "lt": np.array([True]),
        "lte": np.array([True]),
        "mult": np.array([6]),
        "neq": np.array([True]),
        "remainder": np.array([2]),
        "sub": np.array([-1]),
    }


def test_all_unary_ops():
    test_name = "all_unary_ops"
    test_dir = f"{GCC_TEST_DATA_DIRECTORY}/{test_name}"
    run_gcc_plugin_with_c_file(f"{test_dir}/{test_name}.c")

    assert os.path.exists("./ast.json")

    gcc_ast_obj = json.load(open("./ast.json"))

    expected_cast_json = json.load(open(f"{test_dir}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json)
    cast = GCC2CAST(gcc_ast_obj).to_cast()
    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{test_dir}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()
    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    assert result == {
        "bitwise_not": np.array([-2]),
        "logical_not": np.array([False]),
        "unary_plus": np.array([-1]),
    }


def test_function_call():
    test_name = "function_call"
    test_dir = f"{GCC_TEST_DATA_DIRECTORY}/{test_name}"
    run_gcc_plugin_with_c_file(f"{test_dir}/{test_name}.c")

    assert os.path.exists("./ast.json")

    gcc_ast_obj = json.load(open("./ast.json"))

    expected_cast_json = json.load(open(f"{test_dir}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json)
    cast = GCC2CAST(gcc_ast_obj).to_cast()
    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{test_dir}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()

    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    assert result == {
        "x": np.array([25]),
    }


@pytest.mark.skip(reason="Developing still")
def test_one_variable_for_multiple_args():
    pass


@pytest.mark.skip(reason="Developing still")
def test_function_call_no_starting_nodes_in_root():
    # TODO cannot currently execute GrFN with no starting node in root container
    # (This should be fixed when master is merged in?)
    pass


@pytest.mark.skip(reason="Developing still")
def test_function_call_with_args():
    pass


@pytest.mark.skip(reason="Developing still")
def test_function_call_with_complex_return():
    pass


@pytest.mark.skip(reason="Developing still")
def test_nested_function_call():
    pass


@pytest.mark.skip(reason="Developing still")
def test_if_statement():
    pass


@pytest.mark.skip(reason="Developing still")
def test_if_else_statement():
    pass


@pytest.mark.skip(reason="Developing still")
def test_if_elif_statement():
    pass


@pytest.mark.skip(reason="Developing still")
def test_if_elif_else_statement():
    pass


@pytest.mark.skip(reason="Developing still")
def test_nested_if_statements():
    pass


@pytest.mark.skip(reason="Developing still")
def test_for_loop():
    pass


@pytest.mark.skip(reason="Developing still")
def test_while_loop():
    pass


@pytest.mark.skip(reason="Developing still")
def test_nested_loops():
    pass


@pytest.mark.skip(reason="Developing still")
def test_nested_conditionals():
    pass


@pytest.mark.skip(reason="Developing still")
def test_nested_function_calls_and_conditionals():
    pass


@pytest.mark.skip(reason="Developing still")
def test_global_variable_passing():
    pass


@pytest.mark.skip(reason="Developing still")
def test_pack_and_extract():
    pass


@pytest.mark.skip(reason="Developing still")
def test_only_pack():
    pass


@pytest.mark.skip(reason="Developing still")
def test_only_extract():
    pass


@pytest.mark.skip(reason="Developing still")
def test_multiple_levels_extract_and_pack():
    pass


@pytest.mark.skip(reason="Developing still")
def test_multiple_variables_extract_and_pack():
    pass


@pytest.mark.skip(reason="Developing still")
def test_nested_types():
    pass


@pytest.mark.skip(reason="Developing still")
def test_no_root_container():
    pass


@pytest.mark.skip(reason="Developing still")
def test_array_usage():
    pass


@pytest.mark.skip(reason="Developing still")
def test_multi_file():
    pass


@pytest.mark.skip(reason="Developing still")
def test_source_refs():
    pass


@pytest.mark.skip(reason="Developing still")
def test_pid_controller():
    pass
