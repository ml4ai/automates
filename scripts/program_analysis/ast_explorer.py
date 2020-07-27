import ast
import sys


def dfs_traversal(nodes: list):
    for node in nodes:
        if isinstance(node, ast.FunctionDef):
            print(
                f"{node.name} --> {len(node.args.args)} args\t{len(node.body)} lines"
            )
        elif isinstance(node, ast.Assign):
            print(f"{node.lineno}\t{node.targets[0].id} = {node.value}")
            continue
        elif isinstance(node, ast.AugAssign):
            op = "+=" if isinstance(node.op, ast.Add) else "-="
            print(f"{node.lineno}\t{node.target.id} {op} {node.value}")
            continue
        else:
            print(type(node), vars(node))
        dfs_traversal(ast.iter_child_nodes(node))


def main():
    code = ""
    with open(sys.argv[1], "r") as infile:
        code = "".join(infile.readlines())

    tree = ast.parse(code)
    dfs_traversal(ast.iter_child_nodes(tree))


if __name__ == "__main__":
    main()
