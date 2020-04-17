"""
This program allows a user to generate a CSV file with all of the grounding
link hypotheses from a GrFN JSON file. Note that this GrFN JSON file must
already be populated with link information.


Example execution:
    $ python grfn_links_to_csv.py <path-to-GrFN_with_groundings.json>

Author: Paul D. Hein
"""

import json
import sys
import csv

from model_analysis.linking import build_link_graph, extract_link_tables


def main():
    filepath = sys.argv[1]
    grfn_with_hypotheses = json.load(open(filepath, "r"))

    L = build_link_graph(grfn_with_hypotheses["grounding"])
    tables = extract_link_tables(L)
    outpath = filepath.replace(".json", "--links.csv")
    with open(outpath, "w", newline="") as csvfile:
        link_writer = csv.writer(csvfile, dialect="excel")

        for var_name, var_data in tables.items():
            (_, namespace, sub_name, basename, idx) = var_name.split("::")
            short_varname = "::".join([sub_name, basename, idx])
            link_writer.writerow([short_varname])
            link_writer.writerow(
                [
                    "Link Score",
                    "Var-Comm Score",
                    "Comm-Text Score",
                    "Text-Eqn Score",
                    "Comment Span",
                    "Text Mention",
                    "Equation Symbol",
                ]
            )
            for link_data in var_data:
                link_writer.writerow(
                    [
                        link_data["link_score"],
                        link_data["vc_score"],
                        link_data["ct_score"],
                        link_data["te_score"],
                        link_data["comm"],
                        link_data["txt"],
                        link_data["eqn"],
                    ]
                )
            link_writer.writerow([])


if __name__ == "__main__":
    main()
