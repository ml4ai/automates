from automates.program_analysis.CAST2GrFN.model.cast import (
    BinaryOperator,
    UnaryOperator,
    VarType,
)

GCC_OPS_TO_CAST_OPS = {
    "mult_expr": BinaryOperator.MULT,
    "plus_expr": BinaryOperator.ADD,
    "minus_expr": BinaryOperator.SUB,
    "ge_expr": BinaryOperator.GTE,
    "gt_expr": BinaryOperator.GT,
    "rdiv_expr": BinaryOperator.DIV,
}

GCC_CONST_OPS = ["integer_cst", "real_cst"]

GCC_CASTING_OPS = ["float_expr", "int_expr"]
GCC_TRUNC_OPS = ["trunc_div_expr", "trunc_mod_expr", "fix_trunc_expr"]


def is_casting_operator(op):
    return op in GCC_CASTING_OPS


def is_trunc_operator(op):
    return op in GCC_TRUNC_OPS


def is_valid_operator(op):
    # TODO handle all valid ops
    return (
        op in GCC_OPS_TO_CAST_OPS
        or op in GCC_CONST_OPS
        or op in GCC_CASTING_OPS
        or op in GCC_TRUNC_OPS
        # Refers to prexisting var decl
        or op == "var_decl"
        or op == "parm_decl"
        or op == "ssa_name"
        or op == "array_ref"
        or op == "nop_expr"
        or op == "component_ref"
    )


def is_const_operator(op):
    return op in GCC_CONST_OPS


def get_const_value(operand):
    if operand["code"] == "integer_cst":
        return operand["value"]
    elif operand["code"] == "real_cst":
        return float(operand["decimal"])


def get_cast_operator(op):
    return GCC_OPS_TO_CAST_OPS[op] if is_valid_operator(op) else None


def gcc_type_to_var_type(type, type_ids_to_defined_types):
    type_name = type["type"]

    if (
        type_name == "integer_type"
        or type_name == "real_type"
        or type_name == "float_type"
    ):
        return "Number"
    elif type_name == "pointer_type" or type_name == "array_type":
        return "List"
    elif (
        type_name == "record_type"
        and "id" in type
        and type["id"] in type_ids_to_defined_types
    ):
        return "object"
        # TODO how do we specify the name of the object? building the grfn requires
        # just "object" as the type, probably need an additional field to represent
        # the name.
        # return type_ids_to_defined_types[type["id"]]["name"]
    else:
        # TODO custom exception
        raise Exception(f"Error: Unknown gcc type {type_name}")