import sys
import dill
import argparse

from automates.program_analysis.CAST2GrFN.ann_cast.cast_to_annotated_cast import (
    CastToAnnotatedCastVisitor
)
from automates.program_analysis.CAST2GrFN.cast import CAST
from automates.program_analysis.CAST2GrFN.visitors.cast_to_agraph_visitor import CASTToAGraphVisitor
from automates.program_analysis.CAST2GrFN.ann_cast.id_collapse_pass import IdCollapsePass
from automates.program_analysis.CAST2GrFN.ann_cast.container_scope_pass import ContainerScopePass
from automates.program_analysis.CAST2GrFN.ann_cast.variable_version_pass import VariableVersionPass
from automates.program_analysis.CAST2GrFN.ann_cast.grfn_var_creation_pass import GrfnVarCreationPass
from automates.program_analysis.CAST2GrFN.ann_cast.grfn_assignment_pass import GrfnAssignmentPass
from automates.program_analysis.CAST2GrFN.ann_cast.lambda_expression_pass import LambdaExpressionPass
from automates.program_analysis.CAST2GrFN.ann_cast.to_grfn_pass import ToGrfnPass
from automates.program_analysis.CAST2GrFN.ann_cast.to_gromet_pass import ToGrometPass

from automates.utils.script_functions import ann_cast_pipeline
from automates.utils.fold import dictionary_to_gromet_json, del_nulls

def get_args():
    parser = argparse.ArgumentParser(description="Runs Annotated Cast pipeline on input CAST json file.")
    parser.add_argument("--grfn_2_2", 
            help="Generate GrFN 2.2 for the CAST-> Annotated Cast  -> GrFN pipeline",
            action="store_true")
    parser.add_argument("--gromet",
            help="Generates GroMEt using the AnnCAST. CAST -> AnnCast -> GroMEt",
            action="store_true")
    parser.add_argument("--agraph",
            help="Generates a pdf of the Annotated CAST",
            action="store_true")
    parser.add_argument("cast_json", 
            help="input CAST.json file")
    options = parser.parse_args()
    return options

"""
def ann_cast_pipeline(cast_instance, to_file=True, gromet=False, grfn_2_2=False, a_graph=False, from_obj=False):
#    cast_to_annotated.py
#
 #   This function reads a JSON file that contains the CAST representation
  #  of a program, and transforms it to annotated CAST. It then calls a
   # series of passes that each augment the information in the annotatd CAST nodes
#    in preparation for the GrFN generation.
   
 #   One command-line argument is expected, namely the name of the JSON file that
  #  contains the CAST data.
   # TODO: Update this docstring as the program has been tweaked so that this is a function instead of
    #the program
 #   

    if from_obj:
        f_name = ""
        cast = cast_instance
    else:
        # TODO: make filename creation more resilient
        f_name = cast_instance
        f_name = f_name.split("/")[-1]
        file_contents = open(f_name, "r").read()

        cast_json = CAST([], "python")
        cast = cast_json.from_json_str(file_contents)

    visitor = CastToAnnotatedCastVisitor(cast)
    # The Annotated Cast is an attribute of the PipelineState object
    pipeline_state = visitor.generate_annotated_cast(grfn_2_2)


    print("Calling IdCollapsePass------------------------")
    IdCollapsePass(pipeline_state)

    print("\nCalling ContainerScopePass-------------------")
    ContainerScopePass(pipeline_state)

    print("\nCalling VariableVersionPass-------------------")
    VariableVersionPass(pipeline_state)

    # NOTE: CASTToAGraphVisitor uses misc.uuid, so placing it here means
    # that the generated GrFN uuids will not be consistent with GrFN uuids
    # created during test runtime. So, do not use these GrFN jsons as expected 
    # json for testing
    f_name = f_name.replace("--CAST.json", "")
    if a_graph:
        agraph = CASTToAGraphVisitor(pipeline_state)
        pdf_file_name = f"{f_name}-AnnCast.pdf"
        agraph.to_pdf(pdf_file_name)

    print("\nCalling GrfnVarCreationPass-------------------")
    GrfnVarCreationPass(pipeline_state)

    print("\nCalling GrfnAssignmentPass-------------------")
    GrfnAssignmentPass(pipeline_state)

    print("\nCalling LambdaExpressionPass-------------------")
    LambdaExpressionPass(pipeline_state)
    
    if gromet:
        print("\nCalling ToGrometPass-----------------------")
        ToGrometPass(pipeline_state)
        
        if to_file:
            with open(f"{f_name}--Gromet-FN-auto.json","w") as f:
                gromet_collection_dict = pipeline_state.gromet_collection.to_dict()
                # NOTE: level was changed from 0 to 2 to format better
                f.write(dictionary_to_gromet_json(del_nulls(gromet_collection_dict), level=2))
        else:
            return pipeline_state.gromet_collection
    else:
        print("\nCalling ToGrfnPass-------------------")
        ToGrfnPass(pipeline_state)
        grfn = pipeline_state.get_grfn()
        grfn.to_json_file(f"{f_name}--AC-GrFN.json")

        grfn_agraph = grfn.to_AGraph()
        grfn_agraph.draw(f"{f_name}--AC-GrFN.pdf", prog="dot")

        print("\nGenerating pickled AnnCast nodes-----------------")
        pickled_file_name = f"{f_name}--AnnCast.pickled"
        with open(pickled_file_name,"wb") as pkfile:
            dill.dump(pipeline_state, pkfile)
"""

def main():
    """cast_to_annotated.py

    This program reads a JSON file that contains the CAST representation
    of a program, and transforms it to annotated CAST. It then calls a
    series of passes that each augment the information in the annotatd CAST nodes
    in preparation for the GrFN generation.
   
    One command-line argument is expected, namely the name of the JSON file that
    contains the CAST data.
    """

    args = get_args()
    ann_cast_pipeline(args.cast_json, gromet=args.gromet, grfn_2_2=args.grfn_2_2, a_graph=args.agraph, from_obj=False, indent_level=2)


if __name__ == "__main__":
    main()
