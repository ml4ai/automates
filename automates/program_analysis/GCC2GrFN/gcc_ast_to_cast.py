import networkx as nx
from networkx.algorithms.dag import topological_sort

from pprint import pprint
from typing import cast

from automates.program_analysis.CAST2GrFN.cast import CAST
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
    SourceRef,
    Subscript,
    Tuple,
    UnaryOp,
    UnaryOperator,
    VarType,
    Var,
    source_ref,
    subscript,
)
from automates.program_analysis.GCC2GrFN.gcc_ast_to_cast_utils import (
    is_pass_through_expr,
    is_allowed_gcc_builtin_func,
    is_valid_operator,
    is_const_operator,
    is_casting_operator,
    is_trunc_operator,
    get_cast_operator,
    get_builtin_func_cast,
    get_const_value,
    gcc_type_to_var_type,
    default_cast_val_for_gcc_types,
    default_cast_val,
)
from automates.program_analysis.GCC2GrFN.gcc_basic_blocks_to_digraph import (
    basic_blocks_to_digraph,
    make_bbnode,
    find_lca_of_parents
)

class LoopInfo:
    num
    header_bb
    latch_bb
    loop_body
    ...


class GCC2CAST:
    """
    Takes a list of json objects where each object represents the GCC AST
    for one file outputted from our ast_dump.cpp GCC plugin.
    """

    def __init__(self, gcc_asts):
        self.gcc_asts = gcc_asts
        self.variables_ids_to_expression = {}
        self.ssa_ids_to_expression = {}
        self.basic_blocks = []
        # dict mapping BB index to BB
        self.basic_block_map = {}
        self.basic_block_parse_queue = set()
        self.parsed_basic_blocks = set()
        # dict mapping BB index to the CAST body it is in
        self.bb_index_to_cast_body = {}
        self.current_basic_block = None
        self.basic_block_stack = []
        self.type_ids_to_defined_types = {}
        self.curr_func_digraph = None
        self.curr_func_body = []
        self.func_digraphs = {}

        self.bb_headers_to_loop = {} 


    def clear_function_dependent_vars(self):
        self.variables_ids_to_expression = {}
        self.ssa_ids_to_expression = {}
        self.basic_blocks = []
        self.basic_block_map = {}
        self.basic_block_parse_queue = set()
        self.parsed_basic_blocks = set()
        self.bb_index_to_cast_body = {}
        self.current_basic_block = None
        self.basic_block_stack = []
        self.curr_func_digraph = None
        self.curr_func_body = []


    def to_cast(self):
        modules = []
        self.source_language = "unknown"
        # NOTE may have issues with casing of the extension
        if "mainInputFilename" in self.gcc_asts[0]:
            file_extension = self.gcc_asts[0]["mainInputFilename"].split(".")[-1]
            if file_extension == "c":
                self.source_language = "c"
            elif file_extension == "cpp":
                self.source_language = "cpp"
            elif file_extension in {"f", "for", "f90"}:
                self.source_language = "fortran"

        for gcc_ast in self.gcc_asts:
            input_file = gcc_ast["mainInputFilename"]
            input_file_stripped = input_file.split("/")[-1]
            functions = gcc_ast["functions"]
            types = gcc_ast["recordTypes"]
            global_variables = gcc_ast["globalVariables"]
            body = []

            # First fill out the ids to type names in case one type uses another
            # before it is defined.
            for t in types:
                self.type_ids_to_defined_types[t["id"]] = ClassDef(name=t["name"])

            # Parse types defined in AST so we have them before they are referenced
            for t in types:
                full_type_def = self.parse_record_type(t)
                self.type_ids_to_defined_types[t["id"]] = full_type_def
                body.append(full_type_def)

            # Parse global vars in AST so we have them before they are referenced
            for gv in global_variables:
                body.append(self.parse_variable(gv, parse_value=True))

            # Parse each function
            for f in functions:
                body.append(self.parse_function(f))

            modules.append(
                Module(
                    name=input_file_stripped.split("/")[-1].rsplit(".")[0], body=body
                )
            )

        return CAST(modules, self.source_language)

    def get_source_refs(self, obj):
        source_refs = []
        if obj.keys() >= {"line_start", "col_start", "file"}:
            line = obj["line_start"]
            col = obj["col_start"]
            file = obj["file"]
            source_refs.append(
                SourceRef(source_file_name=file, col_start=col, row_start=line)
            )
        return source_refs

    def parse_record_type_field(self, field):
        return self.parse_variable(field)

    def parse_record_type(self, record_type):
        name = record_type["name"]

        # TODO
        bases = []
        funcs = []

        record_type_fields = record_type["fields"]
        fields = [self.parse_record_type_field(f) for f in record_type_fields]

        source_refs = self.get_source_refs(record_type)

        return ClassDef(
            name=name, bases=bases, funcs=funcs, fields=fields, source_refs=source_refs
        )

    def parse_variable(self, variable, parse_value=False):
        if "name" not in variable:
            if "code" in variable and variable["code"] == "addr_expr":
                variable = variable["value"]
            else:
                return None
        var_type = variable["type"]
        name = variable["name"]
        name = name.replace(".", "_")
        cast_type = gcc_type_to_var_type(var_type, self.type_ids_to_defined_types)

        line = variable["line_start"] if "line_start" in variable else None
        col = variable["col_start"] if "col_start" in variable else None
        file = variable["file"] if "file" in variable else None
        source_ref = SourceRef(source_file_name=file, col_start=col, row_start=line)

        var_node = Var(
            val=Name(name=name),
            type=cast_type,
            source_refs=[source_ref],
        )

        if parse_value:
            assign_val = default_cast_val_for_gcc_types(
                var_type, self.type_ids_to_defined_types
            )
            if "value" in variable:
                assign_val = self.parse_operand(variable["value"])
            return Assignment(left=var_node, right=assign_val)
        else:
            return var_node

    def parse_variable_definition(self, v):
        var = self.parse_variable(v)
        default_val = default_cast_val_for_gcc_types(
            v["type"], self.type_ids_to_defined_types
        )
        if "id" in v:
            self.variables_ids_to_expression[v["id"]] = default_val
        if var is not None:
            return Assignment(left=var, right=default_val)
        return None

    def parse_addr_expr(self, operand):
        value = operand["value"]
        val_code = value["code"]
        # test = self.parse_operand(value)
        if is_const_operator(val_code):
            return get_const_value(value)
        elif val_code == "array_ref":
            return self.parse_array_ref_operand(value)
        else:
            name = value["name"]
            name = name.replace(".", "_")
            return Name(name=name)

    def parse_operand(self, operand):
        code = operand["code"]
        if code == "ssa_name":
            ssa_id = operand["ssa_id"]
            stored_ssa_expr = self.ssa_ids_to_expression[ssa_id]
            del self.ssa_ids_to_expression[ssa_id]
            return stored_ssa_expr
        elif is_const_operator(code):
            return get_const_value(operand)
        elif code == "var_decl" or code == "parm_decl":
            if "name" in operand:
                name = operand["name"]
                name = name.replace(".", "_")
                return Name(name=name)
            elif "id" in operand:
                return self.variables_ids_to_expression[operand["id"]]
        elif code == "addr_expr":
            return self.parse_addr_expr(operand)

    def parse_pointer_arithmetic_expr(self, op):
        pointer = self.parse_operand(op[0])
        offset_with_type_mult = self.parse_operand(op[1])
        source_refs = [SourceRef()]

        # For C/C++:
        # Offsets for pointer arithmetic will be a binary op performing
        # the multiplication of the pointer for the particular type with the
        # RHS being the actual position calculation. So, remove the
        # type multiplication part.
        # TODO does this apply for void pointers?
        offset = offset_with_type_mult
        if isinstance(offset_with_type_mult, BinaryOp):
            offset = offset_with_type_mult.right

        return Subscript(
            value=Name(name=pointer.name), slice=offset, source_refs=source_refs
        )

    def parse_array_ref_operand(self, operand):
        array = operand["array"]
        subscript_val = None
        if "name" in array:
            name = array["name"]
            subscript_val = Name(name=name.replace(".", "_"))
        elif "pointer" in array:
            pointer = array["pointer"]
            name = pointer["name"]
            subscript_val = Name(name=name.replace(".", "_"))
        elif array == "component_ref":
            component = self.parse_component_ref(array)[0]
            subscript_val = component

        index = operand["index"]
        index_result = self.parse_operand(index)

        return Subscript(value=subscript_val, slice=index_result)

    def parse_constructor(self, operand):
        type = operand["type"]
        source_refs = self.get_source_refs(operand)
        if type["type"] == "array_type":
            size_bytes = type["size"]
            component_type = type["componentType"]
            array_type = component_type["type"]
            array_type_size = component_type["size"]
            actual_size = int(size_bytes / array_type_size)

            vals = [
                default_cast_val("Number", self.type_ids_to_defined_types)
            ] * actual_size
            # TODO we should probably add type and size into list nodes?
            return List(values=vals, source_refs=source_refs)
        elif type["type"] == "real_type":
            return default_cast_val("Number", self.type_ids_to_defined_types)

    def parse_mem_ref_operand(self, operand):
        offset = operand["offset"]
        index = offset["value"]
        pointer = self.parse_operand(operand["pointer"])
        # In this scenario we have already created the susbscript
        # from a pointer_plus_expr
        if isinstance(pointer, Subscript) and index == 0:
            return pointer
        name = pointer.name
        name = name.replace(".", "_")

        # TODO how will we handle complex memory references? i.e.
        # different pointer types, complex calculations for pointer location

        if index != 0:
            return Subscript(value=Name(name=name), slice=index)
        else:
            return Name(name=name)

    def parse_lhs(self, stmt, lhs, assign_value):
        assign_var = None
        code = lhs["code"]
        if code == "component_ref":
            assign_var = self.parse_component_ref(lhs)[0]
        elif code == "var_decl":
            assign_var = self.parse_variable(lhs)
        elif code == "mem_ref":
            assign_var = self.parse_mem_ref_operand(lhs)
            if isinstance(assign_var, Name):
                cast_type = cast_type = gcc_type_to_var_type(
                    lhs["type"], self.type_ids_to_defined_types
                )
                assign_var = Var(val=assign_var, type=cast_type)
        elif code == "array_ref":
            assign_var = self.parse_array_ref_operand(lhs)
        elif code == "var_decl" or code == "parm_decl":
            cast_type = cast_type = gcc_type_to_var_type(
                lhs["type"], self.type_ids_to_defined_types
            )
            if "name" in lhs:
                name = lhs["name"]
                name = name.replace(".", "_")
                assign_var = Var(val=Name(name=name), type=cast_type)
            elif "id" in lhs:
                assign_var = self.variables_ids_to_expression[lhs["id"]]

        if "id" in lhs:
            self.variables_ids_to_expression[lhs["id"]] = assign_value
            if assign_var is None:
                return []
        elif "ssa_id" in lhs:
            ssa_id = lhs["ssa_id"]
            self.ssa_ids_to_expression[ssa_id] = assign_value
            return []

        source_refs = self.get_source_refs(stmt)

        return [
            Assignment(left=assign_var, right=assign_value, source_refs=source_refs)
        ]

    def parse_component_ref(self, operand):
        value = operand["value"]
        name = value["name"]
        var_name = name.replace(".", "_")
        member = operand["member"]
        field = member["name"]

        line = member["line_start"]
        col = member["col_start"]
        file = member["file"]
        source_ref = SourceRef(source_file_name=file, row_start=line, col_start=col)

        return [
            Attribute(
                value=Name(name=var_name),
                attr=Name(name=field),
                source_refs=[source_ref],
            )
        ]

    def parse_assign_statement(self, stmt):
        lhs = stmt["lhs"]
        operator = stmt["operator"]
        operands = stmt["operands"]
        src_ref = self.get_source_refs(stmt)

        # Integer assignment, so simply grab the value from the first operand
        # node.
        # Note: this would collapse an expression with only constants in it
        # (i.e. 5 + 10 into 15). If we wanted to preserve the original structure,
        # how do we avoid this collapsing?
        assign_value = None
        if is_valid_operator(operator):
            if is_const_operator(operator):
                assign_value = get_const_value(operands[0])
            elif is_pass_through_expr(operator):
                if "name" in operands[0]:
                    name = operands[0]["name"].replace(".", "_")
                    name = name.replace(".", "_")
                    assign_value = Name(name=name)
                elif "id" in operands[0]:
                    assign_value = self.variables_ids_to_expression[operands[0]["id"]]
                else:
                    assign_value = self.parse_operand(operands[0])
            elif (
                is_casting_operator(operator)
                or is_trunc_operator(operator)
                or operator == "nop_expr"
            ):
                assign_value = self.parse_operand(operands[0])
            elif operator == "array_ref":
                assign_value = self.parse_array_ref_operand(operands[0])
            elif operator == "component_ref":
                assign_value = self.parse_component_ref(operands[0])[0]
            elif operator == "mem_ref":
                assign_value = self.parse_mem_ref_operand(operands[0])
            elif operator == "pointer_plus_expr":
                assign_value = self.parse_pointer_arithmetic_expr(operands)
            elif operator == "constructor":
                assign_value = self.parse_constructor(operands[0])
            elif is_allowed_gcc_builtin_func(operator):
                assign_value = get_builtin_func_cast(operator)
                for arg in operands:
                    assign_value.arguments.append(self.parse_operand(arg))
            elif operator == "addr_expr":
                assign_value = self.parse_addr_expr(operands[0])
            else:
                cast_op = get_cast_operator(operator)
                ops = []
                for op in operands:
                    ops.append(self.parse_operand(op))
                assign_value = None
                # TODO handle if there are more than 2 ops
                if len(ops) == 1:
                    assign_value = UnaryOp(
                        op=cast_op, value=ops[0], source_refs=src_ref
                    )
                else:
                    assign_value = BinaryOp(
                        op=cast_op, left=ops[0], right=ops[1], source_refs=src_ref
                    )
        else:
            # TODO custom exception type
            raise Exception(f"Error: Unknown operator type: {operator}")

        return self.parse_lhs(stmt, lhs, assign_value)

    def parse_conditional_expr(self, stmt):
        operator = stmt["operator"]
        operands = stmt["operands"]
        cast_op = get_cast_operator(operator)
        ops = []
        for op in operands:
            ops.append(self.parse_operand(op))

        source_refs = self.get_source_refs(stmt)

        return BinaryOp(op=cast_op, left=ops[0], right=ops[1], source_refs=source_refs)

    def parse_call_statement(self, stmt):
        function = stmt["function"]
        arguments = stmt["arguments"] if "arguments" in stmt else []
        src_ref = self.get_source_refs(stmt)
        func_name = function["value"]["name"]
        # TODO not sure if this is a permenant solution, but ignore these
        # unexpected builtin calls for now
        if "__builtin_" in func_name and not is_allowed_gcc_builtin_func(func_name):
            return []

        cast_args = []
        for arg in arguments:
            cast_args.append(self.parse_operand(arg))

        cast_call = Call(
            func=Name(name=func_name), arguments=cast_args, source_refs=src_ref
        )
        if "lhs" in stmt and stmt["lhs"] is not None:
            return self.parse_lhs(stmt, stmt["lhs"], cast_call)

        return [cast_call]

    def parse_return_statement(self, stmt):
        # In this case, we have a void return
        if "value" not in stmt:
            return []
        value = stmt["value"]
        return_val = None
        return_val = self.parse_operand(value)

        source_refs = self.get_source_refs(stmt)

        return [ModelReturn(value=return_val, source_refs=source_refs)]

    def parse_conditional_statement(self, stmt, statements):
        true_edge = stmt["trueLabel"]
        false_edge = stmt["falseLabel"]

        true_block = [bb for bb in self.basic_blocks if bb["index"] == true_edge][0]
        false_block = [bb for bb in self.basic_blocks if bb["index"] == false_edge][0]

        is_loop = self.current_basic_block["index"] in self.bb_headers_to_loop

#         potential_block_with_goto = [
#             bb for bb in self.basic_blocks if bb["index"] == true_edge - 1
#         ][0]
#         is_loop = False
#         for false_bb_stmt in potential_block_with_goto["statements"]:
#             if (
#                 false_bb_stmt["type"] == "goto"
#                 and false_bb_stmt["target"] == self.current_basic_block["index"]
#             ):
#                 is_loop = True
# 
#         condition_expr = self.parse_conditional_expr(stmt)

        if is_loop:
            temp = self.current_basic_block
            # mark loop header as parse
            # GCC inverts loop expressions to check if the EXIT condition
            # i.e., given "while (count < 100)", gcc converts that to "if (count > 99) leave loop;"
            # So, to revert to the original loop condition, add a boolean NOT
            condition_expr = self.parse_conditional_expr(stmt)
            condition_expr = UnaryOp(
                op=UnaryOperator.NOT,
                value=condition_expr,
                source_refs=condition_expr.source_refs,
            )
            loop_cast_body = []
            loop_cast = Loop(expr=condition_expr, body=loop_cast_body)
            self.bb_index_to_cast_body[temp["index"]] = loop_cast_body
            self.parsed_basic_blocks.add(temp["index"])

            loop = self.bb_headers_to_loop[temp["index"]]
            loop_body = loop.loop_body
            # remove bb_header since we are already processing it
            # make sure this is right subset
            loop_body = loop_body[1:]
            self.basic_block_stack.append(temp)
            self.parse_body(loop_body)
            self.current_basic_block = temp

            return [loop_cast]
        else:
            # If the exit targets for the conditions are the same, then we have
            # an else/elif condition because they both point to the block after
            # this second condition. Otherwise, we only have one condition and
            # the "false block" is the normal block of code following the if,
            # so do not evaluate it here.
            #if true_exit_target == false_exit_target:
             #   false_res = self.parse_basic_block(false_block)
            #elif false_block["statements"][0]["type"] == "conditional":
             #   false_res = self.parse_basic_block(false_block)
            #else:
             #   f 
            #true_exit_target = true_block["edges"][0]["target"]
            #false_exit_target = false_block["edges"][0]["target"]
            curr_block_index = self.current_basic_block['index']
            # print(curr_block_index)

            temp = self.current_basic_block
            print(f"Parsing BB{true_block['index']} as an if body")
            true_res = self.parse_basic_block(true_block)
        
            #print(list(nx.topological_sort(self.curr_func_digraph)))

            # Retrieve the current node in the digraph
            # self.curr_func_digraph.

            false_res = []
            # NOTE: After parsing the true basic block, I believe
            # there should only be one outgoing edge, but I am not 100% sure
            # true_block_target = self.current_basic_block["edges"][0]["target"]
            #print(f"{false_block['index']}:{nx.ancestors(self.curr_func_digraph, make_bbnode(false_block))}")
            #print(f"{false_block['index']}:{self.curr_func_digraph.in_edges(make_bbnode(false_block))}")

            # If the false block has one incoming edge, then we know it either belongs 
            # as the orelse of this current node (in the case of else/else if)
            if len(self.curr_func_digraph.in_edges(make_bbnode(false_block))) == 1:
                print(f"Parsing BB{false_block['index']} as an elif")
                false_res = self.parse_basic_block(false_block)
#             elif len(self.curr_func_digraph.in_edges(make_bbnode(false_block))) > 1:
#                 edges = self.curr_func_digraph.in_edges(make_bbnode(false_block))
#                 par1 = edges[0]
#                 par2 = edges[1]
#                 
#                 print(edges)
# 
#                 false_res = []
            else:
                false_res = []

            # if after parsing the true block, the edge leads to the false_block,
            # then there is no else or else if
            # so, if this is not the case, then we need to parse the false (else) block
            # if true_block_target != false_block["index"]:
            #    false_res = self.parse_basic_block(false_block)

            # TODO: Do we need to reset self.current_basic_block?

            # build a ModelIf CAST node, and add the true_block/false_blocks indices
            # to bb_index_to_cast_body to keep track of where they were attached
            model_if = ModelIf(expr=condition_expr, body=true_res, orelse=false_res)
            assert(true_block["index"] not in self.bb_index_to_cast_body)
            self.bb_index_to_cast_body[true_block["index"]] = model_if.body
            print(f"** BB{true_block['index']} is the if body of BB{curr_block_index}**")
            if false_res != []:
                print(f"** BB{false_block['index']} is the else if body of BB{curr_block_index}**")
                self.bb_index_to_cast_body[false_block["index"]] = model_if.orelse

            return [model_if]

    def parse_body(self, loop_body):
        # blocks = [
        #     bb
        #     for bb in self.basic_blocks
        #     if bb["index"] >= start_block and bb["index"] < end_block
        # ]

        for bb_index in loop_body:
            bb = self.basic_block_map[bb_index]
            res = self.parse_basic_block(bb)
            digraph_node = make_bbnode(bb["index"])
            self.attach_parsed_bb_result(res, digraph_node)


        return [node for b in blocks for node in self.parse_basic_block(b)]

    def parse_statement(self, stmt, statements):
        stmt_type = stmt["type"]
        result = None

        if stmt_type == "assign":
            result = self.parse_assign_statement(stmt)
        elif stmt_type == "return":
            result = self.parse_return_statement(stmt)
        elif stmt_type == "call":
            result = self.parse_call_statement(stmt)
        elif stmt_type == "conditional":
            result = self.parse_conditional_statement(stmt, statements)
        elif (
            # Already handled in the conditional stmt type, just skip
            stmt_type == "goto"
            or stmt_type == "resx"  # Doesnt concern us
        ):
            return []
        else:
            # TODO custom exception
            raise Exception(f"Error: Unknown statement type {stmt_type}")

        return result

    def parse_basic_block(self, bb):
        # check that all parents (in the digraph) of this basic block have already been parsed
        index = bb["index"]
        # UPDATE do not worry about predecessors which are latches
        for par in self.curr_func_digraph.predecessors(make_bbnode(bb)):
            if par.index not in self.parsed_basic_blocks:
                print((f"WARNING: Trying to parse BB{index}, but its parent BB{par.index} has" 
                        " note been parsed yet"))
                self.basic_block_parse_queue.add(bb)
                return []

        # we know all parents have been parsed, so if this basic block has been parsed, then
        # we can skip it
        if bb["index"] in self.parsed_basic_blocks:
            return []

        # otherwise, we parse the basic block
        self.parsed_basic_blocks.add(bb["index"])

        self.current_basic_block = bb
        self.basic_block_stack.append(bb)

        statements = bb["statements"]
        cast_statements = []
        for stmt in statements:
            res = self.parse_statement(stmt, statements)
            cast_statements.extend(res)

        result_statements = cast_statements

        self.basic_block_stack.pop()
        return result_statements

    def check_fortran_arg_updates(self, arguments, body):
        arg_names = {n.val.name for n in arguments}

        args_updated_in_body = set()
        for b in body:
            if (
                isinstance(b, Assignment)
                and isinstance(b.left, Var)
                and b.left.val.name in arg_names
            ):
                args_updated_in_body.add(b.left.val.name)
            elif isinstance(b, (Loop, ModelIf)):
                args_updated_in_body.update(
                    self.check_fortran_arg_updates(arguments, b.body)
                )

        return args_updated_in_body

    def attach_parsed_bb_result(self, res, digraph_node):
        """
        Finds the CAST node body that this parsed basic block result should be added to,
        and extends the body with `res`.
        If the in degree of the associated digraph node is one, then we add the parsed result
        to its parent.  If the in degree of the associated digraph node is greater than one,
        than we find the lowest common ancestor of all its parents, call this the lca. The parsed result
        should be a "sibling" of the lca, so we attach it to lca's parent.

        Parameters:
            res: the result from parse_basic_block()
            digraph_node: the associated BBNode for this basic block in the functions digraph
        """

        # BB0 is always the start of a function, so we should add this res 
        # to curr_func_body
        if digraph_node.index == 0:
            body = self.curr_func_body
            body.extend(res)
            self.bb_index_to_cast_body[digraph_node.index] = body
            print(f"** BB{digraph_node.index} is placed in the function body **")
            return
        
        # MAYBE: don't get latch predecessors
        parents = list(self.curr_func_digraph.predecessors(digraph_node))
        # if a node has a unique parent, then it should be sibling to that parent
        if len(parents) == 1:
            parent = parents[0]
            if parent.index in self.bb_index_to_cast_body:
                body = self.bb_index_to_cast_body[parent.index]
                body.extend(res)
                self.bb_index_to_cast_body[digraph_node.index] = body
                print(f"** BB{digraph_node.index} is going to be sibling to {parent.index} **")
            else:
                print((f"ERROR: Cannot attach {str(digraph_node)}, its parent {str(parent)}"
                       " is not in bb_index_to_cast_body"))

        # if there is more than one parent (i.e. the in degree is greater than one) than
        # we should attach the result to be a sibling of the parents lowest common ancestor
        else:
            # UPDATE: lca function
            lca = find_lca_of_parents(self.curr_func_digraph, digraph_node)
            if lca.index in self.bb_index_to_cast_body:
                body = self.bb_index_to_cast_body[lca.index]
                body.extend(res)
                self.bb_index_to_cast_body[digraph_node.index] = body
                print(f"** BB{digraph_node.index} is going to be sibling to {lca.index} **")
            else:
                print((f"ERROR: Cannot attach {str(digraph_node)}, its parent {str(lca)}"
                       " is not in bb_index_to_cast_body"))
            




    def parse_function(self, f):
        # Clear data from function parsing
        self.clear_function_dependent_vars()

        name = f["name"]
        self.basic_blocks = f["basicBlocks"]
        # build basic block map
        for bb in self.basic_blocks:
            self.basic_block_map[bb["index"]] = bb

        parameters = f["parameters"] if "parameters" in f else []
        var_declarations = (
            f["variableDeclarations"] if "variableDeclarations" in f else []
        )


        # Generate network X function digraph and store it as necessary
        func_digraph = basic_blocks_to_digraph(f["basicBlocks"])
 
        self.curr_func_digraph = func_digraph
        # self.func_digraphs[f["name"]] = func_digraph

        for v in var_declarations:
            res = self.parse_variable_definition(v)
            if res is not None:
                self.curr_func_body.append(res)

        arguments = []
        for p in parameters:
            arguments.append(self.parse_variable(p))

        # process loops field of json and add info to self.bb_headers_to_loop


        # parse basic_blocks in order of loop num 0

        # parse basic blocks along a topological sort of the basic block digraph
        for bb_node in topological_sort(self.curr_func_digraph):
            # before continuing the parsing in the topological sort,
            # try to parse any basic blocks in the parse queue
            if len(self.basic_block_parse_queue) > 0:
                for bb in list(self.basic_block_parse_queue):
                    res = self.parse_basic_block(bb)
                    if res != []:
                        print(f"Parsed BB{bb['index']} from the queue")
                        self.basic_block_parse_queue.remove(bb)
                        self.attach_parsed_bb_result(res, make_bbnode(bb))

            index = bb_node.index

            if index in self.parsed_basic_blocks:
                assert index in self.bb_index_to_cast_body
                continue

            print(f"Parsing BB{index} from topo sort")
            res = self.parse_basic_block(self.basic_block_map[index])
            self.attach_parsed_bb_result(res, bb_node)
            # change to attach_parsed_bb_result
            # body.extend(res)
            
        # for bb in self.basic_blocks:
        #     res = self.parse_basic_block(bb)
        #     body.extend(res)

        # self.parsed_basic_blocks = set()
        # self.basic_block_map = {}
        # self.basic_block_parse_queue = set()
        # self.ssa_ids_to_expression = {}
        # self.variables_ids_to_expression = {}

        line_start = f["line_start"]
        line_end = f["line_end"]
        decl_line = f["decl_line_start"]
        decl_col = f["decl_col_start"]
        file = f["file"]

        body_source_ref = SourceRef(
            source_file_name=file, row_start=line_start, row_end=line_end
        )
        decl_source_ref = SourceRef(
            source_file_name=file, row_start=decl_line, col_start=decl_col
        )

        if self.source_language == "fortran":
            args_updated = self.check_fortran_arg_updates(arguments, self.curr_func_body)
            # TODO this will break with multiple returns within a function
            if len(args_updated) > 0:
                existing_return = [
                    (idx, b) for idx, b in enumerate(self.curr_func_body) if isinstance(b, ModelReturn)
                ]
                new_return = None
                if len(existing_return) == 0:
                    new_return = ModelReturn(
                        value=Tuple(values=[Name(n) for n in args_updated])
                    )
                else:
                    existing_return = existing_return[0][1]
                    existing_return_idx = existing_return[0][0]
                    del self.curr_func_body[existing_return_idx]
                    new_return = ModelReturn(
                        value=Tuple(
                            values=[existing_return.value]
                            + [Name(n) for n in args_updated]
                        )
                    )
                self.curr_func_body.append(new_return)

        return FunctionDef(
            name=name,
            func_args=arguments,
            body=self.curr_func_body,
            source_refs=[body_source_ref, decl_source_ref],
        )
