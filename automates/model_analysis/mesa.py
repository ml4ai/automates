import ast
import sys
import enum
from functools import singledispatch


@enum.unique
class MathOp(enum.Enum):
    NEG = 0
    ADD = 1
    SUB = 2
    MUL = 3
    DIV = 4
    POW = 5
    SQRT = 6
    EXP = 7
    LN = 8
    LOG = 9
    SIN = 10
    COS = 11
    TAN = 12
    CSC = 13
    SEC = 14
    COT = 15
    ASIN = 16
    ACOS = 17
    ATAN = 18
    ACSC = 19
    ASEC = 20
    ACOT = 21
    MIN = 22
    MAX = 23
    ABS = 24
    ROUND = 25
    CEIL = 26
    FLOOR = 27


def mesa(py_eqn_str_1, py_eqn_str_2):
    """Short summary.

    Args:
        py_eqn_str_1 (type): Description of parameter `py_eqn_str_1`.
        py_eqn_str_2 (type): Description of parameter `py_eqn_str_2`.

    Returns:
        type: Description of returned object.

    """
    module_node_2 = ast.parse(py_eqn_str_2)
    ast_2 = module_node_2.body[0].value
    temp = ast_2.left
    ast_2.left = ast_2.right
    ast_2.right = temp
    __visit_child_nodes(ast_2)
    sys.exit()


@singledispatch
def __get_subtree_spelling(node):
    raise TypeError(f"SubtreeSpeller unhandled AST node type: {type(node)}")


@__get_subtree_spelling.register
def _(node: ast.Num):
    return f"{str(node.n)}"


@__get_subtree_spelling.register
def _(node: ast.Name):
    return f"{node.id}"


@__get_subtree_spelling.register
def _(node: ast.BinOp):
    spell_left = __get_subtree_spelling(node.left)
    spell_right = __get_subtree_spelling(node.right)
    op_name = type(node.op).__name__
    return f"{op_name}|{spell_left}|{spell_right}"


@singledispatch
def __visit_child_nodes(node):
    raise TypeError(f"ChildVisitor unhandled AST node type: {type(node)}")


@__visit_child_nodes.register
def _(node: ast.Num):
    node_spelling = __get_subtree_spelling(node)
    print(type(node), node_spelling)


@__visit_child_nodes.register
def _(node: ast.Name):
    node_spelling = __get_subtree_spelling(node)
    print(type(node), node_spelling)


@__visit_child_nodes.register
def _(node: ast.BinOp):
    node_spelling = __get_subtree_spelling(node)
    print(type(node), node_spelling)
    __visit_child_nodes(node.left)
    __visit_child_nodes(node.right)
