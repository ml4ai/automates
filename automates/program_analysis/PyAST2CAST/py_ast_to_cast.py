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

    def visit_Module(self, node: ast.Module):
        #print("Module")

        # Visit all the nodes and make a Module object out of them
        return Module(body=[self.visit(piece) for piece in node.body])

    def visit_ClassDef(self, node:ast.ClassDef):

        pass

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


    def visit_Loop(self, node: Union[ast.For,ast.While]):
        print(type(node))
        pass

    def visit_FunctionDef(self, node: Union[ast.FunctionDef,ast.Lambda]):
        print("Function Def")
        if(type(node) == ast.FunctionDef):
            print(type(node))

            # Might have to change this Name() to a visit 
            func_def = FunctionDef(Name(node.name))
            body = []
            # TODO: Function Args func_def.func_args(self.visit(node.args))
            if(node.body != []):
                body = [self.visit(piece) for piece in node.body]

            #TODO: Decorators? Returns? Type_comment?
            return FunctionDef(Name(node.name),[],body)

        if(type(node) == ast.Lambda):
            print("Lambda Function")
            func_def = FunctionDef(None)
            # TODO: Function Args func_def.func_args(self.visit(node.args))
            func_def.body(self.visit(node.body))

            return func_def

    def visit_BinOp(self, node: ast.BinOp):
        print("BINOP")
        ops = {ast.Add : BinaryOperator.ADD}
        left = node.left
        print(left)
        print("OP",ops[type(node.op)])
        op = ops[type(node.op)]
        right = node.right
        print(right)

        return BinaryOp(op,self.visit(left),self.visit(right))

    def visit_Expr(self, node:ast.Expr):
        print(node.value)
        return self.visit(node.value)


    def visit_Assign(self, node: ast.Assign):
        print("Assign") 
        # TODO: multiple assignments to same value, and 'unpacking' tuple/list
        left = self.visit(node.targets[0])
        right = self.visit(node.value)

        return Assignment(left,right)

    def visit_Call(self, node:ast.Call):
        print("id",node.func.id)
        # TODO args
        return Call(Name(node.func.id),[])

    def visit_Attribute(self, node:ast.Attribute):
        pass

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
        op = node.op
        operand = node.operand

        return UnaryOp(self.visit(op), self.visit(operand))

    def visit_Compare(self, node: ast.Compare):
        left = node.left
        ops = {ast.Eq : BinaryOperator.EQ}
        

        # TODO: Change these to handle more than one comparison operation and
        # Operand (i.e. handle 1 < x < 10)
        op = ops[type(node.ops[0])]
        right = node.comparators[0]

        return BinaryOp(op,self.visit(left),self.visit(right))

    def visit_Subscript(self, node:ast.Subscript):
        """Visits a PyAST Subscript node, and returns a CAST Subscript node
           
        Args:
            node (ast.Subscript): [description]
        """

        value = node.value
        sl = node.slice

        pass

    def visit_Break(self, node:ast.Break):
        """Visits a PyAST Break node, which is just a break statement
           nothing to be done for a Break node, just return a ModelBreak() object

        Args:
            node (ast.Break): An AST Break node

        Returns:
            ModelBreak(): 
        """

        return ModelBreak()

    def visit_Continue(self, node:ast.Continue):
        """Visits a PyAST Continue node, which is just a continue statement
           nothing to be done for a Continue node, just return a ModelContinue() object


        Args:
            node (ast.Continue): An AST Continue node

        Returns:
            ModelContinue(): 
        """

        return ModelContinue()

    def visit_Name(self, node:ast.Name):
        """This visits PyAST Name nodes, which consist of
           id: The name of a variable as a string
           ctx: The context in which the variable is being used

        Args:
            node (ast.Name): [description]
        """

        return Name(name=node.id)
        
    def visit_List(self, node:ast.List):
        pass

    def visit_Tuple(self, node:ast.Tuple):
        pass

    def visit_Dict(self, node:ast.Dict):
        pass

    def visit_Set(self, node:ast.Set):
        pass
        
    def visit_String(self, node:ast.Str):
        pass

    def visit_Constant(self, node:ast.Constant):
        if(type(node.value) == int):
            return Number(node.value)
        pass


def main():
    print("Hi")

main()