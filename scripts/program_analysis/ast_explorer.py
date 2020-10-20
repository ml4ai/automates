import ast
import sys
from functools import singledispatch

import networkx as nx


def main():
    code = load_python_code(sys.argv[1])
    Mod = ast.parse(code)
    CAST = nodes2tree(list(ast.iter_child_nodes(Mod)), nx.DiGraph())
    A = create_graph_viz(CAST)
    A.draw("PID--CAST.pdf", prog="dot")


def create_graph_viz(T: nx.DiGraph):
    A = nx.nx_agraph.to_agraph(T)
    A.graph_attr.update(
        {"dpi": 227, "fontsize": 20, "fontname": "Menlo", "rankdir": "TB"}
    )
    A.node_attr.update(
        {
            "shape": "rectangle",
            "color": "#650021",
            "style": "rounded",
            "fontname": "Menlo",
        }
    )
    A.edge_attr.update({"color": "#650021", "arrowsize": 0.5})
    return A


def load_python_code(path: str) -> str:
    with open(path, "r") as infile:
        return "".join(infile.readlines())


def nodes2tree(nodes: list, G: nx.DiGraph, cur_node: str = "Root"):
    for node in nodes:
        if any(
            [
                isinstance(node, x)
                for x in [
                    ast.ImportFrom,
                    ast.Store,
                    ast.Load,
                    ast.Add,
                    ast.Sub,
                    ast.Mult,
                    ast.Div,
                    ast.Pow,
                    ast.USub,
                    ast.Lt,
                    ast.LtE,
                    ast.Gt,
                    ast.GtE,
                    ast.Eq,
                    ast.NotEq,
                ]
            ]
        ):
            continue

        if isinstance(node, ast.arguments) and len(node.args) == 0:
            continue

        node_name = get_node_str(node)
        G.add_edge(cur_node, node_name)
        nodes2tree(list(ast.iter_child_nodes(node)), G, node_name)
    return G


@singledispatch
def get_node_str(node):
    raise NotImplementedError(f"Unknown node type: {type(node)}\n{vars(node)}")


@get_node_str.register
def _(node: ast.FunctionDef) -> str:
    return node.name


@get_node_str.register
def _(node: ast.arguments) -> str:
    return f"<ARGS>\n({node.args[0].lineno})"


@get_node_str.register
def _(node: ast.arg) -> str:
    return f"{node.arg}\n({node.lineno}, {node.col_offset})"


@get_node_str.register
def _(node: ast.Tuple) -> str:
    return f"<TUPLE>\n({node.lineno}, {node.col_offset})"


@get_node_str.register
def _(node: ast.Assign) -> str:
    return f"<ASSIGN>\n({node.lineno}, {node.col_offset})"


@get_node_str.register
def _(node: ast.AugAssign) -> str:
    cmd = "<ADD>" if isinstance(node.op, ast.Add) else "<SUB>"
    return f"{cmd}\n({node.lineno}, {node.col_offset})"


@get_node_str.register
def _(node: ast.Call) -> str:
    return f"<CALL>\n({node.lineno}, {node.col_offset})"


@get_node_str.register
def _(node: ast.Return) -> str:
    return f"<RETURN>\n({node.lineno}, {node.col_offset})"


@get_node_str.register
def _(node: ast.If) -> str:
    return f"<IF>\n({node.lineno}, {node.col_offset})"


@get_node_str.register
def _(node: ast.While) -> str:
    return f"<WHILE>\n({node.lineno}, {node.col_offset})"


@get_node_str.register
def _(node: ast.BinOp) -> str:
    return f"<{node.op.__class__.__name__.upper()}>\n({node.lineno}, {node.col_offset})"


@get_node_str.register
def _(node: ast.UnaryOp) -> str:
    return f"<{node.op.__class__.__name__.upper()}>\n({node.lineno}, {node.col_offset})"


@get_node_str.register
def _(node: ast.Compare) -> str:
    return f"<{node.ops[0].__class__.__name__.upper()}>\n({node.lineno}, {node.col_offset})"


@get_node_str.register
def _(node: ast.Name) -> str:
    return f"{node.id}\n({node.lineno}, {node.col_offset})"


@get_node_str.register
def _(node: ast.Num) -> str:
    return f"{node.n}\n({node.lineno}, {node.col_offset})"


if __name__ == "__main__":
    main()
