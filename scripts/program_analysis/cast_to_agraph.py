import sys

from automates.program_analysis.CAST2GrFN.visitors.cast_to_agraph_visitor import (
    CASTToAGraphVisitor,
)
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
    C = CAST([], "python")
    C2 = C.from_json_str(file_contents)

    V = CASTToAGraphVisitor(C2)
    last_slash_idx = f_name.rfind("/")
    file_ending_idx = f_name.rfind(".")
    pdf_file_name = f"{f_name[last_slash_idx + 1 : file_ending_idx]}.pdf"
    V.to_pdf(pdf_file_name)


if __name__ == "__main__":
    main()
