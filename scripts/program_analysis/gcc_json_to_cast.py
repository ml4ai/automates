import sys
import json

from automates.program_analysis.GCC2GrFN.gcc_ast_to_cast import GCC2CAST
from automates.program_analysis.CAST2GrFN.visitors.cast_to_agraph_visitor import CASTToAGraphVisitor


def main():
    json_file = sys.argv[1]
    print(f"Loaded json_file: {json_file}")
    ast_json = json.load(open(json_file))
    input_file = ast_json["mainInputFilename"]
    input_file_stripped = input_file.split("/")[-1]

    cast = GCC2CAST([ast_json]).to_cast()
    visitor = CASTToAGraphVisitor(cast)
    visitor.to_pdf(input_file_stripped + "_gcc--CAST.pdf")

if __name__ == "__main__":
    main()
