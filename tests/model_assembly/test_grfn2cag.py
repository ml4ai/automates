import pytest
import os

from automates.model_assembly.networks import CausalAnalysisGraph


def cag_json_comparison(dir_path: str, cag: CausalAnalysisGraph):
    cag_filename = "temp_model--GrFN3.json"
    cag.to_json_file(cag_filename)
    assert cag == CausalAnalysisGraph.from_json(cag_filename)
    os.remove(cag_filename)

    test_name = dir_path[dir_path.rfind("/") + 1 :]
    prev_grfn_json_file = os.path.join(dir_path, f"{test_name}--GrFN3.json")
    assert grfn == CausalAnalysisGraph.from_json(prev_grfn_json_file)
