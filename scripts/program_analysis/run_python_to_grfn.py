"""
    Takes a Python program name as the first argument, 
    creates its corresponding CAST from source
    and then creates GrFN from this CAST. 
      Given <program_name> it creates 
        <program_name>--CAST.json -- CAST json
        <program_name>--GrFN.json -- GrFN json
        <program_name>--GrFN.pdf -- graphviz pdf
"""

import sys
import os
import subprocess
import ast
import json
import argparse
import dill

from automates.program_analysis.PyAST2CAST import py_ast_to_cast
from automates.program_analysis.CAST2GrFN import cast 
from automates.program_analysis.CAST2GrFN.model.cast import SourceRef
from automates.program_analysis.CAST2GrFN.visitors.cast_to_agraph_visitor import (
    CASTToAGraphVisitor,
)
from automates.utils import misc

from automates.program_analysis.CAST2GrFN.ann_cast.cast_to_annotated_cast import (
    CastToAnnotatedCastVisitor
)
from automates.program_analysis.CAST2GrFN.ann_cast.ann_cast_utility import run_all_ann_cast_passes

GCC_10_BIN_DIRECTORY = "/usr/local/gcc-10.1.0/bin/"
GCC_PLUGIN_IMAGE_DIR = "automates/program_analysis/gcc_plugin/plugin/"


def get_args():
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-i", "--inputs", help="Your input file(s).", nargs="*")
    parser.add_argument(
        "-l",
        "--language",
        help="The langugage of the input file. Valid inputs: Python (.py)",
    )
    parser.add_argument("-Cg", "--CASTgraph", help="Create CAST graphviz pdf",
            action='store_true')
    parser.add_argument("-L", "--legacy", 
            help="Generate legacy CAST for the legacy CAST -> AIR -> GrFN pipeline",
            action="store_true")
    parser.add_argument("--grfn_2_2", 
            help="Generate GrFN 2.2 for the CAST -> Annotated Cast -> GrFN pipeline",
            action="store_true")
    options = parser.parse_args()
    return options


def run_python_pipeline():
    assert len(sys.argv) > 1, "Error: No python file name passed in arguments"

    args = get_args()

    if args.inputs is None:
        raise Exception("Error: No input file specified via -i option")
    input_files = args.inputs

    # For now, assume the last input file is the overall program name.
    program_name = input_files[-1].rsplit(".")[0].rsplit("/")[-1]
    # Load json of each files ast

    print("Turning Python Source into CAST...")
    make_legacy_cast = False
    if args.legacy:
        make_legacy_cast = True
    convert = py_ast_to_cast.PyASTToCAST(program_name, legacy=make_legacy_cast)
    
    # Change the curent directory to where the file is located
    pyfile_path = input_files[-1]
    idx = pyfile_path.rfind("/")
    old_path = os.getcwd()
    if idx > -1:
        curr_path = pyfile_path[0:idx]
        os.chdir(curr_path)
    else:
        curr_path = "./"+pyfile_path

    contents = ast.parse(open(pyfile_path).read())
    C = convert.visit(contents, {}, {})
    C.source_refs = [SourceRef(program_name, None, None, 1, 1)]

    os.chdir(old_path)
    out_cast = cast.CAST([C], "python")

    json.dump(out_cast.to_json_object(), open(f"{program_name}--CAST.json", "w+"))


    # NOTE: CASTToAGraphVisitor uses misc.uuid, so resetting the random seed must
    # be called after this to ensure consistent uuids for testing
    if args.CASTgraph:
        V = CASTToAGraphVisitor(out_cast)
        V.to_pdf(program_name + "--CAST.pdf")

    # Before generating GrFN, set the seed to generate uuids consistently
    misc.rd.seed(0)
    
    # if we are making legacy CAST, run the legacy pipeline
    if make_legacy_cast:
        print("Transforming CAST into GrFN...")
        grfn = out_cast.to_GrFN()
        grfn.to_json_file(f"{program_name}--GrFN.json")

        print("Transforming GrFN into AGraph...")
        A = grfn.to_AGraph()
        A.draw(program_name + "--GrFN.pdf", prog="dot")
        # GE Simple PI controller dynamics inputs
        inputs = {
            "GE_simple_PI_controller_dynamics::GE_simple_PI_controller_dynamics.main::integrator_state::-1": 0
            # "GE_simple_PI_controller::GE_simple_PI_controller.main::integrator_state::-1": 0
        }

        print("Executing GrFN...")
        inputs = {}
        result = grfn(inputs)
        from pprint import pprint

        print("GrFn execution results:")
        pprint(result)

    # otherwise use the AnnCast -> GrFN pipeline
    else:
        visitor = CastToAnnotatedCastVisitor(out_cast)
        pipeline_state = visitor.generate_annotated_cast(args.grfn_2_2)
        print("Transforming CAST to AnnCAST and running passes...")
        run_all_ann_cast_passes(pipeline_state, verbose=True)

        print("Saving GrFN pdf and json...")
        grfn = pipeline_state.get_grfn()
        grfn.to_json_file(f"{program_name}--GrFN.json")

        grfn_agraph = grfn.to_AGraph()
        grfn_agraph.draw(f"{program_name}--GrFN.pdf", prog="dot")

        # NOTE: CASTToAGraphVisitor uses misc.uuid, so it should be called after
        # ToGrfnPass so that GrFN uuids are consistent for testing
        print("Saving AnnCAST pdf...")
        agraph = CASTToAGraphVisitor(pipeline_state)
        pdf_file_name = f"{program_name}-AnnCast.pdf"
        agraph.to_pdf(pdf_file_name)

        print("\nGenerating pickled AnnCast -----------------")
        pickled_file_name = f"{program_name}--AnnCast.pickled"
        with open(pickled_file_name,"wb") as pkfile:
            dill.dump(pipeline_state, pkfile)


if __name__ == "__main__":
    run_python_pipeline()
