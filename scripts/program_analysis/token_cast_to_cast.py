import networkx as nx
from typing import cast

from functools import singledispatchmethod
from automates.utils.misc import uuid

import sys
import argparse

from automates.program_analysis.CAST2GrFN.cast import CAST
from automates.program_analysis.CAST2GrFN.model.cast import (
    AstNode,
    Assignment,
    Attribute,
    BinaryOp,
    BinaryOperator,
    Boolean,
    Call,
    ClassDef,
    Dict,
    Expr,
    FunctionDef,
    List,
    Loop,
    ModelBreak,
    ModelContinue,
    ModelIf,
    ModelReturn,
    Module,
    Name,
    Number,
    Set,
    String,
    SourceRef,
    Subscript,
    Tuple,
    UnaryOp,
    UnaryOperator,
    VarType,
    Var,
)

class tCASTNode(object):
    def __init__(self):
        pass

class tCASTFuncNode(tCASTNode):
    name: str

    def __init__(self, name, nodes):
        self.name = name
        self.nodes = nodes

class tCASTBinOPNode(tCASTNode):
    op: str
    left: tCASTNode
    right: tCASTNode

    def __init__(self, op, l, r):
        self.op = op
        self.left = l
        self.right = r

class tCASTUnaryOPNode(tCASTNode):
    op: str
    opnd: tCASTNode

    def __init__(self, op, opnd):
        self.op = op
        self.opnd = opnd

class tCASTVarNode(tCASTNode):
    name: str
    orig_name: str
    
    def __init__(self, name):
        self.name = name
        self.orig_name = ""

class tCASTCallNode(tCASTNode):
    name: str

    def __init__(self, name, args):
        self.name = name
        self.args = args

class tCASTValNode(tCASTNode):
    name: str

    def __init__(self,name):
        self.name = name


class tCASTToAGraphVisitor():

    G: nx.DiGraph

    def __init__(self, tCAST):
        self.G = nx.DiGraph()
        self.tCAST = tCAST
        self.node_counter = 0


    def to_agraph(self):
        self.visit(self.tCAST)
        A = nx.nx_agraph.to_agraph(self.G)
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
        for node in A.iternodes():
            node.attr["fontcolor"] = "black"
            node.attr["style"] = "rounded"
        A.edge_attr.update({"color": "#650021", "arrowsize": 0.5})

        return A

    def to_pdf(self, pdf_filepath):
        A = self.to_agraph()
        A.draw(pdf_filepath, prog="dot")

    @singledispatchmethod
    def visit(self, node: tCASTNode):
        print(f"Unrecognize node type: {type(node)}")

    @visit.register
    def _(self, node: tCASTFuncNode):
        func_uid = self.node_counter
        self.node_counter += 1

        body = []
        for n in node.nodes:
            to_add = self.visit(n)
            body.append(to_add)
        
        body_uid = self.node_counter

        self.G.add_node(func_uid, label=node.name)
        self.G.add_node(body_uid, label="Body")
        self.node_counter += 1

        self.G.add_edge(func_uid, body_uid)

        for n in body:
            self.G.add_edge(body_uid,n)

        return func_uid

    @visit.register
    def _(self, node: tCASTBinOPNode):
        op_uid = self.node_counter
        self.node_counter += 1

        left = self.visit(node.left)
        right = self.visit(node.right)

        self.G.add_node(op_uid, label=node.op)
        self.G.add_edge(op_uid, left)
        self.G.add_edge(op_uid, right)

        return op_uid

    @visit.register
    def _(self, node: tCASTCallNode):
        node_uid = self.node_counter
        self.node_counter += 1

        args_to_add = []
        for arg in node.args:
            to_add = self.visit(arg)
            args_to_add.append(to_add)

        self.G.add_node(node_uid, label=node.name)

        for arg in args_to_add:
            self.G.add_edge(node_uid,arg)

        return node_uid

    @visit.register
    def _(self, node: tCASTUnaryOPNode):
        op_uid = self.node_counter
        self.node_counter += 1

        opnd = self.visit(node.opnd)

        self.G.add_node(op_uid, label=node.op)
        self.G.add_edge(op_uid, opnd)

        return op_uid

    @visit.register
    def _(self, node: tCASTValNode):
        node_uid = self.node_counter
        self.node_counter += 1

        self.G.add_node(node_uid, label=node.name)

        return node_uid

    @visit.register
    def _(self, node: tCASTVarNode):
        node_uid = self.node_counter
        self.node_counter += 1

        self.G.add_node(node_uid, label=node.name)

        return node_uid

class tCASTToCASTVisitor():

    @singledispatchmethod
    def visit(self, node: tCASTNode):
        print(f"Unrecognize node type: {type(node)}")

    @visit.register
    def _(self, node: tCASTFuncNode):
        body = []
        for n in node.nodes:
            to_add = self.visit(n)
            body.append(to_add)
        
        return Module(name=node.name, body=body)

    @visit.register
    def _(self, node: tCASTBinOPNode):
        left = self.visit(node.left)
        right = self.visit(node.right)

        return BinaryOp(op=node.op, left=left, right=right)

    @visit.register
    def _(self, node: tCASTCallNode):
        args = []
        for arg in node.args:
            to_add = self.visit(arg)
            args.append(to_add)

        name = Name(name=node.name)

        return Call(func=name, arguments=args)

    @visit.register
    def _(self, node: tCASTUnaryOPNode):
        val = self.visit(node.opnd)

        return UnaryOp(op=node.op,value=val)

    @visit.register
    def _(self, node: tCASTValNode):
        # TODO: Remap values back so it's not just strings

        return String(string=node.name)


    @visit.register
    def _(self, node: tCASTVarNode):
        name = Name(name=node.name)

        return Var(val=name)
        #return Var(val=name,type="Number")


def main():
    """token_cast_to_cast.py

    """

    # Open the CAST json and load it as a Python object
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-f", "--file", type=str, help="CAST JSON input file"
    )

    parser.add_argument(
        "-d", "--directory", type=str, help="A directory to store files to", default="."
    )

    args = parser.parse_args()

    if args.file == None:
        print("USAGE: python token_cast_to_cast.py -f <file_name> [-d <directory_name>]")
        sys.exit()

    f_name = args.file

    file_contents = open(f_name).readlines()

    tcast = file_contents[0]
    tokens = tcast.strip().split(" ")

    if tokens[0:2] == ['(','main']:
        tokens.pop(0)
        tokens.pop(0)
        
        cast_body = []
        while tokens[0] == '(':
            C = visit_statement(tokens)
            cast_body.append(C)

        if tokens[0] != ')':
            print("PARSE ERROR: main function doesn't have properly matched parentheses!")
            sys.exit()
        tokens.pop(0)

        if len(tokens) != 0:
            print("Tokens still remain")
            print(tokens)
            sys.exit()
    else:
        print("ERROR: Tokenized CAST doesn't start with '( main' !!")
        sys.exit()

    to_ret = tCASTFuncNode('main',cast_body)

    CAST_visitor = tCASTToCASTVisitor()
    visited_CAST = CAST_visitor.visit(to_ret)

    c = CAST([visited_CAST],"c")

    json_string = c.to_json_str()

    agraph_visitor = tCASTToAGraphVisitor(to_ret)
    agraph_visitor.to_pdf("test_visitor.pdf")

    print(json_string)
    
    last_slash_idx = f_name.rfind("/")
    file_ending_idx = f_name.rfind(".")

def visit_operand(tokens):
    if 'Var' in tokens[0]:
        return tCASTVarNode(tokens.pop(0))
    elif 'Val' in tokens[0]: 
        return tCASTValNode(tokens.pop(0))
    elif tokens[0] == '(':
        return visit_statement(tokens)

def visit_statement(tokens):
    if tokens[0] != '(':
        print("Error in visit statement")
        sys.exit()

    tokens.pop(0)

    bin_ops = ('Add','Mult','Sub','Div','Mod','BitAnd','BitXor','BitOr')

    op = tokens.pop(0)
    # Visit left operand
    # Visit right operand
    # Create tCASTOpNode

    if op == 'assign':
        left = visit_operand(tokens)
        right = visit_operand(tokens)

        if tokens[0] != ')':
            print("ERROR 1")
            sys.exit()

        tokens.pop(0)
        return tCASTBinOPNode(op, left, right)
    elif op == 'call':
        func_name = tokens.pop(0)

        args = []

        while tokens[0] != ')':
            args.append(visit_operand(tokens))

        tokens.pop(0)

        return tCASTCallNode(func_name, args)
    elif op == 'return':
        opd = visit_operand(tokens)

        if tokens[0] != ')':
            print("ERROR 2")
            sys.exit()

        tokens.pop(0)
        return tCASTUnaryOPNode(op,opd)
    elif op in bin_ops:
        left = visit_operand(tokens)
        right = visit_operand(tokens)

        if tokens[0] != ')':
            print("ERROR 5")
            sys.exit()

        tokens.pop(0)
        return tCASTBinOPNode(op, left, right)
    else:
        print(f"Unknown token: {op}")
        sys.exit()



    
if __name__ == "__main__":
    main()
