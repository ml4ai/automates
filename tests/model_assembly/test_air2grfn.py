import pytest
import os

import pygraphviz as pgv

from automates.model_assembly.networks import GroundedFunctionNetwork


def grfn_json_comparison(dir_path: str, grfn: GroundedFunctionNetwork):
    grfn_filename = "temp_model--GrFN3.json"
    grfn.to_json_file(grfn_filename)
    assert grfn == GroundedFunctionNetwork.from_json(grfn_filename)
    os.remove(grfn_filename)

    test_name = dir_path[dir_path.rfind("/") + 1 :]
    prev_grfn_json_file = os.path.join(dir_path, f"{test_name}--GrFN3.json")
    assert grfn == GroundedFunctionNetwork.from_json(prev_grfn_json_file)


def grfn_agraph_comparison(dir_path: str, grfn: GroundedFunctionNetwork):
    test_name = dir_path[dir_path.rfind("/") + 1 :]
    prev_dot_file = os.path.join(dir_path, f"{test_name}--GrFN3.dot")
    grfn_A = grfn.to_AGraph()
    prev_A = pgv.AGraph(prev_dot_file)
    assert set(grfn_A.nodes()) == set(prev_A.nodes())
    assert set(grfn_A.edges()) == set(prev_A.edges())

    prev_full_dot_file = os.path.join(
        dir_path, f"{test_name}--GrFN3_expanded.dot"
    )
    grfn_full_A = grfn.to_AGraph(expand_expressions=True)
    prev_full_A = pgv.AGraph(prev_full_dot_file)
    assert set(grfn_full_A.nodes()) == set(prev_full_A.nodes())
    assert set(grfn_full_A.edges()) == set(prev_full_A.edges())


@pytest.mark.literal_tests
def test_literal_direct_assg(
    literal_direct_assg_path, literal_direct_assg_grfn
):
    assert isinstance(literal_direct_assg_grfn, GroundedFunctionNetwork)
    grfn_json_comparison(literal_direct_assg_path, literal_direct_assg_grfn)
    grfn_agraph_comparison(literal_direct_assg_path, literal_direct_assg_grfn)


@pytest.mark.literal_tests
def test_literal_in_stmt(literal_in_stmt_path, literal_in_stmt_grfn):
    assert isinstance(literal_in_stmt_grfn, GroundedFunctionNetwork)
    grfn_json_comparison(literal_in_stmt_path, literal_in_stmt_grfn)
    grfn_agraph_comparison(literal_in_stmt_path, literal_in_stmt_grfn)


@pytest.mark.model_tests
def test_Simple_SIR(Simple_SIR_path, Simple_SIR_grfn):
    assert isinstance(Simple_SIR_grfn, GroundedFunctionNetwork)
    grfn_json_comparison(Simple_SIR_path, Simple_SIR_grfn)
    grfn_agraph_comparison(Simple_SIR_path, Simple_SIR_grfn)
