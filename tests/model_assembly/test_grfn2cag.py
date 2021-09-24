import pytest
import os

from automates.model_assembly.networks import CausalAnalysisGraph


def cag_json_comparison(dir_path: str, cag: CausalAnalysisGraph):
    cag_filename = "temp_model--CAG.json"
    cag.to_json_file(cag_filename)
    assert cag == CausalAnalysisGraph.from_json(cag_filename)
    os.remove(cag_filename)

    test_name = dir_path[dir_path.rfind("/") + 1 :]
    prev_grfn_json_file = os.path.join(dir_path, f"{test_name}--CAG.json")
    assert cag == CausalAnalysisGraph.from_json(prev_grfn_json_file)


@pytest.mark.literal_tests
def test_literal_direct_assg(
    literal_direct_assg_path, literal_direct_assg_cag
):
    assert isinstance(literal_direct_assg_cag, CausalAnalysisGraph)
    cag_json_comparison(literal_direct_assg_path, literal_direct_assg_cag)


@pytest.mark.literal_tests
def test_literal_in_stmt(literal_in_stmt_path, literal_in_stmt_cag):
    assert isinstance(literal_in_stmt_cag, CausalAnalysisGraph)
    cag_json_comparison(literal_in_stmt_path, literal_in_stmt_cag)


@pytest.mark.model_tests
def test_Simple_SIR(Simple_SIR_path, Simple_SIR_cag):
    assert isinstance(Simple_SIR_cag, CausalAnalysisGraph)
    cag_json_comparison(Simple_SIR_path, Simple_SIR_cag)
