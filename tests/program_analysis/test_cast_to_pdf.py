import pytest
import ast
import os 

from automates.program_analysis.CAST2GrFN.visitors.cast_to_agraph_visitor import CASTToAGraphVisitor
from automates.program_analysis.CAST2GrFN import cast

DATA_DIR = "tests/data/program_analysis/CAST2PDF"

def test_cast_all_nodes():
    file_name = "cast_all_nodes.json"

    filepath = f"{DATA_DIR}/{file_name}"
    file_contents = open(filepath).read()

    C = cast.CAST([])
    C2 = C.from_json_str(file_contents)

    V = CASTToAGraphVisitor(C2)
    json_name = file_name.split(".")[0].split("/")[-1]
    V.to_pdf(json_name)

    # The generatd PDF gets put in the root automates directory, so
    # the remove call is 'hardcoded' to reflect that
    os.remove(f"{json_name}.pdf") 

    assert True
