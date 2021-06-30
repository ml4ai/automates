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

from automates.model_assembly.linking import (
    build_link_graph,
    extract_link_tables,
)


def main():
    filepath = sys.argv[1]
    NUM_ROWS = int(sys.argv[2])
    grfn_with_hypotheses = json.load(open(filepath, "r"))

    L = build_link_graph(grfn_with_hypotheses["grounding"])
    tables = extract_link_tables(L)
    outpath = filepath.replace("-alignment.json", "-link-tables.csv")
    with open(outpath, "w", newline="") as csvfile:
        link_writer = csv.writer(csvfile, dialect="excel")
        for var_name, var_data in tables.items():
            short_varname = var_name
            link_writer.writerow([short_varname])
            link_writer.writerow(
                [
                    "Link Score",
                    "Var-Comm Score",
                    "Comm-GVar Score",
                    "GVar-Eqn Score",
                    "Comment Span",
                    "Text Mention(s) List",
                    "Equation Symbol",
                ]
            )
            rows_to_print = min(len(var_data), NUM_ROWS)
            for link_data in var_data[:rows_to_print]:
                link_writer.writerow(
                    [
                        link_data["link_score"],
                        link_data["vc_score"],
                        link_data["ct_score"],
                        link_data["te_score"] if "te_score" in link_data else None,
                        link_data["comm"],
                        link_data["txt"],
                        link_data["eqn"] if "eqn" in link_data else None,
                    ]
                )
            link_writer.writerow([])


if __name__ == "__main__":
    main()
