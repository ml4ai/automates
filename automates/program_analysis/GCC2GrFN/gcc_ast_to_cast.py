from pprint import pprint

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
)
from automates.program_analysis.GCC2GrFN.gcc_ast_to_cast_utils import (
    is_valid_operator,
    is_const_operator,
    is_casting_operator,
    is_trunc_operator,
    get_cast_operator,
    get_const_value,
    gcc_type_to_var_type,
)


class GCC2CAST:
    def __init__(self, gcc_ast):
        self.variables_ids_to_expression = {}
        self.ssa_ids_to_expression = {}
        self.gcc_ast = gcc_ast
        self.basic_blocks = []
        self.parsed_basic_blocks = []
        self.current_basic_block = None
        self.type_ids_to_defined_types = {}

    def to_cast(self):
        input_file = self.gcc_ast["mainInputFilename"]
        functions = self.gcc_ast["functions"]
        types = self.gcc_ast["recordTypes"]
        global_variables = self.gcc_ast["globalVariables"]
        body = []

        # First fill out the ids to type names in case one type uses another
        # before it is defined.
        for t in types:
            self.type_ids_to_defined_types[t["id"]] = ClassDef(name=t["name"])

        for t in types:
            self.type_ids_to_defined_types[t["id"]] = self.parse_record_type(t)

        for gv in global_variables:
            body.append(self.parse_variable(gv))

        for f in functions:
            body.append(self.parse_function(f))

        file_module = Module(name=input_file.rsplit(".")[0], body=body)
        return CAST([file_module])

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
        id = record_type["id"]
        name = record_type["name"]
        self.type_ids_to_defined_types[id] = {"name": name}

        bases = []
        funcs = []

        record_type_fields = record_type["fields"]
        fields = [self.parse_record_type_field(f) for f in record_type_fields]

        source_refs = self.get_source_refs(record_type)

        return ClassDef(
            name=name, bases=bases, funcs=funcs, fields=fields, source_refs=source_refs
        )

    def parse_variable(self, variable):
        if "name" not in variable:
            return None
        var_type = variable["type"]
        name = variable["name"]
        cast_type = gcc_type_to_var_type(var_type, self.type_ids_to_defined_types)

        line = variable["line_start"]
        col = variable["col_start"]
        file = variable["file"]
        source_ref = SourceRef(source_file_name=file, col_start=col, row_start=line)

        return Var(
            val=Name(name=name),
            type=cast_type,
            source_refs=[source_ref],
        )

    def parse_operand(self, operand):
        code = operand["code"]
        if code == "ssa_name":
            ssa_id = operand["ssa_id"]
            stored_ssa_expr = self.ssa_ids_to_expression[ssa_id]
            del self.ssa_ids_to_expression[ssa_id]
            return stored_ssa_expr
        elif is_const_operator(code):
            return Number(number=get_const_value(operand))
        elif code == "var_decl" or code == "parm_decl":
            if "name" in operand:
                return Name(name=operand["name"])
            elif "id" in operand:
                return self.variables_ids_to_expression[operand["id"]]

    def parse_array_ref_operand(self, operand):
        array = operand["array"]
        pointer = array["pointer"]
        name = pointer["name"]

        index = operand["index"]
        index_result = self.parse_operand(index)

        return Subscript(value=Name(name=name), slice=index_result)

    def parse_lhs(self, stmt, lhs, assign_value):
        assign_var = None
        if lhs["code"] == "component_ref":
            assign_var = self.parse_component_ref(lhs)[0]
        elif lhs["code"] == "var_decl":
            assign_var = self.parse_variable(lhs)

        if assign_var is None and "id" in lhs:
            self.variables_ids_to_expression[lhs["id"]] = assign_value
            return []
        elif "ssa_id" in lhs:
            ssa_id = lhs["ssa_id"]
            self.ssa_ids_to_expression[ssa_id] = assign_value
            return []

        source_refs = self.get_source_refs(stmt)
        # if "line_start" in stmt:
        #     source_refs.append(
        #         SourceRef(
        #             source_file_name=stmt["file"],
        #             row_start=stmt["line_start"],
        #             col_start=stmt["col_start"],
        #         )
        #     )

        return [
            Assignment(left=assign_var, right=assign_value, source_refs=source_refs)
        ]

    def parse_component_ref(self, operand):
        value = operand["value"]
        var_name = value["name"]
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
                assign_value = Number(number=get_const_value(operands[0]))
            elif (
                operator == "var_decl"
                or operator == "parm_decl"
                or operator == "ssa_name"
            ):
                if "name" in operands[0]:
                    assign_value = Name(name=operands[0]["name"])
                elif "id" in operands[0]:
                    assign_value = self.variable_ids_to_expression(operands[0]["id"])
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
            else:
                cast_op = get_cast_operator(operator)
                ops = []
                for op in operands:
                    ops.append(self.parse_operand(op))
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
        if "__builtin_" in func_name:
            return []

        cast_args = []
        for arg in arguments:
            cast_args.append(self.parse_operand(arg))

        cast_call = Call(func=Name(func_name), arguments=cast_args, source_refs=src_ref)
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

        is_loop = False
        for false_bb_stmt in false_block["statements"]:
            if (
                false_bb_stmt["type"] == "goto"
                and false_bb_stmt["target"] == self.current_basic_block["index"]
            ):
                is_loop = True

        temp = self.current_basic_block
        false_res = self.parse_basic_block(false_block)
        true_res = self.parse_basic_block(true_block)
        self.current_basic_block = temp

        condition_expr = self.parse_conditional_expr(stmt)

        if is_loop:
            return [Loop(expr=condition_expr, body=false_res)]

        else:
            # TODO handle or else
            return [ModelIf(expr=condition_expr, body=true_res, orelse=[])]

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
            stmt_type
            == "goto"  # Already handled in the conditional stmt type, just skip
            or stmt_type == "resx"  # Doesnt concern us
        ):
            return []
        else:
            # TODO custom exception
            raise Exception(f"Error: Unknown statement type {stmt_type}")

        return result

    def parse_basic_block(self, bb):
        if bb["index"] in self.parsed_basic_blocks:
            return []
        self.parsed_basic_blocks.append(bb["index"])

        self.current_basic_block = bb
        statements = bb["statements"]
        cast_statements = []
        for stmt in statements:
            cast_statements.extend(self.parse_statement(stmt, statements))

        result_statements = cast_statements
        if "edges" in bb:
            edges = bb["edges"]
            for e in edges:
                target_edge = int(e["target"])
                result_statements += self.parse_basic_block(
                    [bb for bb in self.basic_blocks if bb["index"] == target_edge][0]
                )

        return result_statements

    def parse_function(self, f):
        name = f["name"]
        self.basic_blocks = f["basicBlocks"]
        parameters = f["parameters"] if "parameters" in f else []

        arguments = []
        for p in parameters:
            arguments.append(self.parse_variable(p))

        body = []
        for bb in self.basic_blocks:
            body.extend(self.parse_basic_block(bb))

        # Clear data from function parsing
        self.parsed_basic_blocks = []
        self.ssa_ids_to_expression = {}
        self.variables_ids_to_expression = {}

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

        return FunctionDef(
            name=name,
            func_args=arguments,
            body=body,
            source_refs=[body_source_ref, decl_source_ref],
        )
