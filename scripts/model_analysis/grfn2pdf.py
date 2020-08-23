import sys

from model_analysis.networks import GroundedFunctionNetwork


fortran_path = sys.argv[1]
GrFN = GroundedFunctionNetwork.from_fortran_file(fortran_path)
A = GrFN.to_AGraph()
grfn_name = fortran_path[fortran_path.rfind("/") + 1 :]
grfn_pdf_name = grfn_name.replace(".for", "--GrFN.pdf")
A.draw(grfn_pdf_name, prog="dot")
