import sys
import json

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
from automates.model_assembly.expression_trees.expression_walker import expr_trees_from_grfn


def main():
    """cast_to_annotated.py

    This program reads a JSON file that contains the CAST representation
    of a program, and transforms it to annotated CAST. It then calls a
    series of passes that each augment the information in the annotatd CAST nodes
    in preparation for the GrFN generation.
   
    One command-line argument is expected, namely the name of the JSON file that
    contains the CAST data.
    """
    f_name = sys.argv[1]
    file_contents = open(f_name).read()
    cast_json = CAST([], "python")
    cast = cast_json.from_json_str(file_contents)

    visitor = CastToAnnotatedCastVisitor(cast)
    annotated_cast = visitor.generate_annotated_cast()

    # TODO: make filename creation more resilient
    f_name = f_name.split("/")[-1]
    f_name = f_name.replace("--CAST.json", "")

    print("Calling IdCollapsePass------------------------")
    IdCollapsePass(annotated_cast)

    print("\nCalling ContainerScopePass-------------------")
    ContainerScopePass(annotated_cast)

    print("\nCalling VariableVersionPass-------------------")
    VariableVersionPass(annotated_cast)

    agraph = CASTToAGraphVisitor(annotated_cast)
    pdf_file_name = f"{f_name}-AnnCast.pdf"
    agraph.to_pdf(pdf_file_name)

    print("\nCalling GrfnVarCreationPass-------------------")
    GrfnVarCreationPass(annotated_cast)

    print("\nCalling GrfnAssignmentPass-------------------")
    GrfnAssignmentPass(annotated_cast)

    print("\nCalling LambdaExpressionPass-------------------")
    LambdaExpressionPass(annotated_cast)

    print("\nCalling ToGrfnPass-------------------")
    ToGrfnPass(annotated_cast)
    grfn = annotated_cast.get_grfn()
    grfn.to_json_file(f"{f_name}--AC-GrFN.json")

    grfn_agraph = grfn.to_AGraph()
    grfn_agraph.draw(f"{f_name}--AC-GrFN.pdf", prog="dot")

    print("\nExtracting Expression Trees---------------")
    expr_trees = expr_trees_from_grfn(grfn)
    expr_trees_json = json.dumps(expr_trees)

    expr_trees_path = f"{f_name}--expression_trees.json"
    with open(expr_trees_path, "w") as outfile:
        outfile.write(expr_trees_json)

    



if __name__ == "__main__":
    main()
