import pytest
import ast
import json

from automates.program_analysis.PyAST2CAST import py_ast_to_cast
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
)
from automates.program_analysis.CAST2GrFN import cast

DATA_DIR = "tests/data/program_analysis/PyAST2CAST"


def dump_cast(C):
    print(C.to_json_str())


def run_test_case(filepath, prog_name):
    file_handle = open(filepath)
    file_list = file_handle.readlines()
    line_count = 0
    for l in file_list:
        line_count += 1
    file_handle.close()

    file_contents = open(filepath).read()
    convert = py_ast_to_cast.PyASTToCAST(prog_name)

    test_C = convert.visit(ast.parse(file_contents))
    test_C.source_refs = [SourceRef(prog_name, None, None, 1, line_count)]

    out_cast = cast.CAST([test_C], cast_source_language="python")
    to_compare = out_cast.to_json_object()

    raw_json = json.load(
        open(f"{DATA_DIR}/expected_output/{prog_name.split('.')[0]}--CAST.json", "r")
    )

    assert raw_json == to_compare


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_class_1():
    prog_name = "test_class_1.py"
    folder = "class"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_class_2():
    prog_name = "test_class_2.py"
    folder = "class"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_bool_1():
    prog_name = "test_bool_1.py"
    folder = "expression"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_call_1():
    prog_name = "test_call_1.py"
    folder = "expression"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_ext_slice_1():
    prog_name = "test_ext_slice_1.py"
    folder = "expression"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_increment_1():
    prog_name = "test_increment_1.py"
    folder = "expression"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_list_1():
    prog_name = "test_list_1.py"
    folder = "expression"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_list_2():
    prog_name = "test_list_2.py"
    folder = "expression"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_name_1():
    prog_name = "test_name_1.py"
    folder = "expression"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_add_1():
    prog_name = "test_add_1.py"
    folder = "function_def"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_add_2():
    prog_name = "test_add_2.py"
    folder = "function_def"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_assign_1():
    prog_name = "test_assign_1.py"
    folder = "function_def"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_assign_2():
    prog_name = "test_assign_2.py"
    folder = "function_def"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_assign_3():
    prog_name = "test_assign_3.py"
    folder = "function_def"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_assign_4():
    prog_name = "test_assign_4.py"
    folder = "function_def"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_assign_5():
    prog_name = "test_assign_5.py"
    folder = "function_def"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_assign_6():
    prog_name = "test_assign_6.py"
    folder = "function_def"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_function_1():
    prog_name = "test_function_1.py"
    folder = "function_def"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_lambda_1():
    prog_name = "test_lambda_1.py"
    folder = "function_def"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_if_1():
    prog_name = "test_if_1.py"
    folder = "if"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_if_2():
    prog_name = "test_if_2.py"
    folder = "if"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_if_3():
    prog_name = "test_if_3.py"
    folder = "if"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_if_4():
    prog_name = "test_if_4.py"
    folder = "if"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_if_5():
    prog_name = "test_if_5.py"
    folder = "if"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_import_1():
    prog_name = "test_import_1.py"
    folder = "import"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_import_2():
    prog_name = "test_import_2.py"
    folder = "import"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_import_3():
    prog_name = "test_import_3.py"
    folder = "import"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)


@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_for_1():
    prog_name = "test_for_1.py"
    folder = "loop"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)

@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_for_2():
    prog_name = "test_for_2.py"
    folder = "loop"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)

@pytest.mark.skip(reason="cast updates require changes to test cases")
def test_while_1():
    prog_name = "test_while_1.py"
    folder = "loop"

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

    run_test_case(filepath, prog_name)
