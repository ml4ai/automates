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

import networkx as nx
from tqdm import tqdm

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_assembly.expression_visitor import (
    ExpressionVisitor,
    nodes2DiGraph,
)


def main(args):
    grfn_file = args.grfn_file
    G = GroundedFunctionNetwork.from_json(grfn_file)
    visitor = ExpressionVisitor()
    func_node_graphs = list()
    for func_node in tqdm(G.lambdas, desc="Converting Lambdas"):
        node_uid = func_node.uid
        expr_tree = ast.parse(func_node.func_str)
        visitor.visit(expr_tree)

        nodes = visitor.get_nodes()
        nodes2AGraph(node_uid, nodes)

        node_dicts = [n.to_dict() for n in nodes]
        curr_func_node = {"func_node_uid": node_uid, "nodes": node_dicts}
        func_node_graphs.append(curr_func_node)

    outfile_name = grfn_file.replace("--GrFN.json", "--expr-trees.json")
    json.dump(func_node_graphs, open(outfile_name, "w"))


def nodes2AGraph(graph_name: str, nodes: list):
    func_network = nodes2DiGraph(nodes)
    A = nx.nx_agraph.to_agraph(func_network)
    A.graph_attr.update(
        {
            "dpi": 227,
            "fontsize": 20,
            "fontname": "Menlo",
            "rankdir": "TB",
        }
    )
    A.node_attr.update({"fontname": "Menlo"})
    A.draw(f"{graph_name}.pdf", prog="dot")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert lambda expressions in a GrFN JSON file"
        + " into expression trees"
    )
    parser.add_argument("grfn_file", help="Filepath to a GrFN JSON file")
    args = parser.parse_args()
    main(args)
