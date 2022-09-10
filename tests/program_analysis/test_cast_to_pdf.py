import pytest
import json
import os

from automates.program_analysis.CAST2GrFN.visitors.cast_to_agraph_visitor import (
    CASTToAGraphVisitor,
)
from automates.program_analysis.CAST2GrFN import cast

DATA_DIR = "tests/data/program_analysis/CAST2PDF"

def test_cast_all_nodes():
    file_name = "cast_all_nodes.json"

    filepath = os.path.join(DATA_DIR, file_name)

    C = cast.CAST.from_json_file(filepath)

    V = CASTToAGraphVisitor(C)
    pdf_filepath = filepath.replace(".json", ".pdf")
    V.to_pdf(pdf_filepath)
    assert os.path.isfile(pdf_filepath)
    os.remove(pdf_filepath)
