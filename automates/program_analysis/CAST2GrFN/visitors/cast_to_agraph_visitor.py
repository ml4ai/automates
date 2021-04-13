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


class CASTTypeError(TypeError):
    """Used to create errors in the CASTToAGraphVisitor, in particular
    when the visitor encounters some value that it wasn't expecting.

    Args:
        Exception: An exception that occurred during execution.
    """

    pass


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
    follow this pattern for a particular node
        - Visit the node's children
        - Generate a UID for the current node
        - Add the node to the graph with the UID
        - Add edges connecting the node to its children
        - Return the Node's UID, so this can be repeated as necessary

    Some do a little bit of extra work to make the visualization look
    nicer, like add extra 'group' nodes to group certain nodes together
    (i.e. function arguments, class attributes)

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

    def to_pdf(self, pdf_filepath: str):
        """Generates an agraph, and uses it
        to create a PDF using the 'dot' program"""
        A = self.to_agraph()
        A.draw(pdf_filepath, prog="dot")

    @singledispatchmethod
    def visit(self, node: AstNode):
        """Generic visitor for unimplemented/unexpected nodes"""
        raise CASTTypeError(f"Unrecognized node type: {type(node)}")

    @visit.register
    def _(self, node: Assignment):
        """Visits Assignment nodes, the node's UID is returned
        so it can be used to connect nodes in the digraph"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="Assignment")
        self.G.add_edge(node_uid, left)
        self.G.add_edge(node_uid, right)
        return node_uid

    @visit.register
    def _(self, node: Attribute):
        """Visits Attribute nodes, the node's UID is returned
        so it can be used to connect nodes in the digraph"""
        value = self.visit(node.value)
        attr = self.visit(node.attr)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="Attribute")
        self.G.add_edge(node_uid, value)
        self.G.add_edge(node_uid, attr)

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
        if len(node.arguments) > 0:
            args = self.visit_list(node.arguments)

        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="FunctionCall")
        self.G.add_edge(node_uid, func)

        args_uid = uuid.uuid4()
        self.G.add_node(args_uid, label="Arguments")
        self.G.add_edge(node_uid, args_uid)

        for n in args:
            self.G.add_edge(args_uid, n)

        return node_uid

    @visit.register
    def _(self, node: ClassDef):
        """Visits ClassDef nodes. We visit all fields and functions
        of the class definition, and connect them to this node.
        This node's UID is returned."""
        # TODO: Where should bases field be used?
        funcs = []
        fields = []
        if len(node.funcs) > 0:
            funcs = self.visit_list(node.funcs)
        if len(node.fields) > 0:
            fields = self.visit_list(node.fields)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="Class: " + node.name)

        # Add attributes to the graph
        attr_uid = uuid.uuid4()
        self.G.add_node(attr_uid, label="Attributes")
        self.G.add_edge(node_uid, attr_uid)
        for n in fields:
            self.G.add_edge(attr_uid, n)

        # Add functions to the graph
        funcs_uid = uuid.uuid4()
        self.G.add_node(funcs_uid, label="Functions")
        self.G.add_edge(node_uid, funcs_uid)
        for n in funcs:
            self.G.add_edge(funcs_uid, n)

        return node_uid

    @visit.register
    def _(self, node: Dict):
        """Visits Dictionary nodes. We visit all the keys and values of
        this dictionary and then they're added to this node. Right now
        they're just added by adding keys and then values.
        This node's UID is returned."""
        keys = []
        values = []
        if len(node.keys) > 0:
            keys = self.visit_list(node.keys)
        if len(node.values) > 0:
            values = self.visit_list(node.values)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="Dict")

        for n in keys + values:
            self.G.add_edges(node_uid, n)

        return node_uid

    @visit.register
    def _(self, node: Expr):
        """Visits expression nodes. The node's actual expression is visited
        and added to this node. This node's UID is returned."""
        expr = self.visit(node.expr)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="Expression")
        self.G.add_edge(node_uid, expr)

        return node_uid

    @visit.register
    def _(self, node: FunctionDef):
        """Visits FunctionDef nodes. We visit all the arguments, and then
        we visit the function's statements. They're then added to the graph.
        This node's UID is returned."""
        args = []
        body = []
        if len(node.func_args) > 0:
            args = self.visit_list(node.func_args)
        if len(node.body) > 0:
            body = self.visit_list(node.body)

        node_uid = uuid.uuid4()
        args_node = uuid.uuid4()
        body_node = uuid.uuid4()

        self.G.add_node(node_uid, label="Function: " + node.name)
        self.G.add_node(args_node, label="Arguments")
        self.G.add_node(body_node, label="Body")

        self.G.add_edge(node_uid, body_node)
        self.G.add_edge(node_uid, args_node)
        for n in args:
            self.G.add_edge(args_node, n)

        for n in body:
            self.G.add_edge(body_node, n)

        return node_uid

    @visit.register
    def _(self, node: List):
        """Visits List nodes. We visit all the elements and add them to
        this node. This node's UID is returned."""
        values = []
        if len(node.values) > 0:
            values = self.visit_list(node.values)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="List")
        for n in values:
            self.G.add_edge(node_uid, n)

        return node_uid

    @visit.register
    def _(self, node: Loop):
        """Visits Loop nodes. We visit the conditional expression and the
        body of the loop, and connect them to this node in the graph.
        This node's UID is returned."""
        expr = self.visit(node.expr)
        body = []
        if len(node.body) > 0:
            body = self.visit_list(node.body)
        node_uid = uuid.uuid4()
        test_uid = uuid.uuid4()
        body_uid = uuid.uuid4()

        self.G.add_node(node_uid, label="Loop")
        self.G.add_node(test_uid, label="Test")
        self.G.add_node(body_uid, label="Body")

        self.G.add_edge(node_uid, test_uid)
        self.G.add_edge(test_uid, expr)
        self.G.add_edge(node_uid, body_uid)
        for n in body:
            self.G.add_edge(body_uid, n)

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
        orelse = []
        if len(node.body) > 0:
            body = self.visit_list(node.body)
        if node.orelse is not None:
            orelse = self.visit_list(node.orelse)

        node_uid = uuid.uuid4()
        test_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="If")
        self.G.add_node(test_uid, label="Test")
        self.G.add_edge(node_uid, test_uid)
        self.G.add_edge(test_uid, expr)

        body_uid = uuid.uuid4()
        orelse_uid = uuid.uuid4()

        # TODO: Handle strings of If/Elif/Elif/... constructs
        self.G.add_node(body_uid, label="If Body")
        self.G.add_node(orelse_uid, label="Else Body")

        self.G.add_edge(node_uid, body_uid)
        self.G.add_edge(node_uid, orelse_uid)

        for n in body:
            self.G.add_edge(body_uid, n)

        for n in orelse:
            self.G.add_edge(orelse_uid, n)

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
        program_uuid = uuid.uuid4()
        self.G.add_node(program_uuid, label="Program: " + node.name)

        module_uuid = uuid.uuid4()
        self.G.add_node(module_uuid, label="Module: " + node.name)
        self.G.add_edge(program_uuid, module_uuid)

        body = self.visit_list(node.body)
        for b in body:
            self.G.add_edge(module_uuid, b)

        return program_uuid

    @visit.register
    def _(self, node: Name):
        """Visits a Name node. We check to see if this Name node
        belongs to a class. In which case it's being called as an
        init(), and add this node's name to the graph accordingly,
        and return the UID of this node."""
        node_uid = uuid.uuid4()

        class_init = False
        for n in self.cast.nodes[0].body:
            if type(n) == ClassDef and n.name == node.name:
                class_init = True
                self.G.add_node(node_uid, label=node.name + " Init()")
                break

        if not class_init:
            self.G.add_node(node_uid, label=node.name)

        return node_uid

    @visit.register
    def _(self, node: Number):
        """Visits a Number node. We add this node's numeric value to the
        graph and return the UID of this node."""
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label=node.number)
        return node_uid

    @visit.register
    def _(self, node: Set):
        """Visits a Set node. We add all the elements of this set (if any)
        to the graph and return the UID of this node."""
        values = []
        if len(node.values) > 0:
            values = self.visit_list(node.values)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="Set")
        for n in values:
            self.G.add_edge(node_uid, n)

        return node_uid

    @visit.register
    def _(self, node: String):
        """Visits a String node. We add this node's string to the
        graph and return the UID of this node."""
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label=f'"{node.string}"')
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
        if len(node.values) > 0:
            values = self.visit_list(node.values)
        node_uid = uuid.uuid4()
        self.G.add_node(node_uid, label="Tuple")
        for n in values:
            self.G.add_edge(node_uid, n)

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
