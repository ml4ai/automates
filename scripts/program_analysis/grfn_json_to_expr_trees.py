import json
import sys
from automates.model_assembly.expression_trees.expression_walker import expr_trees_from_grfn
from automates.model_assembly.networks import GroundedFunctionNetwork


def main():
    f_name = sys.argv[1]
    grfn = GroundedFunctionNetwork.from_json(f_name)
    print("\nExtracting Expression Trees---------------")
    expr_trees = expr_trees_from_grfn(grfn)

    expr_trees_json = json.dumps(expr_trees)

    f_name = f_name.replace("--GrFN.json", "")
    expr_trees_path = f"{f_name}-expression_trees.json"
    with open(expr_trees_path, "w") as outfile:
        outfile.write(expr_trees_json)

main()
