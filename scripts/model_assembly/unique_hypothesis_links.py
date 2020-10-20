import json
import sys

import networkx as nx


def main():
    links_file = sys.argv[1]

    G = nx.Graph()
    link_data = json.load(open(links_file, "r"))
    for link in link_data["grounding"]:
        var1_name = f"{link['element_1']['type']}:-:{link['element_1']['source']}:-:{link['element_1']['content']}"
        var2_name = f"{link['element_2']['type']}:-:{link['element_2']['source']}:-:{link['element_2']['content']}"
        G.add_edge(var1_name, var2_name)

    equations = list()
    comments = list()
    identifiers = list()
    text_spans = list()
    text_vars = list()
    for node_name in G.nodes:
        print(node_name)
        (link_type, link_src, link_content) = node_name.split(":-:")
        if link_type == "text_span":
            doc_only_src = link_src[link_src.rfind("/") + 1 :]
            text_spans.append((doc_only_src, link_content))
        elif link_type == "text_var":
            doc_only_src = link_src[link_src.rfind("/") + 1 :]
            text_vars.append((doc_only_src, link_content))
        elif link_type == "comment_span":
            comments.append((link_src, link_content))
        elif link_type == "identifier":
            identifiers.append((link_src, link_content))
        elif link_type == "equation_span":
            equations.append((link_src, link_content))
        else:
            raise TypeError(f"Unidentified link type: {link_type}")

    outfile = links_file.replace("-alignment.json", "-links.json")
    json.dump(
        {
            "equations": equations,
            "comments": comments,
            "identifiers": identifiers,
            "text_spans": text_spans,
            "text_vars": text_vars,
            "edges": list(G.edges),
        },
        open(outfile, "w"),
    )


if __name__ == "__main__":
    main()
