import sys
import json
import re

from automates.model_assembly.interpreter import ImperativeInterpreter
from automates.model_assembly.networks import (
    GroundedFunctionNetwork,
    CausalAnalysisGraph,
)

fortran_path = sys.argv[1]
ITP = ImperativeInterpreter.from_src_file(fortran_path)
con_id = ITP.find_root_container()
GrFN = GroundedFunctionNetwork.from_AIR(
    con_id, ITP.containers, ITP.variables, ITP.types, {}
)
A = GrFN.to_AGraph()

file_end_patt = r"\.[A-Za-z0-9]+\Z"
grfn_name = fortran_path[fortran_path.rfind("/") + 1 :]

doc_name = re.sub(file_end_patt, "--documentation.json", grfn_name)
json.dump(ITP.documentation, open(doc_name, "w"))

grfn_pdf_name = re.sub(file_end_patt, "--GrFN.pdf", grfn_name)
A.draw(grfn_pdf_name, prog="dot")
grfn_json_path = re.sub(file_end_patt, "--GrFN.json", grfn_name)
GrFN.to_json_file(grfn_json_path)


CAG = CausalAnalysisGraph.from_GrFN(GrFN)
A_CAG = CAG.to_AGraph()
cag_name = re.sub(file_end_patt, "--CAG.pdf", grfn_name)
A_CAG.draw(cag_name, prog="dot")

cag_json_name = re.sub(file_end_patt, "--CAG.json", grfn_name)
CAG.to_json_file(cag_json_name)
