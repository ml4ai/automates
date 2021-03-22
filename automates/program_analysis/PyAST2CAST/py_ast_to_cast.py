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
    def visit_Assign(self, node: ast.Assign):
        print("Assign") 
        # TODO: multiple assignments to same value, and 'unpacking' tuple/list
        # TODO: Subscript
        print("assign: node.targets",node.targets)
        left = None
        right = None
        # Simple assignment like x = ...
        if(len(node.targets) == 1):
            #print("assign: left",left)            
            #print("assign: node.value", node.value)
            left = self.visit(node.targets[0])
            right = self.visit(node.value)

        # Assignments in the form of x = y = z = ....
        # TODO: Still needs work
        if(len(node.targets) > 1):
            left = Var(node.targets[0].id, "integer")
            right = self.visit(node)

        return Assignment(left,right)

    def visit_Attribute(self, node:ast.Attribute):
        value = self.visit(node.value)
        attr = self.visit(node.attr)
        return Attribute(value,attr)

    def visit_BinOp(self, node: ast.BinOp):
        #print("BINOP")
        ops = {ast.Add : BinaryOperator.ADD, ast.Sub : BinaryOperator.SUB, ast.Mult : BinaryOperator.MULT,
                ast.Div : BinaryOperator.DIV, ast.FloorDiv : BinaryOperator.FLOORDIV, ast.Mod : BinaryOperator.MOD,
                ast.Pow : BinaryOperator.POW, ast.LShift : BinaryOperator.LSHIFT, ast.RShift : BinaryOperator.RSHIFT,
                ast.BitOr : BinaryOperator.BITOR, ast.BitAnd : BinaryOperator.BITAND, ast.BitXor : BinaryOperator.BITXOR}
        left = node.left
        #print(left)
        #print("OP",ops[type(node.op)])
        op = ops[type(node.op)]
        right = node.right
        #print(right)

        return BinaryOp(op,self.visit(left),self.visit(right))

    def visit_Break(self, node:ast.Break):
        """Visits a PyAST Break node, which is just a break statement
           nothing to be done for a Break node, just return a ModelBreak() object

        Args:
            node (ast.Break): An AST Break node

        Returns:
            ModelBreak(): 
        """

        return ModelBreak()

    def visit_Call(self, node:ast.Call):
        print("call: id",node.func.id)
        args = [self.visit(arg) for arg in node.args]
        return Call(Name(node.func.id),args)

    def visit_ClassDef(self, node:ast.ClassDef):
        name = node.name
        print("why am i here",node)
        print("why am i here",name)
        print("why am i here",node.bases)
        print("why am i here",node.body)
        bases = [self.visit(func) for base in node.bases]
        funcs = [self.visit(func) for func in node.body]
        fields = []

        return ClassDef(name,bases,funcs,fields)

    def visit_Compare(self, node: ast.Compare):
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
        print("constant")
        if(type(node.value) == int or type(node.value) == float):
            print("constant: node.value",type(node.value))
            return Number(node.value)
        elif(type(node.value) == str):
            print("constant: node.value",type(node.value))
            return String(node.value)
        else:
            print("constant: unknown type", type(node.value))
            return None

    def visit_Continue(self, node:ast.Continue):
        """Visits a PyAST Continue node, which is just a continue statement
           nothing to be done for a Continue node, just return a ModelContinue() object


        Args:
            node (ast.Continue): An AST Continue node

        Returns:
            ModelContinue(): 
        """

        return ModelContinue()

    def visit_Dict(self, node:ast.Dict):
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
        print("expr: node.value",node.value)
        return Expr(self.visit(node.value))

    def visit_For(self, node: ast.For):
        print("LOOP")
        print(type(node))
        target = self.visit(node.target)
        iterable = self.visit(node.iter)
        
        body = [self.visit(piece) for piece in (node.body+node.orelse)]

        return Loop(expr=[target,iterable],body=body)

    def visit_FunctionDef(self, node: Union[ast.FunctionDef,ast.Lambda]):
        if(type(node) == ast.FunctionDef):
            # Might have to change this Name() to a visit 
            #func_def = FunctionDef(Name(node.name))
            body = []
            args = [] 
            # TODO: Function Args func_def.func_args(self.visit(node.args))
            if(node.args.args != []):
                args = [Var(Name(arg.arg),"integer") for arg in node.args.args]
            if(node.body != []):
                body = [self.visit(piece) for piece in node.body]

            #TODO: Decorators? Returns? Type_comment?
            return FunctionDef(Name(node.name),args,body)

        if(type(node) == ast.Lambda):
            print("Lambda Function")
            func_def = FunctionDef(None)
            # TODO: Function Args func_def.func_args(self.visit(node.args))
            func_def.body(self.visit(node.body))

            return func_def

    def visit_If(self, node: ast.If):
        print(node.test)
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
        if(node.elts != []):
            return List([self.visit(piece) for piece in node.elts])
        else:
            return List([])

    def visit_Module(self, node: ast.Module):
        # Visit all the nodes and make a Module object out of them
        return Module(name="Program",body=[self.visit(piece) for piece in node.body])

    def visit_Name(self, node:ast.Name):
        """This visits PyAST Name nodes, which consist of
           id: The name of a variable as a string
           ctx: The context in which the variable is being used

        Args:
            node (ast.Name): [description]
        """
        print("in name")
        print("name: node.ctx", type(node.ctx))
        if(type(node.ctx) == ast.Load):
            print("name: in load")
            return Name(node.id)
        if(type(node.ctx) == ast.Store):
            print("name: in store")
            # TODO: how to get type?
            return Var(Name(node.id), "integer")    
        if(type(node.ctx) == ast.Del):
            # TODO: At some point..
            return None


    def visit_Pass(self, node: ast.Pass):
        return []

    def visit_Return(self, node:ast.Return):
        """Visits a PyAST Return node and creates a CAST return node
           that has one field, which is the expression computing the value
           to be returned. The PyAST's value node is visited.
           The CAST node is then returned.

        Args:
            node (ast.Return): A PyAST Return node
        """

        return ModelReturn(self.visit(node.value))

    def visit_UnaryOp(self, node: ast.UnaryOp):
        ops = {ast.UAdd : UnaryOperator.UADD, ast.USub : UnaryOperator.USUB, ast.Not : UnaryOperator.NOT,
                ast.Invert : UnaryOperator.INVERT}
        op = ops[type(node.op)]
        operand = node.operand

        return UnaryOp(op, self.visit(operand))

    def visit_Set(self, node:ast.Set):
        if(node.elts != []):
            return Set([self.visit(piece) for piece in node.elts])
        else:
            return Set([])


    def visit_Subscript(self, node:ast.Subscript):
        """Visits a PyAST Subscript node, and returns a CAST Subscript node
           
        Args:
            node (ast.Subscript): [description]
        """

        value = self.visit(node.value)
        print("subscript: node.slice",node.slice)
        sl = self.visit(node.slice)

        return Subscript(value,sl)

    def visit_Index(self, node:ast.Index):
        return self.visit(node.value)

    def visit_Tuple(self, node:ast.Tuple):
        if(node.elts != []):
            return Tuple([self.visit(piece) for piece in node.elts])
        else:
            return Tuple([])


        

    def visit_While(self, node: ast.While):
        print("LOOP")
        print(type(node))
        test = self.visit(node.test)
        body = [self.visit(piece) for piece in (node.body+node.orelse)]

        return Loop(expr=test,body=body)
        