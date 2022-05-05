from typing import Type, Union
import ast
import os 
import copy
import sys
from functools import singledispatchmethod

from automates.utils.misc import uuid
from scripts.program_analysis.astpp import parseprint
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
    source_ref,
)


def merge_dicts(prev_scope, curr_scope):
    """merge_dicts
    Helper function to isolate the work of merging two dictionaries by merging
    key : value pairs from prev_scope into curr_scope
    The merging is done 'in_place'. That is, after the function is done, curr_scope
    is updated with any new key : value pairs that weren't in there before.

    Args:
        prev_scope (dict): Dictionary of name : ID pairs for variables in the enclosing scope 
        curr_scope (dict): Dictionary of name : ID pairs for variables in the current scope
    """
    for k in prev_scope.keys():
        if k not in curr_scope.keys():
            curr_scope[k] = prev_scope[k]

def construct_unique_name(attr_name, var_name):
    """Constructs strings in the form of 
    "attribute.var"
    where 'attribute' is either
        - the name of a module
        - an object    

    Returns:
        string: A string representing a unique name

    """
    return f"{attr_name}.{var_name}"


def get_node_name(ast_node):
    if isinstance(ast_node, ast.Assign):
        return ast_node[0].id
    elif isinstance(ast_node, ast.Attribute):
        return ""
    elif isinstance(ast_node, Assignment):
        if isinstance(ast_node.left, Subscript):
            return ast_node.left.value.name
        else:
            return ast_node.left.val.name
    elif isinstance(ast_node, Subscript):
        raise TypeError(f"Type {ast_node} not supported")
    else:
        raise TypeError(f"Type {type(ast_node)} not supported")


class PyASTToCAST():
    """Class PyASTToCast
    This class is used to convert a Python program into a CAST object.
    In particular, given a PyAST object that represents the Python program's
    Abstract Syntax Tree, we create a Common Abstract Syntax Tree
    representation of it. 
    Most of the functions involve visiting the children
    to generate their CAST, and then connecting them to their parent to form
    the parent node's CAST representation.
    The functions, in most cases, return lists containing their generated CAST.
    This is because in many scenarios (like in slicing) we need to return multiple
    values at once, since multiple CAST nodes gt generated. Returning lists allows us to
    do this, and as long as the visitors handle the data correctly, the CAST will be 
    properly generated.
    All the visitors retrieve line number information from the PyAST nodes, and
    include the information in their respective CAST nodes, with the exception
    of the Module CAST visitor. 

    This class inherits from ast.NodeVisitor, to allow us to use the Visitor
    design pattern to visit all the different kinds of PyAST nodes in a
    similar fashion.

    Current Fields:
        - Aliases
        - Visited
        - Filenames
        - Classes
        - Var_Count
        - global_identifier_dict
    """
    def __init__(self, file_name: str, legacy: Boolean = False):
        """Initializes any auxiliary data structures that are used 
           for generating CAST.
           The current data structures are:
           - aliases: A dictionary used to keep track of aliases that imports use
                     (like import x as y, or from x import y as z)
           - visited: A list used to keep track of which files have been imported
                     this is used to prevent an import cycle that could have no end
           - filenames: A list of strings used as a stack to maintain the current file being
                        visited
           - classes: A dictionary of class names and their associated functions.
           - var_count: An int used when CAST variables need to be generated (i.e. loop variables, etc)
           - global_identifier_dict: A dictionary used to map global variables to unique identifiers
           - legacy: A flag used to determine whether we generate old style CAST (uses strings for function def names)
                     or new style CAST (uses Name CAST nodes for function def names)
        """

        self.aliases = {}
        self.visited = set()
        self.filenames = [file_name.split(".")[0]]
        self.classes = {}
        self.var_count = 0
        self.global_identifier_dict = {}
        self.id_count = 0
        self.legacy = legacy


    def insert_next_id(self, scope_dict: Dict, dict_key: str):
        """ Given a scope_dictionary and a variable name as a key, 
        we insert a new key_value pair for the scope dictionary
        The ID that we inserted gets returned because some visitors
        need the ID for some additional work. In the cases where the returned
        ID isn't needed it gets ignored.

        Args:
            scope_dict (Dict): _description_
            dict_key (str): _description_
        """
        new_id_to_insert = self.id_count
        scope_dict[dict_key] = new_id_to_insert
        self.id_count += 1
        return new_id_to_insert

    def insert_alias(self, original: String, alias: String):
        """ Inserts an alias into a dictionary that keeps track of aliases for 
            names that are aliased. For example, the following import
            import numpy as np
            np is an alias for the original name numpy

        Args:
            original (String): The original name that is being aliased
            alias    (String): The alias of the original name
        """
        # TODO
        pass

    def check_alias(self, name: String):
        """ Given a python string that represents a name, 
            this function checks to see if that name is an alias
            for a different name, and returns it if it is indeed an alias.
            Otherwise, the original name is returned.
        """
        if name in self.aliases:
            return self.aliases[name]
        else:
            return name

    def identify_piece(self, piece: AstNode, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """This function is used to 'centralize' the handling of different node types
        in list/dictionary/set comprehensions.
        Take the following list comprehensions as examples
        L = [ele**2 for small_l in d         for ele in small_l]   -- comp1 
        L = [ele**2 for small_l in foo.bar() for ele in small_l]   -- comp2 
        L = [ele**2 for small_l in foo.baz   for ele in small_l]   -- comp3
               F1         F2        F3            F4      F5
        
        In these comprehensions F3 has a different type for its node
            - In comp1 it's a list
            - In comp2 it's an attribute of an object with a function call
            - In comp3 it's an attribute of an object without a function call    
        
        The code that handles comprehensions generates slightly different AST depending
        on what type these fields (F1 through F5) are, but this handling becomes very repetitive
        and difficult to maintain if it's written in the comprehension visitors. Thus, this method
        is to contain that handling in one place. This method acts on one field at a time, and thus will
        be called multiple times per comprehension as necessary.

        Args:
            piece (AstNode): The current Python AST node we're looking at, generally an individual field
                             of the list comprehension    
            prev_scope_id_dict (Dict): Scope dictionaries in case something needs to be accessed or changed
            curr_scope_id_dict (Dict): see above
        
        [ELT for TARGET in ITER]
          F1       F2      F3 
        F1 - doesn't need to be handled here because that's just code that is done somewhere else
        F2/F4 - commonly it's a Name or a Tuple node
        F3/F5 - generally a list, or something that gives back a list like:
                * a subscript          
                * an attribute of an object with or w/out a function call
        """
        if isinstance(piece, ast.Tuple): # for targets (generator.target)
            return piece
        elif isinstance(piece, ast.Name):
            ref = [self.filenames[-1], piece.col_offset, piece.end_col_offset, piece.lineno, piece.end_lineno]
            # return ast.Name(id=piece.id, ctx=ast.Store(), col_offset=None, end_col_offset=None, lineno=None, end_lineno=None)
            return ast.Name(id=piece.id, ctx=ast.Store(), col_offset=[1], end_col_offset=ref[2], lineno=ref[3], end_lineno=ref[4])
        elif isinstance(piece, ast.Subscript): # for iters (generator.iter)
            return piece.value
        elif isinstance(piece, ast.Call):
            return piece.func
        else:
            return piece



    @singledispatchmethod
    def visit(self, node: AstNode, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        pass

    @visit.register
    def visit_Assign(self, node: ast.Assign, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Assign node, and returns its CAST representation.
        Either the assignment is simple, like x = {expression},
        or the assignment is complex, like x = y = z = ... {expression}
        Which determines how we generate the CAST for this node.

        Args:
            node (ast.Assign): A PyAST Assignment node.

        Returns:
            Assignment: An assignment CAST node
        """

        left = []
        right = []

        if len(node.targets) == 1: # x = 1, or maybe x = y, in general x = {expression}
            l_visit = self.visit(node.targets[0], prev_scope_id_dict, curr_scope_id_dict)
            r_visit = self.visit(node.value, prev_scope_id_dict, curr_scope_id_dict)
            left.extend(l_visit)
            right.extend(r_visit)
        elif len(node.targets) > 1: # x = y = z = ... {Expression} (multiple expressions)
            left.extend(self.visit(node.targets[0], prev_scope_id_dict, curr_scope_id_dict))
            node.targets = node.targets[1:]
            right.extend(self.visit(node, prev_scope_id_dict, curr_scope_id_dict))
        else:
            raise ValueError(f"Unexpected number of targets for node: {len(node.targets)}")

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        
        if isinstance(node.value, ast.DictComp):
            to_ret = []
            to_ret.extend(right)
            to_ret.extend([Assignment(left[0], Name(name="dict__temp_",id=curr_scope_id_dict["dict__temp_"]), source_refs=ref)]) 
            return to_ret
        if isinstance(node.value, ast.ListComp):
            to_ret = []
            to_ret.extend(right)
            to_ret.extend([Assignment(left[0], Name(name="list__temp_",id=curr_scope_id_dict["list__temp_"]), source_refs=ref)]) 
            return to_ret
        else:
            return [Assignment(left[0], right[0], source_refs=ref)]

    @visit.register
    def visit_Attribute(self, node: ast.Attribute, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Attribute node, which is used when accessing
        the attribute of a class. Whether it's a field or method of a class.

        Args:
            node (ast.Attribute): A PyAST Attribute node

        Returns:
            Attribute: A CAST Attribute node representing an Attribute access
        """


        # TODO: aliasing

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]

        # node.value.id gets us module name (string)
        # node.attr gets us attribute we're accessing (string)
        # helper(node.attr) -> "module_name".node.attr
        
        curr = node.value
        
        print("---------------------------------")
        print(f"prev_scope:   {prev_scope_id_dict}")
        print(f"curr_scope:   {curr_scope_id_dict}")
        print(f"global_scope: {self.global_identifier_dict}")
        print("---------------------------------")
        


        # foo.bar.x, foo.bar().x, etc..
        # (multiple layers of attributes)
        if isinstance(curr, ast.Attribute):
            # Construct the name that corresponds to this attribute
            # that is, x.y.z.w, w is the attribute and x.y.z is the name
            temp = curr
            name_list = []
            while isinstance(temp, ast.Attribute):
                name_list.insert(0,temp.attr)
                temp = temp.value       
            if isinstance(temp, ast.Name):
                name_list.insert(0, temp.id)

            unique_name = ".".join(name_list)

            if isinstance(curr.ctx,ast.Load):
                if unique_name not in curr_scope_id_dict:
                    if unique_name in prev_scope_id_dict:
                        curr_scope_id_dict[unique_name] = prev_scope_id_dict[unique_name]
                    else:
                        if unique_name not in self.global_identifier_dict:
                            self.insert_next_id(self.global_identifier_dict, unique_name)
                        curr_scope_id_dict[unique_name] = self.global_identifier_dict[unique_name]
                
            if isinstance(curr.ctx,ast.Store):
                if unique_name not in curr_scope_id_dict:
                    if unique_name in prev_scope_id_dict:
                        curr_scope_id_dict[unique_name] = prev_scope_id_dict[unique_name]
                    else:
                        self.insert_next_id(curr_scope_id_dict, unique_name)


        # foo.x, foo.bar(), etc...
        # (one single layer of attribute)
        elif isinstance(curr, ast.Name):
            unique_name = construct_unique_name(curr.id, node.attr)
        
            if isinstance(curr.ctx,ast.Load):
                if unique_name not in curr_scope_id_dict:
                    if unique_name in prev_scope_id_dict:
                        curr_scope_id_dict[unique_name] = prev_scope_id_dict[unique_name]
                    else:
                        if unique_name not in self.global_identifier_dict: # added for random.seed not exising, and other modules like that. in other words for functions in modules that we don't have visibility for. 
                            self.insert_next_id(self.global_identifier_dict, unique_name)
                        curr_scope_id_dict[unique_name] = self.global_identifier_dict[unique_name]
                
            if isinstance(curr.ctx,ast.Store):
                if unique_name not in curr_scope_id_dict:
                    if unique_name in prev_scope_id_dict:
                        curr_scope_id_dict[unique_name] = prev_scope_id_dict[unique_name]
                    else:
                        self.insert_next_id(curr_scope_id_dict, unique_name)

        elif isinstance(curr, ast.Subscript):
            curr_value = curr.value
            while isinstance(curr_value, ast.Subscript):
                curr_value = curr_value.value
            
            if isinstance(curr_value, ast.Name):
                unique_name = construct_unique_name(curr_value.id, node.attr)

                if isinstance(curr.ctx,ast.Load):
                    if unique_name not in curr_scope_id_dict:
                        if unique_name in prev_scope_id_dict:
                            curr_scope_id_dict[unique_name] = prev_scope_id_dict[unique_name]
                        else:
                            if unique_name not in self.global_identifier_dict: # added for random.seed not exising, and other modules like that. in other words for functions in modules that we don't have visibility for. 
                                self.insert_next_id(self.global_identifier_dict, unique_name)
                            curr_scope_id_dict[unique_name] = self.global_identifier_dict[unique_name]
                    
                if isinstance(curr.ctx,ast.Store):
                    if unique_name not in curr_scope_id_dict:
                        if unique_name in prev_scope_id_dict:
                            curr_scope_id_dict[unique_name] = prev_scope_id_dict[unique_name]
                        else:
                            self.insert_next_id(curr_scope_id_dict, unique_name)
            else:
                raise NotImplementedError(f"Node type: {type(node)} with value {type(curr_value)} not recognized")

        elif isinstance(curr, ast.Constant):
            unique_name = construct_unique_name(curr.value, node.attr)
            if isinstance(node.ctx,ast.Load):
                if unique_name not in curr_scope_id_dict:
                    if unique_name in prev_scope_id_dict:
                        curr_scope_id_dict[unique_name] = prev_scope_id_dict[unique_name]
                    else:
                        if unique_name not in self.global_identifier_dict: # added for random.seed not exising, and other modules like that. in other words for functions in modules that we don't have visibility for. 
                            self.insert_next_id(self.global_identifier_dict, unique_name)
                        curr_scope_id_dict[unique_name] = self.global_identifier_dict[unique_name]
                
            if isinstance(node.ctx,ast.Store):
                if unique_name not in curr_scope_id_dict:
                    if unique_name in prev_scope_id_dict:
                        curr_scope_id_dict[unique_name] = prev_scope_id_dict[unique_name]
                    else:
                        self.insert_next_id(curr_scope_id_dict, unique_name)
        else:
            raise NotImplementedError(f"Node type: {type(curr)}")

        value = self.visit(node.value, prev_scope_id_dict, curr_scope_id_dict)
        
        attr = Name(node.attr, id=curr_scope_id_dict[unique_name], source_refs=ref)

        # module_name : has an ID
        # attr to a module: has an ID
        # don't do just 'y', do 'module_name.y' <- whats its ID? I think it's the attr's ID

        return [Attribute(value[0], attr, source_refs=ref)]
                        # module2   y (really module2.y)

    @visit.register
    def visit_AugAssign(self, node:ast.AugAssign, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST AugAssign node, which is used for an
        augmented assignment, like x += 1. AugAssign node is converted
        to a regular PyAST Assign node and passed to that visitor to 
        generate CAST.

        Args:
            node (ast.AugAssign): A PyAST AugAssign node

        Returns:
            Assign: A CAST Assign node, generated by the Assign visitor.
        """

        # Convert AugAssign to regular Assign, and visit 
        target = node.target
        value = node.value

        if isinstance(target,ast.Attribute):
            convert = ast.Assign(
                targets=[target], 
                value=ast.BinOp(left=target,
                                op=node.op,
                                right=value,
                                col_offset=node.col_offset,
                                end_col_offset=node.end_col_offset,
                                lineno=node.lineno,
                                end_lineno=node.end_lineno
                                ),
                col_offset=node.col_offset,
                end_col_offset=node.end_col_offset,
                lineno=node.lineno,
                end_lineno=node.end_lineno
                                )
        elif isinstance(target,ast.Subscript): 
            convert = ast.Assign(
                targets=[target], 
                value=ast.BinOp(left=target,
                                ctx=ast.Load(),
                                op=node.op,
                                right=value,
                                col_offset=node.col_offset,
                                end_col_offset=node.end_col_offset,
                                lineno=node.lineno,
                                end_lineno=node.end_lineno
                                ),
                col_offset=node.col_offset,
                end_col_offset=node.end_col_offset,
                lineno=node.lineno,
                end_lineno=node.end_lineno
                                )
        else:
            convert = ast.Assign(
                targets=[target], 
                value=ast.BinOp(left=ast.Name(target.id,ctx=ast.Load(),
                                                col_offset=node.col_offset,
                                                end_col_offset=node.end_col_offset,
                                                lineno=node.lineno,
                                                end_lineno=node.end_lineno
                                ),
                                op=node.op,
                                right=value,
                                col_offset=node.col_offset,
                                end_col_offset=node.end_col_offset,
                                lineno=node.lineno,
                                end_lineno=node.end_lineno
                                ),
                col_offset=node.col_offset,
                end_col_offset=node.end_col_offset,
                lineno=node.lineno,
                end_lineno=node.end_lineno
                                )


        return self.visit(convert, prev_scope_id_dict, curr_scope_id_dict)


    @visit.register
    def visit_BinOp(self, node: ast.BinOp, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST BinOp node, which consists of all the arithmetic
        and bitwise operators.

        Args:
            node (ast.BinOp): A PyAST Binary operator node

        Returns:
            BinaryOp: A CAST binary operator node representing a math
                      operation (arithmetic or bitwise)
        """

        ops = {
            ast.Add: BinaryOperator.ADD,
            ast.Sub: BinaryOperator.SUB,
            ast.Mult: BinaryOperator.MULT,
            ast.Div: BinaryOperator.DIV,
            ast.FloorDiv: BinaryOperator.FLOORDIV,
            ast.Mod: BinaryOperator.MOD,
            ast.Pow: BinaryOperator.POW,
            ast.LShift: BinaryOperator.LSHIFT,
            ast.RShift: BinaryOperator.RSHIFT,
            ast.BitOr: BinaryOperator.BITOR,
            ast.BitAnd: BinaryOperator.BITAND,
            ast.BitXor: BinaryOperator.BITXOR,
        }
        left = self.visit(node.left, prev_scope_id_dict, curr_scope_id_dict)
        op = ops[type(node.op)]
        right = self.visit(node.right, prev_scope_id_dict, curr_scope_id_dict)

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        leftb = []
        rightb = []

        if len(left) > 1:
            leftb = left[0:-1]
        if len(right) > 1:
            rightb = right[0:-1]

        return leftb + rightb + [BinaryOp(op, left[-1], right[-1], source_refs=ref)]

    @visit.register
    def visit_Break(self, node: ast.Break, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Break node, which is just a break statement
           nothing to be done for a Break node, just return a ModelBreak()
           object

        Args:
            node (ast.Break): An AST Break node

        Returns:
            ModelBreak: A CAST Break node

        """

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        return [ModelBreak(source_refs=ref)]

    @visit.register
    def visit_BoolOp(self, node: ast.BoolOp, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a BoolOp node, which is a boolean operation connected with 'and'/'or's 
           The BoolOp node gets converted into an AST Compare node, and then the work is 
           passed off to it.

        Args:
            node (ast.BoolOp): An AST BoolOp node

        Returns: 
            BinaryOp: A BinaryOp node that is composed of operations connected with 'and'/'or's 

        """
        op = node.op
        vals = node.values
        bool_ops = [node.op for i in range(len(vals)-1)]
        ref = [self.filenames[-1], node.col_offset, node.end_col_offset, node.lineno, node.end_lineno]

        compare_op = ast.Compare(left=vals[0], ops=bool_ops, comparators=vals[1:], col_offset=node.col_offset, end_col_offset=node.end_col_offset, lineno=node.lineno, end_lineno=node.end_lineno)
        return self.visit(compare_op, prev_scope_id_dict, curr_scope_id_dict) 

    @visit.register
    def visit_Call(self, node: ast.Call, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Call node, which represents a function call.
        Special care must be taken to see if it's a function call or a class's
        method call. The CAST is generated a little different depending on
        what kind of call it is. 

        Args:
            node (ast.Call): a PyAST Call node

        Returns:
            Call: A CAST function call node
        """

        args = []
        func_args = []
        kw_args = []
        if len(node.args) > 0:
            for arg in node.args:
                func_args.extend(self.visit(arg, prev_scope_id_dict, curr_scope_id_dict))

        # g(3,id=4) TODO: Think more about this 
        if len(node.keywords) > 0:
            for arg in node.keywords:
                kw_args.extend(self.visit(arg.value, prev_scope_id_dict, curr_scope_id_dict))

        args = func_args + kw_args

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        if isinstance(node.func,ast.Attribute):
            res = self.visit(node.func, prev_scope_id_dict, curr_scope_id_dict)
            return [Call(res[0], args, source_refs=ref)]
        else:
            # In the case we're calling a function that doesn't have an identifier already
            # This should only be the case for built-in python functions (i.e print, len, etc...)
            # Otherwise it would be an error to call a function before it is defined
            # (An ID would exist for a user-defined function here even if it isn't visited yet because of deferment)
            unique_name = construct_unique_name(self.filenames[-1], node.func.id)
            if unique_name not in prev_scope_id_dict.keys():

                # If a built-in is called, then it gets added to the global dictionary if
                # it hasn't been called before. This is to maintain one consistent ID per built-in 
                # function
                if unique_name not in self.global_identifier_dict.keys():
                    self.insert_next_id(self.global_identifier_dict, unique_name)

                prev_scope_id_dict[unique_name] = self.global_identifier_dict[unique_name]

            return [Call(Name(node.func.id, id=prev_scope_id_dict[unique_name], source_refs=ref), args, source_refs=ref)]

    @visit.register
    def visit_ClassDef(self, node: ast.ClassDef, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST ClassDef node, which is used to define user classes.
        Acquiring the fields of the class involves going through the __init__
        function and seeing if the attributes are associated with the self
        parameter. In addition, we add to the 'classes' dictionary the name of 
        the class and a list of all its functions.

        Args:
            node (ast.ClassDef): A PyAST class definition node

        Returns:
            ClassDef: A CAST class definition node
        """

        name = node.name
        self.classes[name] = []

        bases = []
        for base in node.bases:
            bases.extend(self.visit(base, prev_scope_id_dict))
        
        funcs = []
        for func in node.body:
            funcs.extend(self.visit(func, prev_scope_id_dict))
            if isinstance(func,ast.FunctionDef):
                self.classes[name].append(func.name)
        
        fields = []

        # Get the fields in the class
        init_func = None
        for f in node.body:
            if isinstance(f,ast.FunctionDef) and f.name == "__init__":
                init_func = f.body
                break

        for func_node in init_func:
            if isinstance(func_node,ast.Assign) and isinstance(func_node.targets[0],ast.Attribute):
                attr_node = func_node.targets[0]
                if attr_node.value.id == "self":
                    ref = [SourceRef(source_file_name=self.filenames[-1], col_start=attr_node.col_offset, col_end=attr_node.end_col_offset, row_start=attr_node.lineno, row_end=attr_node.end_lineno)]
                    # Need IDs for name, which one?
                    fields.append(Var(Name(attr_node.attr, id=-1,source_refs=ref), "float", source_refs=ref))

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        return [ClassDef(name, bases, funcs, fields, source_refs=ref)]

    @visit.register
    def visit_Compare(self, node: ast.Compare, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Compare node, which consists of boolean operations

        Args:
            node (ast.Compare): A PyAST Compare node

        Returns:
            BinaryOp: A BinaryOp node, which in this case will hold a boolean
            operation
        """

        ops = {
            ast.And: BinaryOperator.AND,
            ast.Or: BinaryOperator.OR,
            ast.Eq: BinaryOperator.EQ,
            ast.NotEq: BinaryOperator.NOTEQ,
            ast.Lt: BinaryOperator.LT,
            ast.LtE: BinaryOperator.LTE,
            ast.Gt: BinaryOperator.GT,
            ast.GtE: BinaryOperator.GTE,
            ast.In: BinaryOperator.IN,
            ast.NotIn: BinaryOperator.NOTIN,
        }

        # Fetch the first element (which is in left)
        left = node.left

        # Grab the first comparison operation
        op = ops[type(node.ops.pop())]
        
        # If we have more than one operand left, then we 'recurse' without the leftmost
        # operand and the first operator
        if len(node.comparators) > 1:
            node.left = node.comparators.pop()
            right = node
        else:
            right = node.comparators[0]

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        l = self.visit(left, prev_scope_id_dict, curr_scope_id_dict)
        r = self.visit(right, prev_scope_id_dict, curr_scope_id_dict)
        return [BinaryOp(op, l[0], r[0], source_refs=ref)]

    @visit.register
    def visit_Constant(self, node: ast.Constant, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Constant node, which can hold either numeric or
        string values. A dictionary is used to index into which operation
        we're doing.

        Args:
            node (ast.Constant): A PyAST Constant node

        Returns:
            Number: A CAST numeric node, if the node's value is an int or float
            String: A CAST string node, if the node's value is a string
            Boolean: A CAST boolean node, if the node's value is a boolean

        Raises:
            TypeError: If the node's value is something else that isn't
                       recognized by the other two cases
        """

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        if isinstance(node.value,(int,float)):
            return [Number(node.value,source_refs=ref)]
        elif isinstance(node.value,str):
            return [String(node.value,source_refs=ref)]
        elif isinstance(node.value,bool):
            return [Boolean(node.value,source_refs=ref)]
        elif node.value is None:
            return [Number(None,source_refs=ref)]
        else:
            raise TypeError(f"Type {node.value} not supported")

    @visit.register
    def visit_Continue(self, node: ast.Continue, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Continue node, which is just a continue statement
           nothing to be done for a Continue node, just return a ModelContinue node

        Args:
            node (ast.Continue): An AST Continue node

        Returns:
            ModelContinue: A CAST Continue node
        """

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        return [ModelContinue(source_refs=ref)]

    @visit.register
    def visit_Dict(self, node: ast.Dict, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Dict node, which represents a dictionary.

        Args:
            node (ast.Dict): A PyAST dictionary node

        Returns:
            Dict: A CAST Dictionary node.
        """

        keys = []
        values = []
        if len(node.keys) > 0:
            for piece in node.keys:
                keys.extend(self.visit(piece, prev_scope_id_dict, curr_scope_id_dict))

        if len(node.values) > 0:
            for piece in node.values:
                values.extend(self.visit(piece, prev_scope_id_dict, curr_scope_id_dict))

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        return [Dict(keys, values, source_refs=ref)]

    @visit.register
    def visit_Expr(self, node: ast.Expr, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Expr node, which represents some kind of standalone
        expression.

        Args:
            node (ast.Expr): A PyAST Expression node

        Returns:
            Expr:      A CAST Expression node
            [AstNode]: A list of AstNodes if the expression consists 
                       of more than one node
        """

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        val = self.visit(node.value, prev_scope_id_dict, curr_scope_id_dict)
        if len(val) > 1:
            return val
        return [Expr(val[0],source_refs=ref)]

    @visit.register
    def visit_For(self, node: ast.For, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST For node, which represents Python for loops.
        A For loop is different than a While loop, in that we need to do a
        conversion such that the resulting CAST Loop appropriately captures a
        node that is more like a While loop (i.e. using a condition to
        terminate the loop instead of iterating).

        Args:
            node (ast.For): A PyAST For loop node.

        Returns:
            Loop: A CAST loop node, which generically represents both For
                  loops and While loops.
        """

        
        target = self.visit(node.target, prev_scope_id_dict, curr_scope_id_dict)[0]
        iterable = self.visit(node.iter, prev_scope_id_dict, curr_scope_id_dict)[0]

        # The body of a loop contains its own scope (it can create variables only it can see and can use 
        # variables from its enclosing scope) so we copy the current scope and merge scopes
        # to create the enclosing scope for the loop body
        curr_scope_copy = copy.deepcopy(curr_scope_id_dict)
        merge_dicts(prev_scope_id_dict, curr_scope_id_dict)
        loop_scope_id_dict = {}

        # When we pass in scopes, we pass what's currently in the previous scope along with 
        # the curr scope which would consist of the loop variables (node.target) and the item
        # we loop over (iter) though the second one shouldn't ever be accessed
        body = []
        print(curr_scope_id_dict)
        for piece in (node.body + node.orelse):
            body.extend(self.visit(piece, curr_scope_id_dict, loop_scope_id_dict))
        print(loop_scope_id_dict)

        # Once we're out of the loop body we can copy the current scope back
        curr_scope_id_dict = copy.deepcopy(curr_scope_copy)

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        count_var_name = f"generated_index_{self.var_count}"
        list_name = f"generated_list_{self.var_count}"
        self.var_count += 1

        # TODO: Mark these as variables that were generated by this script at some point
        # (^ This was a really old request, not sure if it's still needed at this point)
        count_var_id = self.insert_next_id(curr_scope_id_dict, count_var_name)

        list_var_id = self.insert_next_id(curr_scope_id_dict, list_name)

        # Built-ins used: "list", "len"
        list_id = -1
        if "list" not in self.global_identifier_dict.keys():
            list_id = self.insert_next_id(self.global_identifier_dict, "list")
        else:
            list_id = self.global_identifier_dict["list"]

        len_id = -1
        if "len" not in self.global_identifier_dict.keys():
            len_id = self.insert_next_id(self.global_identifier_dict, "len")
        else:
            len_id = self.global_identifier_dict["len"]

        count_var = Assignment(Var(Name(name=count_var_name, id=count_var_id, source_refs=ref), "float", source_refs=ref), Number(0, source_refs=ref), source_refs=ref)
        list_var = Assignment(Var(Name(name=list_name, id=list_var_id, source_refs=ref), "list", source_refs=ref), 
                    Call(Name(name="list", id=list_id, source_refs=ref),[iterable],source_refs=ref), source_refs=ref)

        loop_cond = BinaryOp(
            BinaryOperator.LT,
            Name(name=count_var_name, id=count_var_id, source_refs=ref),
            Call(Name(name="len", id=len_id, source_refs=ref), [Name(name=list_name,id=list_var_id,source_refs=ref)], source_refs=ref),
            source_refs=ref
        )

        if isinstance(node.iter,ast.Call):   # For function calls like range(), list(), etc...
            if isinstance(node.target,ast.Tuple):
                loop_assign = [Assignment(
                    Tuple([Var(type="float",val=Name(name=f"{node.val.name}_",id=-1,source_refs=ref),source_refs=ref) for node in target.values],source_refs=ref),
                    Subscript(Name(name=list_name, id=list_var_id, source_refs=ref), 
                    Name(name=count_var_name, id=count_var_id, source_refs=ref),source_refs=ref),
                    source_refs=ref
                ),
                Assignment(
                    target,
                    Tuple([Var(type="float",val=Name(name=f"{node.val.name}_",id=-1,source_refs=ref),source_refs=ref) for node in target.values], source_refs=ref),
                    source_refs=ref
                )]
            else:
                loop_assign = [Assignment(
                    Var(Name(name=node.target.id,id=curr_scope_id_dict[node.target.id],source_refs=ref), "float", source_refs=ref),
                    Subscript(Name(name=list_name,id=list_var_id,source_refs=ref), 
                    Name(name=count_var_name,id=count_var_id,source_refs=ref),source_refs=ref),
                    source_refs=ref
                )]
        elif isinstance(node.iter,ast.Attribute): # For attributes like x.foo_list, x.foo(), etc
            if isinstance(node.target,ast.Tuple):
                loop_assign = [Assignment(
                    Tuple([Var(type="float",val=Name(f"{node.val.name}_",id=-1,source_refs=ref),source_refs=ref) for node in target.values],source_refs=ref),
                    Subscript(Name(name=node.iter.value.id,id=curr_scope_id_dict[node.iter.value.id],source_refs=ref), 
                    Name(count_var_name,source_refs=ref),source_refs=ref),
                    source_refs=ref
                ),
                Assignment(
                    target,
                    Tuple([Var(type="float",val=Name(name=f"{node.val.name}_",id=-1,source_refs=ref),source_refs=ref) for node in target.values],source_refs=ref),
                    source_refs=ref
                )]
            else:
                loop_assign = [Assignment(
                    Var(Name(name=node.target.id, id=curr_scope_id_dict[node.target.id], source_refs=ref), "float", source_refs=ref),
                    Subscript(Name(name=list_name, id=list_var_id, source_refs=ref), 
                    Name(name=count_var_name, id=count_var_id, source_refs=ref), source_refs=ref),
                    source_refs=ref
                )]
        else:
            if isinstance(node.target,ast.Tuple):
                loop_assign = [Assignment(
                    Tuple([Var(type="float", val=Name(name=f"{node.val.name}_", id=-1, source_refs=ref), source_refs=ref) for node in target.values],source_refs=ref),
                    Subscript(Name(name=node.iter.id, id=curr_scope_id_dict[node.iter.id], source_refs=ref), 
                    Name(name=count_var_name, id=count_var_id, source_refs=ref), source_refs=ref),
                    source_refs=ref
                ),
                Assignment(
                    target,
                    Tuple([Var(type="float", val=Name(name=f"{node.val.name}_", id=-1, source_refs=ref), source_refs=ref) for node in target.values],source_refs=ref),
                    source_refs=ref
                )]
            else:
                loop_assign = [Assignment(
                    Var(Name(name=node.target.id, id=curr_scope_id_dict[node.target.id], source_refs=ref), "float", source_refs=ref),
                    Subscript(Name(name=list_name, id=list_var_id, source_refs=ref), Name(name=count_var_name, id=count_var_id, source_refs=ref), source_refs=ref),
                    source_refs=ref
                )]
        loop_increment = [Assignment(
            Var(Name(name=count_var_name, id=count_var_id, source_refs=ref), "float", source_refs=ref),
            BinaryOp(BinaryOperator.ADD, Name(name=count_var_name, id=count_var_id, source_refs=ref), Number(1, source_refs=ref), source_refs=ref),
            source_refs=ref
        )]

        return [count_var, list_var, Loop(expr=loop_cond, body=loop_assign + body + loop_increment, source_refs=ref)]

    @visit.register
    def visit_FunctionDef(self, node: ast.FunctionDef, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST FunctionDef node. Which is used for a Python
        function definition.

        Args:
            node (ast.FunctionDef): A PyAST function definition node

        Returns:
            FunctionDef: A CAST Function Definition node
        """

        # Copy the enclosing scope dictionary as it is before we visit the current function
        # The idea for this is to prevent any weird overwritting issues that may arise from modifying
        # dictionaries in place
        prev_scope_id_dict_copy = copy.deepcopy(prev_scope_id_dict)

        body = []
        args = []
        curr_scope_id_dict = {}
        if len(node.args.args) > 0:
            for arg in node.args.args:
                #unique_name = construct_unique_name(self.filenames[-1], arg.arg)
                self.insert_next_id(curr_scope_id_dict, arg.arg)
                #self.insert_next_id(curr_scope_id_dict, unique_name)
                args.append(Var(Name(arg.arg,id=curr_scope_id_dict[arg.arg],source_refs=[SourceRef(self.filenames[-1], arg.col_offset, arg.end_col_offset, arg.lineno, arg.end_lineno)]), 
                "float", # TODO: Correct typing instead of just 'float'
                source_refs=[SourceRef(self.filenames[-1], arg.col_offset, arg.end_col_offset, arg.lineno, arg.end_lineno)]))

        functions_to_visit = []

        if len(node.body) > 0:
            # To account for nested loops we check to see if the CAST node is in a list and
            # extend accordingly
            for piece in node.body:
                # We defer visiting function defs until we've cleared the rest of the code in the function
                if isinstance(piece, ast.FunctionDef):
                    self.insert_next_id(curr_scope_id_dict, piece.name)
                    prev_scope_id_dict[piece.name] = curr_scope_id_dict[piece.name]
                    functions_to_visit.append(piece)
                    continue
                
                # Have to figure out name IDs for imports (i.e. other modules)
                # These asserts will keep us from visiting them from now
                assert not isinstance(piece, ast.Import)
                assert not isinstance(piece, ast.ImportFrom)
                to_add = self.visit(piece, prev_scope_id_dict, curr_scope_id_dict)

                # TODO: Find the case where "__getitem__" is used
                if hasattr(to_add, "__iter__") or hasattr(to_add, "__getitem__"):
                    body.extend(to_add)
                else:
                    raise TypeError(f"Unexpected type in visit_FuncDef: {type(to_add)}")

            # Merge keys from prev_scope not in cur_scope into cur_scope 
            merge_dicts(prev_scope_id_dict, curr_scope_id_dict)

            # Visit the deferred functions
            for piece in functions_to_visit:
                to_add = self.visit(piece, curr_scope_id_dict, {})
                body.extend(to_add)

        # TODO: Decorators? Returns? Type_comment?
        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]

        # "Revert" the enclosing scope dictionary to what it was before we went into this function
        # since none of the variables within here should exist outside of here..?
        # TODO: this might need to be different, since Python variables can exist outside of a scope?? 
        prev_scope_id_dict = copy.deepcopy(prev_scope_id_dict_copy)
        
        # Global level (i.e. module level) functions have their module names appended to them, we make sure
        # we have the correct name depending on whether or not we're visiting a global
        # level function or a function enclosed within another function
        if node.name in prev_scope_id_dict.keys():
            if self.legacy:
                return [FunctionDef(node.name, args, body, source_refs=ref)]
            else:
                return [FunctionDef(Name(node.name,prev_scope_id_dict[node.name]), args, body, source_refs=ref)]
        else:
            unique_name = construct_unique_name(self.filenames[-1], node.name) 
            if self.legacy:
                return [FunctionDef(node.name, args, body, source_refs=ref)]
            else:
                return [FunctionDef(Name(node.name,prev_scope_id_dict[unique_name]), args, body, source_refs=ref)]



    @visit.register
    def visit_Lambda(self, node: ast.Lambda, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Lambda node. Which is used for a Python Lambda
        function definition. It works pretty analogously to the FunctionDef
        node visitor. It also returns a FunctionDef node like the PyAST
        FunctionDef node visitor.

        Args:
            node (ast.Lambda): A PyAST lambda function definition node

        Returns:
            FunctionDef: A CAST Function Definition node

        """

        curr_scope_id_dict = {}

        args = []
        # TODO: Correct typing instead of just 'float'
        if len(node.args.args) > 0:
            for arg in node.args.args:
                self.insert_next_id(curr_scope_id_dict, arg.arg)

                args.append(Var(Name(arg.arg,id=curr_scope_id_dict[arg.arg],source_refs=[SourceRef(self.filenames[-1], arg.col_offset, arg.end_col_offset, arg.lineno, arg.end_lineno)]), 
                "float", # TODO: Correct typing instead of just 'float'
                source_refs=[SourceRef(self.filenames[-1], arg.col_offset, arg.end_col_offset, arg.lineno, arg.end_lineno)]))


        body = self.visit(node.body, prev_scope_id_dict, curr_scope_id_dict)

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        # TODO: add an ID for lambda name
        if self.legacy:
            return [FunctionDef("LAMBDA", args, body, source_refs=ref)]
        else:
            return [FunctionDef(Name("LAMBDA",id=-1), args, body, source_refs=ref)]

    @visit.register
    def visit_ListComp(self, node: ast.ListComp, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST ListComp node, which are used for Python list comprehensions.
        List comprehensions generate a list from some generator expression.

        Args:
            node (ast.ListComp): A PyAST list comprehension node

        Returns:
            Loop: 
        """

        ref = [self.filenames[-1], node.col_offset, node.end_col_offset, node.lineno, node.end_lineno]

        temp_list_name = f"list__temp_"
        temp_assign = ast.Assign(targets=[ast.Name(id=temp_list_name,ctx=ast.Store(),col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])], 
                                 value=ast.List(elts=[], col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4]), 
                                 type_comment=None,col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])
        
        generators = node.generators
        first_gen = generators[-1] 
        i = len(generators)-2

        # Constructs the Python AST for the innermost loop in the list comprehension
        if len(first_gen.ifs) > 0:
            innermost_loop_body = [ast.If(test=first_gen.ifs[0], body=[ast.Expr(value=ast.Call(
                    func=ast.Attribute(value=ast.Name(id=temp_list_name, ctx=ast.Load(), col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4]), attr='append', ctx=ast.Load(), col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4]), 
                    args=[node.elt],
                    keywords=[], col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4]), 
                    col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])],
                    orelse=[],col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])]
        else:
            innermost_loop_body = [ast.Expr(value=ast.Call(
                    func=ast.Attribute(value=ast.Name(id=temp_list_name, ctx=ast.Load(), col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4]), attr='append', ctx=ast.Load(), col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4]), 
                    args=[node.elt],
                    keywords=[], col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4]
                    ), col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])]

        loop_collection = [ast.For(target=self.identify_piece(first_gen.target, prev_scope_id_dict, curr_scope_id_dict),
                                    iter=self.identify_piece(first_gen.iter, prev_scope_id_dict, curr_scope_id_dict),
                                    body=innermost_loop_body,orelse=[],col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])]


        # Every other loop in the list comprehension wraps itself around the previous loop that we 
        # added
        while i >= 0:
            curr_gen = generators[i]
            if len(curr_gen.ifs) > 0:
                # TODO: if multiple ifs exist per a single generator then we have to expand this
                curr_if = curr_gen.ifs[0]
                next_loop = ast.For(target=self.identify_piece(curr_gen.target, curr_scope_id_dict, prev_scope_id_dict),
                                iter=self.identify_piece(curr_gen.iter, curr_scope_id_dict, prev_scope_id_dict),
                                body=[ast.If(test=curr_if, body=[loop_collection[0]],
                                orelse=[],col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])],
                                orelse=[],col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])

            else:
                next_loop = ast.For(target=self.identify_piece(curr_gen.target, curr_scope_id_dict, prev_scope_id_dict),
                                        iter=self.identify_piece(curr_gen.iter, curr_scope_id_dict, prev_scope_id_dict),
                                        body=[loop_collection[0]],orelse=[],col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])
            

            loop_collection.insert(0, next_loop)
            i = i - 1

        temp_cast = self.visit(temp_assign, prev_scope_id_dict, curr_scope_id_dict)
        loop_cast = self.visit(loop_collection[0], prev_scope_id_dict, curr_scope_id_dict)

        to_ret = []
        to_ret.extend(temp_cast)
        to_ret.extend(loop_cast)

        return to_ret

    @visit.register
    def visit_DictComp(self, node: ast.DictComp, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        ref = [self.filenames[-1], node.col_offset, node.end_col_offset, node.lineno, node.end_lineno]
        
        # node (ast.DictComp)
        #  key       - what makes the keys 
        #  value     - what makes the valuedds
        #  generators - list of 'comprehension' nodes 
        
        temp_dict_name = f"dict__temp_"
        
        generators = node.generators
        first_gen = generators[-1] 
        i = len(generators)-2
        temp_assign = ast.Assign(targets=[ast.Name(id=temp_dict_name,ctx=ast.Store(),col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])], 
                                 value=ast.Dict(keys=[], values=[], col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4]), 
                                 type_comment=None,col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])

        # Constructs the Python AST for the innermost loop in the dict comprehension
        if len(first_gen.ifs) > 0:
            innermost_loop_body = ast.If(test=first_gen.ifs[0], body=[ast.Assign(targets=[ast.Subscript(value=ast.Name(id=temp_dict_name, ctx=ast.Load(), 
                                                                col_offset=ref[1], end_col_offset=ref[2], lineno=ref[3], end_lineno=ref[4]),
                                                                slice=node.key,
                                                                ctx=ast.Store(), col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])],
                                                                value=node.value,
                                                                type_comment=None,col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])],
                                    orelse=[],col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])
        else:
            innermost_loop_body = ast.Assign(targets=[ast.Subscript(value=ast.Name(id=temp_dict_name, ctx=ast.Load(), 
                                                                col_offset=ref[1], end_col_offset=ref[2], lineno=ref[3], end_lineno=ref[4]),
                                                                slice=node.key,
                                                                ctx=ast.Store(), col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])],
                                            value=node.value,
                                            type_comment=None,col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])

        loop_collection = [ast.For(target= self.identify_piece(first_gen.target, prev_scope_id_dict, curr_scope_id_dict),
                                    iter=self.identify_piece(first_gen.iter, prev_scope_id_dict, curr_scope_id_dict),
                                    body=[innermost_loop_body],orelse=[],col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])]

        # Every other loop in the list comprehension wraps itself around the previous loop that we 
        # added
        while i >= 0:
            curr_gen = generators[i]
            if len(curr_gen.ifs) > 0:
                # TODO: if multiple ifs exist per a single generator then we have to expand this
                curr_if = curr_gen.ifs[0]
                next_loop = ast.For(target=self.identify_piece(curr_gen.target, prev_scope_id_dict, curr_scope_id_dict),
                                iter=self.identify_piece(curr_gen.iter, prev_scope_id_dict, curr_scope_id_dict),
                                body=[ast.If(test=curr_if, body=[loop_collection[0]],
                                orelse=[],col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])],
                            orelse=[],col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])
            else:
                next_loop = ast.For(target=self.identify_piece(curr_gen.target, prev_scope_id_dict, curr_scope_id_dict),
                                        iter=self.identify_piece(curr_gen.iter, prev_scope_id_dict, curr_scope_id_dict),
                                        body=[loop_collection[0]],orelse=[],col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])
            loop_collection.insert(0, next_loop)
            i = i - 1

        temp_cast = self.visit(temp_assign, prev_scope_id_dict, curr_scope_id_dict)
        loop_cast = self.visit(loop_collection[0], prev_scope_id_dict, curr_scope_id_dict)

        to_ret = []
        to_ret.extend(temp_cast)
        to_ret.extend(loop_cast)

        return to_ret


    @visit.register
    def visit_If(self, node: ast.If, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST If node. Which is used to represent If statements.
        We visit each of the pieces accordingly and construct the CAST
        representation. else/elif statements are stored in the 'orelse' field,
        if there are any.

        Args:
            node (ast.If): A PyAST If node.

        Returns:
            ModelIf: A CAST If statement node.
        """

        node_test = self.visit(node.test, prev_scope_id_dict, curr_scope_id_dict)

        node_body = []
        if len(node.body) > 0:
            for piece in node.body:
                node_body.extend(self.visit(piece, prev_scope_id_dict, curr_scope_id_dict))

        node_orelse = []
        if len(node.orelse) > 0:
            for piece in node.orelse:
                node_orelse.extend(self.visit(piece, prev_scope_id_dict, curr_scope_id_dict))

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]

        return [ModelIf(node_test[0], node_body, node_orelse, source_refs=ref)]

    @visit.register
    def visit_Global(self, node: ast.Global, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Global node. 
        What this does is write in the IDs for variables that are
        explicitly declared as global within a scope using the global keyword
        as follows
        global x [, y, z, etc..]

        Args:
            node (ast.Global): A PyAST Global node
            prev_scope_id_dict (Dict): Dictionary containing the scope's current variable : ID maps

        Returns:
            List: empty list
        """

        for v in node.names:
            unique_name = construct_unique_name(self.filenames[-1],v)
            curr_scope_id_dict[unique_name] = self.global_identifier_dict[unique_name]   
        return []

    @visit.register
    def visit_IfExp(self, node: ast.IfExp, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST IfExp node, which is Python's ternary operator.
        The node gets translated into a CAST ModelIf node by visiting all its parts,
        since IfExp behaves like an If statement.

        # TODO: Rethink how this is done to better reflect
         - ternary for assignments
         - ternary in function call arguments

        Args:
            node (ast.IfExp): [description]
        """

        node_test = self.visit(node.test, prev_scope_id_dict, curr_scope_id_dict)
        node_body = self.visit(node.body, prev_scope_id_dict, curr_scope_id_dict)
        node_orelse = self.visit(node.orelse, prev_scope_id_dict, curr_scope_id_dict)
        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]

        return [ModelIf(node_test[0], node_body, node_orelse, source_refs=ref)]

    @visit.register
    def visit_Import(self, node:ast.Import, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Import node, which is used for importing libraries
        that are used in programs. In particular, it's imports in the form of
        'import X', where X is some library.

        Args:
            node (ast.Import): A PyAST Import node

        Returns: 
        """

        names = node.names
        alias = names[0]

        # Construct the path of the module, relative to where we are at
        # (Still have to handle things like '..')
        name = alias.name
        path = f"./{name.replace('.','/')}.py"

        # module1.x, module2.x
        # {module1: {x: 1}, module2: {x: 4}}

        # For cases like 'import module as something_else'
        # We note the alias that the import uses for this module
        if alias.asname is not None:
            self.aliases[alias.asname] = name
            name = alias.asname

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        
        # If we find the file by searching the path, then this is a user-imported module
        if os.path.isfile(path):
            true_module_name = self.aliases[name] if name in self.aliases else name
            if true_module_name in self.visited:
                return [Module(name=true_module_name,body=[],source_refs=ref)]
            else:
                file_contents = open(path).read()
                self.filenames.append(true_module_name)
                self.visited.add(true_module_name)
                
                self.insert_next_id(self.global_identifier_dict, true_module_name)

                to_ret = self.visit(ast.parse(file_contents), {}, {})
                self.filenames.pop()
                return to_ret
        else:
            self.insert_next_id(self.global_identifier_dict, name)
            return [Module(name=name,body=[],source_refs=ref)]


    @visit.register
    def visit_ImportFrom(self, node:ast.ImportFrom, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST ImportFrom node, which is used for importing libraries
        that are used in programs. In particular, it's imports in the form of
        'import X', where X is some library.

        Args:
            node (ast.Import): A PyAST Import node

        Returns: 
        """

        # Construct the path of the module, relative to where we are at
        # (TODO: Still have to handle things like '..')


        name = node.module
        path = f"./{name.replace('.','/')}.py"

        names = node.names

        for alias in names:
            if alias.asname is not None:
                self.aliases[alias.asname] = alias.name

        # TODO: What about importing individual functions from a module M
        #        that call other functions from that same module M
        if os.path.isfile(path):
            true_name = self.aliases[name] if name in self.aliases else name
            if name in self.visited:
                ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
                return [Module(name=name,body=[],source_refs=ref)]
            else:
                file_contents = open(path).read()
                self.visited.add(name)
                self.filenames.append(path.split("/")[-1])
                contents = ast.parse(file_contents)

                # Importing individual functions
                if name is not None: 
                    funcs = []
                    for func in names:
                        for n in contents.body:
                            if isinstance(n,ast.FunctionDef) and n.name == func.name: 
                                funcs.append(n)
                                break

                    visited_funcs = []
                    for f in funcs:
                        visited_funcs.extend(self.visit(f, {}, {}))
                    
                    self.filenames.pop()
                    return visited_funcs
                else: # Importing the entire file
                    full_file = self.visit(contents, {}, {})
                    self.filenames.pop()
                    return full_file
        else:
            ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
            return [Module(name=name,body=[],source_refs=ref)]


    @visit.register
    def visit_List(self, node:ast.List, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST List node. Which is used to represent Python lists.

        Args:
            node (ast.List): A PyAST List node.

        Returns:
            List: A CAST List node.
        """

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        if len(node.elts) > 0:
            to_ret = []
            for piece in node.elts:
                to_ret.extend(self.visit(piece, prev_scope_id_dict, curr_scope_id_dict))
            return [List(to_ret,source_refs=ref)]
        else:
            return [List([],source_refs=ref)]

    @visit.register
    def visit_Module(self, node: ast.Module, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Module node. This is the starting point of CAST Generation,
        as the body of the Module node (usually) contains the entire Python
        program.

        Args:
            node (ast.Module): A PyAST Module node.

        Returns:
            Module: A CAST Module node.
        """

        # Visit all the nodes and make a Module object out of them
        body = []
        funcs = []
        for piece in node.body:
            # Defer visiting function defs until all global vars are processed
            if isinstance(piece, ast.FunctionDef):
                unique_name = construct_unique_name(self.filenames[-1],piece.name)
                self.insert_next_id(curr_scope_id_dict, unique_name)
                prev_scope_id_dict[unique_name] = curr_scope_id_dict[unique_name]
                funcs.append(piece)
                continue

            to_add = self.visit(piece, prev_scope_id_dict, curr_scope_id_dict)

            # Global variables (which come about from assignments at the module level)
            # need to have their identifier names set correctly so they can be
            # accessed appropriately later on
            # We check if we just visited an assign and fix its key/value pair in the dictionary
            # So instead of 
            #   "var_name" -> ID
            # It becomes
            #   "module_name.var_name" -> ID
            # in the dictionary
            if isinstance(piece, ast.Assign):
                var_name = get_node_name(to_add[0])

                temp_id = curr_scope_id_dict[var_name]
                del curr_scope_id_dict[var_name]
                unique_name = construct_unique_name(self.filenames[-1], var_name)
                curr_scope_id_dict[unique_name] = temp_id

            if isinstance(to_add,Module):
                body.extend([to_add])
            else:
                body.extend(to_add)

        merge_dicts(curr_scope_id_dict, self.global_identifier_dict)
        merge_dicts(prev_scope_id_dict, curr_scope_id_dict)

        # Visit all the functions
        for piece in funcs:
            to_add = self.visit(piece, curr_scope_id_dict, {})
            body.extend(to_add)

        return Module(name=self.filenames[-1].split(".")[0], body=body, source_refs=None)

    @visit.register
    def visit_Name(self, node: ast.Name, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """This visits PyAST Name nodes, which consist of
           id: The name of a variable as a string
           ctx: The context in which the variable is being used

        Args:
            node (ast.Name): A PyAST Name node

        Returns:
            Expr: A CAST Expression node

        """
        # TODO: Typing so it's not hardcoded to floats
        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]

        if isinstance(node.ctx,ast.Load):
            if node.id in self.aliases: 
                return [Name(self.aliases[node.id], id=-1, source_refs=ref)]

            if node.id not in curr_scope_id_dict:
                if node.id in prev_scope_id_dict:
                    curr_scope_id_dict[node.id] = prev_scope_id_dict[node.id]
                else:
                    unique_name = construct_unique_name(self.filenames[-1], node.id)
                    
                    # We can have the very odd case where a variable is used in a function before 
                    # it even exists. To my knowledge this happens in one scenario:
                    # - A global variable, call it z, is used in a function
                    # - Before that function is called in Python code, that global variable
                    #   z is set by another module/another piece of code as a global
                    #   (i.e. by doing module_name.z = a value)
                    # It's not something that is very common (or good) to do, but regardless
                    # we'll catch it here just in case.
                    if unique_name not in self.global_identifier_dict.keys():
                        self.insert_next_id(self.global_identifier_dict, unique_name)

                    curr_scope_id_dict[node.id] = self.global_identifier_dict[unique_name]
            
            return [Name(node.id, id=curr_scope_id_dict[node.id], source_refs=ref)]
            
        if isinstance(node.ctx,ast.Store):
            if node.id in self.aliases: 
                return [Var(Name(self.aliases[node.id], id=-1, source_refs=ref), "float", source_refs=ref)]

            
            if node.id not in curr_scope_id_dict:
                if node.id in prev_scope_id_dict:
                    curr_scope_id_dict[node.id] = prev_scope_id_dict[node.id]
                else:
                    self.insert_next_id(curr_scope_id_dict,node.id)

            return [Var(Name(node.id, id=curr_scope_id_dict[node.id],source_refs=ref), "float", source_refs=ref)]


        if isinstance(node.ctx,ast.Del):
            # TODO: At some point..
            raise NotImplementedError()

    @visit.register
    def visit_Pass(self, node: ast.Pass, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """A PyAST Pass visitor, for essentially NOPs."""

        return []

    @visit.register
    def visit_Raise(self, node: ast.Raise, prev_scope_id_dict: Dict):
        """A PyAST Raise visitor, for Raising exceptions

           TODO: To be implemented.
        """

        return []

    @visit.register
    def visit_Return(self, node: ast.Return, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Return node and creates a CAST return node
           that has one field, which is the expression computing the value
           to be returned. The PyAST's value node is visited.
           The CAST node is then returned.

        Args:
            node (ast.Return): A PyAST Return node

        Returns:
            ModelReturn: A CAST Return node
        """

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        return [ModelReturn(self.visit(node.value, prev_scope_id_dict, curr_scope_id_dict)[0], source_refs=ref)]

    @visit.register
    def visit_UnaryOp(self, node: ast.UnaryOp, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST UnaryOp node. Which represents Python unary operations.
        A dictionary is used to index into which operation we're doing.

        Args:
            node (ast.UnaryOp): A PyAST UnaryOp node.

        Returns:
            UnaryOp: A CAST UnaryOp node.
        """

        ops = {
            ast.UAdd: UnaryOperator.UADD,
            ast.USub: UnaryOperator.USUB,
            ast.Not: UnaryOperator.NOT,
            ast.Invert: UnaryOperator.INVERT,
        }
        op = ops[type(node.op)]
        operand = node.operand

        opd = self.visit(operand, prev_scope_id_dict, curr_scope_id_dict)

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        return [UnaryOp(op, opd[0], source_refs=ref)]

    @visit.register
    def visit_Set(self, node: ast.Set, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Set node. Which is used to represent Python sets.

        Args:
            node (ast.Set): A PyAST Set node.

        Returns:
            Set: A CAST Set node.
        """

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]

        if len(node.elts) > 0:
            to_ret = []
            for piece in node.elts:
                to_ret.extend(self.visit(piece, prev_scope_id_dict, curr_scope_id_dict))
            return [Set(to_ret,source_refs=ref)]
        else:
            return [Set([], source_refs=ref)]

    @visit.register
    def visit_Subscript(self, node: ast.Subscript, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Subscript node, which represents subscripting into
        a list in Python. A Subscript is either a Slice (i.e. x[0:2]), an 
        Extended slice (i.e. x[0:2, 3]), or a constant (i.e. x[3]). 
        In the Slice case, a loop is generated that fetches the correct elements and puts them 
        into a list.
        In the Extended slice case, nested loops are generated as needed to create a final 
        result list with the selected elements.
        In the constant case, we can visit and generate a CAST Subscript in a normal way.

        Args:
            node (ast.Subscript): A PyAST Subscript node

        Returns:
            Subscript: A CAST Subscript node
        """

        value = self.visit(node.value, prev_scope_id_dict, curr_scope_id_dict)[0]
        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]

        # 'Visit' the slice 
        slc = node.slice
        temp_var = f"generated_index_{self.var_count}"
        self.var_count += 1

        if isinstance(slc,ast.Slice):
            if slc.lower is not None:
                lower = self.visit(slc.lower, prev_scope_id_dict, curr_scope_id_dict)[0]
            else:
                lower = Number(0, source_refs=ref)
            
            if slc.upper is not None:
                upper = self.visit(slc.upper, prev_scope_id_dict, curr_scope_id_dict)[0]
            else:
                if isinstance(node.value,ast.Call):
                    if isinstance(node.value.func,ast.Attribute):
                        upper = Call(Name("len", source_refs=ref), [Name(node.value.func.attr, source_refs=ref)], source_refs=ref)
                    else:
                        upper = Call(Name("len", source_refs=ref), [Name(node.value.func.id, source_refs=ref)], source_refs=ref)
                elif isinstance(node.value,ast.Attribute):
                    upper = Call(Name("len", source_refs=ref), [Name(node.value.attr, source_refs=ref)], source_refs=ref)
                else:
                    upper = Call(Name("len", source_refs=ref), [Name(node.value.id, source_refs=ref)], source_refs=ref)

            if slc.step is not None:
                step = self.visit(slc.step, prev_scope_id_dict, curr_scope_id_dict)[0]
            else:
                step = Number(1, source_refs=ref)


            if isinstance(node.value,ast.Call):
                if isinstance(node.value.func,ast.Attribute):
                    temp_list = f"{node.value.func.attr}_generated_{self.var_count}"
                else:
                    temp_list = f"{node.value.func.id}_generated_{self.var_count}"
            elif isinstance(node.value,ast.Attribute):
                temp_list = f"{node.value.attr}_generated_{self.var_count}"
            else: 
                temp_list = f"{value.name}_generated_{self.var_count}"
            self.var_count += 1

            new_list = Assignment(Var(Name(temp_list, source_refs=ref), "float", source_refs=ref), List([], source_refs=ref), source_refs=ref)
            loop_var = Assignment(Var(Name(temp_var, source_refs=ref), "float", source_refs=ref), lower, source_refs=ref)

            loop_cond = BinaryOp(
                BinaryOperator.LT,
                Name(temp_var, source_refs=ref),
                upper,
                source_refs=ref
            )

            if isinstance(node.value,ast.Call):
                if isinstance(node.value.func,ast.Attribute):
                    body = [Call(func=Attribute(Name(temp_list, source_refs=ref),Name("append", source_refs=ref),source_refs=ref),
                                arguments=[Subscript(Name(node.value.func.attr, source_refs=ref),Name(temp_var, source_refs=ref), source_refs=ref)],
                                source_refs=ref)] 
                else:
                    body = [Call(func=Attribute(Name(temp_list, source_refs=ref),Name("append", source_refs=ref),source_refs=ref),
                                arguments=[Subscript(Name(node.value.func.id, source_refs=ref),Name(temp_var, source_refs=ref), source_refs=ref)],
                                source_refs=ref)] 
            elif isinstance(node.value,ast.Attribute):
                body = [Call(func=Attribute(Name(temp_list, source_refs=ref),Name("append", source_refs=ref),source_refs=ref),
                            arguments=[Subscript(Name(node.value.attr, source_refs=ref),Name(temp_var, source_refs=ref), source_refs=ref)],
                            source_refs=ref)] 
            else:
                body = [Call(func=Attribute(Name(temp_list, source_refs=ref),Name("append", source_refs=ref),source_refs=ref),
                            arguments=[Subscript(Name(node.value.id, source_refs=ref),Name(temp_var, source_refs=ref), source_refs=ref)],
                            source_refs=ref)] 

            loop_increment = [Assignment(
                Var(Name(temp_var, source_refs=ref), "float", source_refs=ref),
                BinaryOp(BinaryOperator.ADD, Name(temp_var, source_refs=ref), step, source_refs=ref),
                source_refs=ref
            )]

            slice_loop = Loop(
                expr=loop_cond, body=body + loop_increment, source_refs=ref
            )

            slice_var = Var(Name(temp_list, source_refs=ref), "float", source_refs=ref)

            return [new_list, loop_var, slice_loop, slice_var]
        elif isinstance(slc,ast.ExtSlice):
            dims = slc.dims 
            result = []
            
            if isinstance(node.value,ast.Call):
                if isinstance(node.value.func,ast.Attribute):
                    lists = [node.value.func.attr]
                else:
                    lists = [node.value.func.id]
            elif isinstance(node.value,ast.Attribute): 
                lists = [node.value.attr]
            else:
                lists = [node.value.id]

            temp_count = 1
            for dim in dims:
                temp_list_name = f"{lists[0]}_{str(temp_count)}"
                temp_count += 1

                list_var = Assignment(Var(Name(temp_list_name, source_refs=ref), "float", source_refs=ref), List([], source_refs=ref), source_refs=ref)
                loop_var = Assignment(Var(Name(temp_var, source_refs=ref), "float", source_refs=ref), Number(0, source_refs=ref),source_refs=ref)

                if isinstance(dim,ast.Slice):
                    # For each dim in dimensions
                    # Check if it's a slice or a constant
                    # For a slice
                    # Take the current temp list 
                    # Make a new temp list
                    # Using the slice bounds, generate a loop that assigns the elements of
                    # the slice bounds to the new temp list 
                    # Append the cast and temp list accordingly
                    if dim.lower is not None:
                        lower = self.visit(dim.lower, prev_scope_id_dict, curr_scope_id_dict)[0]
                    else:
                        lower = Number(0, source_refs=ref)
                    
                    if dim.upper is not None:
                        upper = self.visit(dim.upper, prev_scope_id_dict, curr_scope_id_dict)[0]
                    else:
                        if isinstance(node.value,ast.Call):
                            if isinstance(node.value.func,ast.Attribute):
                                upper = Call(Name("len", source_refs=ref), [Name(node.value.func.attr, source_refs=ref)], source_refs=ref)
                            else:
                                upper = Call(Name("len", source_refs=ref), [Name(node.value.func.id, source_refs=ref)], source_refs=ref)
                        elif isinstance(node.value,ast.Attribute):
                            upper = Call(Name("len", source_refs=ref), [Name(node.value.attr, source_refs=ref)], source_refs=ref)
                        else:
                            upper = Call(Name("len", source_refs=ref), [Name(node.value.id, source_refs=ref)], source_refs=ref)

                    if dim.step is not None:
                        step = self.visit(dim.step, prev_scope_id_dict, curr_scope_id_dict)[0]
                    else:
                        step = Number(1, source_refs=ref)


                    loop_cond = BinaryOp(
                        BinaryOperator.LT,
                        Name(temp_var, source_refs=ref),
                        upper,
                        source_refs=ref
                    )

                    body = [Call(Attribute(Name(temp_list_name,source_refs=ref),Name("append", source_refs=ref),source_refs=ref),
                                [Subscript(Name(lists[-1], source_refs=ref),Name(temp_var, source_refs=ref),source_refs=ref)],source_refs=ref)] 

                    loop_increment = [Assignment(
                        Var(Name(temp_var, source_refs=ref), "float", source_refs=ref),
                        BinaryOp(BinaryOperator.ADD, Name(temp_var, source_refs=ref), step, source_refs=ref),
                        source_refs=ref
                    )]

                    slice_loop = Loop(
                        expr=loop_cond, body=body + loop_increment, source_refs=ref
                    )

                    lists.append(temp_list_name)

                    result.extend([list_var,loop_var,slice_loop])
                if isinstance(dim,ast.Index):
                    # For an index
                    # Take the current temp list
                    # Make a new temp list
                    # This new temp list indexes into the current temp list
                    # and copies the elements according to the index number
                    # Append that new temp list and its corresponding CAST 
                    # to our result 
                    curr_dim = self.visit(dim, prev_scope_id_dict, curr_scope_id_dict)[0]

                    loop_cond = BinaryOp(
                        BinaryOperator.LT,
                        Name(temp_var, source_refs=ref),
                        Call(Name("len", source_refs=ref), [Name(lists[-1], source_refs=ref)], source_refs=ref),
                        source_refs=ref
                    )

                    body = [Call(Attribute(Name(temp_list_name, source_refs=ref),Name("append", source_refs=ref), source_refs=ref),
                                [Subscript(Name(lists[-1], source_refs=ref), curr_dim, source_refs=ref)], source_refs=ref)] 
                    

                    loop_increment = [Assignment(
                        Var(Name(temp_var, source_refs=ref), "float", source_refs=ref),
                        BinaryOp(BinaryOperator.ADD, Name(temp_var, source_refs=ref), Number(1, source_refs=ref), source_refs=ref),
                        source_refs=ref
                    )]

                    slice_loop = Loop(
                        expr=loop_cond, body=body + loop_increment, source_refs=ref
                    )

                    lists.append(temp_list_name)

                    result.extend([list_var,loop_var,slice_loop])

            return result
        else:
            sl = self.visit(slc, prev_scope_id_dict, curr_scope_id_dict)

        return [Subscript(value, sl[0], source_refs=ref)]


    @visit.register
    def visit_Index(self, node: ast.Index, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Index node, which represents the value being used
        for an index. This visitor doesn't create its own CAST node, but
        returns CAST depending on the value that the Index node holds.

        Args:
            node (ast.Index): A CAST Index node.

        Returns:
            AstNode: Depending on what the value of the Index node is,
                     different CAST nodes are returned.
        """

        return self.visit(node.value, prev_scope_id_dict, curr_scope_id_dict)

    @visit.register
    def visit_Tuple(self, node: ast.Tuple, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Tuple node. Which is used to represent Python tuple.

        Args:
            node (ast.Tuple): A PyAST Tuple node.

        Returns:
            Set: A CAST Tuple node.
        """

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        if len(node.elts) > 0:
            to_ret = []
            for piece in node.elts:
                to_ret.extend(self.visit(piece, prev_scope_id_dict, curr_scope_id_dict))
            return [Tuple(to_ret, source_refs=ref)]
        else:
            return [Tuple([], source_refs=ref)]

    @visit.register
    def visit_Try(self, node:ast.Try, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST Try node, which represents Try/Except blocks.
        These are used for Python's exception handling

        Currently, the visitor just bypasses the Try/Except feature and just
        generates CAST for the body of the 'Try' block, assuming the exception(s)
        are never thrown.
        """

        body = []
        for piece in node.body:
            body.extend(self.visit(piece, prev_scope_id_dict, curr_scope_id_dict))
            
        return body

    @visit.register
    def visit_While(self, node: ast.While, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST While node, which represents a while loop.

        Args:
            node (ast.While): a PyAST while node

        Returns:
            Loop: A CAST loop node, which generically represents both For
                  loops and While loops.
        """

        test = self.visit(node.test, prev_scope_id_dict, curr_scope_id_dict)[0]

        # Loops have their own enclosing scopes
        curr_scope_copy = copy.deepcopy(curr_scope_id_dict)
        merge_dicts(prev_scope_id_dict, curr_scope_id_dict)
        loop_body_scope = {}
        body = []
        for piece in (node.body + node.orelse):
            to_add = self.visit(piece, curr_scope_id_dict, loop_body_scope)
            body.extend(to_add)
        
        curr_scope_id_dict = copy.deepcopy(curr_scope_copy)
        
        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        return [Loop(expr=test, body=body, source_refs=ref)]

    @visit.register
    def visit_With(self, node: ast.With, prev_scope_id_dict: Dict, curr_scope_id_dict: Dict):
        """Visits a PyAST With node. With nodes are used as follows:
        with a as b, c as d: 
            do things with b and d
        To use aliases on variables and operate on them
        This visitor unrolls the With block and generates the appropriate cast for the
        underlying operations

        Args:
            node (ast.With): a PyAST with node

        Args:
            [AstNode]: A list of CAST nodes, representing whatever operations were happening in the With 
                       block before they got unrolled

        """

        ref = None
        variables = [] 
        for item in node.items:
            ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
            variables.extend([Assignment(left=self.visit(item.optional_vars, prev_scope_id_dict, curr_scope_id_dict)[0],right=self.visit(item.context_expr, prev_scope_id_dict, curr_scope_id_dict)[0], source_refs=ref)])

        body = []
        for piece in node.body:
            body.extend(self.visit(piece, prev_scope_id_dict, curr_scope_id_dict))

        return variables + body        
