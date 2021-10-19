import json
import sys

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_analysis.comparison import GrFNIntersectionGraph


def main():
    grfn1_filename = sys.argv[1]
    grfn2_filename = sys.argv[2]
    intersection_filename = sys.argv[3]

    G1 = GroundedFunctionNetwork.from_json(grfn1_filename)
    G2 = GroundedFunctionNetwork.from_json(grfn2_filename)
    intersection_data = json.load(open(intersection_filename, "r"))

    GIG = GrFNIntersectionGraph.from_GrFN_comparison(G1, G2, intersection_data)
    gig_filename = intersection_filename.replace("--comparison.json",
                                                 "--intersection-graph.json")
    GIG.to_json_file(gig_filename)


if __name__ == '__main__':
    main()
