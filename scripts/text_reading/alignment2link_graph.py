import sys
import json

import networkx as nx

from model_analysis.linking import build_link_graph


def main():
    alignment_filepath = sys.argv[1]
    alignment_data = json.load(open(alignment_filepath, "r"))
    link_graph = build_link_graph(alignment_data["grounding"])

    A = nx.nx_agraph.to_agraph(link_graph)
    A.graph_attr.update(
        {"dpi": 227, "fontsize": 20, "fontname": "Menlo", "rankdir": "RL"}
    )
    A.node_attr.update(
        {"shape": "rectangle", "style": "bold", "fontname": "Menlo"}
    )

    alignment_name = alignment_filepath[alignment_filepath.rfind("/") + 1 :]
    alingment_outname = alignment_name.replace("-alignment.json", "-links.pdf")
    A.draw(alingment_outname, prog="dot")


if __name__ == "__main__":
    main()
