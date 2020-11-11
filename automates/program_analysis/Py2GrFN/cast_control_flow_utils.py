import ast
from functools import singledispatch
from collections import defaultdict

from .cast_utils import (
    ContainerType,
    generate_container_name,
    generate_function_name, 
    generate_decision_name, 
    generate_decision_lambda,
    generate_lambda,
    generate_variable_cond_name,
    create_variable,
    generate_variable_object,
    generate_function_object,
    create_container_object,
    filter_variables_without_scope,
    find_variable_name_at_scope_or_higher,
    flatten
)

@singledispatch
def handle_cf_finished(node, cast_visitor, container_name, cur_cf_type):
    raise NotImplementedError(f"Unknown AST node of type: {type(node)}")

@handle_cf_finished.register
def _(node: ast.If, cast_visitor, container_name, cur_cf_type):
    # Create the decision node for the if statement by finding the
    # highest version assignment for each output variable within each 
    # cond body
    cf_body_statements = cast_visitor.containers[cast_visitor.cur_containers[-1]]["body"]
    output_vars = set(flatten([x["output"] for x in cf_body_statements]))
    cast_visitor.containers[container_name]["updated"].extend(flatten([x["updated"] for x in cf_body_statements]))

    scoped_id_to_ver = defaultdict(lambda: [-1])
    name_to_max_ver = defaultdict(lambda: -1)
    name_to_conds = defaultdict(lambda: defaultdict(lambda: -1))

    for (id, name, version) in [name.rsplit("::", 2) for name in output_vars]:
        # Track the max variables version outputted for each cond
        if "COND" in name:
            (_, _, condition_num) = name.split("_")
            vars_updated_in_condition = [var for var in output_vars if id + "." + name in var]
            for var in vars_updated_in_condition:   
                (_, cond_var_name, _) = var.rsplit("::", 2)
                name_to_conds[cond_var_name][name] = max(name_to_conds[cond_var_name][name], int(condition_num))
        else:
            identifier = id + "::" + name
            cur_scope_ver = scoped_id_to_ver[identifier][0]
            scoped_id_to_ver[identifier] = (max(int(version), cur_scope_ver), name)
            name_to_max_ver[name] = max(int(version), name_to_max_ver[name])

    for name, max_ver in name_to_max_ver.items():
        output_vars = []

        new_var_name = create_variable(name, cast_visitor.cur_scope, cast_visitor.cur_module, cast_visitor.variable_table, version=max_ver+1)
        cast_visitor.variables[new_var_name] = generate_variable_object(new_var_name)
        cast_visitor.containers[container_name]["updated"].append(new_var_name)
        output_vars.append(new_var_name)

        inputted_body_vars = [k + "::" + str(v[0]) for k,v in scoped_id_to_ver.items() if v[1] == name]
        
        conditions_updating_var = name_to_conds[name].keys()
        max_cond_num_used = max(name_to_conds[name].values())

        cond_names = ["COND_" + str(cur_cf_type) + "_" + str(i) for i in range(int(max_cond_num_used) + 1)]
        used_cond_variables = [generate_variable_cond_name(cast_visitor.cur_module, cast_visitor.cur_scope, name) for name in cond_names]
        inputted_body_vars.extend(used_cond_variables)

        is_val_set_in_else = False
        external_var = find_variable_name_at_scope_or_higher(name, cast_visitor.cur_scope[:-1], cast_visitor.variable_table)
        # TODO have to rework else with cf type*
        else_var_used = [var for var in inputted_body_vars if "ELSE_" + str(cur_cf_type) in var]
        if else_var_used:
            # Sorts else value to last item in input list so lamba
            # arg is inputted correctly                    
            inputted_body_vars.sort(key=else_var_used[0].__eq__)
            is_val_set_in_else = True
        elif external_var != "":
            for key in ["container_call_args", "arguments"]:
                cast_visitor.containers[container_name][key].add(external_var)
            inputted_body_vars.append(external_var)
            is_val_set_in_else = True

        inputted_body_vars.sort(key=lambda x: x.rsplit("COND_", 1)[-1])

        decision_function = generate_function_object(
            generate_decision_name(cast_visitor.cur_module, cast_visitor.cur_scope, name, max_ver, \
                is_loop=False), 
            "lambda", input_var_ids=inputted_body_vars, output_var_ids=output_vars, 
            lambda_str=generate_decision_lambda(node, cond_names, conditions_updating_var, name, \
                is_val_set_in_else)
        )
        
        cast_visitor.containers[cast_visitor.cur_containers[-1]]["body"].append(decision_function)

    cast_visitor.cur_scope = cast_visitor.cur_scope[:-1]
    cast_visitor.cur_containers = cast_visitor.cur_containers[:-1]

def handle_cf_finished_loop(node, cast_visitor, container_name, cur_cf_type):
    # If we are in a loop, add all internally created non-cond vars as updated vars
    cf_body_statements = cast_visitor.containers[cast_visitor.cur_containers[-1]]["body"]
    outputs_from_body = flatten([x["output"] for x in cf_body_statements])
    non_cond_updated = [x for x in outputs_from_body if not "COND_" in x.rsplit("::", 2)[1]]
    cast_visitor.containers[container_name]["updated"].extend(non_cond_updated)

    scoped_id_to_ver = defaultdict(lambda: [-1])
    for (id, name, version) in [name.rsplit("::", 2) for name in non_cond_updated]:
        identifier = id + "::" + name
        max_ver = (max(int(version), scoped_id_to_ver[identifier][0]))
        scoped_id_to_ver[identifier] = (max_ver, name, identifier + "::" + str(max_ver))

    # Gather all the externally inputed variables to statements in the body
    externally_inputted_vars = cast_visitor.containers[container_name]["container_call_args"]
    names_of_external_inputs = [x.rsplit("::", 2)[1] for x in externally_inputted_vars]
    # If the name of an inputted variable is the same as an updated variable,
    # we must use the updated value in the next iteration of the loop, so set 
    # the updated value as an argument to this loop container
    updated_var_arguments = [x[2] for x in scoped_id_to_ver.values() if x[1] in names_of_external_inputs]
    cast_visitor.containers[container_name]["arguments"].update(updated_var_arguments)

    # NOTE keep this code even though it looks bad. Will be used when we have multiple conditions
    # for breaks/continues
    cond_names = ["COND_" + str(cur_cf_type) + "_0"]
    used_cond_variables = [generate_variable_cond_name(cast_visitor.cur_module, cast_visitor.cur_scope, name) for name in cond_names]

    # TODO figure out else handling on a loop
    # external_var = find_variable_name_at_scope_or_higher(name, cast_visitor.cur_scope[:-1], cast_visitor.variable_table)
    # # TODO have to rework else with cf type*
    # else_var_used = [var for var in inputted_body_vars if "ELSE_" + str(cur_cf_type) in var]
    # if else_var_used:
    #     # Sorts else value to last item in input list so lamba
    #     # arg is inputted correctly                    
    #     inputted_body_vars.sort(key=else_var_used[0].__eq__)
    # elif external_var != "":
    #     cast_visitor.containers[container_name]["arguments"].add(external_var)
    #     inputted_body_vars.append(external_var)

    new_var_name = create_variable("EXIT", cast_visitor.cur_scope, cast_visitor.cur_module, cast_visitor.variable_table)
    cast_visitor.variables[new_var_name] = generate_variable_object(new_var_name)

    decision_function = generate_function_object(
        generate_decision_name(cast_visitor.cur_module, cast_visitor.cur_scope, "", 0, \
            is_loop=True), 
        "lambda", input_var_ids=used_cond_variables, output_var_ids=[new_var_name], 
        lambda_str=("lambda " + cond_names[0] + ": not (" + cond_names[0] + ")")
    )
    
    cast_visitor.containers[cast_visitor.cur_containers[-1]]["body"].append(decision_function)

    cast_visitor.cur_scope = cast_visitor.cur_scope[:-1]
    cast_visitor.cur_containers = cast_visitor.cur_containers[:-1]

@handle_cf_finished.register
def _(node: ast.While, cast_visitor, container_name, cur_cf_type):
    return handle_cf_finished_loop(node, cast_visitor, container_name, cur_cf_type)

@handle_cf_finished.register
def _(node: ast.For, cast_visitor, container_name, cur_cf_type):
    return handle_cf_finished_loop(node, cast_visitor, container_name, cur_cf_type)

def keep_most_updated_vars(cast_visitor, container_name):
    max_updated = {}
    for updated in cast_visitor.containers[container_name]["updated"]:
        (identifier, name, ver) = updated.rsplit("::", 2)
        if not name in max_updated or max_updated[name][0] < int(ver):
            max_updated[name] = (int(ver), identifier, name)
        
    cast_visitor.containers[container_name]["updated"] = [x[1] + "::" + x[2] + "::" + str(x[0]) for x in max_updated.values()]

def visit_control_flow_container(node, cast_visitor, container_type):
    # Determine the current control flow # we are in within the parent container and
    # update the scope for evaluation
    container_type_name = container_type.to_name(container_type)
    cur_cf_type = cast_visitor.cur_control_flow
    cur_cf_cond = cast_visitor.cur_condition

    cast_visitor.cur_control_flow += 1
    cast_visitor.cur_condition = 0

    cast_visitor.cur_scope.append(container_type_name + "_" + str(cur_cf_type))

    container_name = generate_container_name(node, cast_visitor.cur_module, cast_visitor.cur_scope, cast_visitor.variable_table)
    create_container_object(cast_visitor.containers, container_name, container_type.to_type(container_type))

    # TODO only set cond for if?
    # Set current container and condition scope within the control flow
    cast_visitor.cur_containers.append(container_name)
    cond_name = "COND_" + str(cur_cf_type) + "_" + str(cur_cf_cond)

    # Generate variable for this condition
    cond_var = generate_variable_cond_name(cast_visitor.cur_module, cast_visitor.cur_scope, cond_name)
    cast_visitor.variables[cond_var] = generate_variable_object(cond_var)
    cast_visitor.cur_scope.append(cond_name)

    # Generate function node for comparison        
    condition_translate = cast_visitor.visit(node.test)
    condition_input_identifiers = condition_translate.var_identifiers_used
    condition = generate_function_object(
        generate_function_name(node, cast_visitor.cur_module, cast_visitor.cur_scope, cast_visitor.variable_table), \
        "lambda", input_var_ids=condition_input_identifiers, output_var_ids=[cond_var], \
        lambda_str=generate_lambda(condition_input_identifiers, condition_translate.lambda_expr)
    )
    
    # Generate functions for body of control flow
    cast_visitor.visit_node_list(node.body)
    cast_visitor.containers[container_name]["body"].append(condition)

    # Pop the current condition number off of scope
    cast_visitor.cur_scope = cast_visitor.cur_scope[:-1]

    # If we are dealing with an else condition in orelse, evaluate the 
    # statements and append to current statements        
    else_nodes = [x for x in node.orelse if not isinstance(x, ast.If)]
    if else_nodes:
        cast_visitor.cur_control_flow = cur_cf_type + 1
        cast_visitor.cur_condition = 0
        # Push new scope for else body
        cond_name = "ELSE_" + str(cur_cf_type)
        cast_visitor.cur_scope.append(cond_name)
        # Handle else body nodes
        # statements.extend(
        cast_visitor.visit_node_list(else_nodes)
            # )
        # Pop the else condition number off of scope
        cast_visitor.cur_scope = cast_visitor.cur_scope[:-1]

    # Add all control flow / else body statements into our control
    # flow container body
    # cast_visitor.containers[container_name]["body"].extend(statements)

    # Set the input variables. Find what variables we use as 
    # inputs that were defined in different scope than ours
    external_input_variables = set(filter_variables_without_scope( \
        flatten([x["input"] for x in cast_visitor.containers[container_name]["body"]]), cast_visitor.cur_scope))
    for key in ["container_call_args", "arguments"]:
        cast_visitor.containers[container_name][key].update(external_input_variables)

    # Perform end of control flow node tasks if we are at the end of the 
    # control flow statement. We know we are at the end if
    #   1) node.orelse is empty meaning we have recursed to the last
    #      elif block or there were none provided
    #   2) else_nodes (defined above) is not empty meaning we had an else body
    if not node.orelse or else_nodes:
        handle_cf_finished(node, cast_visitor, container_name, cur_cf_type)
        keep_most_updated_vars(cast_visitor, container_name)
    else:
        # Reduce current container and scope. Note we reduce before
        # processing "orelse" as orelse will be a list of If nodes
        cast_visitor.cur_scope = cast_visitor.cur_scope[:-1]
        cast_visitor.cur_containers = cast_visitor.cur_containers[:-1]

        # Update current if statements condition number
        cast_visitor.containers[cast_visitor.cur_containers[-1]][f"cur_{container_type_name}_cond"] = cur_cf_cond + 1

    # Visit additional elif conditions if present in orelse
    cast_visitor.cur_control_flow = cur_cf_type
    cast_visitor.cur_condition = cur_cf_cond + 1

    elif_nodes = [x for x in node.orelse if isinstance(x, ast.If)]
    cast_visitor.visit_node_list(elif_nodes)

    cast_visitor.cur_control_flow = cur_cf_type + 1
    cast_visitor.cur_condition = 0

    return [generate_function_object(container_name, "container", 
        input_var_ids=cast_visitor.containers[container_name]["container_call_args"], 
        updated_var_ids=cast_visitor.containers[container_name]["updated"])]


def for_loop_to_while(node, cast_visitor):
    for_loop_name = "FOR_" + str(cast_visitor.cur_control_flow) + "_" 

    # Create variable holding list
    extracted_list_name_str = for_loop_name + "list"
    iterated_list_assign = ast.Assign(
        targets=[ast.Name(extracted_list_name_str, ctx=ast.Store())], 
        value=node.iter)
    # Create iterator var
    iterator_var_name_str = for_loop_name + "i"
    iterator_var_name = ast.Name(
        id=iterator_var_name_str, 
        ctx=ast.Store())
    iterator_var_assign = ast.Assign(
        targets=[iterator_var_name], 
        value=ast.Constant(value=1))

    # These are done before the loop, so visit them
    cast_visitor.visit_node_list([iterated_list_assign, 
        iterator_var_assign])

    # Place statement at start of loop body to retrieve next item from list
    extracted_list_name_load = ast.Name(extracted_list_name_str, ctx=ast.Load())
    node.body.insert(0, 
        ast.Assign(
            targets=[node.target], 
            value=ast.Subscript(
                value=extracted_list_name_load,
                slice=ast.Index(value=iterator_var_name),
                ctx=ast.Load()
            )))

    # Append iterator increment to end of list
    node.body.append(
        ast.AugAssign(
            iterator_var_name, 
            ast.Add(), 
            ast.Constant(value=1)))

    # Create new while loop node with transformed values from For loop
    transformed_while_test = ast.Compare(
        left=ast.Name(
            id=iterator_var_name_str, 
            ctx=ast.Load()),
        ops=[ast.Lt()],
        comparators=[
            ast.Call(
                func=ast.Name(id="len", ctx=ast.Load()),
                args=[extracted_list_name_load]
            )])

    return ast.While(
            transformed_while_test,
            node.body,
            node.orelse
    )
        