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
        print("Not implemented: ",node)
        print("Type not implemented: ",type(node))
        return None+1

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
    def _(self, node: Attribute):
        value = self.visit(node.value)
        attr = self.visit(node.attr)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="Attribute")
        self.G.add_edge(node_uid,value)
        self.G.add_edge(node_uid,attr)
        
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
    def _(self, node: Call):
        func = self.visit(node.func)
        if(node.arguments != []):
            args = self.visit_list(node.arguments)
        else:
            args = []
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="FunctionCall")
        self.G.add_edge(node_uid, func)
        for n in args:
            self.G.add_edge(node_uid,n)

        return node_uid

    @visit.register
    def _(self, node: ClassDef):
        # TODO: Where should bases field be used?
        funcs = self.visit_list(node.funcs)
        fields = self.visit_list(node.fields)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="Class " + node.name)
        for n in funcs + fields:
            self.G.add_edge(node_uid,n)

        return node_uid

    @visit.register
    def _(self, node: Dict):
        keys = self.visit_list(node.keys)
        values = self.visit_list(node.values)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="Dict")

        # TODO: Make this prettier
        for n in keys + values:
            self.G.add_edges(node_uid, n)        

        #for (k,v) in list(zip(keys,values)):
         #   self.G.add_edges(node_uid, (k,v)) 

        return node_uid

    @visit.register
    def _(self, node: Expr):
        expr = self.visit(node.expr)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="Expression")
        self.G.add_edge(node_uid,expr)

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
    def _(self, node: List):
        values = self.visit_list(node.values)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="List")
        for n in values:
            self.G.add_edge(node_uid,n)

        return node_uid

    @visit.register 
    def _(self, node: Loop):
        expr = self.visit(node.expr)
        body = self.visit_list(node.body)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="Loop")
        self.G.add_edge(node_uid,expr)
        for n in body:
            self.G.add_edge(node_uid,n)

        return node_uid
    
    @visit.register
    def _(self, node: ModelBreak):
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="Break")
        return node_uid

    @visit.register
    def _(self, node: ModelContinue):
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="Continue")
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

    @visit.register
    def _(self, node: ModelReturn):
        value = self.visit(node.value)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="Return")
        self.G.add_edge(node_uid, value)

        return node_uid

    @visit.register
    def _(self, node: Module):
        return self.visit_list(node.body) 

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
    def _(self, node: Set):
        values = self.visit_list(node.values)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="Set")
        for n in values:
            self.G.add_edge(node_uid,n)

        return node_uid

    @visit.register
    def _(self, node: String):
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="\""+node.string+"\"")
        return node_uid 

    @visit.register
    def _(self, node: Subscript):
        value = self.visit(node.value)
        s_slice = self.visit(node.slice)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="Subscript")
        self.G.add_edge(node_uid, value)
        self.G.add_edge(node_uid, s_slice)

        return node_uid

    @visit.register
    def _(self, node: Tuple):
        values = self.visit_list(node.values)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="Tuple")
        for n in values:
            self.G.add_edge(node_uid,n)

        return node_uid

    @visit.register
    def _(self, node: UnaryOp):
        val = self.visit(node.value)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label=node.op)
        self.G.add_edge(node_uid, val)

        return node_uid        

    @visit.register
    def _(self, node: Var):
        val = self.visit(node.val) 
        return val
