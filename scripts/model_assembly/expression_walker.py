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
    ExprVariableNode,
    ExprDefinitionNode,
)


def main(args):
    grfn_file = args.grfn_file
    G = GroundedFunctionNetwork.from_json(grfn_file)
    func2hyperedge = {edge.lambda_fn.uid: edge for edge in G.hyper_edges}
    visitor = ExpressionVisitor()
    func_node_graphs = list()
    for func_node in tqdm(G.lambdas, desc="Converting Lambdas"):
        node_uid = func_node.uid
        expr_tree = ast.parse(func_node.func_str)
        visitor.visit(expr_tree)

        nodes = visitor.get_nodes()
        add_grfn_uids(nodes, func2hyperedge, node_uid)
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


def add_grfn_uids(nodes, F2H, func_uid):
    input_var_uids = [ivar.uid for ivar in F2H[func_uid].inputs]
    id2node = {n.uid: n for n in nodes}
    variable_nodes = [n for n in nodes if isinstance(n, ExprVariableNode)]

    arguments_node = None
    for n in nodes:
        if isinstance(n, ExprDefinitionNode) and n.def_type == "ARGUMENTS":
            arguments_node = n
            break

    arg_names = [
        id2node[node_uid].identifier for node_uid in arguments_node.children
    ]
    arg_name2input_uid = {
        arg_name: input_uid
        for arg_name, input_uid in zip(arg_names, input_var_uids)
    }
    for node in variable_nodes:
        if node.identifier in arg_name2input_uid:
            node.grfn_uid = arg_name2input_uid[node.identifier]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert lambda expressions in a GrFN JSON file"
        + " into expression trees"
    )
    parser.add_argument("grfn_file", help="Filepath to a GrFN JSON file")
    args = parser.parse_args()
    main(args)
