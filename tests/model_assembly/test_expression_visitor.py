import pytest
import pickle
import json
import ast
from typing import NoReturn

import networkx as nx

from automates.model_assembly.expression_visitor import (
    ExpressionVisitor,
    nodes2DiGraph,
)


def create_expr_trees(test_cases) -> list:
    graphs = list()
    visitor = ExpressionVisitor()
    for case_name, case_lambda in test_cases.items():
        visitor.visit(ast.parse(case_lambda))
        nodes = visitor.get_nodes()

        graphs.append({"id": case_name, "nodes": [n.to_dict() for n in nodes]})
    return graphs


def compare_graph_lists(tests, expected_file) -> NoReturn:
    expected = json.load(open(expected_file, "r"))
    assert {g["id"]: g for g in tests} == {g["id"]: g for g in expected}


def test_single_value_returns():
    test_cases = {
        "int_constant_return": "lambda : 0",
        "str_constant_return": "lambda : 'foo'",
        "float_constant_return": "lambda : 3.14",
        "variable_return": "lambda x: x",
        "wrapped_variable_return": "lambda x: (x)",
        "list": "lambda : [1,2,3]",
        "tuple": "lambda : (1,2,3)",
        "dict": "lambda x, y: {'a': 1, 'b': 'b', '3': x}",
    }

    graphs = create_expr_trees(test_cases)
    compare_graph_lists(
        graphs,
        "tests/data/model_assembly/expression_visitor/single_values.json",
    )


def test_unary_ops():
    test_cases = {
        "negate_bool_x": "lambda x: not x",
        "invert_x": "lambda x: ~ x",
        "negate_x": "lambda x: - x",
    }

    graphs = create_expr_trees(test_cases)
    compare_graph_lists(
        graphs,
        "tests/data/model_assembly/expression_visitor/unary_ops.json",
    )


def test_binary_ops():
    test_cases = {
        "add_op": "lambda x, y: x + y",
        "multi_add_op": "lambda w, x, y, z: x + y + z + w",
        "sub_op": "lambda x, y: x - y",
        "multi_sub_op": "lambda x, y, z: x - y - z",
        "mult_op": "lambda x, y: x * y",
        "pow_op": "lambda x, y: x ** y",
        "multi_mult_op": "lambda x, y, z, w: x * y * z * w",
        "mat_mult_op": "lambda x, y: x @ y",
        "div_op": "lambda x, y: x / y",
        "floor_div_op": "lambda x, y: x // y",
        "mod_op": "lambda x, y: x % y",
        "multi_div_op": "lambda x, y, z: x / y / z // x // y % z % y",
        "lshift_op": "lambda x, y: x << y",
        "rshift_op": "lambda x, y: x >> y",
        "bitor_op": "lambda x, y: x | y",
        "bitand_op": "lambda x, y: x & y",
        "bitxor_op": "lambda x, y: x ^ y",
    }

    graphs = create_expr_trees(test_cases)
    compare_graph_lists(
        graphs,
        "tests/data/model_assembly/expression_visitor/binary_ops.json",
    )


def test_boolean_ops():
    test_cases = {
        "and_op": "lambda x, y: x and y",
        "multi_and_op": "lambda w, x, y, z: x and y and z and w",
        "or_op": "lambda x, y: x or y",
        "multi_or_op": "lambda x, y, z, w: x or y or z or w",
    }

    graphs = create_expr_trees(test_cases)
    compare_graph_lists(
        graphs,
        "tests/data/model_assembly/expression_visitor/boolean_ops.json",
    )


def test_comparative_ops():
    test_cases = {
        "eq_op": "lambda x, y: x == y",
        "multi_eq_op": "lambda w, x, y, z: x == y == z == w",
        "noteq_op": "lambda x, y: x != y",
        "multi_noteq_op": "lambda x, y, z, w: x != y != z != w",
        "lt_op": "lambda x, y: x < y",
        "lte_op": "lambda x, y: x <= y",
        "gt_op": "lambda x, y: x > y",
        "gte_op": "lambda x, y: x >= y",
        "is_op": "lambda x, y: x is y",
        "isnot_op": "lambda x, y: x is not y",
        "in_op": "lambda x, y: x in y",
        "notin_op": "lambda x, y: x not in y",
    }

    graphs = create_expr_trees(test_cases)
    compare_graph_lists(
        graphs,
        "tests/data/model_assembly/expression_visitor/comparative_ops.json",
    )


def test_complex_expr():
    test_cases = {
        "ifexp": "lambda c, x, y: x if c else y",
        "compound_ifexp": "lambda c1,c2,x,y,z: x if c1 else y if c2 else z",
        "multi_cond_ifexp": "lambda c1, c2, x, y: x if c1 or c2 else y",
        "indexed_expr": "lambda x: x[0]",
        "str_indexed_expr": "lambda x: x['test']",
        "var_indexed_expr": "lambda x, y: x[y]",
        "exprs_in_list": "lambda x, y, z: [x + y, x * 3 + 1, x[2]]",
        "exprs_in_tuple": "lambda x, y, z: (x + y, x * 3 + 1, x[2])",
        "call_expr": "lambda x, y, z: max(x, y) + min(x, y, z)",
    }

    graphs = create_expr_trees(test_cases)
    compare_graph_lists(
        graphs,
        "tests/data/model_assembly/expression_visitor/complex_ops.json",
    )


def test_nodes2DiGraph():
    lambda_str = "lambda x: 4 * x**3 + 2 * x + 1"
    visitor = ExpressionVisitor()
    visitor.visit(ast.parse(lambda_str))
    nodes = visitor.get_nodes()
    G = nodes2DiGraph(nodes)

    expected_G = pickle.load(
        open(
            "tests/data/model_assembly/expression_visitor/sample_network.pkl",
            "rb",
        )
    )

    assert isinstance(G, nx.DiGraph)
    assert len(G.nodes) == 12
    assert G.nodes == expected_G.nodes
