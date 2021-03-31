import sys

from automates.program_analysis.CAST2GrFN.visitors.cast_to_agraph_visitor import CASTToAGraphVisitor
from automates.program_analysis.CAST2GrFN.cast import CAST

def main():
    """cast_to_agraph.py

        This program reads a JSON file that contains the CAST representation
        of a program, and generates a PDF file out of it to visualize it.
    
        One command-line argument is expected, namely the name of the JSON file that 
        contains the CAST data.
    """
    f_name = sys.argv[1]
    file_contents = open(f_name).read()
    C = CAST([])
    C2 = C.from_json_str(file_contents)

    V = CASTToAGraphVisitor(C2)
    V.to_pdf(f_name.split(".")[0].split("/")[-1])

main()
