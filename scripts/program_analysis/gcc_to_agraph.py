import sys
import json
import html
from typing import Dict
from collections import defaultdict, namedtuple

import pygraphviz as pgv
from pygraphviz import AGraph

OPS_TO_STR = {
    "mult_expr": "*",
    "plus_expr": "+",
    "minus_expr": "-",
    "ge_expr": ">=",
    "gt_expr": ">",
    "le_expr": "<=",
    "lt_expr": "<",
    "rdiv_expr": "/",
    "trunc_div_expr": "/", 
    "eq_expr": "==",
    "ne_expr": "!=",
    "negate_expr": "-",
    "lshift_expr": "<<",
    "rshift_expr": ">>",
    "bit_xor_expr": "^",
    "bit_and_expr": "&",
    "bit_ior_expr": "|",
    "bit_not_expr": "~",
    "logical_or": "||",
    "logical_and": "&&",
    "trunc_mod_expr": "%", 
}

Edge = namedtuple("Edge", ["src", "tgt", "flags"])

FALLTHROUGH_FLAG = 2**0
TRUE_FLAG = 2**8
FALSE_FLAG = 2**9

edge_colors = {}
edge_colors[FALLTHROUGH_FLAG] = "grey"
edge_colors[TRUE_FLAG] = "green"
edge_colors[FALSE_FLAG] = "red"

EDGE_FLAGS = [FALLTHROUGH_FLAG, TRUE_FLAG, FALSE_FLAG]


def json_to_agraph_pdf(gcc_ast):
    input_file = gcc_ast["mainInputFilename"]
    input_file_stripped = input_file.split("/")[-1]
    functions = gcc_ast["functions"]
    types = gcc_ast["recordTypes"]
    global_variables = gcc_ast["globalVariables"]

    G = pgv.AGraph(directed=True)

    for f in functions:
        add_function_subgraph(f, G)

    G.graph_attr.update(
        {"dpi": 227, "fontsize": 20, "fontname": "Menlo", "rankdir": "TB"}
    )
    G.node_attr.update({"fontname": "Menlo"})

    G.draw(f"{input_file_stripped}--gcc_ast-graph.pdf", prog="dot")

def add_basic_block_node(bb: Dict, name: str, subgraph: AGraph):
    """Parameters:
        bb: the dict storing the basic block data from the json output of gcc plugin
        name: the name for the basic block node
        subgraph: the graph to add the basic block node to
        Adds an HTML node to `subgraph` with the statements from `bb`
    """
    label = f"<<table border=\"0\" cellborder=\"1\" cellspacing=\"0\">"
    label += f"<tr><td><b>{name}</b></td></tr>"
    for index, stmt in enumerate(bb["statements"]):
        type = stmt["type"]
        l_start = stmt["line_start"] if "line_start" in stmt else -1
        c_start = stmt["col_start"] if "col_start" in stmt else -1
        loc = f"{l_start}:{c_start}"

        if type == "conditional":
            stmt_str = parse_conditional_stmt(stmt)
            # have to convert stmt_str to valid HTML
            label += f"<tr><td>{html.escape(stmt_str)}</td></tr>"
        # default label
        else:
            label += f"<tr><td>{type} at {loc}</td></tr>"


    label += "</table>>"
    print(label)

    subgraph.add_node(name, label=label, shape="plaintext")

def add_function_subgraph(function: Dict, graph: AGraph):
    """
    Parameters:
        function: the dict storing the function data from the json output of gcc plugin
        graph: the graph to add the function cluster to
        Adds a function cluster/subraph consisting of all the basic blocks
        in the `function` dict
    """
    func_name = function["name"]
    bb_label = lambda index: f"{func_name}.BB{index}"
    F = graph.add_subgraph(name=f"cluster_{func_name}", label=func_name, 
            style="bold, rounded", rankdir="LR")

    # TODO: verify that index 0 basic block is the entry point and 
    # index 1 basic block is the exit point
    # entry_index = 0
    # exit_index = 1

    edges_to_add = defaultdict(list)

    for bb in function["basicBlocks"]:
        # special case nodes for entry and exit
        # if bb["index"] == entry_index:
        #     F.add_node(f"{func_name}.Entry")
        # elif bb["index"] == exit_index:
        #     F.add_node(f"{func_name}.Exit")
        bb_name = bb_label(bb["index"])
        add_basic_block_node(bb, bb_name, F)

        for e in bb["edges"]:
            src = bb_label(e["source"])
            tgt = bb_label(e["target"])
            edge = Edge(src=src, tgt=tgt, flags=e["flags"])
            edges_to_add[src].append(edge)

    for src in edges_to_add:
        for edge in edges_to_add[src]:
            color = "black"
            if edge.flags in EDGE_FLAGS:
                color = edge_colors[edge.flags]

            F.add_edge(edge.src, edge.tgt, color=color)

def parse_conditional_stmt(stmt: Dict):
    """
    Parameters:
        `stmt` 'conditional' type statement from a basic block
        obtained from gcc plugin generated json
    Returns:
            A str representing a suitable label for the conditional statement
    """
    op = OPS_TO_STR[stmt["operator"]]
    lhs = parse_operand(stmt["operands"][0])
    rhs = parse_operand(stmt["operands"][1])

    if len(stmt["operands"]) > 2:
        print("WARNING: parse_conditional_stmt() more than two operands!")

    return f"{lhs} {op} {rhs}"


def parse_operand(operand: Dict):
    """
    Parameter:
        `operand` is a operand dict obtained from gcc plugin generated json
    Returns: 
        A str representing the operand
    """
    # TODO: This only parses a couple things
    if "name" in operand:
        return operand["name"]
    elif "value" in operand:
        return operand["value"]
    else:
        return "Operand"



def main():
    json_file = sys.argv[1]
    print(f"Loaded json_file: {json_file}")
    ast_json = json.load(open(json_file))

    json_to_agraph_pdf(ast_json)

if __name__ == "__main__":
    main()
