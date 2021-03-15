import typing
import networkx as nx

from functools import singledispatchmethod
from automates.utils.misc import uuid

from .cast_visitor import CASTVisitor
from automates.program_analysis.CAST2GrFN.cast import CAST

from automates.program_analysis.CAST2GrFN.model.cast import (
    AstNode,
    Assignment,
    Attribute,
    BinaryOp,
    BinaryOperator,
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
    Subscript,
    Tuple,
    UnaryOp,
    UnaryOperator,
    VarType,
    Var,
)

class CASTToAGraphVisitor(CASTVisitor):
    cast: CAST
    G: nx.DiGraph

    def __init__(self, cast: CAST):
        self.cast = cast
        self.G = nx.DiGraph()

    def to_agraph(self):
        self.visit_list(self.cast.nodes)
        A = nx.nx_agraph.to_agraph(self.G)
        return A        

    def to_pdf(self,filename):
        A = self.to_agraph()
        A.draw(filename+".pdf",prog="dot")

    @singledispatchmethod
    def visit(self, node: AstNode):
        print("Not implemented: ",type(node))
        return None

    @visit.register
    def _(self, node: Module):
        return self.visit_list(node.body) 

    @visit.register
    def _(self, node: Assignment):
        left = self.visit(node.left)
        right = self.visit(node.right)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label='Assignment')
        self.G.add_edge(node_uid,left)
        self.G.add_edge(node_uid,right)
        return node_uid

    @visit.register
    def _(self, node: Var):
        val = self.visit(node.val) 
        return val

    @visit.register
    def _(self, node: Name):
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label=node.name)
        return node_uid 

    @visit.register
    def _(self, node: Number):
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label=node.number)
        return node_uid 

    @visit.register
    def _(self, node: FunctionDef):
        args = self.visit_list(node.func_args)
        body = self.visit_list(node.body) 
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="Function: "+node.name.name)
        for n in args + body:
            self.G.add_edge(node_uid,n)

        return node_uid

    @visit.register
    def _(self, node: BinaryOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label=node.op)
        self.G.add_edge(node_uid, left)
        self.G.add_edge(node_uid, right)

        return node_uid

    @visit.register
    def _(self, node: UnaryOp):
        val = self.visit(node.value)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label=node.op)
        self.G.add_edge(node_uid, val)

        return node_uid        

    @visit.register
    def _(self, node: ModelIf):
        expr = self.visit(node.expr)
        body = self.visit_list(node.body) 
        orelse = None if node.orelse == None else self.visit(node.orelse)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="If")
        self.G.add_edge(node_uid,expr)
        for n in body:
            self.G.add_edge(node_uid,n)

        if(orelse != None):
            self.G.add_edge(node_uid,orelse)

        return node_uid

    