import sys
import os
import subprocess
import json
import argparse

from automates.program_analysis.GCC2GrFN.gcc_ast_to_cast import GCC2CAST
from automates.program_analysis.CAST2GrFN.cast import CAST


def main():

    cast_name = "SIR-simple--CAST.json"
    if len(sys.argv) > 1:
        cast_name = sys.argv[1]

    cast = CAST.from_json_file(cast_name)
    program_name = cast_name.split("--CAST.json")[0]

    grfn = cast.to_GrFN()
    grfn.to_json_file(f"{program_name}--GrFN.json")
    A = grfn.to_AGraph()
    A.draw(program_name + "--GrFN.pdf", prog="dot")


if __name__ == "__main__":
    main()