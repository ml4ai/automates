import ast
import sys

import networkx as nx


def dfs_traversal(nodes: list, G: nx.DiGraph, cur_node: str = "Root"):
    for node in nodes:
        node_name = ""
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
        elif isinstance(node, ast.FunctionDef):
            node_name = node.name
            # print(
            #     f"{node.name} --> {len(node.args.args)} args\t{len(node.body)} lines"
            # )
        elif isinstance(node, ast.arguments):
            node_name = "<ARGS>"
        elif isinstance(node, ast.arg):
            node_name = f"{node.arg}\n({node.lineno}, {node.col_offset})"
        elif isinstance(node, ast.Assign):
            node_name = f"=\n({node.lineno}, {node.col_offset})"
            # print(f"{node.lineno}\t{node.targets[0].id} = {node.value}")
            # continue
        elif isinstance(node, ast.AugAssign):
            node_name = f"{node.op}\n({node.lineno}, {node.col_offset})"
            op = "+=" if isinstance(node.op, ast.Add) else "-="
            # print(f"{node.lineno}\t{node.target.id} {op} {node.value}")
            # continue
        elif isinstance(node, ast.Call):
            node_name = f"<CALL>\n({node.lineno}, {node.col_offset})"
        elif isinstance(node, ast.Return):
            node_name = f"<RETURN>\n({node.lineno}, {node.col_offset})"
        elif isinstance(node, ast.If):
            node_name = f"<IF>\n({node.lineno}, {node.col_offset})"
        elif isinstance(node, ast.BinOp):
            node_name = f"<{node.op.__class__.__name__.upper()}>\n({node.lineno}, {node.col_offset})"
        elif isinstance(node, ast.UnaryOp):
            node_name = f"<{node.op.__class__.__name__.upper()}>\n({node.lineno}, {node.col_offset})"
        elif isinstance(node, ast.Compare):
            node_name = f"<{node.ops[0].__class__.__name__.upper()}>\n({node.lineno}, {node.col_offset})"
        elif isinstance(node, ast.Name):
            node_name = f"{node.id}\n({node.lineno}, {node.col_offset})"
        elif isinstance(node, ast.Num):
            node_name = f"{node.n}\n({node.lineno}, {node.col_offset})"
        else:
            node_name = node.__class__.__name__
            print(type(node), vars(node))
        G.add_edge(cur_node, node_name)
        dfs_traversal(list(ast.iter_child_nodes(node)), G, node_name)
    return G


def main():
    code = ""
    with open(sys.argv[1], "r") as infile:
        code = "".join(infile.readlines())

    tree = ast.parse(code)
    G = dfs_traversal(list(ast.iter_child_nodes(tree)), nx.DiGraph())

    A = nx.nx_agraph.to_agraph(G)
    A.draw("trajectory--CAST.pdf", prog="dot")


if __name__ == "__main__":
    main()
