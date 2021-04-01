import argparse


from automates.model_assembly.networks import (
    GroundedFunctionNetwork,
    CausalAnalysisGraph,
)


def main(args):
    filepath = args.grfn_json
    G = GroundedFunctionNetwork.from_json(filepath)
    C = CausalAnalysisGraph.from_GrFN(G)
    C.to_igraph_gml(args.outpath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="Convert a GrFN JSON to a CAG and then output the CAG "
        + "representation in a dotfile to be used with igraph."
    )
    parser.add_argument("grfn_json", help="GrFN JSON file to be converted")
    parser.add_argument(
        "-o",
        "--outpath",
        type=str,
        default=".",
        help="Path to output GML file",
    )
    args = parser.parse_args()
    main(args)
