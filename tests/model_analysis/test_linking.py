import pytest
import json

import networkx as nx

from  automates.model_assembly.linking import (
    build_link_graph,
    extract_link_tables,
    print_table_data,
)


@pytest.fixture
def pno_alignment():
    return json.load(open("tests/data/model_analysis/PEN-alignment.json", "r"))


def test_link_graph_and_tables(pno_alignment):
    L = build_link_graph(pno_alignment["grounding"])
    assert isinstance(L, nx.DiGraph)

    tables = extract_link_tables(L)
    assert isinstance(tables, dict)

    print_table_data(tables)
