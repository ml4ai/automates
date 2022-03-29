from typing import Type, Union
import ast
import os 
import sys
from functools import singledispatchmethod

from numpy import isin

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
    def __init__(self, file_name: str):
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
        """

        self.aliases = {}
        self.visited = set()
        self.filenames = [file_name]
        self.classes = {}
        self.var_count = 0
        self.global_identifier_dict = {}
        self.id_count = 0

    @singledispatchmethod
    def visit(self, node: AstNode, prev_scope_id_dict: Dict):
        pass

    @visit.register
    def visit_Assign(self, node: ast.Assign, prev_scope_id_dict: Dict):
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

        if len(node.targets) == 1:
            l_visit = self.visit(node.targets[0], prev_scope_id_dict)
            r_visit = self.visit(node.value, prev_scope_id_dict)
            left.extend(l_visit)
            right.extend(r_visit)
        elif len(node.targets) > 1:
            left.extend(self.visit(node.targets[0],prev_scope_id_dict))
            node.targets = node.targets[1:]
            right.extend(self.visit(node,prev_scope_id_dict))
        else:
            raise ValueError(f"Unexpected number of targets for node: {len(node.targets)}")


        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]

        return [Assignment(left[0], right[0], source_refs=ref)]

    @visit.register
    def visit_Attribute(self, node: ast.Attribute, prev_scope_id_dict: Dict):
        """Visits a PyAST Attribute node, which is used when accessing
        the attribute of a class. Whether it's a field or method of a class.

        Args:
            node (ast.Attribute): A PyAST Attribute node

        Returns:
            Attribute: A CAST Attribute node representing an Attribute access
        """

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]

        value = self.visit(node.value, prev_scope_id_dict)
        
        # TODO: We need a variable ID name here, which one?
        attr = Name(node.attr, id=-1, source_refs=ref)

        return [Attribute(value[0], attr, source_refs=ref)]

    @visit.register
    def visit_AugAssign(self, node:ast.AugAssign, prev_scope_id_dict: Dict):
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


        return self.visit(convert, prev_scope_id_dict)


    @visit.register
    def visit_BinOp(self, node: ast.BinOp, prev_scope_id_dict: Dict):
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
        left = self.visit(node.left, prev_scope_id_dict)
        op = ops[type(node.op)]
        right = self.visit(node.right, prev_scope_id_dict)

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        leftb = []
        rightb = []

        if len(left) > 1:
            leftb = left[0:-1]
        if len(right) > 1:
            rightb = right[0:-1]

        return leftb + rightb + [BinaryOp(op, left[-1], right[-1], source_refs=ref)]

    @visit.register
    def visit_Break(self, node: ast.Break, prev_scope_id_dict: Dict):
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
    def visit_BoolOp(self, node: ast.BoolOp, prev_scope_id_dict: Dict):
        """Visits a BoolOp node, which is a boolean operation connected with 'and'/'or's 
           The BoolOp node gets converte into an AST Compare node, and then the work is 
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
        return self.visit(compare_op, prev_scope_id_dict) 

    @visit.register
    def visit_Call(self, node: ast.Call, prev_scope_id_dict: Dict):
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
                func_args.extend(self.visit(arg, prev_scope_id_dict))

        if len(node.keywords) > 0:
            for arg in node.keywords:
                kw_args.extend(self.visit(arg.value, prev_scope_id_dict))

        args = func_args + kw_args

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        if isinstance(node.func,ast.Attribute):
            res = self.visit(node.func, prev_scope_id_dict)
            return [Call(res[0], args, source_refs=ref)]
        else:
            # TODO: We need an id here, which one?
            return [Call(Name(node.func.id, id=-1, source_refs=ref), args, source_refs=ref)]

    @visit.register
    def visit_ClassDef(self, node: ast.ClassDef, prev_scope_id_dict: Dict):
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
    def visit_Compare(self, node: ast.Compare, prev_scope_id_dict: Dict):
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
        l = self.visit(left, prev_scope_id_dict)
        r = self.visit(right, prev_scope_id_dict)
        return [BinaryOp(op, l[0], r[0], source_refs=ref)]

    @visit.register
    def visit_Constant(self, node: ast.Constant, prev_scope_id_dict: Dict):
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
    def visit_Continue(self, node: ast.Continue, prev_scope_id_dict: Dict):
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
    def visit_Dict(self, node: ast.Dict, prev_scope_id_dict: Dict):
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
                keys.extend(self.visit(piece, prev_scope_id_dict))

        if len(node.values) > 0:
            for piece in node.values:
                values.extend(self.visit(piece, prev_scope_id_dict))

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        return [Dict(keys, values, source_refs=ref)]

    @visit.register
    def visit_Expr(self, node: ast.Expr, prev_scope_id_dict: Dict):
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
        val = self.visit(node.value, prev_scope_id_dict)
        if len(val) > 1:
            return val
        return [Expr(val[0],source_refs=ref)]

    @visit.register
    def visit_For(self, node: ast.For, prev_scope_id_dict: Dict):
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

        target = self.visit(node.target, prev_scope_id_dict)[0]
        iterable = self.visit(node.iter, prev_scope_id_dict)[0]

        body = []
        for piece in (node.body + node.orelse):
            body.extend(self.visit(piece, prev_scope_id_dict))

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        var_name = f"generated_index_{self.var_count}"
        list_name = f"generated_list_{self.var_count}"
        self.var_count += 1

        # TODO: Mark these as variables that were generated by this script at some point
        # TODO: Need some identifiers for these
        count_var = Assignment(Var(Name(var_name, id=-1, source_refs=ref), "float", source_refs=ref), Number(0, source_refs=ref), source_refs=ref)
        list_var = Assignment(Var(Name(list_name, id=-1, source_refs=ref), "list", source_refs=ref), Call(Name("list", id=-1,source_refs=ref),[iterable],source_refs=ref), source_refs=ref)

        loop_cond = BinaryOp(
            BinaryOperator.LT,
            Name(var_name, source_refs=ref),
            Call(Name("len", source_refs=ref), [Name(list_name,source_refs=ref)], source_refs=ref),
            source_refs=ref
        )

        if isinstance(node.iter,ast.Call):
            if isinstance(node.target,ast.Tuple):
                loop_assign = [Assignment(
                    Tuple([Var(type="float",val=Name(f"{node.val.name}_",source_refs=ref),source_refs=ref) for node in target.values],source_refs=ref),
                    Subscript(Name(list_name, source_refs=ref),Name(var_name,source_refs=ref),source_refs=ref),
                    source_refs=ref
                ),
                Assignment(
                    target,
                    Tuple([Var(type="float",val=Name(f"{node.val.name}_",source_refs=ref),source_refs=ref) for node in target.values], source_refs=ref),
                    source_refs=ref
                )]
            else:
                loop_assign = [Assignment(
                    Var(Name(node.target.id,source_refs=ref), "float", source_refs=ref),
                    Subscript(Name(list_name, source_refs=ref), Name(var_name, source_refs=ref),source_refs=ref),
                    source_refs=ref
                )]
        elif isinstance(node.iter,ast.Attribute):
            if isinstance(node.target,ast.Tuple):
                loop_assign = [Assignment(
                    Tuple([Var(type="float",val=Name(f"{node.val.name}_",source_refs=ref),source_refs=ref) for node in target.values],source_refs=ref),
                    Subscript(Name(node.iter.id,source_refs=ref), Name(var_name,source_refs=ref),source_refs=ref),
                    source_refs=ref
                ),
                Assignment(
                    target,
                    Tuple([Var(type="float",val=Name(f"{node.val.name}_",source_refs=ref),source_refs=ref) for node in target.values],source_refs=ref),
                    source_refs=ref
                )]
            else:
                loop_assign = [Assignment(
                    Var(Name(node.target.id, source_refs=ref), "float", source_refs=ref),
                    Subscript(Name(list_name, source_refs=ref), Name(var_name, source_refs=ref), source_refs=ref),
                    source_refs=ref
                )]
        else:
            if isinstance(node.target,ast.Tuple):
                loop_assign = [Assignment(
                    Tuple([Var(type="float",val=Name(f"{node.val.name}_",source_refs=ref),source_refs=ref) for node in target.values],source_refs=ref),
                    Subscript(Name(node.iter.id,source_refs=ref), Name(var_name,source_refs=ref),source_refs=ref),
                    source_refs=ref
                ),
                Assignment(
                    target,
                    Tuple([Var(type="float",val=Name(f"{node.val.name}_",source_refs=ref),source_refs=ref) for node in target.values],source_refs=ref),
                    source_refs=ref
                )]
            else:
                loop_assign = [Assignment(
                    Var(Name(node.target.id, source_refs=ref), "float", source_refs=ref),
                    Subscript(Name(list_name, source_refs=ref), Name(var_name, source_refs=ref), source_refs=ref),
                    source_refs=ref
                )]
        loop_increment = [Assignment(
            Var(Name(var_name, source_refs=ref), "float", source_refs=ref),
            BinaryOp(BinaryOperator.ADD, Name(var_name, source_refs=ref), Number(1, source_refs=ref), source_refs=ref),
            source_refs=ref
        )]

        return [count_var, list_var, Loop(expr=loop_cond, body=loop_assign + body + loop_increment, source_refs=ref)]

    @visit.register
    def visit_FunctionDef(self, node: ast.FunctionDef, prev_scope_id_dict: Dict):
        """Visits a PyAST FunctionDef node. Which is used for a Python
        function definition.

        Args:
            node (ast.FunctionDef): A PyAST function definition node

        Returns:
            FunctionDef: A CAST Function Definition node
        """

        # TODO: SCOPING

        body = []
        args = []
        # TODO: Correct typing instead of just 'float'
        cur_scope_identifier_dict = {}
        if len(node.args.args) > 0:
            args = [Var(Name(arg.arg,id=-1,source_refs=[SourceRef(self.filenames[-1], arg.col_offset, arg.end_col_offset, arg.lineno, arg.end_lineno)]), 
                    "float", 
                    source_refs=[SourceRef(self.filenames[-1], arg.col_offset, arg.end_col_offset, arg.lineno, arg.end_lineno)]) 
                    for arg in node.args.args]

        functions_to_visit = []

        if len(node.body) > 0:
            # To account for nested loops we check to see if the CAST node is in a list and
            # extend accordingly
            for piece in node.body:
                # We defer visiting function defs until we've cleared the other variables in this function
                if isinstance(piece, ast.FunctionDef):
                    cur_scope_identifier_dict[piece.name] = self.id_count
                    self.id_count += 1
                    functions_to_visit.append(piece)
                    continue
                
                # If we have any global declarations we use their 
                # ids instead of the local variables
                #if isinstance(piece, ast.Global):
                 #   for v in piece.names:
                  #      cur_scope_identifier_dict[v] = self.global_identifier_dict[v]   
               # if isinstance(piece,ast.Name):
                    # On a load, the variable either exists in the current scope, or on the previous one
                    # So we load the identifier appropriately, or if it's not in the current scope, load from the previous scope
                #    if isinstance(piece.ctx,ast.Load):
                 #       if piece.id not in cur_scope_identifier_dict:
                  #          cur_scope_identifier_dict[piece.id] = prev_scope_id_dict[piece.id]

                    # On a store, the variable is either in the previous scope, or doesn't exist
                    # If it doesn't exist then we have to create it and store it
                   # if isinstance(piece.ctx, ast.Store):
                    #    if piece.id not in cur_scope_identifier_dict:
                     #       cur_scope_identifier_dict[piece.id] = self.id_count
                      #      self.id_count += 1
                                 
                print(piece)
                to_add = self.visit(piece, cur_scope_identifier_dict)
                if isinstance(to_add,Module):
                    body.extend([to_add])
                elif hasattr(to_add, "__iter__") or hasattr(to_add, "__getitem__"):
                    body.extend(to_add)
                else:
                    raise TypeError(f"Unexpected type in visit_FuncDef: {type(to_add)}")

            # Visit the functions here
            for piece in functions_to_visit:
                
                # Currently visiting the entire function, instead of just the body
                # This might have to change to properly reflect the GIST in github
                to_add = self.visit(piece, prev_scope_id_dict)
                body.extend(to_add)


        # TODO: Decorators? Returns? Type_comment?
        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        return [FunctionDef(node.name, args, body, source_refs=ref)]

    @visit.register
    def visit_Lambda(self, node: ast.Lambda, prev_scope_id_dict: Dict):
        """Visits a PyAST Lambda node. Which is used for a Python Lambda
        function definition. It works pretty analogously to the FunctionDef
        node visitor. It also returns a FunctionDef node like the PyAST
        FunctionDef node visitor.

        Args:
            node (ast.Lambda): A PyAST lambda function definition node

        Returns:
            FunctionDef: A CAST Function Definition node

        """

        # TODO: SCOPING?


        body = self.visit(node.body, prev_scope_id_dict)
        args = []
        # TODO: Correct typing instead of just 'float'
        if len(node.args.args) > 0:
            args = [Var(Name(arg.arg,source_refs=[SourceRef(self.filenames[-1], arg.col_offset, arg.end_col_offset, arg.lineno, arg.end_lineno)]), 
                    "float",
                    source_refs=[SourceRef(self.filenames[-1], arg.col_offset, arg.end_col_offset, arg.lineno, arg.end_lineno)]) 
                    for arg in node.args.args]

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        return [FunctionDef("LAMBDA", args, body, source_refs=ref)]

    @visit.register
    def visit_ListComp(self, node: ast.ListComp, prev_scope_id_dict: Dict):
        """Visits a PyAST ListComp node, which are used for Python list comprehensions.
        List comprehensions generate a list from some generator expression.

        Args:
            node (ast.ListComp): A PyAST list comprehension node

        Returns:
            Loop: 
        """

        generators = node.generators

        first_gen = generators[0]
        i = 1
        outer_loop = None

        ref = [self.filenames[-1], node.col_offset, node.end_col_offset, node.lineno, node.end_lineno]

        if isinstance(first_gen.iter,ast.Subscript):
            if isinstance(first_gen.target,ast.Tuple):
                outer_loop = ast.For(target=first_gen.target,iter=first_gen.iter.value,body=[node.elt],orelse=[], col_offset=ref[1], end_col_offset=ref[2], lineno=ref[3], end_lineno=ref[4])
            else:
                outer_loop = ast.For(target=ast.Name(id=first_gen.target.id,ctx=ast.Store(), col_offset=ref[1], end_col_offset=ref[2], lineno=ref[3], end_lineno=ref[4]),iter=first_gen.iter.value,body=[node.elt],orelse=[],col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])
        elif isinstance(first_gen.iter,ast.Call):
            if isinstance(first_gen.target,ast.Tuple):
                outer_loop = ast.For(target=first_gen.target,iter=first_gen.iter.func,body=[node.elt],orelse=[],col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])
            else:
                outer_loop = ast.For(target=ast.Name(id=first_gen.target.id,ctx=ast.Store(), col_offset=ref[1], end_col_offset=ref[2], lineno=ref[3], end_lineno=ref[4]),iter=first_gen.iter.func,body=[node.elt],orelse=[],col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])
        else:
            if isinstance(first_gen.target,ast.Tuple):
                outer_loop = ast.For(target=first_gen.target,iter=first_gen.iter,body=[node.elt],orelse=[],col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])
            else:
                outer_loop = ast.For(target=ast.Name(id=first_gen.target.id,ctx=ast.Store(), col_offset=ref[1], end_col_offset=ref[2], lineno=ref[3], end_lineno=ref[4]),iter=first_gen.iter,body=[node.elt],orelse=[],col_offset=ref[1],end_col_offset=ref[2],lineno=ref[3],end_lineno=ref[4])

        visit_loop = self.visit(outer_loop, prev_scope_id_dict)

        #TODO: Multiple generators, if statements
        while i < len(generators):    
            i += 1

        return visit_loop


    @visit.register
    def visit_If(self, node: ast.If, prev_scope_id_dict: Dict):
        """Visits a PyAST If node. Which is used to represent If statements.
        We visit each of the pieces accordingly and construct the CAST
        representation. else/elif statements are stored in the 'orelse' field,
        if there are any.

        Args:
            node (ast.If): A PyAST If node.

        Returns:
            ModelIf: A CAST If statement node.
        """

        node_test = self.visit(node.test, prev_scope_id_dict)

        node_body = []
        if len(node.body) > 0:
            for piece in node.body:
                node_body.extend(self.visit(piece, prev_scope_id_dict))

        node_orelse = []
        if len(node.orelse) > 0:
            for piece in node.orelse:
                node_orelse.extend(self.visit(piece, prev_scope_id_dict))

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]

        return [ModelIf(node_test[0], node_body, node_orelse, source_refs=ref)]

    @visit.register
    def visit_Global(self, node: ast.Global, prev_scope_id_dict: Dict):
        for v in node.names:
            prev_scope_id_dict[v] = self.global_identifier_dict[v]   
        return []

    @visit.register
    def visit_IfExp(self, node: ast.IfExp, prev_scope_id_dict: Dict):
        """Visits a PyAST IfExp node, which is Python's ternary operator.
        The node gets translated into a CAST ModelIf node by visiting all its parts,
        since IfExp behaves like an If statement.

        Args:
            node (ast.IfExp): [description]
        """

        node_test = self.visit(node.test, prev_scope_id_dict)
        node_body = self.visit(node.body, prev_scope_id_dict)
        node_orelse = self.visit(node.orelse, prev_scope_id_dict)
        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]

        return [ModelIf(node_test[0], node_body, node_orelse, source_refs=ref)]

    @visit.register
    def visit_Import(self, node:ast.Import, prev_scope_id_dict: Dict):
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


        if alias.asname is not None:
            self.aliases[alias.asname] = name
            name = alias.asname

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        if os.path.isfile(path):
            true_name = self.aliases[name] if name in self.aliases else name
            if true_name in self.visited:
                return [Module(name=true_name,body=[],source_refs=ref)]
            else:
                file_contents = open(path).read()
                self.visited.add(true_name)
                return self.visit(ast.parse(file_contents), {})
        else:
            return [Module(name=name,body=[],source_refs=ref)]


    @visit.register
    def visit_ImportFrom(self, node:ast.ImportFrom, prev_scope_id_dict: Dict):
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
                        visited_funcs.extend(self.visit(f, {}))
                    
                    self.filenames.pop()
                    return visited_funcs
                else: # Importing the entire file
                    full_file = self.visit(contents, {})
                    self.filenames.pop()
                    return full_file
        else:
            ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
            return [Module(name=name,body=[],source_refs=ref)]


    @visit.register
    def visit_List(self, node:ast.List, prev_scope_id_dict: Dict):
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
                to_ret.extend(self.visit(piece, prev_scope_id_dict))
            return [List(to_ret,source_refs=ref)]
        else:
            return [List([],source_refs=ref)]

    @visit.register
    def visit_Module(self, node: ast.Module, prev_scope_id_dict: Dict):
        """Visits a PyAST Module node. This is the starting point of CAST Generation,
        as the body of the Module node (usually) contains the entire Python
        program.

        Args:
            node (ast.Module): A PyAST Module node.

        Returns:
            Module: A CAST Module node.
        """

        # TODO: SCOPING

        # Visit all the nodes and make a Module object out of them
        body = []
        funcs = []
        for piece in node.body:
            # Assignments at the global level are a special case
            # These are global variables
            # We 'pretend' they're in a function by passing in the global map
            #if isinstance(piece, ast.Assign):
             #   for nm in piece.targets:
              #      if isinstance(nm, ast.Name):
               #         if not nm.id in self.global_identifier_dict.keys():
                            # Insert the name into global id_dict
                #            self.global_identifier_dict[nm.id] = self.id_count
                 #           self.id_count = self.id_count + 1
                # to_add = self.visit(piece, self.global_identifier_dict)
                # body.extend(to_add)
                # continue

            # Defer visiting function defs until all global vars are processed
            if isinstance(piece, ast.FunctionDef):
                self.global_identifier_dict[piece.name] = self.id_count
                self.id_count += 1
                funcs.append(piece)
                continue

            to_add = self.visit(piece, prev_scope_id_dict)
            if isinstance(piece, ast.Assign):
                for k in prev_scope_id_dict.keys():
                    self.global_identifier_dict[k] = prev_scope_id_dict[k]

            if isinstance(to_add,Module):
                body.extend([to_add])
            else:
                body.extend(to_add)

        # Visit all the functions
        for piece in funcs:
            to_add = self.visit(piece, prev_scope_id_dict)
            body.extend(to_add)

        return Module(name=self.filenames[-1].split(".")[0], body=body, source_refs=None)

    @visit.register
    def visit_Name(self, node: ast.Name, prev_scope_id_dict: Dict):
        """This visits PyAST Name nodes, which consist of
           id: The name of a variable as a string
           ctx: The context in which the variable is being used

        Args:
            node (ast.Name): A PyAST Name node

        Returns:
            Expr: A CAST Expression node

        """
        
        # TODO: SCOPING
        
        # ref = None #[self.filenames[-1], node.col_offset, node.end_col_offset, node.lineno, node.end_lineno]
        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]

        print(prev_scope_id_dict)
        #ref = [self.filenames[-1], node.col_offset, node.end_col_offset, node.lineno, node.end_lineno]
        if isinstance(node.ctx,ast.Load):
            if node.id in self.aliases: 
                return [Name(self.aliases[node.id], id=-1, source_refs=ref)]

            if node.id in prev_scope_id_dict:
                return [Name(node.id, id=prev_scope_id_dict[node.id], source_refs=ref)]
            else:
                prev_scope_id_dict[node.id] = self.global_identifier_dict[node.id]
                return [Name(node.id, id=self.global_identifier_dict[node.id], source_refs=ref)]
            
        if isinstance(node.ctx,ast.Store):
            if node.id in self.aliases: 
                return [Var(Name(self.aliases[node.id], id=-1, source_refs=ref), "float", source_refs=ref)]

            # TODO: Typing so it's not hardcoded to floats
            if node.id in prev_scope_id_dict:
                return [Var(Name(node.id, id=prev_scope_id_dict[node.id],source_refs=ref), "float", source_refs=ref)]
            else:
                prev_scope_id_dict[node.id] = self.id_count
                self.id_count += 1
                return [Var(Name(node.id, id=prev_scope_id_dict[node.id],source_refs=ref), "float", source_refs=ref)]

        if isinstance(node.ctx,ast.Del):
            # TODO: At some point..
            raise NotImplementedError()

    @visit.register
    def visit_Pass(self, node: ast.Pass, prev_scope_id_dict: Dict):
        """A PyAST Pass visitor, for essentially NOPs."""

        return []

    @visit.register
    def visit_Raise(self, node: ast.Raise, prev_scope_id_dict: Dict):
        """A PyAST Raise visitor, for Raising exceptions

           TODO: To be implemented.
        """

        return []

    @visit.register
    def visit_Return(self, node: ast.Return, prev_scope_id_dict: Dict):
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
        return [ModelReturn(self.visit(node.value, prev_scope_id_dict)[0], source_refs=ref)]

    @visit.register
    def visit_UnaryOp(self, node: ast.UnaryOp, prev_scope_id_dict: Dict):
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

        opd = self.visit(operand, prev_scope_id_dict)

        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        return [UnaryOp(op, opd[0], source_refs=ref)]

    @visit.register
    def visit_Set(self, node: ast.Set, prev_scope_id_dict: Dict):
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
                to_ret.extend(self.visit(piece, prev_scope_id_dict))
            return [Set(to_ret,source_refs=ref)]
        else:
            return [Set([], source_refs=ref)]

    @visit.register
    def visit_Subscript(self, node: ast.Subscript, prev_scope_id_dict: Dict):
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

        value = self.visit(node.value, prev_scope_id_dict)[0]
        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]

        # 'Visit' the slice 
        slc = node.slice
        temp_var = f"generated_index_{self.var_count}"
        self.var_count += 1

        if isinstance(slc,ast.Slice):
            if slc.lower is not None:
                lower = self.visit(slc.lower, prev_scope_id_dict)[0]
            else:
                lower = Number(0, source_refs=ref)
            
            if slc.upper is not None:
                upper = self.visit(slc.upper, prev_scope_id_dict)[0]
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
                step = self.visit(slc.step, prev_scope_id_dict)[0]
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
                        lower = self.visit(dim.lower, prev_scope_id_dict)[0]
                    else:
                        lower = Number(0, source_refs=ref)
                    
                    if dim.upper is not None:
                        upper = self.visit(dim.upper, prev_scope_id_dict)[0]
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
                        step = self.visit(dim.step, prev_scope_id_dict)[0]
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
                    curr_dim = self.visit(dim, prev_scope_id_dict)[0]

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
            sl = self.visit(slc, prev_scope_id_dict)

        return [Subscript(value, sl[0], source_refs=ref)]


    @visit.register
    def visit_Index(self, node: ast.Index, prev_scope_id_dict: Dict):
        """Visits a PyAST Index node, which represents the value being used
        for an index. This visitor doesn't create its own CAST node, but
        returns CAST depending on the value that the Index node holds.

        Args:
            node (ast.Index): A CAST Index node.

        Returns:
            AstNode: Depending on what the value of the Index node is,
                     different CAST nodes are returned.
        """

        return self.visit(node.value, prev_scope_id_dict)

    @visit.register
    def visit_Tuple(self, node: ast.Tuple, prev_scope_id_dict: Dict):
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
                to_ret.extend(self.visit(piece, prev_scope_id_dict))
            return [Tuple(to_ret, source_refs=ref)]
        else:
            return [Tuple([], source_refs=ref)]

    @visit.register
    def visit_Try(self, node:ast.Try, prev_scope_id_dict: Dict):
        """Visits a PyAST Try node, which represents Try/Except blocks.
        These are used for Python's exception handling

        Currently, the visitor just bypasses the Try/Except feature and just
        generates CAST for the body of the 'Try' block, assuming the exception(s)
        are never thrown.
        """

        body = []
        for piece in node.body:
            body.extend(self.visit(piece, prev_scope_id_dict))
            
        return body

    @visit.register
    def visit_While(self, node: ast.While, prev_scope_id_dict: Dict):
        """Visits a PyAST While node, which represents a while loop.

        Args:
            node (ast.While): a PyAST while node

        Returns:
            Loop: A CAST loop node, which generically represents both For
                  loops and While loops.
        """

        test = self.visit(node.test, prev_scope_id_dict)[0]

        body = []
        for piece in (node.body + node.orelse):
            to_add = self.visit(piece, prev_scope_id_dict)
            body.extend(to_add)
        
        ref = [SourceRef(source_file_name=self.filenames[-1], col_start=node.col_offset, col_end=node.end_col_offset, row_start=node.lineno, row_end=node.end_lineno)]
        return [Loop(expr=test, body=body, source_refs=ref)]


    @visit.register
    def visit_With(self, node: ast.With, prev_scope_id_dict: Dict):
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
            variables.extend([Assignment(left=self.visit(item.optional_vars, prev_scope_id_dict)[0],right=self.visit(item.context_expr, prev_scope_id_dict)[0], source_refs=ref)])

        body = []
        for piece in node.body:
            body.extend(self.visit(piece, prev_scope_id_dict))

        return variables + body        
