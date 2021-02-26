import pytest
import subprocess
import os
import random

import automates.model_assembly.networks as networks
from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.program_analysis.GCC2GrFN.gcc_ast_to_cast import GCC2CAST

GCC_10_BIN_DIRECTORY = "/usr/local/gcc-10.1.0/bin/"
GCC_PLUGIN_IMAGE = "automates/program_analysis/gcc_plugin/plugin/ast_dump.so"
GCC_TEST_DATA_DIRECTORY = "tests/data/program_analysis/GCC2GrFN/"


def cleanup():
    os.remove("ast.json")


@pytest.fixture(autouse=True)
def run_around_tests():
    assert os.path.exists(
        "automates/program_analysis/gcc_plugin/plugin/ast_dump.so"
    ), f"Error: GCC AST dump plugin does not exist at expected location: {GCC_PLUGIN_IMAGE}"
    # Before each test, set the seed for generating uuids to 0 for consistency
    # between tests and expected output
    networks.rd = random.Random()
    networks.rd.seed(0)

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
            "-o",
            "/dev/null",
        ]
    )

    # Assert return code is 0 which is success
    assert results.returncode == 0


def test_c_simple_function_and_assignments():
    run_gcc_plugin_with_c_file(
        f"{GCC_TEST_DATA_DIRECTORY}/simple_function_and_assignments/simple_function_and_assignments.c"
    )

    assert os.path.exists("./ast.json")