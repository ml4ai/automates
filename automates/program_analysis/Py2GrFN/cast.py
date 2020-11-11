import ast
import re

from functools import singledispatch, reduce
from collections import defaultdict

from .cast_control_flow_utils import (
    visit_control_flow_container,
    for_loop_to_while
)

from .cast_utils import (
    ContainerType,
    generate_container_name,
    generate_function_name, 
    generate_variable_name,
    create_or_update_variable,
    create_variable,
    op_to_lambda,
    generate_variable_object,
    create_container_object,
    generate_function_object,
    generate_assign_function_name,
    flatten
)

from model_assembly.networks import GroundedFunctionNetwork

from model_assembly.structures import (
    GenericContainer,
    GenericStmt,
    GenericIdentifier,
    GenericDefinition,
    VariableDefinition,
)

class ExprInfo:
    def __init__(self, var_names: list, var_identifiers_used: list, lambda_expr: str):
        self.var_names = var_names
        self.var_identifiers_used = var_identifiers_used
        self.lambda_expr = lambda_expr

class CAST2GrFN(ast.NodeVisitor):
    """ 
    Handles the translation of the Common Abstract Syntax Tree (CAST) to GrFN. 
    Currently, CAST is represented by the Python 3.7 AST. 
    """

    def __init__(self, cast):
        self.cast = cast

        # AIR data
        self.containers = dict()
        self.variables = dict()
        self.types = dict()
        self.cur_control_flow = 0
        self.cur_condition = 0

        # Memoized data for computing AIR
        self.cur_statements = list()
        self.cur_containers = list()
        self.variable_table = defaultdict(lambda: { 'version' : -1 })

        # TODO set the default module to initial as we cannot determine input module.
        self.cur_module = "initial"
        self.cur_scope = ["@global"]

    def to_grfn(self):
        initial_container_name = "initial::@global"
        create_container_object(self.containers, initial_container_name, "function")
        self.cur_containers.append(initial_container_name)
        # Use our python AST visitor to fill out AIR data
        self.visit(self.cast)

        from pprint import pprint
        pprint(self.containers)
        pprint(self.variables)

        C, V, T, D = dict(), dict(), dict(), dict()

        # Create variable definitions
        for var_data in self.variables.values():
            new_var = GenericDefinition.from_dict(var_data)
            V[new_var.identifier] = new_var

        # Create type definitions
        for type_data in self.types.values():
            new_type = GenericDefinition.from_dict(type_data)
            T[new_type.identifier] = new_type

        # Create container definitions
        for con_data in self.containers.values():
            new_container = GenericContainer.from_dict(con_data)
            for in_var in new_container.arguments:
                if in_var not in V:
                    V[in_var] = VariableDefinition.from_identifier(in_var)
            C[new_container.identifier] = new_container

        # Use funbction container in "initial" named "main" as the primary
        # container. If this does not exist, use the last defined function
        # container in the list, as this will be the furthest down defined
        # function and will be a good guess to the starting point.
        if "@container::initial::@global::main" in self.containers:
            con_id = GenericIdentifier.from_str("@container::initial::@global::main")
        else:
            con = list(filter(lambda c: c["type"] == "function", self.containers.values()))[-1]
            con_id = GenericIdentifier.from_str(con["name"])
        grfn = GroundedFunctionNetwork.from_AIR(
            con_id, C, V, T
        )

        return grfn

    def visit_node_list(self, node_list):
        """ 
        Generically handle a list of assumed AST nodes and attempt to translate
        each item 
        """
        return list(flatten([self.visit(child) for child in node_list]))

    # ==========================================================================
    # TOP LEVEL NODES
    # ==========================================================================

    def visit_Module(self, node: ast.Module):
        """ Module has a list of nodes representing its body """
        # Fill out function definitions in case a function is called
        function_defs = [n for n in node.body if type(n) == ast.FunctionDef]
        for function_def in function_defs:
            function_name = generate_container_name(function_def, self.cur_module, 
                self.cur_scope, self.variable_table)
            create_container_object(self.containers, function_name, "function")

        # Visit node bodies
        self.visit_node_list(node.body)

    def visit_Expression(self, node: ast.Expression):
        """ The root of the AST for single expressions parsed using the eval mode """
        pass

    def visit_Interactive(self, node: ast.Interactive):
        pass

    # ==========================================================================

    # ==========================================================================
    # FUNCTION AND DEFINITION NODES
    # ==========================================================================
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        # There should only be one container def per defined function, ensure this
        # assumption is true
        function_name = generate_container_name(node, self.cur_module, self.cur_scope, 
            self.variable_table)
        create_container_object(self.containers, function_name, "function")

        self.cur_containers.append(function_name)
        self.cur_scope.append(node.name)

        # Translate the arguments and track them as variables
        self.visit(node.args)

        # Translate child nodes
        self.visit_node_list(node.body)

        # Pop current container off of scope
        self.cur_containers = self.cur_containers[:-1]
        # Pop the current functions scope off
        self.cur_scope = self.cur_scope[:-1]

        # Clear variable table
        # TODO KEEP GLOBALS / Things above this functions scope
        self.variable_table = defaultdict(lambda: { 'version' : -1 })

    def visit_arguments(self, node: ast.arguments):
        # TODO handle defaults for positional arguments? (in node.defaults)
        # padded_default_arg_valeus = [None] * (len(self.args) - len(self.defaults)) + self.defaults
        self.visit_node_list(node.args)

        # TODO handle kwonlyargs, need to handle default values as well?
        # Keyword only arguments are named from *args

        # TODO handle **kwags and *args

    def visit_arg(self, node: ast.arg):
        # TODO could take advantage of type hint or annotation for variable types
        create_variable(node.arg, self.cur_scope, self.cur_module, self.variable_table)
        arg_name = generate_variable_name(node, self.cur_module, self.cur_scope, self.variable_table)

        self.containers[self.cur_containers[-1]]['arguments'].add(arg_name)
        self.variables[arg_name] = generate_variable_object(arg_name)

    def visit_Import(self, node: ast.Import):
        # TODO: finish implementing this function
        aliases = [self.visit(name) for name in node.names]
        return NotImplemented

    def visit_ImportFrom(self, node: ast.ImportFrom):
        # TODO: finish implementing this function
        module_names = [self.visit(name) for name in node.names]
        return NotImplemented

    def visit_alias(self, node: ast.alias):
        # TODO: finish implementing this function
        return NotImplemented

    # ==========================================================================

    # ==========================================================================
    # CONTROL FLOW NODES
    # ==========================================================================

    def visit_If(self, node: ast.If):
        functions = visit_control_flow_container(
            node,
            self,
            ContainerType.IF
        )
        self.containers[self.cur_containers[-1]]["body"].extend(functions)

    def visit_For(self, node: ast.For):
        # Return tuple with first position as new variable declaration
        # functions before loop and second position is the while loop ast
        # node
        while_loop_translation = for_loop_to_while(node, self)

        while_loop_function = visit_control_flow_container(
            while_loop_translation,
            self,
            ContainerType.WHILE
        )

        self.containers[self.cur_containers[-1]]["body"].extend(while_loop_function)

    def visit_While(self, node: ast.While):
        functions = visit_control_flow_container(
            node,
            self,
            ContainerType.WHILE
        )
        self.containers[self.cur_containers[-1]]["body"].extend(functions)

    # ==========================================================================

    # ==========================================================================
    # STATEMENT NODES
    #
    # Statement nodes that will usually be its own function with inputs/outputs
    #
    # ==========================================================================

    def visit_Assign(self, node: ast.Assign):     
        value_translated = self.visit(node.value)

        # Generate outputs post value translation in order to update the version
        # of the output variables.
        targets_translated_list = self.visit_node_list(node.targets)
        for target in targets_translated_list:
            print(target.var_names)
            var_name_assigned = target.var_names[0]
            target_identifiers_used = target.var_identifiers_used
            output = create_or_update_variable(var_name_assigned, self.cur_scope, self.cur_module, self.variable_table)
            self.variables[output] = generate_variable_object(output)

            functions = [{
                "function": {
                    "name": generate_assign_function_name(var_name_assigned, \
                        self.cur_module, self.cur_scope, self.variable_table),
                    "type": "lambda",
                    "code": "lambda " + ",".join(set(value_translated.var_names)) \
                        + ":" + value_translated.lambda_expr,
                },
                "input": value_translated.var_identifiers_used + target_identifiers_used,
                "output": [output],
                "updated": list()
            }]
            self.containers[self.cur_containers[-1]]["body"].extend(functions)   

    def visit_AnnAssign(self, node: ast.AnnAssign):
        output = self.visit(node.target)
        lambda_expr = self.visit(node.value)
        inputs = list()

    def visit_AugAssign(self, node: ast.AugAssign):
        value_translated = self.visit(node.value)
        target_translated = self.visit(node.target)
        # There can only be one target, so select only var name from 
        # target result to update for assign
        inputted_aug_var = target_translated.var_identifiers_used[0]
        output = create_or_update_variable(target_translated.var_names[0], self.cur_scope, \
            self.cur_module, self.variable_table)  
        # Add the new variable id to var table
        self.variables[output] = generate_variable_object(output)

        lambda_expr_str = f"({target_translated.var_names[0]}){op_to_lambda(node.op)}({value_translated.lambda_expr})"
        functions = [{
            "function": {
                "name": generate_function_name(node, self.cur_module, self.cur_scope, 
                    self.variable_table),
                "type": "lambda",
                "code": "lambda " + ",".join(set(target_translated.var_names)) \
                    + ":" + lambda_expr_str,
            },
            "input": value_translated.var_identifiers_used + [inputted_aug_var],
            "output": [output],
            "updated": list()
        }]
        self.containers[self.cur_containers[-1]]["body"].extend(functions)


    # NOTE: Represents a statement consisting of only one Expr where the result 
    #   is not used or stored. For instance,
    #       print(a + 1) 
    #   would be an Expr with child nodes for the internal expression type expr
    # @translate.register
    def visit_Expr(self, node: ast.Expr):
        translated = self.visit(node.value)
        functions = [{
                "function": {
                    "name": generate_function_name(node, self.cur_module, self.cur_scope, 
                        self.variable_table),
                    "type": "lambda",
                    "code": "lambda " + ",".join(set(translated.var_names)) + ":" + translated.lambda_expr,
                },
                "input": translated.var_identifiers_used,
                "output": list(),
                "updated": list(),
            }]
        self.containers[self.cur_containers[-1]]["body"].extend(functions)
        # return functions

    def visit_expr(self, node: ast.expr):
        # TODO: Implement this function
        return NotImplemented

    def visit_Raise(self, node: ast.Raise):
        # NOTE: Nothing to be done for now
        pass

    def visit_Assert(self, node: ast.Assert):
        # NOTE: Nothing to be done for now
        pass

    def visit_Delete(self, node: ast.Delete):
        # NOTE: Nothing to be done for now
        pass

    def visit_Pass(self, node: ast.Pass):
        # NOTE: Nothing to be done for now
        pass

    def visit_Return(self, node: ast.Return):
        translated = self.visit(node.value)
        
        # For now, create a variable that we output the return expression to.
        # This is because we expect a named variable for the return of a container.
        output_var_name = "RETURN"
        output = create_or_update_variable(output_var_name, self.cur_scope, 
            self.cur_module, self.variable_table)  
        self.variables[output] = generate_variable_object(output)

        functions = [{
                "function": {
                    "name": generate_function_name(node, self.cur_module, self.cur_scope, 
                        self.variable_table),
                    "type": "lambda",
                    "code": "lambda :" + translated.lambda_expr,
                },
                "input": translated.var_identifiers_used,
                "output": [output],
                "updated": list(),
            }]

        self.containers[self.cur_containers[-1]]["body"].extend(functions)
        self.containers[self.cur_containers[-1]]["return_value"].append(output)

    # ==========================================================================

    # ==========================================================================
    # EXPRESSION NODES
    # 
    # Expressions nodes will return a tuple with input values in the first 
    # position and the constucted lamba in the second position.
    # ==========================================================================

    def visit_Call(self, node: ast.Call):
        # TODO handle keyword args and *args
        args_translated = self.visit_node_list(node.args)
        # Note: Function node is usually a ast.Name node which is also used for
        # variable names. So, we ignore the first field in the resulting tuple
        func_translated = self.visit(node.func)
        inputs = reduce(lambda a1, a2: a1 + a2, [arg.var_identifiers_used for arg in args_translated], [])

        # TODO this could break in some cases
        # Find function id with called func name
        function_ids = [c for c in self.containers.keys()
            if c.rsplit("::", 1)[1] == func_translated.var_names[0]]
        if len(function_ids) > 0:
            function_id = function_ids[0]
            output_var_name = function_id.rsplit("::", 1)[1] + "_RESULT"
            output = create_or_update_variable(output_var_name, self.cur_scope, 
                self.cur_module, self.variable_table)  
            self.variables[output] = generate_variable_object(output)

            # Add container func to cur body to body
            func_obj = generate_function_object(function_id, "container", 
                input_var_ids=inputs, output_var_ids=[output])
            self.containers[self.cur_containers[-1]]["body"].append(func_obj)
            inputs.append(output)

        lambda_function = func_translated.lambda_expr + "(" + ",".join([arg.lambda_expr for arg in args_translated]) + ")"
        vars_used = reduce(lambda a1, a2: a1 + a2, [arg.var_names for arg in args_translated], [])

        return ExprInfo(vars_used, inputs, lambda_function)

    def visit_ListComp(self, node: ast.ListComp):
        pass

    # BINOPS
    def visit_BinOp(self, node: ast.BinOp):
        left_translated = self.visit(node.left)
        right_translated = self.visit(node.right)

        lambda_function = "(" + left_translated.lambda_expr + ")" \
            + op_to_lambda(node.op) \
            + "(" + right_translated.lambda_expr + ")"  

        return ExprInfo(left_translated.var_names + right_translated.var_names, \
            left_translated.var_identifiers_used + right_translated.var_identifiers_used, \
            lambda_function)

    # UNOPS
    def visit_UnaryOp(self, node: ast.UnaryOp):        
        translated = self.visit(node.operand)

        lambda_function = op_to_lambda(node.op) + "(" + translated.lambda_expr + ")"

        return ExprInfo(translated.var_names, translated.var_identifiers_used, \
            lambda_function)

    # BOOLOPS
    def visit_BoolOp(self, node: ast.BoolOp):
        translated = self.visit_node_list(node.values)
        lambda_function = op_to_lambda(node.op).join([val.lambda_expr for val in translated])
        return ExprInfo(flatten([res.var_names for res in translated]), \
            flatten([val.var_identifiers_used for val in translated]), lambda_function)

    # COMPARATORS
    def visit_Compare(self, node: ast.Compare):
        left_translated = self.visit(node.left)

        comparators = self.visit_node_list(node.comparators)
        operators = [op_to_lambda(op) for op in node.ops]

        lambda_function = "(" + left_translated.lambda_expr + ")" \
            + "".join([op + "(" + comp.lambda_expr + ")"  \
                for (op, comp) in zip(operators, comparators)])

        input_vars = left_translated.var_identifiers_used \
            + reduce(lambda c1, c2: c1 + c2,  [c.var_identifiers_used for c in comparators])
        var_names = left_translated.var_names \
            + reduce(lambda c1, c2: c1 + c2,  [c.var_names for c in comparators])

        return ExprInfo(var_names, input_vars, lambda_function)

    def visit_Subscript(self, node: ast.Subscript):
        value_translated = self.visit(node.value)
        slice_translated = self.visit(node.slice)

        lambda_expr = f"{value_translated.lambda_expr}[{slice_translated.lambda_expr}]"

        return ExprInfo(
            value_translated.var_names, 
            value_translated.var_identifiers_used + slice_translated.var_identifiers_used, 
            lambda_expr)

    def visit_Index(self, node: ast.Index):
        return self.visit(node.value)

    def visit_Slice(self, node: ast.Slice):
        return None

    def visit_ExtSlice(self, node: ast.ExtSlice):
        return None

    # Expression literals/leaf nodes

    def visit_List(self, node: ast.List):
        elems = self.visit_node_list(node.elts)
        vars_used = reduce(lambda a1, a2: a1 + a2, [elem.var_names for elem in elems], [])
        inputs = reduce(lambda a1, a2: a1 + a2, [elem.var_identifiers_used for elem in elems], [])
        lambda_function = "[" + ",".join([elem.lambda_expr for elem in elems]) + "]"
        return ExprInfo(vars_used, inputs, lambda_function)

    def visit_Tuple(self, node: ast.Tuple):
        elems = self.visit_node_list(node.elts)
        vars_used = reduce(lambda a1, a2: a1 + a2, [elem.var_names for elem in elems], [])
        inputs = []
        # Gather inputs as we are creating new tuple to be assigned with their values
        if type(node.ctx) == ast.Load:
            inputs = reduce(lambda a1, a2: a1 + a2, [elem.var_identifiers_used for elem in elems], [])
            lambda_function = "(" + ",".join([elem.lambda_expr for elem in elems]) + ")"
        elif type(node.ctx) == ast.Store:
            # TODO we have to assign each element somehow... 
            res = []
            for elem in elems:
                res.append(ExprInfo(elem.var_names, elem.var_identifiers_used, elem.lambda_expr))
            return res
        
        return ExprInfo(vars_used, inputs, lambda_function)

    def visit_Set(self, node: ast.Set):
        pass

    def visit_Name(self, node: ast.Name):
        name = generate_variable_name(node, self.cur_module, self.cur_scope, self.variable_table)
        var_identifiers_used = []
        # We only use/have inputed var identifier if we are loading this
        # var, not storing/creating a new version of a var
        if name:
            var_identifiers_used.append(name)
        return ExprInfo([node.id], var_identifiers_used, str(node.id))

    def visit_Attribute(self, node: ast.Attribute):
        value_translated = self.visit(node.value)
        return ExprInfo(value_translated.var_names, value_translated.var_identifiers_used, \
            value_translated.lambda_expr + "." + str(node.attr))

    def visit_Constant(self, node: ast.Constant):
        return ExprInfo(list(), list(), str(node.value))

    def visit_Num(self, node: ast.Num):
        return ExprInfo(list(), list(), str(node.n))

    def visit_Str(self, node: ast.Str):
        return ExprInfo(list(), list(), "\"" + str(node.s) + "\"")

    # ==========================================================================