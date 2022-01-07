import os
import json

from automates.program_analysis.GCC2GrFN.gcc_basic_blocks_to_digraph import basic_blocks_to_digraph, find_lca_of_parents

GCC_TEST_DATA_DIRECTORY = "tests/data/program_analysis/GCC2GrFN"

def test_lca_of_parents_if_else_if_06():
    test_name = "if_else_if_06"
    test_dir = f"{GCC_TEST_DATA_DIRECTORY}/{'lca_of_parents'}"

    assert os.path.exists(f"{test_dir}/{test_name}_gcc_ast.json")

    gcc_ast_obj = json.load(open(f"{test_dir}/{test_name}_gcc_ast.json"))
    functions = gcc_ast_obj["functions"]
    func_to_check = next((f for f in functions if f["name"] == "func"))
    digraph = basic_blocks_to_digraph(func_to_check["basicBlocks"])

    # map the node index we want to check to the index of its lca of parents
    node_indices_to_lcas = {8: 2, 10: 8}

    for n in digraph.nodes():
        if n.index in node_indices_to_lcas:
            lca = find_lca_of_parents(digraph, n)
            assert(lca.index == node_indices_to_lcas[n.index])

def test_lca_of_parents_if_else_if_07():
    test_name = "if_else_if_07"
    test_dir = f"{GCC_TEST_DATA_DIRECTORY}/{'lca_of_parents'}"

    assert os.path.exists(f"{test_dir}/{test_name}_gcc_ast.json")

    gcc_ast_obj = json.load(open(f"{test_dir}/{test_name}_gcc_ast.json"))
    functions = gcc_ast_obj["functions"]
    func_to_check = next((f for f in functions if f["name"] == "func"))
    digraph = basic_blocks_to_digraph(func_to_check["basicBlocks"])

    # map the node index we want to check to the index of its lca of parents
    node_indices_to_lcas = {8: 6, 9: 2, 11: 9}

    for n in digraph.nodes():
        if n.index in node_indices_to_lcas:
            lca = find_lca_of_parents(digraph, n)
            assert(lca.index == node_indices_to_lcas[n.index])

def test_lca_of_parents_if_else_if_08():
    test_name = "if_else_if_08"
    test_dir = f"{GCC_TEST_DATA_DIRECTORY}/{'lca_of_parents'}"

    assert os.path.exists(f"{test_dir}/{test_name}_gcc_ast.json")

    gcc_ast_obj = json.load(open(f"{test_dir}/{test_name}_gcc_ast.json"))
    functions = gcc_ast_obj["functions"]
    func_to_check = next((f for f in functions if f["name"] == "func"))
    digraph = basic_blocks_to_digraph(func_to_check["basicBlocks"])

    # map the node index we want to check to the index of its lca of parents
    node_indices_to_lcas = {11: 9, 12: 6, 13: 2, 15: 13}

    for n in digraph.nodes():
        if n.index in node_indices_to_lcas:
            lca = find_lca_of_parents(digraph, n)
            assert(lca.index == node_indices_to_lcas[n.index])

def test_lca_of_parents_nested_if_01():
    test_name = "nested_if_01"
    test_dir = f"{GCC_TEST_DATA_DIRECTORY}/{'lca_of_parents'}"

    assert os.path.exists(f"{test_dir}/{test_name}_gcc_ast.json")

    gcc_ast_obj = json.load(open(f"{test_dir}/{test_name}_gcc_ast.json"))
    functions = gcc_ast_obj["functions"]
    func_to_check = next((f for f in functions if f["name"] == "main"))
    digraph = basic_blocks_to_digraph(func_to_check["basicBlocks"])

    # map the node index we want to check to the index of its lca of parents
    node_indices_to_lcas = {5: 2}

    for n in digraph.nodes():
        if n.index in node_indices_to_lcas:
            lca = find_lca_of_parents(digraph, n)
            assert(lca.index == node_indices_to_lcas[n.index])
