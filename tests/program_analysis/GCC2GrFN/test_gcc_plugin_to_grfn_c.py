import pytest
import subprocess
import os
import random
import json
import numpy as np
from sys import platform

import automates.utils.misc as misc
from automates.program_analysis.CAST2GrFN.cast import CAST
from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.program_analysis.GCC2GrFN.gcc_ast_to_cast import GCC2CAST

GCC_10_BIN_DIRECTORY = "/usr/local/gcc-10.1.0/bin/"
GCC_PLUGIN_IMAGE = "automates/program_analysis/gcc_plugin/plugin/ast_dump.so"
TEST_DATA_DIR = "tests/data/program_analysis/GCC2GrFN/legacy_gcc_to_grfn"


def cleanup():
    for item in os.listdir("./"):
        if item.endswith(".o") or item.endswith("_gcc_ast.json"):
            os.remove("./" + item)


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


@pytest.fixture(autouse=True)
def run_around_tests():
    # Before each test, set the seed for generating uuids to 0 for consistency
    # between tests and expected output
    misc.rd = random.Random()
    misc.rd.seed(0)

    # Run the test function
    yield

    # clean up generated files
    cleanup()


def run_gcc_plugin_with_c_file(c_file):
    gpp_command = os.getenv("CUSTOM_GCC_10_PATH")
    if gpp_command is None:
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


def evaluate_execution_results(expected_result, result):
    for k, v in expected_result.items():
        assert k in result
        try:
            assert v == result[k]
        except AssertionError:
            raise AssertionError(f"Error in result for key {k}: {v} != {result[k]}")


def test_c_simple_function_and_assignments():
    test_name = "simple_function_and_assignments"
    run_gcc_plugin_with_c_file(f"{TEST_DATA_DIR}/{test_name}.c")

    assert os.path.exists(f"./{test_name}_gcc_ast.json")

    gcc_ast_obj = json.load(open(f"./{test_name}_gcc_ast.json"))

    expected_cast_json = json.load(open(f"{TEST_DATA_DIR}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json, cast_source_language="c")
    cast = GCC2CAST([gcc_ast_obj], legacy_cast=True).to_cast()

    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{TEST_DATA_DIR}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()

    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    expected_result = {"y": np.array([465])}
    evaluate_execution_results(expected_result, result)


def test_all_binary_ops():
    test_name = "all_binary_ops"
    run_gcc_plugin_with_c_file(f"{TEST_DATA_DIR}/{test_name}.c")

    assert os.path.exists(f"./{test_name}_gcc_ast.json")

    gcc_ast_obj = json.load(open(f"./{test_name}_gcc_ast.json"))

    expected_cast_json = json.load(open(f"{TEST_DATA_DIR}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json, cast_source_language="c")
    cast = GCC2CAST([gcc_ast_obj], legacy_cast=True).to_cast()

    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{TEST_DATA_DIR}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()

    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    expected_result = {
        "add": np.array([3]),
        "bitwise_and": np.array([0]),
        "bitwise_l_shift": np.array([2]),
        "bitwise_or": np.array([3]),
        "bitwise_r_shift": np.array([1]),
        "bitwise_xor": np.array([3]),
        "div": np.array([0.5]),
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

    evaluate_execution_results(expected_result, result)


def test_all_unary_ops():
    test_name = "all_unary_ops"
    run_gcc_plugin_with_c_file(f"{TEST_DATA_DIR}/{test_name}.c")

    assert os.path.exists(f"./{test_name}_gcc_ast.json")

    gcc_ast_obj = json.load(open(f"./{test_name}_gcc_ast.json"))

    expected_cast_json = json.load(open(f"{TEST_DATA_DIR}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json)
    cast = GCC2CAST([gcc_ast_obj], legacy_cast=True).to_cast()

    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{TEST_DATA_DIR}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()

    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    expected_result = {
        "bitwise_not": np.array([-2]),
        "logical_not": np.array([False]),
        "unary_plus": np.array([-1]),
    }
    evaluate_execution_results(expected_result, result)


def test_function_call():
    test_name = "function_call"
    run_gcc_plugin_with_c_file(f"{TEST_DATA_DIR}/{test_name}.c")

    assert os.path.exists(f"./{test_name}_gcc_ast.json")
    gcc_ast_obj = json.load(open(f"./{test_name}_gcc_ast.json"))

    expected_cast_json = json.load(open(f"{TEST_DATA_DIR}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json)
    cast = GCC2CAST([gcc_ast_obj], legacy_cast=True).to_cast()

    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{TEST_DATA_DIR}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()

    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    expected_result = {
        "x": np.array([25]),
    }
    evaluate_execution_results(expected_result, result)


def test_function_call_one_variable_for_multiple_args():
    test_name = "function_call_one_variable_for_multiple_args"
    run_gcc_plugin_with_c_file(f"{TEST_DATA_DIR}/{test_name}.c")

    assert os.path.exists(f"./{test_name}_gcc_ast.json")
    gcc_ast_obj = json.load(open(f"./{test_name}_gcc_ast.json"))

    expected_cast_json = json.load(open(f"{TEST_DATA_DIR}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json)
    cast = GCC2CAST([gcc_ast_obj], legacy_cast=True).to_cast()

    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{TEST_DATA_DIR}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()

    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    expected_result = {
        "x": np.array([25]),
    }
    evaluate_execution_results(expected_result, result)


@pytest.mark.skip(reason="Need to fix trimming hanging lambdas in cast_to_air_model")
def test_function_call_no_args():
    test_name = "function_call_no_args"
    run_gcc_plugin_with_c_file(f"{TEST_DATA_DIR}/{test_name}.c")

    assert os.path.exists(f"./{test_name}_gcc_ast.json")
    gcc_ast_obj = json.load(open(f"./{test_name}_gcc_ast.json"))

    expected_cast_json = json.load(open(f"{TEST_DATA_DIR}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json)
    cast = GCC2CAST([gcc_ast_obj], legacy_cast=True).to_cast()

    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{TEST_DATA_DIR}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()

    assert expected_grfn == grfn

    # TODO cannot currently execute GrFN with no starting node in root container
    # (This should be fixed when master is merged in?) no_starting_nodes_in_root
    # inputs = {}
    # result = grfn(inputs)
    # assert result == {
    #     "x": np.array([25]),
    # }


def test_function_call_with_literal_return():
    test_name = "function_call_with_literal_return"
    run_gcc_plugin_with_c_file(f"{TEST_DATA_DIR}/{test_name}.c")

    assert os.path.exists(f"./{test_name}_gcc_ast.json")
    gcc_ast_obj = json.load(open(f"./{test_name}_gcc_ast.json"))

    expected_cast_json = json.load(open(f"{TEST_DATA_DIR}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json)
    cast = GCC2CAST([gcc_ast_obj], legacy_cast=True).to_cast()

    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{TEST_DATA_DIR}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()

    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    expected_result = {
        "x": np.array([5]),
    }
    evaluate_execution_results(expected_result, result)


def test_function_same_func_multiple_times():
    test_name = "function_same_func_multiple_times"
    run_gcc_plugin_with_c_file(f"{TEST_DATA_DIR}/{test_name}.c")

    assert os.path.exists(f"./{test_name}_gcc_ast.json")
    gcc_ast_obj = json.load(open(f"./{test_name}_gcc_ast.json"))

    expected_cast_json = json.load(open(f"{TEST_DATA_DIR}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json)
    cast = GCC2CAST([gcc_ast_obj], legacy_cast=True).to_cast()

    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{TEST_DATA_DIR}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()

    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    expected_result = {
        "five_squared": np.array([25]),
        "two_hundred": np.array([200]),
        "fifty": np.array([50]),
    }
    evaluate_execution_results(expected_result, result)


def test_function_call_literal_args():
    test_name = "function_call_literal_args"
    run_gcc_plugin_with_c_file(f"{TEST_DATA_DIR}/{test_name}.c")

    assert os.path.exists(f"./{test_name}_gcc_ast.json")
    gcc_ast_obj = json.load(open(f"./{test_name}_gcc_ast.json"))

    expected_cast_json = json.load(open(f"{TEST_DATA_DIR}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json)
    cast = GCC2CAST([gcc_ast_obj], legacy_cast=True).to_cast()

    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{TEST_DATA_DIR}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()

    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    expected_result = {
        "five_squared": np.array([25]),
        "two_hundred": np.array([200]),
        "fifty": np.array([50]),
    }
    evaluate_execution_results(expected_result, result)


def test_function_call_expression_args():
    test_name = "function_call_expression_args"
    run_gcc_plugin_with_c_file(f"{TEST_DATA_DIR}/{test_name}.c")

    assert os.path.exists(f"./{test_name}_gcc_ast.json")
    gcc_ast_obj = json.load(open(f"./{test_name}_gcc_ast.json"))

    expected_cast_json = json.load(open(f"{TEST_DATA_DIR}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json)
    cast = GCC2CAST([gcc_ast_obj], legacy_cast=True).to_cast()

    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{TEST_DATA_DIR}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()

    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    expected_result = {
        "r1": np.array([7000]),
        "r2": np.array([50]),
        "r3": np.array([250]),
        "r4": np.array([125]),
    }
    evaluate_execution_results(expected_result, result)


@pytest.mark.skip(reason="Developing still")
def test_function_call_with_mixed_args():
    pass


def test_function_call_with_complex_return():
    test_name = "function_call_with_complex_return"
    run_gcc_plugin_with_c_file(f"{TEST_DATA_DIR}/{test_name}.c")

    assert os.path.exists(f"./{test_name}_gcc_ast.json")
    gcc_ast_obj = json.load(open(f"./{test_name}_gcc_ast.json"))

    expected_cast_json = json.load(open(f"{TEST_DATA_DIR}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json)
    cast = GCC2CAST([gcc_ast_obj], legacy_cast=True).to_cast()

    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{TEST_DATA_DIR}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()

    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    expected_result = {"nine": np.array([9])}
    evaluate_execution_results(expected_result, result)


@pytest.mark.skip(reason="Need to develop a way to trim out the function")
def test_function_no_args_void_return():
    pass


def test_function_call_nested():
    test_name = "function_call_nested"
    run_gcc_plugin_with_c_file(f"{TEST_DATA_DIR}/{test_name}.c")

    assert os.path.exists(f"./{test_name}_gcc_ast.json")
    gcc_ast_obj = json.load(open(f"./{test_name}_gcc_ast.json"))

    expected_cast_json = json.load(open(f"{TEST_DATA_DIR}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json)
    cast = GCC2CAST([gcc_ast_obj], legacy_cast=True).to_cast()

    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{TEST_DATA_DIR}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()

    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    expected_result = {"onesixtyeight": np.array([168])}
    evaluate_execution_results(expected_result, result)


@pytest.mark.skip(reason="GrFN may be incorrect")
def test_if_statement():
    test_name = "if_statement"
    run_gcc_plugin_with_c_file(f"{TEST_DATA_DIR}/{test_name}.c")

    assert os.path.exists(f"./{test_name}_gcc_ast.json")
    gcc_ast_obj = json.load(open(f"./{test_name}_gcc_ast.json"))

    expected_cast_json = json.load(open(f"{TEST_DATA_DIR}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json)
    cast = GCC2CAST([gcc_ast_obj], legacy_cast=True).to_cast()
    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{TEST_DATA_DIR}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()

    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    expected_result = {"x": np.array([10]), "a": np.array([3]), "b": np.array([5])}
    evaluate_execution_results(expected_result, result)


@pytest.mark.skip(reason="GrFN may be incorrect")
def test_if_else_statement():
    test_name = "if_else_statement"
    run_gcc_plugin_with_c_file(f"{TEST_DATA_DIR}/{test_name}.c")

    assert os.path.exists(f"./{test_name}_gcc_ast.json")
    gcc_ast_obj = json.load(open(f"./{test_name}_gcc_ast.json"))

    expected_cast_json = json.load(open(f"{TEST_DATA_DIR}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json)
    cast = GCC2CAST([gcc_ast_obj], legacy_cast=True).to_cast()
    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{TEST_DATA_DIR}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()

    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    expected_result = {"x": np.array([5]), "a": np.array([10]), "b": np.array([5])}
    evaluate_execution_results(expected_result, result)


@pytest.mark.skip(reason="CAST is incorrect (and so is GrFN)")
def test_if_elif_statement():
    test_name = "if_elif_statement"
    run_gcc_plugin_with_c_file(f"{TEST_DATA_DIR}/{test_name}.c")

    assert os.path.exists(f"./{test_name}_gcc_ast.json")
    gcc_ast_obj = json.load(open(f"./{test_name}_gcc_ast.json"))

    expected_cast_json = json.load(open(f"{TEST_DATA_DIR}/{test_name}--CAST.json"))
    expected_cast = CAST.from_json_data(expected_cast_json)
    cast = GCC2CAST([gcc_ast_obj], legacy_cast=True).to_cast()
    assert expected_cast == cast

    expected_grfn = GroundedFunctionNetwork.from_json(
        f"{TEST_DATA_DIR}/{test_name}--GrFN.json"
    )
    grfn = cast.to_GrFN()

    assert expected_grfn == grfn

    inputs = {}
    result = grfn(inputs)
    expected_result = {"x": np.array([5]), "a": np.array([10]), "b": np.array([7])}
    evaluate_execution_results(expected_result, result)


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
def test_function_no_args_void_return_obj_update():
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
def test_array_iterating_length():
    pass


@pytest.mark.skip(reason="Developing still")
def test_array_updated_in_lower_scopes():
    pass


@pytest.mark.skip(reason="Developing still")
def test_multi_file():
    pass


@pytest.mark.skip(reason="Developing still")
def test_source_refs():
    pass


##### Model tests ######


@pytest.mark.skip(reason="Developing still")
def test_pid_controller():
    pass


# TODO move to fortran tests
# @pytest.mark.skip(reason="Developing still")
# def test_stemp_soilt_for():
#     pass

# @pytest.mark.skip(reason="Developing still")
# def test_stemp_epic_soilt_for():
#     pass


@pytest.mark.skip(reason="Developing still")
def test_GE_simple_PI_controller():
    pass


@pytest.mark.skip(reason="Developing still")
def test_simple_controller_bhpm():
    pass
