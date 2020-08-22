import sys
import re

import networkx as nx


def main():
    filepath = sys.argv[1]
    match = re.search(r"[a-z_0-9]+(?=\.dot)", filepath)
    filename = match.group()
    G = nx.DiGraph(nx.drawing.nx_pydot.read_dot(filepath))
    A = nx.nx_agraph.to_agraph(G)
    A.draw(f"{filename}.png", prog="dot")


if __name__ == "__main__":
    main()
