import ast
import sys

from cast import CAST2GrFN


def main():
    code = ""
    with open(sys.argv[1], "r") as infile:
        code = "".join(infile.readlines())

    tree = ast.parse(code)


if __name__ == "__main__":
    main()
