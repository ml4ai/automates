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
    """class CASTToAGraphVisitor - A visitor that traverses
    CAST nodes to generate a networkx DiGraph that represents
    the CAST as a DiGraph. The CAST object itself is a representation
    of a program.
    A common theme across most visitors is they generate a UID
    that is used with networkx as identifiers for the nodes in the digraph, 
    so we know which nodes to connect to other nodes with edges. They then
    add themselves to a networkx DiGraph object that is updated across
    most the visitors by either adding nodes or edges.
    A lot of the visitors are relatively straightforward and
    follow the pattern for a particular node
        - Visit the node's children
        - Generate a UID for the current node
        - Add the node to the graph with the UID
        - Add edges connecting the node to its children
        - Return the Node's UID, so this can be repeated as necessary

    Inherits from CASTVisitor to use its visit functions.

    Attributes:
        cast (CAST): The CAST object representation of the program
                     we're generating a DiGraph for.
        G (nx.DiGraph): The graph of the program. Gets populated as 
                     nodes are visited. 

    """
    cast: CAST
    G: nx.DiGraph

    def __init__(self, cast: CAST):
        self.cast = cast
        self.G = nx.DiGraph()

    def to_agraph(self):
        """Visits the entire CAST object to populate the graph G
        and returns an AGraph of the graph G as a result.
        """
        self.visit_list(self.cast.nodes)
        A = nx.nx_agraph.to_agraph(self.G)
        A.graph_attr.update(
            {"dpi": 227, "fontsize": 20, "fontname": "Menlo", "rankdir": "TB"}
        )
        A.node_attr.update({"fontname": "Menlo"})
        return A        

    def to_pdf(self,filename):
        """Creates a pdf of the generated agraph"""
        A = self.to_agraph()
        A.draw(filename+".pdf",prog="dot")

    @singledispatchmethod
    def visit(self, node: AstNode):
        """Generic visitor for unimplemented/incorrect nodes"""
        print("Not implemented: ",node)
        print("Type not implemented: ",type(node))
        return None

    @visit.register
    def _(self, node: Assignment):
        """Visits Assignment nodes, the node's UID is returned
        so it can be used to connect nodes in the digraph"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label='Assignment')
        self.G.add_edge(node_uid,left)
        self.G.add_edge(node_uid,right)
        return node_uid

    @visit.register
    def _(self, node: Attribute):
        """Visits Attribute nodes, the node's UID is returned
        so it can be used to connect nodes in the digraph"""
        value = self.visit(node.value)
        attr = self.visit(node.attr)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="Attribute")
        self.G.add_edge(node_uid,value)
        self.G.add_edge(node_uid,attr)
        
        return node_uid

    @visit.register
    def _(self, node: BinaryOp):
        """Visits BinaryOp nodes, the node's UID is returned
        so it can be used to connect nodes in the digraph"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label=node.op)
        self.G.add_edge(node_uid, left)
        self.G.add_edge(node_uid, right)

        return node_uid

    @visit.register
    def _(self, node: Call):
        """Visits Call (function call) nodes. We check to see
        if we have arguments to the node and act accordingly. 
        Appending all the arguments of the function to this node,
        if we have any. The node's UID is returned."""
        func = self.visit(node.func)
        args = []
        if(node.arguments != []):
            args = self.visit_list(node.arguments)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="FunctionCall")
        self.G.add_edge(node_uid, func)
        for n in args:
            self.G.add_edge(node_uid,n)

        return node_uid

    @visit.register
    def _(self, node: ClassDef):
        """Visits ClassDef nodes. We visit all fields and functions
        of the class definition, and connect them to this node.
        This node's UID is returned."""
        # TODO: Where should bases field be used?
        funcs = []
        fields = [] 
        if(node.funcs != []):
            funcs = self.visit_list(node.funcs)
        if(node.fields != []):
            fields = self.visit_list(node.fields)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="Class " + node.name)
        for n in funcs + fields:
            self.G.add_edge(node_uid,n)

        return node_uid

    @visit.register
    def _(self, node: Dict):
        """Visits Dictionary nodes. We visit all the keys and values of
        this dictionary and then they're added to this node. Right now 
        they're just added by adding keys and then values.
        This node's UID is returned."""
        keys = []
        values = []
        if(node.keys != []):
            keys = self.visit_list(node.keys)
        if(node.values != []):
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
        """Visits expression nodes. The node's actual expression is visited
        and added to this node. This node's UID is returned."""
        expr = self.visit(node.expr)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="Expression")
        self.G.add_edge(node_uid,expr)

        return node_uid

    @visit.register
    def _(self, node: FunctionDef):
        """Visits FunctionDef nodes. We visit all the arguments, and then
        we visit the function's statements. They're then added to the graph.
        This node's UID is returned."""
        args = []
        body = []
        if(node.func_args != []):
            args = self.visit_list(node.func_args)
        if(node.body != []):
            body = self.visit_list(node.body) 

        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="Function: "+node.name.name)
        for n in args + body:
            self.G.add_edge(node_uid,n)

        return node_uid

    @visit.register
    def _(self, node: List):
        """Visits List nodes. We visit all the elements and add them to
        this node. This node's UID is returned."""
        values = []
        if(node.values != []):
            values = self.visit_list(node.values)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="List")
        for n in values:
            self.G.add_edge(node_uid,n)

        return node_uid

    @visit.register 
    def _(self, node: Loop):
        """Visits Loop nodes. We visit the conditional expression and the
        body of the loop, and connect them to this node in the graph.
        This node's UID is returned."""
        expr = self.visit(node.expr)
        body = []
        if(node.body != []):
            body = self.visit_list(node.body)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="Loop")
        self.G.add_edge(node_uid,expr)
        for n in body:
            self.G.add_edge(node_uid,n)

        return node_uid
    
    @visit.register
    def _(self, node: ModelBreak):
        """Visits a ModelBreak (break statment) node. 
        The node's UID is returned"""
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="Break")
        return node_uid

    @visit.register
    def _(self, node: ModelContinue):
        """Visits a ModelContinue (continue statment) node. 
        The node's UID is returned"""
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="Continue")
        return node_uid

    @visit.register
    def _(self, node: ModelIf):
        """Visits a ModelIf (If statement) node.
        We visit the condition, and then the body and orelse 
        attributes if we have any. They're all added to the Graph 
        accordingly. The node's UID is returned."""
        expr = self.visit(node.expr)
        body = []
        if(node.body != []):
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
        """Visits a ModelReturn (return statment) node. 
        We add the return value to this node with an edge.
        The node's UID is returned"""
        value = self.visit(node.value)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="Return")
        self.G.add_edge(node_uid, value)

        return node_uid

    @visit.register
    def _(self, node: Module):
        """Visits a Module node. This is the starting point for visiting
        a CAST object. The return value isn't relevant here (I think)"""
        return self.visit_list(node.body) 

    @visit.register
    def _(self, node: Name):
        """Visits a Name node. We add this node's name to the graph, 
        and return the UID of this node."""
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label=node.name)
        return node_uid 

    @visit.register
    def _(self, node: Number):
        """Visits a Number node. We add this node's numeric value to the
        graph and return the UID of this node."""
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label=node.number)
        return node_uid 

    @visit.register
    def _(self, node: Set):
        """Visits a Set node. We add all the elements of this set (if any)
        to the graph and return the UID of this node."""
        values = []
        if(node.values != []):
            values = self.visit_list(node.values)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="Set")
        for n in values:
            self.G.add_edge(node_uid,n)

        return node_uid

    @visit.register
    def _(self, node: String):
        """Visits a String node. We add this node's string to the
        graph and return the UID of this node."""
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="\""+node.string+"\"")
        return node_uid 

    @visit.register
    def _(self, node: Subscript):
        """Visits a Subscript node. We visit its value and slice, and add
        them to the graph along with this node. This node's UID is returned."""
        value = self.visit(node.value)
        s_slice = self.visit(node.slice)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="Subscript")
        self.G.add_edge(node_uid, value)
        self.G.add_edge(node_uid, s_slice)

        return node_uid

    @visit.register
    def _(self, node: Tuple):
        """Visits a Tuple node. We add all the elements of this 
        tuple (if any) to the graph and return the UID of this node."""
        values = []
        if(node.values != []):
            values = self.visit_list(node.values)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid,label="Tuple")
        for n in values:
            self.G.add_edge(node_uid,n)

        return node_uid

    @visit.register
    def _(self, node: UnaryOp):
        """Visits a UnaryOp node. We add this node's value and operator
        to the graph and return this node's UID."""
        val = self.visit(node.value)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label=node.op)
        self.G.add_edge(node_uid, val)

        return node_uid        

    @visit.register
    def _(self, node: Var):
        """Visits a Var node by visiting its value"""
        val = self.visit(node.val) 
        return val
