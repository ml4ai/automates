import pytest
import json
import os

from automates.text_reading.sparql.query_svo import (
    QueryConductor,
    process_text_var_terms,
)


def test_QueryConductor():
    qc = QueryConductor()
    assert hasattr(qc, "SPARQL_CONN")


def test_process_text_var_terms():
    with pytest.raises(RuntimeError, match=r".* JSON files"):
        process_text_var_terms("some/path/foo.jsn", "other/path/bar.txt")
    with pytest.raises(RuntimeError, match=r".* JSON files"):
        process_text_var_terms("some/path/foo.json", "other/path/bar.txt")
    with pytest.raises(RuntimeError, match=r".* JSON files"):
        process_text_var_terms("some/path/foo.jsn", "other/path/bar.json")

    process_text_var_terms(
        "tests/data/TR/var_terms.json", "gen_query_result.json"
    )
    expected = json.load(open("tests/data/TR/query-results.json", "r"))
    observed = json.load(open("gen_query_result.json", "r"))
    os.remove("gen_query_result.json")
    assert expected == observed
