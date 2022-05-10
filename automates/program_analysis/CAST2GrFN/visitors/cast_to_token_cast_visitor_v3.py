import networkx as nx
import sys

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


class CASTToTokenCASTVisitorV3(CASTVisitor):
    """class CASTToTokenCASTVisitorV3 - A visitor that traverses
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

    def __init__(self, cast: CAST):
        self.cast = cast
        self.filename = ""
        self.func_map_ctr = 0
        self.global_map_ctr = 0
        self.func_map = {}
        self.global_map = {} 
        self.global_value_map = {}

        # Gets reset per function
        self.param_map_ctr = 0
        self.param_map = {}        
        self.visit_params = True

        self.var_map_ctr = 0
        self.var_map = {}

        self.val_map_ctr = 0
        self.val_map = {}

        self.local_map = {}

    def reset_local_maps(self):
        self.param_map = {}
        self.param_map_ctr = 0
        self.visit_params = True

        self.var_map_ctr = 0
        self.var_map = {}

        self.val_map_ctr = 0
        self.val_map = {}
        
        self.local_map = {}

    def insert_param(self, param_name: str):
        self.param_map[param_name] = f"_p{self.param_map_ctr}"
        self.local_map[param_name] = self.param_map[param_name]
        self.param_map_ctr += 1

    def insert_var(self, var_name: str):
        self.var_map[var_name] = f"_v{self.var_map_ctr}"
        self.local_map[var_name] = self.var_map[var_name]
        self.var_map_ctr += 1

    def insert_val(self, val_name: str):
        self.val_map[val_name] = f"_val{self.val_map_ctr}"
        self.val_map_ctr += 1

    def populate_global_maps(self):
        """Populates the global variable and function name maps

        Args:
            cast (CAST): _description_
        """
        cast_nodes = self.cast.nodes[0].body

        for node in cast_nodes: 
            if isinstance(node, Assignment):
                # TODO: We're assuming the left child is a name node for now
                # but we could have an attribute, or a subscript, or something else
                node_left = node.left
                assert isinstance(node_left.val, Name)
                node_left_val = node_left.val
                if node_left.source_refs[0].source_file_name == self.filename:
                    # TODO: We might need the actual ID from the name field in the future
                    self.global_map[node_left_val.name] = f"_g{self.global_map_ctr}"

                    node_right = node.right
                    self.global_value_map[node_left_val.name] = node_right.number 
                    self.global_map_ctr += 1
                
            elif isinstance(node, FunctionDef):
                if node.source_refs[0].source_file_name == self.filename:
                    self.func_map[node.name] =  f"_f{self.func_map_ctr}"
                    self.func_map_ctr += 1

    def dump_function_token_map(self):
        funcs = ["function_tokens_map"]
        for (func_name, fn_token) in self.func_map.items():
            funcs.append(f"{fn_token}:{func_name}")

        return funcs

    def dump_global_tokens_map(self):
        globals = ["global_tokens_map"]
        for (global_var_name,global_token) in self.global_map.items():
            global_val = self.global_value_map[global_var_name] if global_var_name in self.global_value_map.keys() else None
            if global_val is not None:
                globals.append(f"{global_token}:{global_var_name} = {global_val}")
            else:
                globals.append(f"{global_token}:{global_var_name}")

        return globals

    def dump_local_maps(self):
        # TODO: Function parameter map
        params = ["parameter_tokens_map"]
        for (param_name, param_token) in self.param_map.items():
            params.append(f"{param_token}:{param_name}")

        vars = ["variable_tokens_map"]
        for (var_name, var_token) in self.var_map.items():
            vars.append(f"{var_token}:{var_name}")

        vals = ["value_tokens_map"]
        for (val_name, val_token) in self.val_map.items():
            vals.append(f"{val_token}:{val_name}")

        return (params,vars,vals)


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

    def tokenize(self, file_name):
        """Visits the portion of the CAST that contains the main body of
        the program to generate a tokenized CAST string.
        After the token CAST string is generated, it's written out alongside
        the variable and value maps."""
        main_body = self.cast.nodes[0].body[-1]

        # TODO: make this work for Python files also at a later time
        self.filename = f"{str(self.cast.nodes[0].name)}.c"
        self.populate_global_maps()       


        for tok in self.dump_global_tokens_map():
            print(tok)

        print()
        print()

        for tok in self.dump_function_token_map():
            print(tok)

        print()
        print()
        
        token_string = ""
        self.reset_local_maps()

        
        # TODO: In the future, change this for programs with multiple modules
        for node in self.cast.nodes[0].body:
            if isinstance(node, FunctionDef) and node.source_refs[0].source_file_name == self.filename:
                token_string = self.visit(node)
                print(token_string)
                (params, local_vars, local_vals) = self.dump_local_maps()

                print()

                for tok in params:
                    print(tok)

                print()

                for tok in local_vars:
                    print(tok)

                print()

                for tok in local_vals:
                    print(tok)

                token_string = ""
                self.reset_local_maps()
                
                print()
                print()


        sys.exit()
        
        
       # assert False

#        variable_map = self.dump_var_map()
 #       value_map = self.dump_val_map()

#        out_file = open(file_name, "w")
 #       out_file.write(f"{token_string}\n")

#        for var in variable_map:
 #           out_file.write(f"{var}\n")

#        for val in value_map:
#            out_file.write(f"{val}\n")


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

        if node.func.name in ["sqrt", "sin", "abs", "fmin", "fmax"]:
            return f"( call {node.func.name} {func_args} )"
        else:
            return f"( call {self.func_map[node.func.name]} {func_args} )"

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
        
        arg_nodes = []
        for n in node.func_args:
            curr_piece = self.visit(n)
            arg_nodes.append(curr_piece)

        args = " ".join(arg_nodes)

        self.visit_params = False

        body_nodes = []
        for n in node.body:
            curr_piece = self.visit(n)
            if len(curr_piece) > 0:
                body_nodes.append(curr_piece)

        func_body = " ".join(body_nodes)

        return f"function_name: {node.name}\ntoken_sequence\n( {node.name} {args} {func_body} )"

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
        if node.name in self.global_map:
            return self.global_map[node.name]

        if node.name not in self.var_map:
            self.insert_var(node.name)

        return self.local_map[node.name]


    @visit.register
    def _(self, node: Number):
        """Visits a Number node. The node's numeric value is stored in the
        value map and a value identifier returned as a token CAST."""
        if node.number not in self.val_map:
            self.insert_val(node.number)

        return self.val_map[node.number]

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
        return f"val{idx}"

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
        
        # We look in the global map to see if this name exists there first
        if node.val.name in self.global_map:
            return f"{self.global_map[node.val.name]}"


        if self.visit_params:
            self.insert_param(node.val.name)
        else:
            # If it's not in the global map, then either it's been used before 
            # or is brand new and local to the function scope
            if node.val.name not in self.var_map:
                self.insert_var(node.val.name)

        return self.local_map[node.val.name]

