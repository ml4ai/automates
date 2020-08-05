import ast
from functools import singledispatch


@singledispatch
def translate(node):
    pass


@translate
def _(node: ast.FunctionDef):
    print(
        f"{node.name} --> {len(node.args.args)} args\t{len(node.body)} lines"
    )


@translate
def _(node: ast.Assign):
    print(f"{node.lineno}\t{node.targets[0].id} = {node.value}")
