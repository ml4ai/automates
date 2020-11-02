import ast
from functools import singledispatch
from collections.abc import Sequence
from collections import defaultdict
from enum import Enum

class ContainerType(Enum): 
    IF = 1
    FOR = 2
    WHILE = 3
    FUNCTION = 4

    def to_name(self, t):
        return {
            ContainerType.IF: "IF",
            ContainerType.FOR: "LOOP",
            ContainerType.WHILE: "LOOP",
            ContainerType.FUNCTION: "function"
        }[t]
    
    def to_type(self, t):
        return {
            ContainerType.IF: "if-block",
            ContainerType.FOR: "loop",
            ContainerType.WHILE: "loop",
            ContainerType.FUNCTION: "function"
        }[t]

    def is_loop(self, t):
        return t == ContainerType.WHILE or t == ContainerType.FOR


def flatten_generator(l):
    for el in l:
        if (isinstance(el, Sequence) or isinstance(el, set)) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el

def flatten(l):
    return list(flatten_generator(l))

def op_to_lambda(op):
    return {
        ast.Add : "+",
        ast.Sub : "-",
        ast.Mult : "*",
        ast.Div : "/",
        ast.FloorDiv : "//",
        ast.MatMult : "@",
        ast.Mod : "%",
        ast.BitAnd : "&",
        ast.BitOr : "|",
        ast.BitXor : "^",
        ast.LShift : "<<",
        ast.RShift : ">>",
        ast.Pow : "**",
        ast.UAdd : "+",
        ast.USub : "-",
        ast.Not : " not ",
        ast.Invert : "~",
        ast.And : " and ",
        ast.Or : " or ",
        ast.Lt : "<",
        ast.LtE : "<=",
        ast.Gt : ">",
        ast.GtE : ">=",
        ast.Eq : "==",
        ast.NotEq : "!=",
        ast.Is : " is ",
        ast.IsNot : " is not ",
        ast.In : " in ",
        ast.NotIn : " not in "
    }[type(op)]

def generate_function_object(name, func_type, input_var_ids=list(), \
        output_var_ids=list(), updated_var_ids=list(), lambda_str=""):
    return {
        "function": {
            "name": name,
            "type": func_type,
            "code": lambda_str,
        },
        "input": input_var_ids,
        "output": output_var_ids,
        "updated": updated_var_ids,
    }

def generate_variable_object(name):
    return {
        "name": name,
        "source_refs": [],
        "domain": {
            "name": "none",
            "type": "",
            "mutable": False
        },
        "domain_constraint": ""
    }

def create_container_object(containers, container_name, container_type):
    if not container_name in containers:
        containers[container_name] = defaultdict(lambda: list())
        containers[container_name]["arguments"] = set()
        containers[container_name]["name"] = container_name
        containers[container_name]["type"] = container_type
    return containers

def scope_to_string(scope_list):
    return ".".join(scope_list)

def generate_lambda(input_variable_identifiers, expr):
    inputs = [x.split("::")[3] for x in input_variable_identifiers]
    return "lambda " + ",".join(inputs) + ": " + expr 

# NOTE For loops, the decision should have just on input car (the calculated
# condition var) and one output var (the exit var)
def generate_decision_lambda(node: ast.For, cond_vars, conditions_updating_var, name, \
        is_val_set_in_else):
    return "lambda " + cond_vars[0] + ": not (" + cond_vars[0] + ")"

def generate_decision_lambda(node: ast.While, cond_vars, conditions_updating_var, name, \
        is_val_set_in_else):
    return "lambda " + cond_vars[0] + ": not (" + cond_vars[0] + ")"

# NOTE cond_vars must be sorted in order of appearing conditions in source
def generate_decision_lambda(node: ast.If, cond_vars, conditions_updating_var, name, \
        is_val_set_in_else):
    all_vars = []

    cur_var_num = 0
    else_string = ""
    lambda_body_string = ""
    group = []
    for var in cond_vars:
        group.append(var)
        all_vars.append(var)
        if var in conditions_updating_var:
            lambda_var = name + "_" + str(cur_var_num)
            cur_var_num += 1 
            all_vars.append(lambda_var)

            lambda_body_string += else_string + lambda_var + " if " \
                + " and not ".join(group[:-1]) \
                + (" and " if len(group) > 1 else "") + group[-1] 

            else_string = " else "
            group = []

    if is_val_set_in_else:
        else_var =  name + "_" + str(cur_var_num)
        all_vars.append(else_var)
        lambda_body_string += " else "  + else_var
    else:
        lambda_body_string += " else None"

    return "lambda " + ",".join(all_vars) + ": " + lambda_body_string



def generate_decision_name(module, scope, var_name, version, is_loop=False):
    return module + "::" + scope_to_string(scope) + "::__decision__" \
        + ("EXIT__" if is_loop else var_name) \
        + "::" + str(version)

def generate_variable_cond_name(module, scope, cond):
    return "@variable::" + module + "::" + scope_to_string(scope) + "::" + cond + "::0"


@singledispatch
def generate_container_name(node, module, scope, variable_table):
    raise NotImplementedError(f"Unknown AST node of type: {type(node)}")

@generate_container_name.register
def _(node: ast.FunctionDef, module, scope, variable_table):
    return "@container::" + module + "::" + scope_to_string(scope) + "::" + node.name

@generate_container_name.register
def _(node: ast.If, module, scope, variable_table):
    return  "@container::" + module + "::" + scope_to_string(scope[:-1]) + "::" + scope[-1]

@generate_container_name.register
def _(node: ast.While, module, scope, variable_table):
    return  "@container::" + module + "::" + scope_to_string(scope[:-1]) + "::" + scope[-1]


@singledispatch
def generate_function_name(node, module, scope, variable_table):
    raise NotImplementedError(f"Unknown AST node of type: {type(node)}")

# TODO cond # 
@generate_function_name.register
def _(node: ast.If, module, scope, variable_table):
    return module + "__" + scope_to_string(scope) + "__condition__COND" 

# TODO cond # 
@generate_function_name.register
def _(node: ast.While, module, scope, variable_table):
    return module + "__" + scope_to_string(scope) + "__condition__COND" 

@generate_function_name.register
def _(node: ast.Assign, module, scope, variable_table):
    # TODO we can assign to multiple vars at once
    assign_name = generate_variable_name(node.targets[0], module, scope, variable_table)
    return module + "__" + scope_to_string(scope) + "__assign__" + assign_name

@generate_function_name.register
def _(node: ast.AugAssign, module, scope, variable_table):
    assign_name = generate_variable_name(node.target, module, scope, variable_table)
    return module + "__" + scope_to_string(scope) + "__assign__" + assign_name

@generate_function_name.register
def _(node: ast.Return, module, scope, variable_table):
    # TODO we can assign to multiple vars at once
    return module + "__" + scope_to_string(scope) + "__assign____return"

@generate_function_name.register
def _(node: ast.Expr, module, scope, variable_table):
    return module + "__" + scope_to_string(scope) + "__assign__expr"


# TODO fix naming and document all the vartiable string methods
def generate_variable_string(name, scope, module):
    return "@variable::" + module + "::" + scope_to_string(scope) + "::" + name

def generate_scopes(scope):
    potential_scope_strings = []
    while scope:
        potential_scope_strings.append(scope_to_string(scope))
        scope = scope[:-1]
    return potential_scope_strings

def find_variable_name_at_scope_or_higher(name, scope, variable_table):
    potential_scope_strings = generate_scopes(scope)
    def has_name_and_scope(id):
        return id and id.split("::")[2] in potential_scope_strings and id.split("::")[3] == name
    ids_with_name = [var_identifier + "::" + str(variable_table[var_identifier]["version"]) \
        for var_identifier in variable_table.keys() if has_name_and_scope(var_identifier)]
    return max(ids_with_name, key=lambda x: int(x.split("::")[4]), default="")

def filter_variables_without_scope(identifiers, scope):
    scope_str = scope_to_string(scope)
    # Variable id split will have structure (_, module, scope, name, version).
    # Keep variables whose scope is not the current scope passed in. This allows
    # us to find variables defined outside of the current container scope that 
    # are passed in.
    return [id for id in identifiers if not (scope_str in id.split("::")[2])]

def get_largest_scope_variable_identifier(id, scope, module, variable_table):
    variable_identifier = ""
    highest_version = -1

    def is_valid_var(x):
        if x == "":
            return False
        (_, _, _, name) = x.split("::")
        return name == id

    vars_with_name = [x for x in variable_table.keys() if is_valid_var(x)]
    for var in vars_with_name:
        if variable_table[var]["version"] >= highest_version:
            highest_version = variable_table[var]["version"]
            variable_identifier = var

    return variable_identifier

@singledispatch
def generate_variable_name(node, module, scope, variable_table):
    raise NotImplementedError(f"Unknown AST node of type: {type(node)}")

@generate_variable_name.register
def _(node: str, module, scope, variable_table):
    variable_identifier = get_largest_scope_variable_identifier(node, scope, module, variable_table)
    return variable_identifier \
         + "::" + str(variable_table[variable_identifier]['version'])

@generate_variable_name.register
def _(node: ast.arg, module, scope, variable_table):
    return generate_variable_name(node.arg, module, scope, variable_table)

@generate_variable_name.register
def _(node: ast.Name, module, scope, variable_table):
    return generate_variable_name(node.id, module, scope, variable_table)

def create_variable(name, scope, module, variable_table, version=-1):
    var_id = generate_variable_string(name, scope, module)
    variable_table[var_id] = { 'version': version }
    return var_id + "::" + str(version)

def create_or_update_variable(name, scope, module, variable_table):
    var_id = get_largest_scope_variable_identifier(name, scope, module, variable_table)
    if not var_id:
        return create_variable(name, scope, module, variable_table)
    else:
        return create_variable(name, scope, module, variable_table, 
            version=variable_table[var_id]['version'] + 1)