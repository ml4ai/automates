import sys
import argparse

from automates.program_analysis.CAST2GrFN.visitors.cast_to_token_cast_visitor import (
    CASTToTokenCASTVisitor,
)
from automates.program_analysis.CAST2GrFN.cast import CAST


def main():
    """cast_to_token_cast.py

    This program reads a JSON file that contains the CAST representation
    of a program, and generates a string that represents the tokenized CAST
    in addition, a mapping of the variables to variable identifiers and a mapping
    of values to value identifiers are generated.

    One command-line argument is expected, namely the name of the JSON file that
    contains the CAST data.
    """

    # Open the CAST json and load it as a Python object
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-f", "--file", type=str, help="CAST JSON input file"
    )

    parser.add_argument(
        "-d", "--directory", type=str, help="A directory to store files to", default="."
    )

    args = parser.parse_args()

    if args.file == None:
        print("USAGE: python cast_to_token_cast.py -f <file_name> [-d <directory_name>]")
        sys.exit()

    f_name = args.file

    file_contents = open(f_name).read()
    C = CAST([], "c")
    C2 = C.from_json_str(file_contents)

    V = CASTToTokenCASTVisitor(C2)

    last_slash_idx = f_name.rfind("/")
    file_ending_idx = f_name.rfind(".")

    dir_name = args.directory
    if dir_name.endswith('/'):
        dir_name = dir_name[0:-1]

    token_file_name = f"{dir_name}/{f_name[last_slash_idx + 1 : file_ending_idx]}.tcast"
    V.tokenize(token_file_name)
    
if __name__ == "__main__":
    main()
