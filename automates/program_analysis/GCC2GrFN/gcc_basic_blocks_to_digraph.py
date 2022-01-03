import json
import argparse
from typing import Dict, List
from collections import namedtuple
from enum import IntFlag

import networkx as nx
from networkx import DiGraph

# BBNode is used for the nodes in the networkx digraph
BBNode = namedtuple("BBNode", ["index"])
# EdgeData is used to store edge metadata in the networkx digraph
EdgeData = namedtuple("EdgeData", ["flags", "type"])

# enum class for gcc edge flags, see below links for references
# https://gcc.gnu.org/onlinedocs/gccint/Edges.html#Edges
# https://github.com/gcc-mirror/gcc/blob/master/gcc/cfg-flags.def
class GccEdgeFlag(IntFlag):
    """enum to store gcc edge flags.  
    It is a subclass of `IntFlag` to allow bitwise operations
    e.g. one can have an int variable `flag` and do
    flag & GccEdgeFlag.FALLTHROUGH 
    """
    FALLTHROUGH = 2**0
    ABNORMAL = 2**1
    EH = 2**3
    TRUE_VALUE = 2**8
    FALSE_VALUE = 2**9

def edge_flags_to_str(flags: int):
    to_return = ""
    for flag in GccEdgeFlag:
        if flag & flags:
            to_return += flag.name + " "
    
    return to_return[:-1]


def basic_blocks_to_digraph(basic_blocks: List, return_edges_data = False):
    """ 
    Parameters:
        `basic_blocks` should be a list of basic_blocks obtained from
        the gcc AST plugin.  For example, it could be the list of basic blocks
        obtained from a function definition.

        `return_edges_data` is a boolean.  If it is True, a string
        representing the digraphs collective edge data will be returned.

    Returns:
        returns a networkx digraph where the nodes are `BBNode`s and the edge relationship
        is defined by the `edges` field in the `basic_blocks` list.  The returned graph also
        stores `EdgeData` instances at each edge using edge objects.

        Optionally returns a string of the digraphs collective edge data if
        `return_edges_data` is True.
    """
    digraph = nx.DiGraph()
    collective_edges_data = ""

    # we complete two passes to make the digraph
    # on the first pass, we add the BBNodes, and cache them within a dict
    bb_cache = {}
    for bb in basic_blocks:
        bb_node = make_bbnode(bb)
        bb_cache[bb["index"]] = bb_node
        digraph.add_node(bb_node)

    # on the second pass, we add in the edges
    for bb in basic_blocks:
        index = bb["index"]
        collective_edges_data += f"\nEdges for BB{index}"
        for e in bb["edges"]:
            src = bb_cache[e["source"]]
            tgt = bb_cache[e["target"]]
            flags = e["flags"]
            edge_data = EdgeData(flags=flags, type=edge_flags_to_str(flags))
            digraph.add_edge(src, tgt, object=edge_data)
            collective_edges_data += f"\n\t{src} --> {tgt} with data: {edge_data}"

    # prune of first '\n' of collective_edges_data
    collective_edges_data = collective_edges_data[1:]
    
    if return_edges_data:
        return digraph, collective_edges_data

    # otherwise
    return digraph


def make_bbnode(bb: Dict):
    """
    Parameters:
        bb: the dict storing the basic block data from the json output of gcc plugin
    
    Returns:
        returns a BBNode encompassing the data stored in `bb`
    """
    return BBNode(index=bb["index"])


def digraph_to_pdf(digraph: DiGraph, filename: str):
    """
    Convert the digraph to a PyGraphviz AGraph, and then
    save it to a pdf with filename `filename`
    """

    agraph = nx.nx_agraph.to_agraph(digraph)
    agraph.graph_attr.update(
        {"dpi": 227, "fontsize": 20, "fontname": "Menlo", "rankdir": "TB"}
    )
    agraph.node_attr.update({"fontname": "Menlo"})

    agraph.draw(f"{filename}--basic_blocks.pdf", prog="dot")

def find_lca(digraph: DiGraph, bb1: dict, bb2: dict):
    # Finds the least common ancestor of node1 and node2 in digraph

    pass


def json_ast_to_bb_graphs(gcc_ast: Dict):
    """
    Given a gcc AST json, create the networkx basic block digraphs for each function in it.
    Generates the digraphs pdfs, and also prints the edge data out to the console
    """
    input_file = gcc_ast["mainInputFilename"]
    input_file_stripped = input_file.split("/")[-1]
    functions = gcc_ast["functions"]

    for f in functions:
        basic_blocks = f["basicBlocks"]
        digraph, output = basic_blocks_to_digraph(basic_blocks, return_edges_data=True)
        print(f"\nCollective Edge Data for function {f['name']}")
        print(f"{30*'-'}")
        print(output)
        filename = f"{input_file_stripped}.{f['name']}"
        digraph_to_pdf(digraph, filename)
        

def main():
    parser = argparse.ArgumentParser(description=("Creates networkx digraphs for the "
            "basic blocks in each function from the provided gcc ast json file.  "
            "The edge data for each digraph is printed to the console, and a "
            "pdf of the graph is generated in the cwd."))
    parser.add_argument("json_file", nargs=1, 
            help="the gcc ast json file to be read")

    json_file = parser.parse_args().json_file[0]

    print(f"Loaded json_file: {json_file}")
    ast_json = json.load(open(json_file))

    json_ast_to_bb_graphs(ast_json)

if __name__ == "__main__":
    main()
