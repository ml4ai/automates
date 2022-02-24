import sys

from automates.program_analysis.CAST2GrFN.visitors.cast_to_annotated_cast import (
    CastToAnnotatedCastVisitor
)
from automates.program_analysis.CAST2GrFN.cast import CAST


def main():
    """cast_to_annotated.py

    This program reads a JSON file that contains the CAST representation
    of a program, and transforms it to annotated CAST.

    One command-line argument is expected, namely the name of the JSON file that
    contains the CAST data.
    """
    f_name = sys.argv[1]
    file_contents = open(f_name).read()
    C = CAST([], "python")
    C2 = C.from_json_str(file_contents)

    visitor = CastToAnnotatedCastVisitor(C2)
    annotated_cast = visitor.generate_annotated_cast()


if __name__ == "__main__":
    main()
