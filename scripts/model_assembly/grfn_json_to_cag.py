import json
import sys
import re

from automates.model_assembly.networks import (
    GroundedFunctionNetwork,
    CausalAnalysisGraph,
)

grfn_json_filepath = sys.argv[1]
file_end_patt = r"\.[A-Za-z0-9]+\Z"

GrFN = GroundedFunctionNetwork.from_json(grfn_json_filepath)
CAG = CausalAnalysisGraph.from_GrFN(GrFN)
A_CAG = CAG.to_AGraph()
cag_name = grfn_json_filepath.replace("--GrFN.json", "--CAG.pdf")
A_CAG.draw(cag_name, prog="dot")

cag_json_name = grfn_json_filepath.replace("--GrFN.json", "--CAG.json")
CAG.to_json_file(cag_json_name)