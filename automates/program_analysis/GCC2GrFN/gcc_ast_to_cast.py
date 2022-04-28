from pprint import pprint
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path

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

@dataclass
class LoopInfo:
    num: int
    header_bb: int
    depth: int
    num_latches: int
    latch_bbs: List
    num_nodes: int
    loop_body: List
    immediate_superloop: Optional[int]
    superloops: List
    children: List

def loop_json_to_loop_info(loop_json: Dict): 
    """
    Converts the loop json object obtained from the gcc plugin to a LoopInfo object
    and returns it
    """
    num = loop_json["num"]
    header_bb = loop_json["headerBB"]
    depth = loop_json["depth"]
    num_latches = loop_json["numLatches"]
    latch_bbs = loop_json["latchBBs"]
    num_nodes = loop_json["numNodes"]
    loop_body = loop_json["loopBody"]
    immediate_superloop = loop_json["immediateSuperloop"] if "immediateSuperloop" in loop_json else None
    superloops = loop_json["superloops"]
    children = loop_json["children"]

    return LoopInfo(num=num, header_bb=header_bb, depth=depth, num_latches=num_latches,
                    latch_bbs=latch_bbs, num_nodes=num_nodes, loop_body=loop_body,
                    immediate_superloop=immediate_superloop, superloops=superloops, children=children)


class GCC2CAST:
    """
    Takes a list of json objects where each object represents the GCC AST
    for one file outputted from our ast_dump.cpp GCC plugin.
    """

    def __init__(self, gcc_asts, legacy_cast: bool = False):
        self.gcc_asts = gcc_asts
        self.variables_ids_to_expression = {}
        self.ssa_ids_to_expression = {}
        self.type_ids_to_defined_types = {}
        self.basic_blocks = []
        self.bb_index_to_bb = {}
        self.basic_block_parse_queue = set()
        self.parsed_basic_blocks = set()
        # dict mapping BB index to the CAST body it is in
        self.bb_index_to_cast_body = {}
        self.current_basic_block = None
        
        # loop data
        self.top_level_pseudo_loop_body = []
        self.loop_num_to_loop_info = {}
        self.bb_headers_to_loop_info = {} 

        # legacy CAST generation does not create Name nodes
        # for the `name` attribute of FunctionDef's.
        # This allows the legacy CAST -> AIR -> GrFN 
        # pipeline to be run on the resulting CAST json
        self.legacy_cast = legacy_cast

    def clear_function_dependent_vars(self):
        self.variables_ids_to_expression = {}
        self.ssa_ids_to_expression = {}
        self.basic_blocks = []
        self.bb_index_to_bb = {}
        self.basic_block_parse_queue = set()
        self.parsed_basic_blocks = set()
        self.bb_index_to_cast_body = {}
        self.current_basic_block = None

        # loop data
        self.top_level_pseudo_loop_body = []
        self.loop_num_to_loop_info = {}
        self.bb_headers_to_loop_info = {} 


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
            file_path = Path(obj["file"])
            file_name = file_path.name
            source_refs.append(
                SourceRef(source_file_name=file_name, col_start=col, row_start=line)
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

        id = variable["id"] if "id" in variable else None
        source_refs = self.get_source_refs(variable)

        var_node = Var(
            val=Name(name=name, id=id, source_refs=source_refs),
            type=cast_type,
            source_refs=source_refs,
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
        # TODO: Rethink how variable declarations are handled
        # It does not make much sense to create an Assignment node from
        # a declaration
        # We could just return None, however there is a potential issue with
        # code like
        # int x;
        # int y = x + 1;
        # this would compile fine, and both x and y would end up with random
        # values
        # However, the translation to CAST would fail, when trying to 
        # evaluate the expression "x + 1" because there is no value for "x"
        # in `self.variables_ids_to_expression`
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
            id = value["id"]
            # TODO: add in source_refs to returned Name
            return Name(name=name, id=id)

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
                id = operand["id"]
                source_refs = self.get_source_refs(operand)
                return Name(name=name, id=id, source_refs=source_refs)
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
                id = lhs["id"]
                source_refs = self.get_source_refs(lhs)
                assign_var = Var(val=Name(name=name,id=id, source_refs=source_refs), type=cast_type, source_refs=source_refs)
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

        source_refs = self.get_source_refs(operand)

        return [
            Attribute(
                value=Name(name=var_name),
                attr=Name(name=field),
                source_refs=source_refs,
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
                    id = operands[0]["id"]
                    source_refs = self.get_source_refs(operands[0])
                    assign_value = Name(name=name,id=id, source_refs=source_refs)
                # When do we have an id but no name
                # Do we need to track the numerical id in this situation?
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
        func_id = function["value"]["id"]
        # TODO not sure if this is a permenant solution, but ignore these
        # unexpected builtin calls for now
        if "__builtin_" in func_name and not is_allowed_gcc_builtin_func(func_name):
            return []

        cast_args = []
        for arg in arguments:
            cast_args.append(self.parse_operand(arg))

        cast_call = Call(
            func=Name(name=func_name, id=func_id), arguments=cast_args, source_refs=src_ref
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
        cur_bb = self.current_basic_block
        cur_bb_index = cur_bb["index"]

        is_loop = cur_bb_index in self.bb_headers_to_loop_info
        condition_expr = self.parse_conditional_expr(stmt)

        if is_loop:
            # GCC inverts loop expressions to check if the EXIT condition
            # i.e., given "while (count < 100)", gcc converts that to "if (count > 99) leave loop;"
            # So, to revert to the original loop condition, add a boolean NOT
            condition_expr = UnaryOp(
                op=UnaryOperator.NOT,
                value=condition_expr,
                source_refs=condition_expr.source_refs,
            )
            # create Loop CAST node with header and empty body, we will attach parsed body later
            parsed_loop_body = []
            parsed_loop = Loop(expr=condition_expr, body=parsed_loop_body)
            self.bb_index_to_cast_body[cur_bb_index] = parsed_loop_body
            self.parsed_basic_blocks.add(cur_bb_index)

            loop = self.bb_headers_to_loop_info[cur_bb_index]
            loop_body = loop.loop_body
            # remove bb_header since we are already processing it
            assert(loop_body[0] == cur_bb_index)
            loop_body = loop_body[1:]
            self.parse_body(loop_body)

            return [parsed_loop]
        # otherwise parse as an if statement
        else:
            print(f"Parsing BB{true_block['index']} as an if body")
            true_res = self.parse_basic_block(true_block)
        
            # If the false block has one incoming edge, then we know it belongs 
            # as the orelse of this current node (in the case of else/else if)
            false_res = []
            # check if their is only one parent of false block, if so parse it as `orelse`
            if len(false_block["parents"]) == 1:
                print(f"Parsing BB{false_block['index']} as an elif")
                false_res = self.parse_basic_block(false_block)

            # build a ModelIf CAST node, and add the true_block/false_blocks indices
            # to bb_index_to_cast_body to keep track of where they were attached
            model_if = ModelIf(expr=condition_expr, body=true_res, orelse=false_res)
            assert(true_block["index"] not in self.bb_index_to_cast_body)
            self.bb_index_to_cast_body[true_block["index"]] = model_if.body
            print(f"** BB{true_block['index']} is the if body of BB{cur_bb_index}**")
            if false_res != []:
                print(f"** BB{false_block['index']} is the else if body of BB{cur_bb_index}**")
                self.bb_index_to_cast_body[false_block["index"]] = model_if.orelse

            return [model_if]

    def parse_body(self, loop_body):
        for bb_index in loop_body:
            bb = self.bb_index_to_bb[bb_index]
            res = self.parse_basic_block(bb)
            self.attach_parsed_bb_result(bb, res)


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
        # TODO from Ryan: we actually need to parse gotos, for example they can appear
        # because of break statements
        # we also need to start parsing predict statements which can occur from continue's
        # or labeled goto's
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
        bb_index = bb["index"]
        # make sure all dominators of the current BB have already been parsed
        for dom in bb["dominators"]:
            if dom != bb_index and dom not in self.parsed_basic_blocks:
                print((f"WARNING: Trying to parse BB{bb_index}, but its parent BB{dom} has" 
                        " note been parsed yet"))
                self.basic_block_parse_queue.add(bb)
                return []

        # we know all dominators have been parsed, so if this basic block has been parsed, then
        # we can skip it
        if bb_index in self.parsed_basic_blocks:
            return []

        # otherwise, we parse the basic block
        self.parsed_basic_blocks.add(bb_index)
        self.current_basic_block = bb

        statements = bb["statements"]
        cast_statements = []
        for stmt in statements:
            res = self.parse_statement(stmt, statements)
            cast_statements.extend(res)

        result_statements = cast_statements

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

    def attach_parsed_bb_result(self, bb, res):
        """
        Finds the CAST node body that this parsed basic block result should be added to,
        and extends the body with `res`.
        The body we attach `res` to is found by checking the "parentsNearestCommonDom" field
        of `bb`, except when `bb` has index 0 or 1, since these are
        the entry and exit points of a function, respectively.  If `bb` 
        has index 0 or 1, we attach `res` to `self.top_level_pseudo_loop_body`.  

        Parameters:
            res: the result from parse_basic_block()
            bb: the associated basic block json in dict form 
        """
        # BB0 is always the start of a function, and BB1 is the exist of a function
        # so we should add this res top_level_pseudo_loop_body
        if bb["index"] in [0, 1]:
            body = self.top_level_pseudo_loop_body
            body.extend(res)
            self.bb_index_to_cast_body[bb["index"]] = body
            print(f"** BB{bb['index']} is placed in the function body **")
            return

        # otherwise we should attach the result to be a sibling of its parents nearest 
        # common dominator
        nearest_common_dom = bb["parentsNearestCommonDom"]
        try:
            body = self.bb_index_to_cast_body[nearest_common_dom]
            body.extend(res)
            self.bb_index_to_cast_body[bb["index"]] = body
            print(f"** BB{bb['index']} is going to be sibling to {nearest_common_dom} **")
        except IndexError as e:
            print((f"ERROR: Cannot attach BB{bb['index']} because its nearest common dom {nearest_common_dom}"
                   " is not in bb_index_to_cast_body"))
            print(e)


    def parse_loops_field(self, loops_json):
        for loop in loops_json:
            loop_info = loop_json_to_loop_info(loop)
            self.bb_headers_to_loop_info[loop_info.header_bb] = loop_info
            self.loop_num_to_loop_info[loop_info.num] = loop_info


    def parse_basic_blocks(self, function):
        self.basic_blocks = function["basicBlocks"]
        # build basic block map
        for bb in self.basic_blocks:
            self.bb_index_to_bb[bb["index"]] = bb

        # parse basic_blocks in order of loop num 0
        loop_zero = self.loop_num_to_loop_info[0]
        for bb_index in loop_zero.loop_body:
            # before continuing to parse
            # try to parse any basic blocks in the parse queue
            if len(self.basic_block_parse_queue) > 0:
                for bb in list(self.basic_block_parse_queue):
                    res = self.parse_basic_block(bb)
                    if res != []:
                        print(f"Parsed BB{bb['index']} from the queue")
                        self.basic_block_parse_queue.remove(bb)
                        self.attach_parsed_bb_result(bb, res)

            if bb_index in self.parsed_basic_blocks:
                assert(bb_index in self.bb_index_to_cast_body)
                continue

            print(f"Parsing BB{bb_index} from loop zero loop_body")
            bb = self.bb_index_to_bb[bb_index]
            res = self.parse_basic_block(bb)
            self.attach_parsed_bb_result(bb, res)


    def get_func_source_refs(self, function):
        line_start = function["line_start"]
        line_end = function["line_end"]
        decl_line = function["decl_line_start"]
        decl_col = function["decl_col_start"]
        file_path = Path(function["file"])
        file_name = file_path.name

        body_source_ref = SourceRef(
            source_file_name=file_name, row_start=line_start, row_end=line_end
        )
        decl_source_ref = SourceRef(
            source_file_name=file_name, row_start=decl_line, col_start=decl_col
        )

        return body_source_ref, decl_source_ref


    def parse_function(self, function):
        # clear functions variables to prepare for parsing
        self.clear_function_dependent_vars()
        name = Name(function["name"], function["id"])

        # if we want legacy CAST, the `name` attribute should just be a string
        if self.legacy_cast:
            name = function["name"]

        parameters = function["parameters"] if "parameters" in function else []
        var_declarations = (
            function["variableDeclarations"] if "variableDeclarations" in function else []
        )

        for v in var_declarations:
            res = self.parse_variable_definition(v)
            if res is not None:
                self.top_level_pseudo_loop_body.append(res)

        arguments = []
        for p in parameters:
            arguments.append(self.parse_variable(p))

        # iterate over "loops" field of function json, and create LoopInfo's
        assert(len(function["loops"]) == function["numberOfLoops"])
        self.parse_loops_field(function["loops"])

        # parse basic blocks
        self.parse_basic_blocks(function)

        body_source_ref, decl_source_ref = self.get_func_source_refs(function)

        if self.source_language == "fortran":
            args_updated = self.check_fortran_arg_updates(arguments, self.top_level_pseudo_loop_body)
            # TODO this will break with multiple returns within a function
            if len(args_updated) > 0:
                existing_return = [
                    (idx, b) for idx, b in enumerate(self.top_level_pseudo_loop_body) if isinstance(b, ModelReturn)
                ]
                new_return = None
                if len(existing_return) == 0:
                    new_return = ModelReturn(
                        value=Tuple(values=[Name(n) for n in args_updated])
                    )
                else:
                    existing_return = existing_return[0][1]
                    existing_return_idx = existing_return[0][0]
                    del self.top_level_pseudo_loop_body[existing_return_idx]
                    new_return = ModelReturn(
                        value=Tuple(
                            values=[existing_return.value]
                            + [Name(n) for n in args_updated]
                        )
                    )
                self.top_level_pseudo_loop_body.append(new_return)

        return FunctionDef(
            name=name,
            func_args=arguments,
            body=self.top_level_pseudo_loop_body,
            source_refs=[body_source_ref, decl_source_ref],
        )
