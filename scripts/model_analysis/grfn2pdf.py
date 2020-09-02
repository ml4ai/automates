import sys

from automates.model_assembly.interpreter import ImperativeInterpreter
from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_assembly.structures import GenericIdentifier

fortran_path = sys.argv[1]
ITP = ImperativeInterpreter.from_src_file(fortran_path)
print(ITP.containers)
con_id = GenericIdentifier.from_str(
    "@container::ASKE-E-SEIR-9-alt::@global::aske_e_seir_9"
)
GrFN = GroundedFunctionNetwork.from_AIR(
    con_id, ITP.containers, ITP.variables, ITP.types,
)
A = GrFN.to_AGraph()
grfn_name = fortran_path[fortran_path.rfind("/") + 1 :]
grfn_pdf_name = grfn_name.replace(".for", "--GrFN.pdf")
A.draw(grfn_pdf_name, prog="dot")

grfn_json_path = grfn_name.replace(".for", "--GrFN.json")
GrFN.to_json_file(grfn_json_path)
