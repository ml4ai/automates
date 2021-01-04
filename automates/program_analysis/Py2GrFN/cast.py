import ast
import re

from functools import singledispatch, reduce
from collections import defaultdict, OrderedDict

from .cast_control_flow_utils import visit_control_flow_container, for_loop_to_while

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
    flatten,
    add_argument_to_container,
    create_class_object,
    build_dict_key_list,
)

from automates.model_assembly.networks import GroundedFunctionNetwork

from automates.model_assembly.structures import (
    GenericContainer,
    GenericStmt,
    GenericIdentifier,
    GenericDefinition,
    VariableDefinition,
)


class ExprInfo:
    def __init__(
        self,
        var_names: list,
        var_identifiers_used: list,
        lambda_expr: str,
        type="",
        dict_keys={},
    ):
        # Cast to set list of names should be unique
        OrderedDict([(k, None) for k in var_names]).keys()
        self.var_names = list(OrderedDict([(k, None) for k in var_names]).keys())
        self.var_identifiers_used = list(
            OrderedDict([(k, None) for k in var_identifiers_used]).keys()
        )
        self.lambda_expr = lambda_expr
        self.type = type
        self.dict_keys = dict_keys


class CAST2GrFN(ast.NodeVisitor):
    """
    Handles the translation of the Common Abstract Syntax Tree (CAST) to GrFN.
    Currently, CAST is represented by the Python 3.7 AST.
    """

    def __init__(self, cast):
        self.cast = cast

        # AIR data
        self.containers = dict()
        self.variables = OrderedDict()
        self.types = dict()
        self.classes = dict()
        self.imports = list()
        self.cur_control_flow = 0
        self.cur_condition = 0

        # Memoized data for computing AIR
        self.cur_statements = list()
        self.cur_containers = list()
        self.variable_table = defaultdict(lambda: {"version": -1})

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

        # Use function container in "initial" named "main" as the primary
        # container. If this does not exist, use the last defined function
        # container in the list, as this will be the furthest down defined
        # function and will be a good guess to the starting point.
        if "@container::initial::@global::main" in self.containers:
            con_id = GenericIdentifier.from_str("@container::initial::@global::main")
        else:
            con = list(
                filter(lambda c: c["type"] == "function", self.containers.values())
            )[-1]
            con_id = GenericIdentifier.from_str(con["name"])
        grfn = GroundedFunctionNetwork.from_AIR(
            con_id,
            C,
            V,
            T,
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
            function_name = generate_container_name(
                function_def, self.cur_module, self.cur_scope, self.variable_table
            )
            create_container_object(self.containers, function_name, "function")

        # Fill out class definitions in case an object is created or method is called
        class_defs = [n for n in node.body if type(n) == ast.ClassDef]
        for class_def in class_defs:
            self.visit(class_def)

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
    def visit_ClassDef(self, node: ast.ClassDef):
        # TODO bases and keywords for meta classes and base classes
        self.cur_scope.append(node.name)
        class_name = generate_container_name(
            node, self.cur_module, self.cur_scope, self.variable_table
        )

        if not class_name in self.classes:
            # TODO determine all class fields
            self.classes = create_class_object(
                self.classes, class_name, node.name, node.body
            )
            self.visit_node_list(node.body)

        self.cur_scope = self.cur_scope[:-1]

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # There should only be one container def per defined function, ensure this
        # assumption is true
        function_name = generate_container_name(
            node, self.cur_module, self.cur_scope, self.variable_table
        )
        create_container_object(self.containers, function_name, "function")

        self.cur_containers.append(function_name)
        self.cur_scope.append(node.name)

        if function_name.rsplit("::")[-1] == "__init__":
            # Remove self from a __init__ func as self is "created" in that func
            node.args.args = [arg for arg in node.args.args if not (arg.arg == "self")]
            # create the "self" dict at the start of the func
            self_var_name = ast.Name(id="self", ctx=ast.Store())
            self_var_assign = ast.Assign(
                targets=[self_var_name], value=ast.Constant(value={})
            )
            node.body.insert(0, self_var_assign)
            node.body.append(ast.Return(self_var_name))

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
        self.variable_table = defaultdict(lambda: {"version": -1})

    def visit_Lambda(self, node: ast.Lambda):

        # has args and body
        print(type(node.body))

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
        arg_name = generate_variable_name(
            node, self.cur_module, self.cur_scope, self.variable_table
        )

        add_argument_to_container(
            arg_name, self.containers[self.cur_containers[-1]]["arguments"]
        )
        # TODO pass type
        self.variables[arg_name] = generate_variable_object(arg_name, "")

    def visit_Import(self, node: ast.Import):
        imports = [
            {**res, "name": None, "module": res["name"]}
            for res in self.visit_node_list(node.names)
        ]
        self.imports.extend(imports)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        imports = [
            {**res, "module": node.module} for res in self.visit_node_list(node.names)
        ]
        self.imports.extend(imports)

    def visit_alias(self, node: ast.alias):
        return {"name": node.name, "alias": node.asname, "module": None}

    # ==========================================================================

    # ==========================================================================
    # CONTROL FLOW NODES
    # ==========================================================================

    def visit_If(self, node: ast.If):
        functions = visit_control_flow_container(node, self, ContainerType.IF)
        self.containers[self.cur_containers[-1]]["body"].extend(functions)

    def visit_IfExp(self, node: ast.IfExp):
        # In a ternary if exp, you can have a single expression in the body or
        # orelse portion, so add an assignment so it is produced out of the
        # ternary
        ifexp_output_name = "IF_EXP_" + str(
            self.containers[self.cur_containers[-1]]["cur_if_exp"]
        )
        self.containers[self.cur_containers[-1]]["cur_if_exp"] += 1
        ifexp_var_name = ast.Name(id=ifexp_output_name, ctx=ast.Store())
        ifexp_body_var_assign = ast.Assign(targets=[ifexp_var_name], value=node.body)
        ifexp_orelse_var_assign = ast.Assign(
            targets=[ifexp_var_name], value=node.orelse
        )

        as_if_node = ast.If(
            test=node.test,
            body=[ifexp_body_var_assign],
            orelse=[ifexp_orelse_var_assign],
        )

        functions = visit_control_flow_container(as_if_node, self, ContainerType.IF)
        self.containers[self.cur_containers[-1]]["body"].extend(functions)

        var_identifiers_used = functions[-1]["updated"]

        return ExprInfo([ifexp_output_name], var_identifiers_used, ifexp_output_name)

    def visit_For(self, node: ast.For):
        # Return tuple with first position as new variable declaration
        # functions before loop and second position is the while loop ast
        # node
        while_loop_translation = for_loop_to_while(node, self)

        while_loop_function = visit_control_flow_container(
            while_loop_translation, self, ContainerType.WHILE
        )

        self.containers[self.cur_containers[-1]]["body"].extend(while_loop_function)

    def visit_While(self, node: ast.While):
        functions = visit_control_flow_container(node, self, ContainerType.WHILE)
        self.containers[self.cur_containers[-1]]["body"].extend(functions)

    # ==========================================================================

    # ==========================================================================
    # STATEMENT NODES
    #
    # Statement nodes that will usually be its own function with inputs/outputs
    #
    # ==========================================================================

    def visit_Assign(self, node: ast.Assign):
        # TODO need to work out a multiple var assign example
        value_translated = self.visit(node.value)

        # Generate outputs post value translation in order to update the version
        # of the output variables.
        targets_translated_list = self.visit_node_list(node.targets)

        for target in targets_translated_list:
            var_name_assigned = target.var_names[0]
            target_identifiers_used = target.var_identifiers_used
            outputs = []
            updates = []

            identifiers = value_translated.var_identifiers_used
            identifiers.sort()
            var_names_sorted = []
            for id in identifiers:
                name = id.rsplit("::", 2)[1]
                if not name in var_names_sorted:
                    var_names_sorted.append(name)

            if target.type == "dict":
                dict_name = target_identifiers_used[0]
                existing_dict_to_update = self.variables[dict_name]
                next_instance = int(self.variables[dict_name]["instances"][-1]) + 1
                existing_dict_to_update["instances"].append(next_instance)

                cur_keys = build_dict_key_list(existing_dict_to_update)
                add, update = [], []
                for i in target.dict_keys:
                    (update if i in cur_keys else add).append(i)

                existing_dict_to_update["key_instances"][str(next_instance)] = {
                    "add": add,
                    "update": update,
                    "delete": [],
                }

                updates.append(dict_name)
                identifiers.extend(target_identifiers_used)

            else:
                output = create_or_update_variable(
                    var_name_assigned,
                    self.cur_scope,
                    self.cur_module,
                    self.variable_table,
                )
                self.variables[output] = generate_variable_object(
                    output, value_translated.type
                )
                if value_translated.type == "dict":
                    self.variables[output].update(
                        {
                            "instances": [1],
                            "key_instances": {
                                "1": defaultdict(
                                    lambda: [], {"add": value_translated.dict_keys}
                                )
                            },
                        }
                    )
                outputs.append(output)

            functions = [
                {
                    "function": {
                        "name": generate_assign_function_name(
                            var_name_assigned,
                            self.cur_module,
                            self.cur_scope,
                            self.variable_table,
                        ),
                        "type": "lambda",
                        "code": "lambda "
                        + ",".join(var_names_sorted)
                        + ":"
                        + value_translated.lambda_expr,
                    },
                    "input": identifiers,
                    "output": outputs,
                    "updated": updates,
                }
            ]
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
        output = create_or_update_variable(
            target_translated.var_names[0],
            self.cur_scope,
            self.cur_module,
            self.variable_table,
        )
        # Add the new variable id to var table
        # TODO type
        self.variables[output] = generate_variable_object(output, "")

        identifiers = (
            value_translated.var_identifiers_used
            + target_translated.var_identifiers_used
        )
        identifiers.sort()
        var_names_sorted = []
        for id in identifiers:
            name = id.rsplit("::", 2)[1]
            if not name in var_names_sorted:
                var_names_sorted.append(name)

        lambda_expr_str = f"({target_translated.var_names[0]}){op_to_lambda(node.op)}({value_translated.lambda_expr})"
        functions = [
            {
                "function": {
                    "name": generate_function_name(
                        node, self.cur_module, self.cur_scope, self.variable_table
                    ),
                    "type": "lambda",
                    "code": "lambda "
                    + ",".join(var_names_sorted)
                    + ":"
                    + lambda_expr_str,
                },
                "input": identifiers,
                "output": [output],
                "updated": list(),
            }
        ]
        self.containers[self.cur_containers[-1]]["body"].extend(functions)

    # NOTE: Represents a statement consisting of only one Expr where the result
    #   is not used or stored. For instance,
    #       print(a + 1)
    #   would be an Expr with child nodes for the internal expression type expr
    # @translate.register
    def visit_Expr(self, node: ast.Expr):
        translated = self.visit(node.value)

        translated.var_identifiers_used.sort()
        var_names_sorted = []
        for id in translated.var_identifiers_used:
            name = id.rsplit("::", 2)[1]
            if not name in var_names_sorted:
                var_names_sorted.append(name)

        functions = [
            {
                "function": {
                    "name": generate_function_name(
                        node, self.cur_module, self.cur_scope, self.variable_table
                    ),
                    "type": "lambda",
                    "code": "lambda "
                    + ",".join(list(var_names_sorted))
                    + ":"
                    + translated.lambda_expr,
                },
                "input": translated.var_identifiers_used,
                "output": list(),
                "updated": list(),
            }
        ]
        self.containers[self.cur_containers[-1]]["body"].extend(functions)

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
        # If the return from the function is a single var,
        # otherwise it is an expression we must mitigate
        if type(node.value) == ast.Name:
            translated = self.visit(node.value)
            returned_var_id = translated.var_identifiers_used[0]
            self.containers[self.cur_containers[-1]]["return_value"].append(
                returned_var_id
            )
        elif node.value:
            translated = self.visit(node.value)

            # For now, create a variable that we output the return expression to.
            # This is because we expect a named variable for the return of a container.
            output_var_name = "RETURN"
            output = create_or_update_variable(
                output_var_name, self.cur_scope, self.cur_module, self.variable_table
            )
            self.variables[output] = generate_variable_object(output, translated.type)

            translated.var_identifiers_used.sort()
            var_names_sorted = []
            for id in translated.var_identifiers_used:
                name = id.rsplit("::", 2)[1]
                if not name in var_names_sorted:
                    var_names_sorted.append(name)

            functions = [
                {
                    "function": {
                        "name": generate_function_name(
                            node, self.cur_module, self.cur_scope, self.variable_table
                        ),
                        "type": "lambda",
                        "code": "lambda "
                        + ",".join(var_names_sorted)
                        + ":"
                        + translated.lambda_expr,
                    },
                    "input": translated.var_identifiers_used,
                    "output": [output],
                    "updated": list(),
                }
            ]

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
        # Note: Function node is usually a ast.Name node which is also used for
        # variable names. So, we ignore the first field in the resulting tuple
        func_translated = self.visit(node.func)

        # TODO handle keyword args and *args
        args_translated = self.visit_node_list(node.args)

        inputs = []
        # If we called a function from an object, input that object var into this container
        if type(node.func) == ast.Attribute:
            inputs.extend(func_translated.var_identifiers_used)

        inputs.extend(
            reduce(
                lambda a1, a2: a1 + a2,
                [arg.var_identifiers_used for arg in args_translated],
                [],
            )
        )

        # TODO this could break in some cases
        # Find function id with called func name
        function_ids = [
            c
            for c in self.containers.keys()
            if [v for v in func_translated.var_names if c.endswith(v)]
        ]

        # Extend potential function ids with class constructers if the
        # function name called matches the name of a class
        potential_classes = [
            (k + "::__init__", v["name"])
            for k, v in self.classes.items()
            if v["name"] == func_translated.var_names[0]
        ]
        function_ids.extend([i[0] for i in potential_classes])

        # Extend with potential function calls from a class

        func_result_type = ""
        if len(function_ids) == 1:
            function_id = function_ids[0]
            output_var_name = function_id.rsplit("::", 1)[1] + "_RESULT"
            output = create_or_update_variable(
                output_var_name, self.cur_scope, self.cur_module, self.variable_table
            )
            # TODO type of output var from function
            self.variables[output] = generate_variable_object(output, "")

            # Add container func to cur body to body
            func_call_obj = generate_function_object(
                function_id, "container", input_var_ids=inputs, output_var_ids=[output]
            )
            self.containers[self.cur_containers[-1]]["body"].append(func_call_obj)

            if len(potential_classes) > 0:
                func_result_type = potential_classes[0][1]
            elif len(self.containers[function_id]["return_value"]) > 0:
                return_var = self.containers[function_id]["return_value"][0]
                func_result_type = self.variables[return_var]["domain"]["type"]

            func_result_name = output.rsplit("::", 1)[1]
            return ExprInfo(
                [func_result_name],
                [output],
                func_result_name,
                type=func_result_type,
            )

        elif len(function_ids) == 0:

            # Could be a library function, loop over the imported libraries and check
            # if we are using a name/alias imported from a module or using an attribute
            # from an imported modules name/alias
            output = ""
            for i in self.imports:
                module = i["module"]
                name = i["name"]
                alias = i["alias"]
                if name:
                    library_call = alias if alias else name
                    if func_translated.lambda_expr.startswith(library_call):
                        func_translated.lambda_expr = (
                            func_translated.lambda_expr.replace(library_call, name)
                        )
                        break
                else:
                    library_call = alias + "." if alias else module + "."
                    if func_translated.lambda_expr.startswith(library_call):
                        func_translated.lambda_expr = (
                            func_translated.lambda_expr.replace(
                                library_call, module + "."
                            )
                        )
                        break

            # TODO outputs
            output_var_name = func_translated.lambda_expr.replace(".", "_") + "_RESULT"
            output = create_or_update_variable(
                output_var_name,
                self.cur_scope,
                self.cur_module,
                self.variable_table,
            )
            self.variables[output] = generate_variable_object(output, "")

            vars_used = reduce(
                lambda a1, a2: a1 + a2, [arg.var_names for arg in args_translated], []
            )
            vars_used.extend(func_translated.var_names)

            box_assign_func_name = generate_assign_function_name(
                output_var_name,
                self.cur_module,
                self.cur_scope,
                self.variable_table,
            )

            # TODO sort inputs
            lambda_function = (
                "lambda "
                + ",".join(inputs)
                + ": "
                + func_translated.lambda_expr
                + "("
                + ",".join([arg.lambda_expr for arg in args_translated])
                + ")"
            )

            boxed_obj = {
                "function": {
                    "name": box_assign_func_name,
                    "type": "boxed",
                    "code": lambda_function,
                },
                "input": inputs,
                "output": [output],
                "updated": [],
            }

            self.containers[self.cur_containers[-1]]["body"].append(boxed_obj)

            func_result_name = output.rsplit("::", 1)[1]

            return ExprInfo(
                [output_var_name],
                [output],
                output_var_name,
                type=func_result_type,
            )

        print("Error: Unable to resolve function call.")
        return

    def visit_ListComp(self, node: ast.ListComp):
        pass

    def visit_DictComp(self, node: ast.DictComp):
        pass

    # BINOPS
    def visit_BinOp(self, node: ast.BinOp):
        left_translated = self.visit(node.left)
        right_translated = self.visit(node.right)

        lambda_function = (
            "("
            + left_translated.lambda_expr
            + ")"
            + op_to_lambda(node.op)
            + "("
            + right_translated.lambda_expr
            + ")"
        )

        return ExprInfo(
            left_translated.var_names + right_translated.var_names,
            left_translated.var_identifiers_used
            + right_translated.var_identifiers_used,
            lambda_function,
        )

    # UNOPS
    def visit_UnaryOp(self, node: ast.UnaryOp):
        translated = self.visit(node.operand)

        lambda_function = (
            "(" + op_to_lambda(node.op) + "(" + translated.lambda_expr + "))"
        )

        return ExprInfo(
            translated.var_names, translated.var_identifiers_used, lambda_function
        )

    # BOOLOPS
    def visit_BoolOp(self, node: ast.BoolOp):
        translated = self.visit_node_list(node.values)
        lambda_function = op_to_lambda(node.op).join(
            [val.lambda_expr for val in translated]
        )
        return ExprInfo(
            flatten([res.var_names for res in translated]),
            flatten([val.var_identifiers_used for val in translated]),
            lambda_function,
        )

    # COMPARATORS
    def visit_Compare(self, node: ast.Compare):
        left_translated = self.visit(node.left)

        comparators = self.visit_node_list(node.comparators)
        operators = [op_to_lambda(op) for op in node.ops]

        lambda_function = (
            "("
            + left_translated.lambda_expr
            + ")"
            + "".join(
                [
                    op + "(" + comp.lambda_expr + ")"
                    for (op, comp) in zip(operators, comparators)
                ]
            )
        )

        input_vars = left_translated.var_identifiers_used + reduce(
            lambda c1, c2: c1 + c2, [c.var_identifiers_used for c in comparators]
        )
        var_names = left_translated.var_names + reduce(
            lambda c1, c2: c1 + c2, [c.var_names for c in comparators]
        )

        return ExprInfo(var_names, input_vars, lambda_function)

    def visit_Subscript(self, node: ast.Subscript):
        value_translated = self.visit(node.value)
        slice_translated = self.visit(node.slice)

        lambda_expr = f"{value_translated.lambda_expr}[{slice_translated.lambda_expr}]"

        # TODO check to make sure it is a dict for dict keys
        return ExprInfo(
            value_translated.var_names,
            value_translated.var_identifiers_used
            + slice_translated.var_identifiers_used,
            lambda_expr,
            dict_keys=[slice_translated.lambda_expr],
            type=value_translated.type,
        )

    def visit_Index(self, node: ast.Index):
        return self.visit(node.value)

    def visit_Slice(self, node: ast.Slice):
        self.visit(node.lower)
        self.visit(node.upper)
        self.visit(node.step)
        return ExprInfo([], [], "")

    def visit_ExtSlice(self, node: ast.ExtSlice):
        return None

    # Expression literals/leaf nodes

    def visit_List(self, node: ast.List):
        elems = self.visit_node_list(node.elts)
        vars_used = reduce(
            lambda a1, a2: a1 + a2, [elem.var_names for elem in elems], []
        )
        inputs = reduce(
            lambda a1, a2: a1 + a2, [elem.var_identifiers_used for elem in elems], []
        )
        lambda_function = "[" + ",".join([elem.lambda_expr for elem in elems]) + "]"
        return ExprInfo(vars_used, inputs, lambda_function)

    def visit_Dict(self, node: ast.Dict):
        keys = self.visit_node_list(node.keys)

        vals_with_exprs_precomputed = []
        i = 0
        for val in node.values:
            # If we are dealing with a simple expression, do not precompute
            if (
                type(val) == ast.Name
                or type(val) == ast.Num
                or type(val) == ast.Constant
                or type(val) == ast.Str
            ):
                vals_with_exprs_precomputed.append(val)
            else:

                dict_precompute_name = "grfn_dict_precompute_field_" + str(i)
                dict_precompute_var_name_store = ast.Name(
                    id=dict_precompute_name, ctx=ast.Store()
                )
                dict_precompute_var_assign = ast.Assign(
                    targets=[dict_precompute_var_name_store], value=val
                )
                self.visit(dict_precompute_var_assign)

                dict_precompute_var_name_load = ast.Name(
                    id=dict_precompute_name, ctx=ast.Store()
                )
                vals_with_exprs_precomputed.append(dict_precompute_var_name_load)
                i += 1

        values = self.visit_node_list(vals_with_exprs_precomputed)

        # Determine all vars used in the keys/values
        vars_used = reduce(lambda a1, a2: a1 + a2, [k.var_names for k in keys], [])
        vars_used.extend(
            reduce(lambda a1, a2: a1 + a2, [v.var_names for v in values], [])
        )
        inputs = reduce(
            lambda a1, a2: a1 + a2, [k.var_identifiers_used for k in keys], []
        )
        inputs.extend(
            reduce(lambda a1, a2: a1 + a2, [v.var_identifiers_used for v in values], [])
        )

        # Create key/value lambda strings and build dictionary lambda definition
        key_strs = [elem.lambda_expr for elem in keys]
        kv_lambdas = [
            k + ": " + v
            for k, v in zip(key_strs, [elem.lambda_expr for elem in values])
        ]
        lambda_function = "{" + ",".join(kv_lambdas) + "}"

        return ExprInfo(
            vars_used, inputs, lambda_function, type="dict", dict_keys=key_strs
        )

    def visit_Tuple(self, node: ast.Tuple):
        elems = self.visit_node_list(node.elts)
        vars_used = reduce(
            lambda a1, a2: a1 + a2, [elem.var_names for elem in elems], []
        )
        inputs = []
        # Gather inputs as we are creating new tuple to be assigned with their values
        if type(node.ctx) == ast.Load:
            inputs = reduce(
                lambda a1, a2: a1 + a2,
                [elem.var_identifiers_used for elem in elems],
                [],
            )
            lambda_function = "(" + ",".join([elem.lambda_expr for elem in elems]) + ")"
        elif type(node.ctx) == ast.Store:
            # TODO we have to assign each element somehow...
            res = []
            for elem in elems:
                res.append(
                    ExprInfo(
                        elem.var_names, elem.var_identifiers_used, elem.lambda_expr
                    )
                )
            return res

        return ExprInfo(vars_used, inputs, lambda_function)

    def visit_Set(self, node: ast.Set):
        pass

    def visit_Name(self, node: ast.Name):
        name = generate_variable_name(
            node, self.cur_module, self.cur_scope, self.variable_table
        )
        var_identifiers_used = []
        # We only use/have inputed var identifier if we are loading this
        # var, not storing/creating a new version of a var
        var_type = "str"
        if name:
            var_identifiers_used.append(name)
            if type(node.ctx) == ast.Load:
                var_type = self.variables[name]["domain"]["type"]

        return ExprInfo([node.id], var_identifiers_used, str(node.id), type=var_type)

    def visit_Attribute(self, node: ast.Attribute):
        expr_type = ""

        value_translated = self.visit(node.value)
        var_identifiers_used = value_translated.var_identifiers_used
        var_names = value_translated.var_names

        if type(node.ctx) == ast.Load:
            class_names = [v["name"] for v in self.classes.values()]

            if value_translated.type in class_names:
                attr_name = node.attr
                class_funcs = [
                    v
                    for v in self.containers.keys()
                    if value_translated.type + "::" + attr_name in v
                ]

                # We are calling a funciton
                if len(class_funcs) == 1:
                    # TODO get result type of function
                    # expr_type = class_funcs[0]["type"]
                    var_names.append(class_funcs[0])

                # We are accessing a class field
                else:
                    var_names.append(attr_name)
                    # var_identifiers_used.append()

        return ExprInfo(
            var_names,
            var_identifiers_used,
            value_translated.lambda_expr + "." + str(node.attr),
            type=expr_type,
        )

    def visit_Constant(self, node: ast.Constant):
        return ExprInfo(list(), list(), str(node.value))

    # Depricated after 3.8
    def visit_NameConstant(self, node: ast.NameConstant):
        return ExprInfo(list(), list(), str(node.value))

    def visit_Num(self, node: ast.Num):
        return ExprInfo(list(), list(), str(node.n))

    def visit_Str(self, node: ast.Str):
        str_newline_escaped = node.s.replace("\n", "\\n")
        return ExprInfo(list(), list(), '"' + str_newline_escaped + '"')

    # ==========================================================================
