"""
PURPOSE: Given a GrFN JSON file, this scrip generates a JSON file containing
            expression treees for all lambda expressions found in the GrFN.
            PDFs of each expression tree are also generated for
            visual inspection.
AUTHOR: Paul D. Hein
DATE: 03/08/2020
"""
import ast
import json
import argparse

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_assembly.expression_trees.expression_walker import expr_trees_from_grfn

def main(args):
    grfn_file = args.grfn_file
    G = GroundedFunctionNetwork.from_json(grfn_file)
    func_node_graphs = expr_trees_from_grfn(G, generate_agraph=True)
    outfile_name = grfn_file.replace("--GrFN.json", "--expr-trees.json")
    json.dump(func_node_graphs, open(outfile_name, "w"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert lambda expressions in a GrFN JSON file"
        + " into expression trees"
    )
    parser.add_argument("grfn_file", help="Filepath to a GrFN JSON file")
    args = parser.parse_args()
    main(args)
