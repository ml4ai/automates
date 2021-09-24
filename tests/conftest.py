import pytest
import ast
import os


from automates.program_analysis.PyAST2CAST import py_ast_to_cast
from automates.program_analysis.CAST2GrFN import cast
from automates.program_analysis.CAST2GrFN.cast import CAST
from automates.program_analysis.CAST2GrFN.model.cast import SourceRef
from automates.model_assembly.air import AutoMATES_IR
from automates.model_assembly.networks import (
    CausalAnalysisGraph,
    GroundedFunctionNetwork,
)
from automates.utils.misc import rd

DATA_DIR = os.path.normpath(
    "tests/data/program_analysis/language_tests/python/"
)

# =============================================================================
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def py2CAST(python_filepath: str):
    # TODO: move this into the CAST creation portion somewhere
    # Open Python file as a giant string
    file_contents = list()
    with open(python_filepath, "r") as infile:
        file_contents = infile.read()

    file_name = python_filepath.split("/")[-1]

    # Count the number of lines in the file
    line_count = 0
    with open(python_filepath, "r") as infile:
        line_count = infile.readlines()

    # Create a PyASTToCAST Object
    convert = py_ast_to_cast.PyASTToCAST(file_name)

    # 'Root' the current working directory so that it's where the
    # Source file we're generating CAST for is (for Import statements)
    old_path = os.getcwd()
    os.chdir(python_filepath[: python_filepath.rfind("/")])

    # Parse the python program's AST and create the CAST
    contents = ast.parse(file_contents)
    C = convert.visit(contents)
    C.source_refs = [SourceRef(file_name, None, None, 1, line_count)]
    out_cast = cast.CAST([C], "python")
    os.chdir(old_path)
    return out_cast


def CAST2AIR(cast: CAST):
    return AutoMATES_IR.from_CAST(cast.to_air_dict())


def AIR2GrFN(air: AutoMATES_IR):
    G = GroundedFunctionNetwork.from_AIR(air)
    rd.seed(0)
    return G


def GrFN2CAG(grfn: GroundedFunctionNetwork):
    return CausalAnalysisGraph.from_GrFN(grfn)


# =============================================================================
# LITERAL LANGUAGE TEST FIXTURES
# -----------------------------------------------------------------------------
@pytest.fixture
def literal_direct_assg_path():
    return os.path.join(DATA_DIR, "literals", "literal_direct_assg")


@pytest.fixture
def literal_direct_assg_cast(literal_direct_assg_path):
    return py2CAST(
        os.path.join(literal_direct_assg_path, "literal_direct_assg.py")
    )


@pytest.fixture
def literal_direct_assg_air(literal_direct_assg_cast):
    return CAST2AIR(literal_direct_assg_cast)


@pytest.fixture
def literal_direct_assg_grfn(literal_direct_assg_air):
    return AIR2GrFN(literal_direct_assg_air)


@pytest.fixture
def literal_direct_assg_cag(literal_direct_assg_grfn):
    return GrFN2CAG(literal_direct_assg_grfn)


@pytest.fixture
def literal_in_stmt_path():
    return os.path.join(DATA_DIR, "literals", "literal_in_stmt")


@pytest.fixture
def literal_in_stmt_cast(literal_in_stmt_path):
    return py2CAST(os.path.join(literal_in_stmt_path, "literal_in_stmt.py"))


@pytest.fixture
def literal_in_stmt_air(literal_in_stmt_cast):
    return CAST2AIR(literal_in_stmt_cast)


@pytest.fixture
def literal_in_stmt_grfn(literal_in_stmt_air):
    return AIR2GrFN(literal_in_stmt_air)


@pytest.fixture
def literal_in_stmt_cag(literal_in_stmt_grfn):
    return GrFN2CAG(literal_in_stmt_grfn)


# =============================================================================
# FULL MODEL LANGUAGE TEST FIXTURES
# -----------------------------------------------------------------------------
@pytest.fixture
def Simple_SIR_path():
    return os.path.join(DATA_DIR, "full_models", "Simple_SIR")


@pytest.fixture
def Simple_SIR_cast(Simple_SIR_path):
    return py2CAST(os.path.join(Simple_SIR_path, "Simple_SIR.py"))


@pytest.fixture
def Simple_SIR_air(Simple_SIR_cast):
    return CAST2AIR(Simple_SIR_cast)


@pytest.fixture
def Simple_SIR_grfn(Simple_SIR_air):
    return AIR2GrFN(Simple_SIR_air)


@pytest.fixture
def Simple_SIR_cag(Simple_SIR_grfn):
    return GrFN2CAG(Simple_SIR_grfn)
