import pytest
import os

import numpy as np
import networkx as nx

from model_assembly.interpreter import ImperativeInterpreter
from model_assembly.networks import GroundedFunctionNetwork
from model_assembly.structures import GenericIdentifier, LambdaStmt


@pytest.mark.skip("Need to handle constants in function call")
def test_mini_pet():
    ITP = ImperativeInterpreter.from_src_dir("tests/data/model_analysis")
    assert hasattr(ITP, "containers")
    assert hasattr(ITP, "variables")
    assert hasattr(ITP, "types")
    assert hasattr(ITP, "documentation")
    ITP.gather_container_stats()
    ITP.label_container_code_types()
    grfns = ITP.build_GrFNs()
    grfn_list = list(grfns.keys())
    # TODO Adarsh: fill this list out
    expected_grfns = sorted(["PETPT", "PETASCE", "PSE", "FLOOD_EVAP"])
    assert sorted(grfn_list) == expected_grfns


def test_pet_files():
    def interpreter_test(filepath, con_name, outfile):
        ITP = ImperativeInterpreter.from_src_file(filepath)
        con_id = GenericIdentifier.from_str(con_name)

        G = GroundedFunctionNetwork.from_AIR(
            con_id, ITP.containers, ITP.variables, ITP.types,
        )

        A = G.to_AGraph()
        A.draw(outfile, prog="dot")
        return G

    GrFN = interpreter_test(
        "tests/data/program_analysis/PETASCE_simple.for",
        "@container::PETASCE_simple::@global::petasce",
        "PETASCE--GrFN.pdf",
    )

    assert isinstance(GrFN, GroundedFunctionNetwork)
    assert len(GrFN.inputs) == 13
    assert len(GrFN.outputs) == 1

    outputs = GrFN(
        {
            name: np.array([1.0], dtype=np.float32)
            for name in GrFN.input_name_map.keys()
        }
    )
    res = outputs[0]
    assert res[0] == np.float32(0.05697568)


def test_single_file_analysis():
    ITP = ImperativeInterpreter.from_src_file(
        "tests/data/program_analysis/PETPNO.for"
    )
    petpno_con_id = GenericIdentifier.from_str(
        "@container::PETPNO::@global::petpno"
    )

    PNO_GrFN = GroundedFunctionNetwork.from_AIR(
        petpno_con_id, ITP.containers, ITP.variables, ITP.types
    )

    A = PNO_GrFN.to_AGraph()
    # A = nx.nx_agraph.to_agraph(PNO_GrFN)
    A.draw("PETPNO--GrFN.pdf", prog="dot")
    # CAG = PNO_GrFN.CAG_to_AGraph()
    # CAG.draw("PETPT--CAG.pdf", prog="dot")
    # assert isinstance(PNO_GrFN, GroundedFunctionNetwork)
    # assert len(PNO_GrFN.inputs) == 5
    # assert len(PNO_GrFN.outputs) == 1
    #
    # outputs = PNO_GrFN.run(
    #     {
    #         name: np.array([1.0], dtype=np.float32)
    #         for name in PNO_GrFN.input_name_map.keys()
    #     }
    # )
    # res = outputs[0]
    # assert res[0] == np.float32(0.02998372)
    # os.remove("PETPT--GrFN.pdf")
    # os.remove("PETPT--CAG.pdf")


def test_file_with_loops():
    ITP = ImperativeInterpreter.from_src_file(
        "tests/data/program_analysis/SIR-Gillespie-SD.f"
    )
    con_id = GenericIdentifier.from_str(
        "@container::SIR-Gillespie-SD::@global::main"
    )
    G = GroundedFunctionNetwork.from_AIR(
        con_id, ITP.containers, ITP.variables, ITP.types
    )
    A = G.to_AGraph()
    A.draw("Gillespie-SD--GrFN.pdf", prog="dot")
    assert isinstance(G, GroundedFunctionNetwork)
