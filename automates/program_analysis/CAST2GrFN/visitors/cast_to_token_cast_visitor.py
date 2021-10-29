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


class CASTTypeError(TypeError):
    """Used to create errors in the visitor, in particular
    when the visitor encounters some value that it wasn't expecting.

    Args:
        Exception: An exception that occurred during execution.
    """
    pass


class CASTToTokenCASTVisitor(CASTVisitor):
    """class CASTToTokenCASTVisitor - A visitor that traverses
    CAST nodes to generate a compact, tokenized version of the CAST (token CAST)
    that can then be used as input to a training model. The main purpose is to have
    a smaller structure that can be easily used as input. The actual tokenization is just
    a giant string composed of lisp-like expressions (i.e. parenthesized s-expressions) like
        "(add 1 2)"

    The visitors use a depth-first traversal to generate the tokenized CAST
    and they follow a general pattern of:
        - Visiting the node's children to generate their tokenized CAST
        - Adding the current node's tokenized CAST information along with their children
          to create the token CAST for this node (as a string) and return it.
    
    A couple of maps are generated while visiting the CAST and are 
    used to store information about the values and variables in the CAST.
    This is to make the tokenized CAST simpler, so the model training is less complicated,
    and in a later step the maps will be used to map the information back into the token CAST
    as necessary.

    Inherits from CASTVisitor to use its visit functions.

    Attributes:
        cast (CAST): The CAST object representation of the program
                     we're generating a DiGraph for.
        var_map (list): A list that serves as a mapping between variable names and their mapped 
                     identifier
        val_map (list): A list that serves as a mapping between literal values and their mapped
                     identifier
    """
    cast: CAST
    var_map: list
    val_map: list

    def __init__(self, cast: CAST):
        self.cast = cast
        self.var_map = []
        self.val_map = []

    def tokenize(self, file_name):
        """Visits the portion of the CAST that contains the main body of
        the program to generate a tokenized CAST string.
        After the token CAST string is generated, it's written out alongside
        the variable and value maps."""
        main_body = self.cast.nodes[0].body[-1]
        token_string = self.visit(main_body)

        variable_map = self.dump_var_map()
        value_map = self.dump_val_map()

        out_file = open(file_name, "w")
        out_file.write(f"{token_string}\n")

        for var in variable_map:
            out_file.write(f"{var}\n")

        for val in value_map:
            out_file.write(f"{val}\n")


    def dump_var_map(self):
        """Dumps out the map of the variables."""
        vars = []
        vars.append("--------- VARIABLES ---------")
        for var in self.var_map:
            vars.append(var)

        return vars

    def dump_val_map(self):
        """Dumps out the map of the values."""
        vals = []
        vals.append("--------- VALUES ---------")
        for val in self.val_map:
            vals.append(val)

        return vals

    @singledispatchmethod
    def visit(self, node: AstNode):
        """Generic visitor for unimplemented/unexpected nodes"""
        raise CASTTypeError(f"Unrecognized node type: {type(node)}")

    @visit.register
    def _(self, node: Assignment):
        """Visits Assignment nodes, the left and right nodes are visited
        and their generated token CASTs are used to generate this Assignment 
        node's token CAST."""

        # This check allows us to ignore the initialization nodes
        # in the CAST 'i.e. x0 = -1'
        if node.source_refs == None:
            if type(node.left) == Var:
                if type(node.right) == Number and node.right.number == -1:
                    return ""

        left = self.visit(node.left)
        right = self.visit(node.right)

        to_ret = f"( assign {left} {right} )"
        return to_ret

    @visit.register
    def _(self, node: Attribute):
        """TODO
        """
        return ""

    @visit.register
    def _(self, node: BinaryOp):
        """Visits BinaryOp nodes, we visit the left and right nodes, and then
        generate the token CAST string."""
        left = self.visit(node.left)
        right = self.visit(node.right)

        return f"( {node.op} {left} {right} )"

    @visit.register
    def _(self, node: Boolean):
        """TODO
        """
        return ""

    @visit.register
    def _(self, node: Call):
        """Visits Call (function call) nodes. We check to see
        if we have arguments to the node and generate their tokenized CAST strings.
        Appending all the arguments of the function to this node,
        if we have any. Then we create a string of the arguments and 
        generate a token CAST string."""

        args = []
        for n in node.arguments:
            args.append(self.visit(n))

        func_args = " ".join(args)

        return f"( call {node.func.name} {func_args} )"

    @visit.register
    def _(self, node: ClassDef):
        """TODO
        """
        return ""

    @visit.register
    def _(self, node: Dict):
        """TODO
        """
        return ""

    @visit.register
    def _(self, node: Expr):
        """TODO
        """
        return ""

    @visit.register
    def _(self, node: FunctionDef):
        """Visits FunctionDef nodes. We visit all the arguments, and then
        we visit the function's statements. Their token CAST strings are generated
        and then used to generate this FunctionDef's token CAST string."""
        body_nodes = []
        for n in node.body:
            curr_piece = self.visit(n)
            if len(curr_piece) > 0:
                body_nodes.append(curr_piece)

        func_body = " ".join(body_nodes)

        return f"( {node.name} {func_body} )"

    @visit.register
    def _(self, node: List):
        """TODO
        """
        return ""

    @visit.register
    def _(self, node: Loop):
        """TODO
        """
        return ""

    @visit.register
    def _(self, node: ModelBreak):
        """TODO
        """
        return ""

    @visit.register
    def _(self, node: ModelContinue):
        """TODO
        """
        return ""

    @visit.register
    def _(self, node: ModelIf):
        """TODO
        """
        return ""

    @visit.register
    def _(self, node: ModelReturn):
        """Visits a ModelReturn (return statment) node. The 
        value of the return is visited, and we use its token CAST
        to generate the return's token CAST string."""
        val = self.visit(node.value)
        return f"( return {val} )"

    @visit.register
    def _(self, node: Module):
        """TODO
        """
        return ""

    @visit.register
    def _(self, node: Name):
        """Visits a Name node. As of now, the name nodes belong
        to variables, so we check to see if the variable is in the 
        variable map and return a variable identifier accordingly."""
        if node.name not in self.var_map:
            self.var_map.append(node.name)

        idx = self.var_map.index(node.name)

        return f"Var{idx}"

    @visit.register
    def _(self, node: Number):
        """Visits a Number node. The node's numeric value is stored in the
        value map and a value identifier returned as a token CAST."""
        if node.number not in self.val_map:
            self.val_map.append(node.number)

        idx = self.val_map.index(node.number)

        return f"Val{idx}"

    @visit.register
    def _(self, node: Set):
        """TODO
        """
        return ""

    @visit.register
    def _(self, node: String):
        """Visits a String node. The string is edited to remove the null terminator
        and is then stored in the value map. A value identifier for the map is returned
        for the token CAST string."""
        stripped_str = repr(node.string.replace('\0',''))
        if stripped_str not in self.val_map:
            self.val_map.append(stripped_str)

        idx = self.val_map.index(stripped_str)
        return f"Val{idx}"

    @visit.register
    def _(self, node: Subscript):
        """TODO
        """
        return ""

    @visit.register
    def _(self, node: Tuple):
        """TODO
        """
        return ""

    @visit.register
    def _(self, node: UnaryOp):
        """TODO
        """
        return ""

    @visit.register
    def _(self, node: Var):
        """Visits a Var node by visiting its value
        The variable name gets stored in the map, and a 
        variable identifier is returned for the token CAST string."""
        if node.val.name not in self.var_map:
            self.var_map.append(node.val.name)

        idx = self.var_map.index(node.val.name)
        return f"Var{idx}"
