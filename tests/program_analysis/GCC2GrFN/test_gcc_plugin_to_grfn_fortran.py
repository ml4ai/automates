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


@pytest.fixture(scope="module", autouse=True)
def run_before_tests(request):
    # prepare something ahead of all tests
    results = subprocess.run([])


@pytest.fixture(autouse=True)
def run_around_tests():
    assert os.path.exists(
        GCC_PLUGIN_IMAGE
    ), f"Error: GCC AST dump plugin does not exist at expected location: {GCC_PLUGIN_IMAGE}"
    # Before each test, set the seed for generating uuids to 0 for consistency
    # between tests and expected output
    networks.rd = random.Random()
    networks.rd.seed(0)

    # Run the test function
    yield

    cleanup()


@pytest.mark.skip(reason="Need to implement")
def run_gcc_plugin_with_for_file(c_file):
    gpp_command = GCC_10_BIN_DIRECTORY + "gfortran++-10.1"
    plugin_option = f"-fplugin={GCC_PLUGIN_IMAGE}"
    # Runs gfortrsn with the given fortran file. This should create the file
    # ast.json with the programs ast inside of it.
    results = subprocess.run(
        [
            gpp_command,
            plugin_option,
            "-c",
            c_file,
            "-o",
            "/dev/null",
        ]
    )

    # Assert return code is 0 which is success
    assert results.returncode == 0


# TODO all pre-existing for2py tests


@pytest.mark.skip(reason="Need to implement")
def test_simple_soilt_routine():
    pass
