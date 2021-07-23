import pytest
import os

from igraph import Graph
from automates.model_assembly.networks import (
    GroundedFunctionNetwork,
    CausalAnalysisGraph,
)


def test_igraph_conversion():
    gml_filepath = "tests/data/model_assembly"
    gml_filename = "PETPT__@global__petpt--igraph.gml"
    gml_file_location = os.path.join(gml_filepath, gml_filename)
    G = GroundedFunctionNetwork.from_json(
        "tests/data/model_assembly/GrFN/PETPT--GrFN.json"
    )
    C = CausalAnalysisGraph.from_GrFN(G)
    C.to_igraph_gml(gml_filepath)

    g = Graph.Load(gml_file_location, format="gml")
    expected_node_names = [
        "PETPT::petpt::msalb::-1",
        "PETPT::petpt::srad::-1",
        "PETPT::petpt::tmax::-1",
        "PETPT::petpt::tmin::-1",
        "PETPT::petpt::xhlai::-1",
        "PETPT::petpt::td::0",
        "PETPT::petpt.IF_0::COND_0_0::0",
        "PETPT::petpt.IF_0::albedo::0",
        "PETPT::petpt.IF_0::albedo::1",
        "PETPT::petpt.IF_0::albedo::2",
        "PETPT::petpt::slang::0",
        "PETPT::petpt::eeq::0",
        "PETPT::petpt::eo::0",
        "PETPT::petpt.IF_1::COND_1_0::0",
        "PETPT::petpt.IF_1::eo::0",
        "PETPT::petpt.IF_1::COND_1_1::0",
        "PETPT::petpt.IF_1::eo::1",
        "PETPT::petpt.IF_1::eo::2",
    ]
    expected_node_degrees = [
        2,
        1,
        5,
        1,
        2,
        3,
        2,
        2,
        3,
        4,
        2,
        6,
        2,
        2,
        3,
        2,
        3,
        5,
    ]

    expected_edge_betweenness = [
        4.0,
        4.0,
        6.0,
        3.0,
        1.25,
        1.25,
        1.25,
        1.25,
        6.0,
        4.0,
        4.0,
        12.0,
        9.0,
        9.0,
        12.0,
        30.0,
        10.0,
        15.66666666666667,
        14.666666666666668,
        14.666666666666668,
        4.666666666666667,
        1.25,
        4.916666666666668,
        1.25,
        4.916666666666668,
    ]

    node_names_without_uids = [v.rsplit("::", 1)[0] for v in g.vs["label"]]
    assert node_names_without_uids == expected_node_names
    assert g.vs.degree() == expected_node_degrees
    assert g.es.edge_betweenness() == expected_edge_betweenness
    os.remove(gml_file_location)
