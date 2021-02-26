import ast
import sys
import json

import networkx as nx
from tqdm import tqdm

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_assembly.expression_visitor import (
    ExpressionVisitor,
    nodes2DiGraph,
)


def main():
    grfn_file = sys.argv[1]
    G = GroundedFunctionNetwork.from_json(grfn_file)
    visitor = ExpressionVisitor()
    func_node_graphs = list()
    for func_node in tqdm(G.lambdas, desc="Converting Lambdas"):
        node_uid = func_node.uid
        expr_tree = ast.parse(func_node.func_str)

        visitor.visit(expr_tree)
        node_list = visitor.get_nodes()
        func_network = nodes2DiGraph(node_list)

        A = nx.nx_agraph.to_agraph(func_network)
        A.graph_attr.update(
            {"dpi": 227, "fontsize": 20, "fontname": "Menlo", "rankdir": "TB"}
        )
        A.node_attr.update({"fontname": "Menlo"})
        A.draw(f"{node_uid}.pdf", prog="dot")

        func_node_graphs.append(
            {
                "func_node_uid": node_uid,
                "nodes": [n.to_dict() for n in node_list],
            }
        )

    outfile_name = sys.argv[2]
    json.dump(func_node_graphs, open(outfile_name, "w"))


if __name__ == "__main__":
    main()
