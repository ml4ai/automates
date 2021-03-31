from typing import Union
import ast

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

class PyASTToCAST(ast.NodeVisitor):
    """Class PyASTToCast
    This class is used to convert a Python program into a CAST object.
    In particular, given a PyAST object that represents the Python program's
    Abstract Syntax Tree, we create a Common Abstract Syntax Tree representation of it.
    Most of the functions involve visiting the children to generate their CAST, and then
    connecting them to their parent to form the parent node's CAST representation.

    This class inherits from ast.NodeVisitor, to allow us to use the Visitor design pattern
    to visit all the different kinds of PyAST nodes in a similar fashion. 

    This class has no inherent fields of its own at this time. 
    """

    def visit_Assign(self, node: ast.Assign):
        """Visits a PyAST Assign node, and returns its CAST representation.
        Either the assignment is simple, like x = {expression},
        or the assignment is complex, like x = y = z = ... {expression}
        Which determines how we generate the CAST for this node.

        Args:
            node (ast.Assign): A PyAST Assignment node. 

        Returns:
            Assignment: An assignment node in CAST
        """
        left = None
        right = None
        # Simple assignment like x = ...
        if(len(node.targets) == 1):
            left = self.visit(node.targets[0])
            right = self.visit(node.value)

        # Assignments in the form of x = y = z = ....
        if(len(node.targets) > 1):
            left = self.visit(node.targets[0])
            node.targets = node.targets[1:]
            right = self.visit(node)

        return Assignment(left,right)

    def visit_Attribute(self, node:ast.Attribute):
        """Visits a PyAST Attribute node, which is used when accessing
        the attribute of a class. Whether it's a field or method of a class.

        Args:
            node (ast.Attribute): A PyAST Attribute node

        Returns:
            Attribute: A CAST Attribute node representing an Attribute access
        """

        value = self.visit(node.value)
        attr = Name(node.attr)
        return Attribute(value,attr)

    def visit_BinOp(self, node: ast.BinOp):
        """Visits a PyAST BinOp node, which consists of all the arithmetic and bitwise operators.

        Args:
            node (ast.BinOp): A PyAST Binary operator node

        Returns:
            BinaryOp: A CAST binary operator node representing a math operation (arithmetic or bitwise)
        """
        ops = {ast.Add : BinaryOperator.ADD, ast.Sub : BinaryOperator.SUB, ast.Mult : BinaryOperator.MULT,
                ast.Div : BinaryOperator.DIV, ast.FloorDiv : BinaryOperator.FLOORDIV, ast.Mod : BinaryOperator.MOD,
                ast.Pow : BinaryOperator.POW, ast.LShift : BinaryOperator.LSHIFT, ast.RShift : BinaryOperator.RSHIFT,
                ast.BitOr : BinaryOperator.BITOR, ast.BitAnd : BinaryOperator.BITAND, ast.BitXor : BinaryOperator.BITXOR}
        left = node.left
        op = ops[type(node.op)]
        right = node.right

        return BinaryOp(op,self.visit(left),self.visit(right))

    def visit_Break(self, node:ast.Break):
        """Visits a PyAST Break node, which is just a break statement
           nothing to be done for a Break node, just return a ModelBreak() object

        Args:
            node (ast.Break): An AST Break node

        Returns:
            ModelBreak: A CAST Break node
        """

        return ModelBreak()

    def visit_Call(self, node:ast.Call):
        """Visits a PyAST Call node, which represents a function call.
        Special care must be taken to see if it's a function call or a class's method call.
        The CAST is generated a little different depending on what kind of call it is.

        Args:
            node (ast.Call): a PyAST Call node

        Returns:
            Call: A CAST function call node
        """
        args = [self.visit(arg) for arg in node.args]
        if(type(node.func) == ast.Attribute):
            return Call(self.visit(node.func),args)
        else:
            return Call(Name(node.func.id),args)

    def visit_ClassDef(self, node:ast.ClassDef):
        """Visits a PyAST ClassDef node, which is used to define user classes.
        Acquiring the fields of the class involves going through the __init__ function
        and seeing if the attributes are associated with the self parameter.
        Otherwise, it's a pretty straight conversion.

        Args:
            node (ast.ClassDef): A PyAST class definition node

        Returns:
            ClassDef: A CAST class definition node
        """
        name = node.name
        bases = [self.visit(base) for base in node.bases]
        funcs = [self.visit(func) for func in node.body]
        fields = []
        
        # Get the fields in the class
        init_func = None
        for f in node.body:
            if(type(f) == ast.FunctionDef and f.name=="__init__"):
                init_func = f.body
                break
        
        for node in init_func:
            if(type(node) == ast.Assign and type(node.targets[0]) == ast.Attribute):
                attr_node = node.targets[0]
                if(attr_node.value.id == 'self'):
                    fields.append(Var(Name(attr_node.attr),"integer"))
                
        return ClassDef(name,bases,funcs,fields)

    def visit_Compare(self, node: ast.Compare):
        """Visits a PyAST Compare node, which consists of boolean operations

        Args:
            node (ast.Compare): A PyAST Compare node

        Returns:
            BinaryOp: A BinaryOp node, which in this case will hold a boolean operation
        """
        left = node.left
        ops = {ast.And : BinaryOperator.AND, ast.Or : BinaryOperator.OR, ast.Eq : BinaryOperator.EQ, 
        ast.NotEq : BinaryOperator.NOTEQ, ast.Lt : BinaryOperator.LT, ast.LtE : BinaryOperator.LTE,  
        ast.Gt : BinaryOperator.GT, ast.GtE : BinaryOperator.GTE, ast.In: BinaryOperator.IN,  
        ast.NotIn : BinaryOperator.NOTIN
        }

        # TODO: Change these to handle more than one comparison operation and
        # Operand (i.e. handle 1 < x < 10)
        op = ops[type(node.ops[0])]
        right = node.comparators[0]

        return BinaryOp(op,self.visit(left),self.visit(right))

    def visit_Constant(self, node:ast.Constant):
        """Visits a PyAST Constant node, which can hold either numeric or string values.
        A dictionary is used to index into which operation we're doing.

        Args:
            node (ast.Constant): A PyAST Constant node

        Returns:
            Number: A CAST numeric node, if the node's value is an int or float
            String: A CAST string node, if the node's value is a string
            None: If the node's value is something else that isn't recognized by the other two cases
        """
        if(type(node.value) == int or type(node.value) == float):
            return Number(node.value)
        elif(type(node.value) == str):
            return String(node.value)
        else:
            return None

    def visit_Continue(self, node:ast.Continue):
        """Visits a PyAST Continue node, which is just a continue statement
           nothing to be done for a Continue node, just return a ModelContinue() object

        Args:
            node (ast.Continue): An AST Continue node

        Returns:
            ModelContinue: A CAST Continue node
        """

        return ModelContinue()

    def visit_Dict(self, node:ast.Dict):
        """Visits a PyAST Dict node, which represents a dictionary.

        Args:
            node (ast.Dict): A PyAST dictionary node

        Returns:
            Dict: A CAST Dictionary node. 
        """
        if(node.keys != []):
            keys = [self.visit(piece) for piece in node.keys]
        else:
            keys = []
        if(node.values != []):
            values = [self.visit(piece) for piece in node.values]
        else:
            values = []

        return Dict(keys,values)

    def visit_Expr(self, node: ast.Expr):
        """Visits a PyAST Expr node, which represents some kind of standalone expression.

        Args:
            node (ast.Expr): A PyAST Expression node

        Returns:
            Expr: A CAST Expression node
        """
        return Expr(self.visit(node.value))

    def visit_For(self, node: ast.For):
        """Visits a PyAST For node, which represents Python for loops.
        A For loop is different than a While loop, in that we need to do a conversion
        such that the resulting CAST Loop appropriately captures a node that is more 
        like a While loop (i.e. using a condition to terminate the loop instead of iterating).

        Args:
            node (ast.For): A PyAST For loop node.

        Returns:
            Loop: A CAST loop node, which generically represents both For loops and While loops.
        """
        target = self.visit(node.target)
        iterable = self.visit(node.iter)
        
        body = [self.visit(piece) for piece in (node.body+node.orelse)]

        #TODO: Works with iterating over lists in the form of for i in LIST,
        #Figure out how to do range() and other function calls
        count_var = Assignment(Var(Name("i_"),"integer"),Number(0))
        loop_cond = BinaryOp(BinaryOperator.LT,Name("i_"),Call(Name("len"),[Name(node.iter.id)]))
        loop_assign = Assignment(Var("integer",Name(node.target.id)),Subscript(Name(node.iter.id),Name("i_")))
        loop_increment = Assignment(Var(Name("i_"),"integer"),BinaryOp(BinaryOperator.ADD,Name("i_"),Number(1)))

        return Loop(expr=loop_cond,body=[loop_assign]+body+[loop_increment])

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visits a PyAST FunctionDef node. Which is used for a Python function definition.

        Args:
            node (ast.FunctionDef): A PyAST function definition node

        Returns:
            FunctionDef: A CAST Function Definition node
        """
        body = []
        args = [] 
        # TODO: Correct typing instead of just 'integer'
        if(node.args.args != []):
            args = [Var(Name(arg.arg),"integer") for arg in node.args.args]
        if(node.body != []):
            body = [self.visit(piece) for piece in node.body]

        #TODO: Decorators? Returns? Type_comment?
        return FunctionDef(node.name,args,body)
            
    def visit_Lambda(self, node: ast.Lambda):
        """Visits a PyAST Lambda node. Which is used for a Python Lambda function definition.
        It works pretty analogously to the FunctionDef node visitor. 
        It also returns a FunctionDef node like the PyAST FunctionDef node visitor.

        Args:
            node (ast.Lambda): A PyAST lambda function definition node

        Returns:
            FunctionDef: A CAST Function Definition node

        """
        body = self.visit(node.body)
        args = [] 
        # TODO: Correct typing instead of just 'integer'
        if(node.args.args != []):
            args = [Var(Name(arg.arg),"integer") for arg in node.args.args]

        return FunctionDef("LAMBDA",args,body)

    def visit_If(self, node: ast.If):
        """Visits a PyAST If node. Which is used to represent If statements.
        We visit each of the pieces accordingly and construct the CAST representation.
        else/elif statements are stored in the 'orelse' field, if there are any.

        Args:
            node (ast.If): A PyAST If node.

        Returns:
            ModelIf: A CAST If statement node.
        """
        node_test = self.visit(node.test)
        
        if(node.body != []):
            node_body = [self.visit(piece) for piece in node.body]
        else:
            node_body = []

        if(node.orelse != []):
            node_orelse = [self.visit(piece) for piece in node.orelse]
        else:  
            node_orelse = []
        
        return ModelIf(node_test, node_body, node_orelse)

    def visit_List(self, node:ast.List):
        """Visits a PyAST List node. Which is used to represent Python lists.

        Args:
            node (ast.List): A PyAST List node.

        Returns:
            List: A CAST List node.
        """
        if(node.elts != []):
            return List([self.visit(piece) for piece in node.elts])
        else:
            return List([])

    def visit_Module(self, node: ast.Module):
        """Visits a PyAST Module node. This is the starting point of CAST Generation,
        as the body of the Module node (usually) contains the entire Python program.

        Args:
            node (ast.Module): A PyAST Module node.

        Returns:
            Module: A CAST Module node.
        """
        # Visit all the nodes and make a Module object out of them
        return Module(name="Program",body=[self.visit(piece) for piece in node.body])

    def visit_Name(self, node:ast.Name):
        """This visits PyAST Name nodes, which consist of
           id: The name of a variable as a string
           ctx: The context in which the variable is being used

        Args:
            node (ast.Name): A PyAST Name node

        Returns:
            Expr: A CAST Expression node


        """
        if(type(node.ctx) == ast.Load):
            return Name(node.id)
        if(type(node.ctx) == ast.Store):
            # TODO: how to get type?
            return Var(Name(node.id), "integer")    
        if(type(node.ctx) == ast.Del):
            # TODO: At some point..
            return None


    def visit_Pass(self, node: ast.Pass):
        """A PyAST Pass visitor, for essentially NOPs.
        """
        return []

    def visit_Return(self, node:ast.Return):
        """Visits a PyAST Return node and creates a CAST return node
           that has one field, which is the expression computing the value
           to be returned. The PyAST's value node is visited.
           The CAST node is then returned.

        Args:
            node (ast.Return): A PyAST Return node

        Returns:
            ModelReturn: A CAST Return node
        """

        return ModelReturn(self.visit(node.value))

    def visit_UnaryOp(self, node: ast.UnaryOp):
        """Visits a PyAST UnaryOp node. Which represents Python unary operations.
        A dictionary is used to index into which operation we're doing.

        Args:
            node (ast.UnaryOp): A PyAST UnaryOp node.

        Returns:
            UnaryOp: A CAST UnaryOp node.
        """
        ops = {ast.UAdd : UnaryOperator.UADD, ast.USub : UnaryOperator.USUB, ast.Not : UnaryOperator.NOT,
                ast.Invert : UnaryOperator.INVERT}
        op = ops[type(node.op)]
        operand = node.operand

        return UnaryOp(op, self.visit(operand))

    def visit_Set(self, node:ast.Set):
        """Visits a PyAST Set node. Which is used to represent Python sets.

        Args:
            node (ast.Set): A PyAST Set node.

        Returns:
            Set: A CAST Set node.
        """
        if(node.elts != []):
            return Set([self.visit(piece) for piece in node.elts])
        else:
            return Set([])

    def visit_Subscript(self, node:ast.Subscript):
        """Visits a PyAST Subscript node, which represents subscripting into a list in Python
           
        Args:
            node (ast.Subscript): A PyAST Subscript node

        Returns:
            Subscript: A CAST Subscript node
        """
        value = self.visit(node.value)
        sl = self.visit(node.slice)

        return Subscript(value,sl)

    def visit_Index(self, node:ast.Index):
        """Visits a PyAST Index node, which represents the value being used for an index.
        This visitor doesn't create its own CAST node, but returns CAST depending on the
        value that the Index node holds.

        Args:
            node (ast.Index): A CAST Index node.

        Returns:
            AstNode: Depending on what the value of the Index node is, different CAST nodes are returned.
        """
        return self.visit(node.value)

    def visit_Tuple(self, node:ast.Tuple):
        """Visits a PyAST Tuple node. Which is used to represent Python tuple.

        Args:
            node (ast.Tuple): A PyAST Tuple node.

        Returns:
            Set: A CAST Tuple node.
        """
        if(node.elts != []):
            return Tuple([self.visit(piece) for piece in node.elts])
        else:
            return Tuple([])

    def visit_While(self, node: ast.While):
        """Visits a PyAST While node, which represents a while loop. 

        Args:
            node (ast.While): a PyAST while node

        Returns:
            Loop: A CAST loop node, which generically represents both For loops and While loops.
        """
        test = self.visit(node.test)
        body = [self.visit(piece) for piece in (node.body+node.orelse)]

        return Loop(expr=test,body=body)
        