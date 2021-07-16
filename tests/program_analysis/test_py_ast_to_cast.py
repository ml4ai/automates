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


def test_class_1():
    prog_name = "test_class_1.py"
    folder = "class"

    raw_json = '{"nodes": [{"body": [{"bases": [], "fields": [{"node_type": "Var", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_class_1.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_class_1.py"}]}}, {"node_type": "Var", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_class_1.py"}], "type": "integer", "val": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_class_1.py"}]}}], "funcs": [{"body": [{"left": {"attr": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_class_1.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_class_1.py"}], "value": {"name": "self", "node_type": "Name", "source_refs": [{"col_end": 12, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_class_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 18, "col_start": 17, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_class_1.py"}]}, "source_refs": [{"col_end": 18, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_class_1.py"}]}, {"left": {"attr": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_class_1.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_class_1.py"}], "value": {"name": "self", "node_type": "Name", "source_refs": [{"col_end": 12, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_class_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 18, "col_start": 17, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_class_1.py"}]}, "source_refs": [{"col_end": 18, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_class_1.py"}]}], "func_args": [{"node_type": "Var", "source_refs": [{"col_end": 21, "col_start": 17, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_class_1.py"}], "type": "integer", "val": {"name": "self", "node_type": "Name", "source_refs": [{"col_end": 21, "col_start": 17, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_class_1.py"}]}}], "name": "__init__", "node_type": "FunctionDef", "source_refs": [{"col_end": 18, "col_start": 4, "node_type": "SourceRef", "row_end": 4, "row_start": 2, "source_file_name": "test_class_1.py"}]}], "name": "Foo", "node_type": "ClassDef", "source_refs": [{"col_end": 18, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_class_1.py"}]}, {"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_class_1.py"}], "type": "integer", "val": {"name": "f", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_class_1.py"}]}}, "node_type": "Assignment", "right": {"arguments": [], "func": {"name": "Foo", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 8, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_class_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 13, "col_start": 8, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_class_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_class_1.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 13, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 6, "source_file_name": "test_class_1.py"}]}, {"expr": {"arguments": [], "func": {"name": "main", "node_type": "Name", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 9, "row_start": 9, "source_file_name": "test_class_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 9, "row_start": 9, "source_file_name": "test_class_1.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 9, "row_start": 9, "source_file_name": "test_class_1.py"}]}], "name": "test_class_1", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 9, "row_start": 1, "source_file_name": "test_class_1.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare


def test_class_2():
    prog_name = "test_class_2.py"
    folder = "class"

    raw_json = '{"nodes": [{"body": [{"bases": [], "fields": [{"node_type": "Var", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_class_2.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_class_2.py"}]}}, {"node_type": "Var", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_class_2.py"}], "type": "integer", "val": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_class_2.py"}]}}], "funcs": [{"body": [{"left": {"attr": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_class_2.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_class_2.py"}], "value": {"name": "self", "node_type": "Name", "source_refs": [{"col_end": 12, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_class_2.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 18, "col_start": 17, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_class_2.py"}]}, "source_refs": [{"col_end": 18, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_class_2.py"}]}, {"left": {"attr": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_class_2.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_class_2.py"}], "value": {"name": "self", "node_type": "Name", "source_refs": [{"col_end": 12, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_class_2.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 18, "col_start": 17, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_class_2.py"}]}, "source_refs": [{"col_end": 18, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_class_2.py"}]}], "func_args": [{"node_type": "Var", "source_refs": [{"col_end": 21, "col_start": 17, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_class_2.py"}], "type": "integer", "val": {"name": "self", "node_type": "Name", "source_refs": [{"col_end": 21, "col_start": 17, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_class_2.py"}]}}], "name": "__init__", "node_type": "FunctionDef", "source_refs": [{"col_end": 18, "col_start": 4, "node_type": "SourceRef", "row_end": 4, "row_start": 2, "source_file_name": "test_class_2.py"}]}, {"body": [{"left": {"attr": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_class_2.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_class_2.py"}], "value": {"name": "self", "node_type": "Name", "source_refs": [{"col_end": 12, "col_start": 8, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_class_2.py"}]}}, "node_type": "Assignment", "right": {"attr": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 23, "col_start": 17, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_class_2.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 23, "col_start": 17, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_class_2.py"}], "value": {"name": "self", "node_type": "Name", "source_refs": [{"col_end": 21, "col_start": 17, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_class_2.py"}]}}, "source_refs": [{"col_end": 23, "col_start": 8, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_class_2.py"}]}, {"node_type": "ModelReturn", "source_refs": [{"col_end": 21, "col_start": 8, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_class_2.py"}], "value": {"attr": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 21, "col_start": 15, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_class_2.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 21, "col_start": 15, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_class_2.py"}], "value": {"name": "self", "node_type": "Name", "source_refs": [{"col_end": 19, "col_start": 15, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_class_2.py"}]}}}], "func_args": [{"node_type": "Var", "source_refs": [{"col_end": 16, "col_start": 12, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_class_2.py"}], "type": "integer", "val": {"name": "self", "node_type": "Name", "source_refs": [{"col_end": 16, "col_start": 12, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_class_2.py"}]}}], "name": "bar", "node_type": "FunctionDef", "source_refs": [{"col_end": 21, "col_start": 4, "node_type": "SourceRef", "row_end": 8, "row_start": 6, "source_file_name": "test_class_2.py"}]}], "name": "Foo", "node_type": "ClassDef", "source_refs": [{"col_end": 18, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_class_2.py"}]}, {"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_class_2.py"}], "type": "integer", "val": {"name": "f", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_class_2.py"}]}}, "node_type": "Assignment", "right": {"arguments": [], "func": {"name": "Foo", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 8, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_class_2.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 13, "col_start": 8, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_class_2.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_class_2.py"}]}, {"expr": {"arguments": [], "func": {"attr": {"name": "bar", "node_type": "Name", "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 12, "row_start": 12, "source_file_name": "test_class_2.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 12, "row_start": 12, "source_file_name": "test_class_2.py"}], "value": {"name": "f", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 12, "row_start": 12, "source_file_name": "test_class_2.py"}]}}, "node_type": "Call", "source_refs": [{"col_end": 11, "col_start": 4, "node_type": "SourceRef", "row_end": 12, "row_start": 12, "source_file_name": "test_class_2.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 11, "col_start": 4, "node_type": "SourceRef", "row_end": 12, "row_start": 12, "source_file_name": "test_class_2.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 11, "col_start": 0, "node_type": "SourceRef", "row_end": 12, "row_start": 10, "source_file_name": "test_class_2.py"}]}, {"expr": {"arguments": [], "func": {"name": "main", "node_type": "Name", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 14, "row_start": 14, "source_file_name": "test_class_2.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 14, "row_start": 14, "source_file_name": "test_class_2.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 14, "row_start": 14, "source_file_name": "test_class_2.py"}]}], "name": "test_class_2", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 14, "row_start": 1, "source_file_name": "test_class_2.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])
    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare


def test_bool_1():
    prog_name = "test_bool_1.py"
    folder = "expression"

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_bool_1.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_bool_1.py"}]}}, "node_type": "Assignment", "right": {"boolean": true, "node_type": "Boolean", "source_refs": [{"col_end": 12, "col_start": 8, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_bool_1.py"}]}, "source_refs": [{"col_end": 12, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_bool_1.py"}]}, {"body": [{"expr": {"arguments": [{"name": "x", "node_type": "Name", "source_refs": [{"col_end": 15, "col_start": 14, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_bool_1.py"}]}], "func": {"name": "print", "node_type": "Name", "source_refs": [{"col_end": 16, "col_start": 8, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_bool_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 16, "col_start": 8, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_bool_1.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 16, "col_start": 8, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_bool_1.py"}]}], "expr": {"left": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 8, "col_start": 7, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_bool_1.py"}]}, "node_type": "BinaryOp", "op": "Eq", "right": {"boolean": true, "node_type": "Boolean", "source_refs": [{"col_end": 16, "col_start": 12, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_bool_1.py"}]}, "source_refs": [{"col_end": 16, "col_start": 7, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_bool_1.py"}]}, "node_type": "ModelIf", "orelse": [], "source_refs": [{"col_end": 16, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_bool_1.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 16, "col_start": 0, "node_type": "SourceRef", "row_end": 5, "row_start": 1, "source_file_name": "test_bool_1.py"}]}], "name": "test_bool_1", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 6, "row_start": 1, "source_file_name": "test_bool_1.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])
    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare



def test_call_1():
    prog_name = "test_call_1.py"
    folder = "expression"

    raw_json = '{"nodes": [{"body": [{"body": [{"node_type": "ModelReturn", "source_refs": [{"col_end": 16, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_call_1.py"}], "value": {"left": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 12, "col_start": 11, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_call_1.py"}]}, "node_type": "BinaryOp", "op": "Mult", "right": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 16, "col_start": 15, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_call_1.py"}]}, "source_refs": [{"col_end": 16, "col_start": 11, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_call_1.py"}]}}], "func_args": [{"node_type": "Var", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_call_1.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_call_1.py"}]}}], "name": "foo", "node_type": "FunctionDef", "source_refs": [{"col_end": 16, "col_start": 0, "node_type": "SourceRef", "row_end": 3, "row_start": 2, "source_file_name": "test_call_1.py"}]}, {"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_call_1.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_call_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_call_1.py"}]}, "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_call_1.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_call_1.py"}], "type": "integer", "val": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_call_1.py"}]}}, "node_type": "Assignment", "right": {"left": {"node_type": "Number", "number": 3, "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_call_1.py"}]}, "node_type": "BinaryOp", "op": "Add", "right": {"arguments": [{"node_type": "Number", "number": 2, "source_refs": [{"col_end": 17, "col_start": 16, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_call_1.py"}]}], "func": {"name": "foo", "node_type": "Name", "source_refs": [{"col_end": 18, "col_start": 12, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_call_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 18, "col_start": 12, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_call_1.py"}]}, "source_refs": [{"col_end": 18, "col_start": 8, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_call_1.py"}]}, "source_refs": [{"col_end": 18, "col_start": 4, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_call_1.py"}]}, {"expr": {"arguments": [{"name": "y", "node_type": "Name", "source_refs": [{"col_end": 11, "col_start": 10, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_call_1.py"}]}], "func": {"name": "print", "node_type": "Name", "source_refs": [{"col_end": 12, "col_start": 4, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_call_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 12, "col_start": 4, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_call_1.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 12, "col_start": 4, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_call_1.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 12, "col_start": 0, "node_type": "SourceRef", "row_end": 8, "row_start": 5, "source_file_name": "test_call_1.py"}]}], "name": "test_call_1", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 8, "row_start": 1, "source_file_name": "test_call_1.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])
    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare

def test_ext_slice_1():
    prog_name = "test_ext_slice_1.py"
    folder = "expression"

    raw_json = '{"nodes": [{"body": [{"body": [], "name": "np", "node_type": "Module", "source_refs": [{"col_end": 18, "col_start": 0, "node_type": "SourceRef", "row_end": 1, "row_start": 1, "source_file_name": "test_ext_slice_1.py"}]}, {"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_ext_slice_1.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_ext_slice_1.py"}]}}, "node_type": "Assignment", "right": {"arguments": [{"node_type": "Tuple", "source_refs": [{"col_end": 24, "col_start": 17, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_ext_slice_1.py"}], "values": [{"node_type": "Number", "number": 3, "source_refs": [{"col_end": 19, "col_start": 18, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_ext_slice_1.py"}]}, {"node_type": "Number", "number": 3, "source_refs": [{"col_end": 21, "col_start": 20, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_ext_slice_1.py"}]}, {"node_type": "Number", "number": 3, "source_refs": [{"col_end": 23, "col_start": 22, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_ext_slice_1.py"}]}]}], "func": {"attr": {"name": "zeros", "node_type": "Name", "source_refs": [{"col_end": 16, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_ext_slice_1.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 16, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_ext_slice_1.py"}], "value": {"name": "numpy", "node_type": "Name", "source_refs": [{"col_end": 10, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_ext_slice_1.py"}]}}, "node_type": "Call", "source_refs": [{"col_end": 25, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_ext_slice_1.py"}]}, "source_refs": [{"col_end": 25, "col_start": 4, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_ext_slice_1.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}], "type": "integer", "val": {"name": "x_1", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "List", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}], "values": []}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}], "type": "integer", "val": {"name": "generated_index%", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 0, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, {"body": [{"arguments": [{"node_type": "Subscript", "slice": {"name": "generated_index%", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}], "value": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}}], "func": {"attr": {"name": "append", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}], "value": {"name": "x_1", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}}, "node_type": "Call", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}], "type": "integer", "val": {"name": "generated_index%", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}}, "node_type": "Assignment", "right": {"left": {"name": "generated_index%", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "node_type": "BinaryOp", "op": "Add", "right": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}], "expr": {"left": {"name": "generated_index%", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "node_type": "BinaryOp", "op": "Lt", "right": {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "node_type": "Loop", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}], "type": "integer", "val": {"name": "x_2", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "List", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}], "values": []}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}], "type": "integer", "val": {"name": "generated_index%", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 0, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, {"body": [{"arguments": [{"node_type": "Subscript", "slice": {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 12, "col_start": 11, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}], "value": {"name": "x_1", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}}], "func": {"attr": {"name": "append", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}], "value": {"name": "x_2", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}}, "node_type": "Call", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}], "type": "integer", "val": {"name": "generated_index%", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}}, "node_type": "Assignment", "right": {"left": {"name": "generated_index%", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "node_type": "BinaryOp", "op": "Add", "right": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}], "expr": {"left": {"name": "generated_index%", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "node_type": "BinaryOp", "op": "Lt", "right": {"arguments": [{"name": "x_1", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}], "func": {"name": "len", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}, "node_type": "Loop", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_ext_slice_1.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 13, "col_start": 0, "node_type": "SourceRef", "row_end": 6, "row_start": 3, "source_file_name": "test_ext_slice_1.py"}]}], "name": "test_ext_slice_1", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 6, "row_start": 1, "source_file_name": "test_ext_slice_1.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])
    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare

def test_increment_1():
    prog_name = "test_increment_1.py"
    folder = "expression"

    raw_json = '{"nodes": [{"body": [{"bases": [], "fields": [{"node_type": "Var", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_increment_1.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_increment_1.py"}]}}], "funcs": [{"body": [{"left": {"attr": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_increment_1.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 14, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_increment_1.py"}], "value": {"name": "self", "node_type": "Name", "source_refs": [{"col_end": 12, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_increment_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 18, "col_start": 17, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_increment_1.py"}]}, "source_refs": [{"col_end": 18, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_increment_1.py"}]}], "func_args": [{"node_type": "Var", "source_refs": [{"col_end": 21, "col_start": 17, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_increment_1.py"}], "type": "integer", "val": {"name": "self", "node_type": "Name", "source_refs": [{"col_end": 21, "col_start": 17, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_increment_1.py"}]}}], "name": "__init__", "node_type": "FunctionDef", "source_refs": [{"col_end": 18, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 2, "source_file_name": "test_increment_1.py"}]}], "name": "Foo", "node_type": "ClassDef", "source_refs": [{"col_end": 18, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_increment_1.py"}]}, {"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_increment_1.py"}], "type": "integer", "val": {"name": "i", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_increment_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 0, "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_increment_1.py"}]}, "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_increment_1.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_increment_1.py"}], "type": "integer", "val": {"name": "i", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_increment_1.py"}]}}, "node_type": "Assignment", "right": {"left": {"name": "i", "node_type": "Name", "source_refs": [{"col_end": 10, "col_start": 4, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_increment_1.py"}]}, "node_type": "BinaryOp", "op": "Add", "right": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 10, "col_start": 9, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_increment_1.py"}]}, "source_refs": [{"col_end": 10, "col_start": 4, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_increment_1.py"}]}, "source_refs": [{"col_end": 10, "col_start": 4, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_increment_1.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_increment_1.py"}], "type": "integer", "val": {"name": "i", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_increment_1.py"}]}}, "node_type": "Assignment", "right": {"left": {"name": "i", "node_type": "Name", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_increment_1.py"}]}, "node_type": "BinaryOp", "op": "Add", "right": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_increment_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 8, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_increment_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_increment_1.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 10, "row_start": 10, "source_file_name": "test_increment_1.py"}], "type": "integer", "val": {"name": "f", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 10, "row_start": 10, "source_file_name": "test_increment_1.py"}]}}, "node_type": "Assignment", "right": {"arguments": [], "func": {"name": "Foo", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 8, "node_type": "SourceRef", "row_end": 10, "row_start": 10, "source_file_name": "test_increment_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 13, "col_start": 8, "node_type": "SourceRef", "row_end": 10, "row_start": 10, "source_file_name": "test_increment_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 10, "row_start": 10, "source_file_name": "test_increment_1.py"}]}, {"left": {"attr": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 7, "col_start": 4, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_increment_1.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 7, "col_start": 4, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_increment_1.py"}], "value": {"name": "f", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_increment_1.py"}]}}, "node_type": "Assignment", "right": {"left": {"attr": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 7, "col_start": 4, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_increment_1.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 7, "col_start": 4, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_increment_1.py"}], "value": {"name": "f", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_increment_1.py"}]}}, "node_type": "BinaryOp", "op": "Add", "right": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 12, "col_start": 11, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_increment_1.py"}]}, "source_refs": [{"col_end": 12, "col_start": 4, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_increment_1.py"}]}, "source_refs": [{"col_end": 12, "col_start": 4, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_increment_1.py"}]}, {"left": {"attr": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 7, "col_start": 4, "node_type": "SourceRef", "row_end": 12, "row_start": 12, "source_file_name": "test_increment_1.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 7, "col_start": 4, "node_type": "SourceRef", "row_end": 12, "row_start": 12, "source_file_name": "test_increment_1.py"}], "value": {"name": "f", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 12, "row_start": 12, "source_file_name": "test_increment_1.py"}]}}, "node_type": "Assignment", "right": {"left": {"attr": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 10, "node_type": "SourceRef", "row_end": 12, "row_start": 12, "source_file_name": "test_increment_1.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 13, "col_start": 10, "node_type": "SourceRef", "row_end": 12, "row_start": 12, "source_file_name": "test_increment_1.py"}], "value": {"name": "f", "node_type": "Name", "source_refs": [{"col_end": 11, "col_start": 10, "node_type": "SourceRef", "row_end": 12, "row_start": 12, "source_file_name": "test_increment_1.py"}]}}, "node_type": "BinaryOp", "op": "Add", "right": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 17, "col_start": 16, "node_type": "SourceRef", "row_end": 12, "row_start": 12, "source_file_name": "test_increment_1.py"}]}, "source_refs": [{"col_end": 17, "col_start": 10, "node_type": "SourceRef", "row_end": 12, "row_start": 12, "source_file_name": "test_increment_1.py"}]}, "source_refs": [{"col_end": 17, "col_start": 4, "node_type": "SourceRef", "row_end": 12, "row_start": 12, "source_file_name": "test_increment_1.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 17, "col_start": 0, "node_type": "SourceRef", "row_end": 12, "row_start": 5, "source_file_name": "test_increment_1.py"}]}, {"expr": {"arguments": [], "func": {"name": "main", "node_type": "Name", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 13, "row_start": 13, "source_file_name": "test_increment_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 13, "row_start": 13, "source_file_name": "test_increment_1.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 13, "row_start": 13, "source_file_name": "test_increment_1.py"}]}], "name": "test_increment_1", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 13, "row_start": 1, "source_file_name": "test_increment_1.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])
    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare



def test_list_1():
    prog_name = "test_list_1.py"
    folder = "expression"

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_list_1.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_list_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "List", "source_refs": [{"col_end": 13, "col_start": 8, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_list_1.py"}], "values": [{"node_type": "Number", "number": 1.0, "source_refs": [{"col_end": 12, "col_start": 9, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_list_1.py"}]}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_list_1.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 13, "col_start": 0, "node_type": "SourceRef", "row_end": 2, "row_start": 1, "source_file_name": "test_list_1.py"}]}, {"expr": {"arguments": [], "func": {"name": "main", "node_type": "Name", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_list_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_list_1.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_list_1.py"}]}], "name": "test_list_1", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 4, "row_start": 1, "source_file_name": "test_list_1.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare


def test_list_2():
    prog_name = "test_list_2.py"
    folder = "expression"

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_list_2.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_list_2.py"}]}}, "node_type": "Assignment", "right": {"node_type": "List", "source_refs": [{"col_end": 17, "col_start": 8, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_list_2.py"}], "values": [{"node_type": "Number", "number": 1, "source_refs": [{"col_end": 10, "col_start": 9, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_list_2.py"}]}, {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 12, "col_start": 11, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_list_2.py"}]}, {"node_type": "Number", "number": 3, "source_refs": [{"col_end": 14, "col_start": 13, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_list_2.py"}]}, {"node_type": "Number", "number": 4, "source_refs": [{"col_end": 16, "col_start": 15, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_list_2.py"}]}]}, "source_refs": [{"col_end": 17, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_list_2.py"}]}, {"left": {"node_type": "Subscript", "slice": {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 7, "col_start": 6, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_list_2.py"}]}, "source_refs": [{"col_end": 8, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_list_2.py"}], "value": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_list_2.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 10, "source_refs": [{"col_end": 13, "col_start": 11, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_list_2.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_list_2.py"}]}, {"left": {"node_type": "Subscript", "slice": {"left": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 7, "col_start": 6, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_list_2.py"}]}, "node_type": "BinaryOp", "op": "Add", "right": {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_list_2.py"}]}, "source_refs": [{"col_end": 9, "col_start": 6, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_list_2.py"}]}, "source_refs": [{"col_end": 10, "col_start": 4, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_list_2.py"}], "value": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_list_2.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 7, "source_refs": [{"col_end": 14, "col_start": 13, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_list_2.py"}]}, "source_refs": [{"col_end": 14, "col_start": 4, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_list_2.py"}]}, {"left": {"node_type": "Subscript", "slice": {"node_type": "Number", "number": 0, "source_refs": [{"col_end": 7, "col_start": 6, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_list_2.py"}]}, "source_refs": [{"col_end": 8, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_list_2.py"}], "value": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_list_2.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Subscript", "slice": {"node_type": "Number", "number": 3, "source_refs": [{"col_end": 14, "col_start": 13, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_list_2.py"}]}, "source_refs": [{"col_end": 15, "col_start": 11, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_list_2.py"}], "value": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 12, "col_start": 11, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_list_2.py"}]}}, "source_refs": [{"col_end": 15, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_list_2.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 15, "col_start": 0, "node_type": "SourceRef", "row_end": 5, "row_start": 1, "source_file_name": "test_list_2.py"}]}, {"expr": {"arguments": [], "func": {"name": "main", "node_type": "Name", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_list_2.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_list_2.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_list_2.py"}]}], "name": "test_list_2", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 7, "row_start": 1, "source_file_name": "test_list_2.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])
    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare

def test_name_1():
    prog_name = "test_name_1.py"
    folder = "expression"

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_name_1.py"}], "type": "integer", "val": {"name": "w", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_name_1.py"}]}}, "node_type": "Assignment", "right": {"left": {"left": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_name_1.py"}]}, "node_type": "BinaryOp", "op": "Mult", "right": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_name_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 8, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_name_1.py"}]}, "node_type": "BinaryOp", "op": "Sub", "right": {"name": "z", "node_type": "Name", "source_refs": [{"col_end": 17, "col_start": 16, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_name_1.py"}]}, "source_refs": [{"col_end": 17, "col_start": 8, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_name_1.py"}]}, "source_refs": [{"col_end": 17, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_name_1.py"}]}, {"node_type": "ModelReturn", "source_refs": [{"col_end": 18, "col_start": 4, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_name_1.py"}], "value": {"node_type": "Tuple", "source_refs": [{"col_end": 18, "col_start": 11, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_name_1.py"}], "values": [{"name": "x", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_name_1.py"}]}, {"name": "w", "node_type": "Name", "source_refs": [{"col_end": 15, "col_start": 14, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_name_1.py"}]}, {"name": "z", "node_type": "Name", "source_refs": [{"col_end": 17, "col_start": 16, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_name_1.py"}]}]}}], "func_args": [{"node_type": "Var", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 1, "row_start": 1, "source_file_name": "test_name_1.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 1, "row_start": 1, "source_file_name": "test_name_1.py"}]}}, {"node_type": "Var", "source_refs": [{"col_end": 11, "col_start": 10, "node_type": "SourceRef", "row_end": 1, "row_start": 1, "source_file_name": "test_name_1.py"}], "type": "integer", "val": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 11, "col_start": 10, "node_type": "SourceRef", "row_end": 1, "row_start": 1, "source_file_name": "test_name_1.py"}]}}, {"node_type": "Var", "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 1, "row_start": 1, "source_file_name": "test_name_1.py"}], "type": "integer", "val": {"name": "z", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 1, "row_start": 1, "source_file_name": "test_name_1.py"}]}}], "name": "foo", "node_type": "FunctionDef", "source_refs": [{"col_end": 18, "col_start": 0, "node_type": "SourceRef", "row_end": 4, "row_start": 1, "source_file_name": "test_name_1.py"}]}, {"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_name_1.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_name_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_name_1.py"}]}, "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_name_1.py"}]}, {"expr": {"arguments": [{"name": "x", "node_type": "Name", "source_refs": [{"col_end": 11, "col_start": 10, "node_type": "SourceRef", "row_end": 9, "row_start": 9, "source_file_name": "test_name_1.py"}]}], "func": {"name": "print", "node_type": "Name", "source_refs": [{"col_end": 12, "col_start": 4, "node_type": "SourceRef", "row_end": 9, "row_start": 9, "source_file_name": "test_name_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 12, "col_start": 4, "node_type": "SourceRef", "row_end": 9, "row_start": 9, "source_file_name": "test_name_1.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 12, "col_start": 4, "node_type": "SourceRef", "row_end": 9, "row_start": 9, "source_file_name": "test_name_1.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 12, "col_start": 0, "node_type": "SourceRef", "row_end": 9, "row_start": 7, "source_file_name": "test_name_1.py"}]}, {"expr": {"arguments": [], "func": {"name": "main", "node_type": "Name", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_name_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_name_1.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 11, "row_start": 11, "source_file_name": "test_name_1.py"}]}], "name": "test_name_1", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 11, "row_start": 1, "source_file_name": "test_name_1.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])
    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare


def test_add_1():
    prog_name = "test_add_1.py"
    folder = "function_def"

    raw_json = '{"nodes": [{"body": [{"expr": {"left": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 1, "col_start": 0, "node_type": "SourceRef", "row_end": 1, "row_start": 1, "source_file_name": "test_add_1.py"}]}, "node_type": "BinaryOp", "op": "Add", "right": {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 3, "col_start": 2, "node_type": "SourceRef", "row_end": 1, "row_start": 1, "source_file_name": "test_add_1.py"}]}, "source_refs": [{"col_end": 3, "col_start": 0, "node_type": "SourceRef", "row_end": 1, "row_start": 1, "source_file_name": "test_add_1.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 3, "col_start": 0, "node_type": "SourceRef", "row_end": 1, "row_start": 1, "source_file_name": "test_add_1.py"}]}], "name": "test_add_1", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 1, "row_start": 1, "source_file_name": "test_add_1.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])
    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare


def test_add_2():
    prog_name = "test_add_2.py"
    folder = "function_def"

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_add_2.py"}], "type": "integer", "val": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_add_2.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_add_2.py"}]}, "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_add_2.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_add_2.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_add_2.py"}]}}, "node_type": "Assignment", "right": {"left": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_add_2.py"}]}, "node_type": "BinaryOp", "op": "Sub", "right": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_add_2.py"}]}, "source_refs": [{"col_end": 13, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_add_2.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_add_2.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 13, "col_start": 0, "node_type": "SourceRef", "row_end": 3, "row_start": 1, "source_file_name": "test_add_2.py"}]}, {"expr": {"arguments": [], "func": {"name": "main", "node_type": "Name", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_add_2.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_add_2.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_add_2.py"}]}], "name": "test_add_2", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 5, "row_start": 1, "source_file_name": "test_add_2.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])
    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare


def test_assign_1():
    prog_name = "test_assign_1.py"
    folder = "function_def"

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_assign_1.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_assign_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_assign_1.py"}]}, "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_assign_1.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 9, "col_start": 0, "node_type": "SourceRef", "row_end": 3, "row_start": 2, "source_file_name": "test_assign_1.py"}]}], "name": "test_assign_1", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 3, "row_start": 1, "source_file_name": "test_assign_1.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])
    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare


def test_assign_2():
    prog_name = "test_assign_2.py"
    folder = "function_def"

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_assign_2.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_assign_2.py"}]}}, "node_type": "Assignment", "right": {"left": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_assign_2.py"}]}, "node_type": "BinaryOp", "op": "Add", "right": {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_assign_2.py"}]}, "source_refs": [{"col_end": 13, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_assign_2.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_assign_2.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 13, "col_start": 0, "node_type": "SourceRef", "row_end": 3, "row_start": 2, "source_file_name": "test_assign_2.py"}]}], "name": "test_assign_2", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 3, "row_start": 1, "source_file_name": "test_assign_2.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare


def test_assign_3():
    prog_name = "test_assign_3.py"
    folder = "function_def"

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Tuple", "source_refs": [{"col_end": 7, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_3.py"}], "values": [{"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_3.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_3.py"}]}}, {"node_type": "Var", "source_refs": [{"col_end": 7, "col_start": 6, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_3.py"}], "type": "integer", "val": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 7, "col_start": 6, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_3.py"}]}}]}, "node_type": "Assignment", "right": {"node_type": "Tuple", "source_refs": [{"col_end": 13, "col_start": 10, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_3.py"}], "values": [{"node_type": "Number", "number": 1, "source_refs": [{"col_end": 11, "col_start": 10, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_3.py"}]}, {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_3.py"}]}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_3.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 13, "col_start": 0, "node_type": "SourceRef", "row_end": 2, "row_start": 1, "source_file_name": "test_assign_3.py"}]}], "name": "test_assign_3", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 2, "row_start": 1, "source_file_name": "test_assign_3.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare



def test_assign_4():
    prog_name = "test_assign_4.py"
    folder = "function_def"

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_4.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_4.py"}]}}, "node_type": "Assignment", "right": {"node_type": "List", "source_refs": [{"col_end": 15, "col_start": 8, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_4.py"}], "values": [{"node_type": "Number", "number": 1, "source_refs": [{"col_end": 10, "col_start": 9, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_4.py"}]}, {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 12, "col_start": 11, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_4.py"}]}, {"node_type": "Number", "number": 3, "source_refs": [{"col_end": 14, "col_start": 13, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_4.py"}]}]}, "source_refs": [{"col_end": 15, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_4.py"}]}, {"left": {"node_type": "Subscript", "slice": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 7, "col_start": 6, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_assign_4.py"}]}, "source_refs": [{"col_end": 8, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_assign_4.py"}], "value": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_assign_4.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 3.0, "source_refs": [{"col_end": 14, "col_start": 11, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_assign_4.py"}]}, "source_refs": [{"col_end": 14, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_assign_4.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 14, "col_start": 0, "node_type": "SourceRef", "row_end": 3, "row_start": 1, "source_file_name": "test_assign_4.py"}]}], "name": "test_assign_4", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 3, "row_start": 1, "source_file_name": "test_assign_4.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare


def test_assign_5():
    prog_name = "test_assign_5.py"
    folder = "function_def"

    raw_json = '{"nodes": [{"body": [{"body": [{"node_type": "ModelReturn", "source_refs": [{"col_end": 20, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_5.py"}], "value": {"node_type": "Tuple", "source_refs": [{"col_end": 20, "col_start": 11, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_5.py"}], "values": [{"name": "x", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_5.py"}]}, {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 15, "col_start": 14, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_5.py"}]}, {"left": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 17, "col_start": 16, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_5.py"}]}, "node_type": "BinaryOp", "op": "Add", "right": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 19, "col_start": 18, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_5.py"}]}, "source_refs": [{"col_end": 19, "col_start": 16, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_5.py"}]}]}}], "func_args": [{"node_type": "Var", "source_refs": [{"col_end": 11, "col_start": 10, "node_type": "SourceRef", "row_end": 1, "row_start": 1, "source_file_name": "test_assign_5.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 11, "col_start": 10, "node_type": "SourceRef", "row_end": 1, "row_start": 1, "source_file_name": "test_assign_5.py"}]}}, {"node_type": "Var", "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 1, "row_start": 1, "source_file_name": "test_assign_5.py"}], "type": "integer", "val": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 1, "row_start": 1, "source_file_name": "test_assign_5.py"}]}}], "name": "adder", "node_type": "FunctionDef", "source_refs": [{"col_end": 20, "col_start": 0, "node_type": "SourceRef", "row_end": 2, "row_start": 1, "source_file_name": "test_assign_5.py"}]}, {"body": [{"left": {"node_type": "Tuple", "source_refs": [{"col_end": 11, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_assign_5.py"}], "values": [{"node_type": "Var", "source_refs": [{"col_end": 6, "col_start": 5, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_assign_5.py"}], "type": "integer", "val": {"name": "a", "node_type": "Name", "source_refs": [{"col_end": 6, "col_start": 5, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_assign_5.py"}]}}, {"node_type": "Var", "source_refs": [{"col_end": 8, "col_start": 7, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_assign_5.py"}], "type": "integer", "val": {"name": "b", "node_type": "Name", "source_refs": [{"col_end": 8, "col_start": 7, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_assign_5.py"}]}}, {"node_type": "Var", "source_refs": [{"col_end": 10, "col_start": 9, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_assign_5.py"}], "type": "integer", "val": {"name": "c", "node_type": "Name", "source_refs": [{"col_end": 10, "col_start": 9, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_assign_5.py"}]}}]}, "node_type": "Assignment", "right": {"arguments": [{"node_type": "Number", "number": 1, "source_refs": [{"col_end": 21, "col_start": 20, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_assign_5.py"}]}, {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 23, "col_start": 22, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_assign_5.py"}]}], "func": {"name": "adder", "node_type": "Name", "source_refs": [{"col_end": 24, "col_start": 14, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_assign_5.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 24, "col_start": 14, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_assign_5.py"}]}, "source_refs": [{"col_end": 24, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_assign_5.py"}]}, {"expr": {"arguments": [{"left": {"node_type": "String", "source_refs": [{"col_end": 14, "col_start": 10, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_assign_5.py"}], "string": "a "}, "node_type": "BinaryOp", "op": "Add", "right": {"arguments": [{"name": "a", "node_type": "Name", "source_refs": [{"col_end": 22, "col_start": 21, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_assign_5.py"}]}], "func": {"name": "str", "node_type": "Name", "source_refs": [{"col_end": 23, "col_start": 17, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_assign_5.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 23, "col_start": 17, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_assign_5.py"}]}, "source_refs": [{"col_end": 23, "col_start": 10, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_assign_5.py"}]}], "func": {"name": "print", "node_type": "Name", "source_refs": [{"col_end": 24, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_assign_5.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 24, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_assign_5.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 24, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_assign_5.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 24, "col_start": 0, "node_type": "SourceRef", "row_end": 6, "row_start": 4, "source_file_name": "test_assign_5.py"}]}], "name": "test_assign_5", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 6, "row_start": 1, "source_file_name": "test_assign_5.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare


def test_assign_6():
    prog_name = "test_assign_6.py"
    folder = "function_def"

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_6.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_6.py"}]}}, "node_type": "Assignment", "right": {"left": {"node_type": "Var", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_6.py"}], "type": "integer", "val": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_6.py"}]}}, "node_type": "Assignment", "right": {"left": {"node_type": "Var", "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_6.py"}], "type": "integer", "val": {"name": "z", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_6.py"}]}}, "node_type": "Assignment", "right": {"left": {"node_type": "Var", "source_refs": [{"col_end": 17, "col_start": 16, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_6.py"}], "type": "integer", "val": {"name": "w", "node_type": "Name", "source_refs": [{"col_end": 17, "col_start": 16, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_6.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 100, "source_refs": [{"col_end": 23, "col_start": 20, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_6.py"}]}, "source_refs": [{"col_end": 23, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_6.py"}]}, "source_refs": [{"col_end": 23, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_6.py"}]}, "source_refs": [{"col_end": 23, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_6.py"}]}, "source_refs": [{"col_end": 23, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_assign_6.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 23, "col_start": 0, "node_type": "SourceRef", "row_end": 2, "row_start": 1, "source_file_name": "test_assign_6.py"}]}], "name": "test_assign_6", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 2, "row_start": 1, "source_file_name": "test_assign_6.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"
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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare


def test_function_1():
    prog_name = "test_function_1.py"
    folder = "function_def"

    raw_json = '{"nodes": [{"body": [{"body": [], "func_args": [], "name": "foo", "node_type": "FunctionDef", "source_refs": [{"col_end": 8, "col_start": 0, "node_type": "SourceRef", "row_end": 3, "row_start": 2, "source_file_name": "test_function_1.py"}]}, {"body": [], "func_args": [], "name": "bar", "node_type": "FunctionDef", "source_refs": [{"col_end": 8, "col_start": 0, "node_type": "SourceRef", "row_end": 6, "row_start": 5, "source_file_name": "test_function_1.py"}]}, {"body": [{"expr": {"arguments": [], "func": {"name": "foo", "node_type": "Name", "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 9, "row_start": 9, "source_file_name": "test_function_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 9, "row_start": 9, "source_file_name": "test_function_1.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 9, "row_start": 9, "source_file_name": "test_function_1.py"}]}, {"expr": {"arguments": [], "func": {"name": "bar", "node_type": "Name", "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 10, "row_start": 10, "source_file_name": "test_function_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 10, "row_start": 10, "source_file_name": "test_function_1.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 10, "row_start": 10, "source_file_name": "test_function_1.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 9, "col_start": 0, "node_type": "SourceRef", "row_end": 10, "row_start": 8, "source_file_name": "test_function_1.py"}]}], "name": "test_function_1", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 10, "row_start": 1, "source_file_name": "test_function_1.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare


def test_lambda_1():
    prog_name = "test_lambda_1.py"
    folder = "function_def"

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_lambda_1.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_lambda_1.py"}]}}, "node_type": "Assignment", "right": {"body": [{"left": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 20, "col_start": 19, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_lambda_1.py"}]}, "node_type": "BinaryOp", "op": "Mult", "right": {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 24, "col_start": 23, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_lambda_1.py"}]}, "source_refs": [{"col_end": 24, "col_start": 19, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_lambda_1.py"}]}], "func_args": [{"node_type": "Var", "source_refs": [{"col_end": 16, "col_start": 15, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_lambda_1.py"}], "type": "integer", "val": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 16, "col_start": 15, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_lambda_1.py"}]}}], "name": "LAMBDA", "node_type": "FunctionDef", "source_refs": [{"col_end": 24, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_lambda_1.py"}]}, "source_refs": [{"col_end": 24, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_lambda_1.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 24, "col_start": 0, "node_type": "SourceRef", "row_end": 3, "row_start": 2, "source_file_name": "test_lambda_1.py"}]}], "name": "test_lambda_1", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 4, "row_start": 1, "source_file_name": "test_lambda_1.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

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

    out_cast = cast.CAST([test_C])
    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare


def test_if_1():
    prog_name = "test_if_1.py"
    folder = "if"

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_1.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 10, "source_refs": [{"col_end": 10, "col_start": 8, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_1.py"}]}, "source_refs": [{"col_end": 10, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_1.py"}]}, {"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_if_1.py"}], "type": "integer", "val": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_if_1.py"}]}}, "node_type": "Assignment", "right": {"left": {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_if_1.py"}]}, "node_type": "BinaryOp", "op": "Add", "right": {"node_type": "Number", "number": 4, "source_refs": [{"col_end": 17, "col_start": 16, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_if_1.py"}]}, "source_refs": [{"col_end": 17, "col_start": 12, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_if_1.py"}]}, "source_refs": [{"col_end": 17, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_if_1.py"}]}], "expr": {"left": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 8, "col_start": 7, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_1.py"}]}, "node_type": "BinaryOp", "op": "Eq", "right": {"node_type": "Number", "number": 10, "source_refs": [{"col_end": 14, "col_start": 12, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_1.py"}]}, "source_refs": [{"col_end": 14, "col_start": 7, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_1.py"}]}, "node_type": "ModelIf", "orelse": [], "source_refs": [{"col_end": 17, "col_start": 4, "node_type": "SourceRef", "row_end": 4, "row_start": 3, "source_file_name": "test_if_1.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_if_1.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_if_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 5, "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_if_1.py"}]}, "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_if_1.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 9, "col_start": 0, "node_type": "SourceRef", "row_end": 5, "row_start": 1, "source_file_name": "test_if_1.py"}]}], "name": "test_if_1", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 5, "row_start": 1, "source_file_name": "test_if_1.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare


def test_if_2():
    prog_name = "test_if_2.py"
    folder = "if"

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_2.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_2.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 10, "source_refs": [{"col_end": 10, "col_start": 8, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_2.py"}]}, "source_refs": [{"col_end": 10, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_2.py"}]}, {"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_if_2.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_if_2.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_if_2.py"}]}, "source_refs": [{"col_end": 13, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_if_2.py"}]}], "expr": {"left": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 8, "col_start": 7, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_2.py"}]}, "node_type": "BinaryOp", "op": "Eq", "right": {"node_type": "Number", "number": 5, "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_2.py"}]}, "source_refs": [{"col_end": 13, "col_start": 7, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_2.py"}]}, "node_type": "ModelIf", "orelse": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_if_2.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_if_2.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_if_2.py"}]}, "source_refs": [{"col_end": 13, "col_start": 8, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_if_2.py"}]}], "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 3, "source_file_name": "test_if_2.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_if_2.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_if_2.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 3, "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_if_2.py"}]}, "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_if_2.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 9, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 1, "source_file_name": "test_if_2.py"}]}], "name": "test_if_2", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 7, "row_start": 1, "source_file_name": "test_if_2.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare


def test_if_3():
    prog_name = "test_if_3.py"
    folder = "if"

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_3.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_3.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 10, "source_refs": [{"col_end": 10, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_3.py"}]}, "source_refs": [{"col_end": 10, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_3.py"}]}, {"body": [], "expr": {"left": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 8, "col_start": 7, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_if_3.py"}]}, "node_type": "BinaryOp", "op": "Eq", "right": {"node_type": "Number", "number": 5, "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_if_3.py"}]}, "source_refs": [{"col_end": 13, "col_start": 7, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_if_3.py"}]}, "node_type": "ModelIf", "orelse": [{"body": [], "expr": {"left": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 10, "col_start": 9, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_if_3.py"}]}, "node_type": "BinaryOp", "op": "Eq", "right": {"node_type": "Number", "number": 6, "source_refs": [{"col_end": 15, "col_start": 14, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_if_3.py"}]}, "source_refs": [{"col_end": 15, "col_start": 9, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_if_3.py"}]}, "node_type": "ModelIf", "orelse": [], "source_refs": [{"col_end": 12, "col_start": 4, "node_type": "SourceRef", "row_end": 9, "row_start": 6, "source_file_name": "test_if_3.py"}]}], "source_refs": [{"col_end": 12, "col_start": 4, "node_type": "SourceRef", "row_end": 9, "row_start": 4, "source_file_name": "test_if_3.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 10, "row_start": 10, "source_file_name": "test_if_3.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 10, "row_start": 10, "source_file_name": "test_if_3.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 20, "source_refs": [{"col_end": 10, "col_start": 8, "node_type": "SourceRef", "row_end": 10, "row_start": 10, "source_file_name": "test_if_3.py"}]}, "source_refs": [{"col_end": 10, "col_start": 4, "node_type": "SourceRef", "row_end": 10, "row_start": 10, "source_file_name": "test_if_3.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 10, "col_start": 0, "node_type": "SourceRef", "row_end": 10, "row_start": 2, "source_file_name": "test_if_3.py"}]}], "name": "test_if_3", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 10, "row_start": 1, "source_file_name": "test_if_3.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare

def test_if_4():
    prog_name = "test_if_4.py"
    folder = "if"

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_4.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_4.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_4.py"}]}, "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_4.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_4.py"}], "type": "integer", "val": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_4.py"}]}}, "node_type": "Assignment", "right": {"body": [{"node_type": "Number", "number": 3, "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_4.py"}]}], "expr": {"left": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 14, "col_start": 13, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_4.py"}]}, "node_type": "BinaryOp", "op": "Eq", "right": {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 19, "col_start": 18, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_4.py"}]}, "source_refs": [{"col_end": 19, "col_start": 13, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_4.py"}]}, "node_type": "ModelIf", "orelse": [{"node_type": "Number", "number": 4, "source_refs": [{"col_end": 26, "col_start": 25, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_4.py"}]}], "source_refs": [{"col_end": 26, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_4.py"}]}, "source_refs": [{"col_end": 26, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_4.py"}]}, {"expr": {"arguments": [{"name": "y", "node_type": "Name", "source_refs": [{"col_end": 11, "col_start": 10, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_if_4.py"}]}], "func": {"name": "print", "node_type": "Name", "source_refs": [{"col_end": 12, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_if_4.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 12, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_if_4.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 12, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_if_4.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 12, "col_start": 0, "node_type": "SourceRef", "row_end": 5, "row_start": 1, "source_file_name": "test_if_4.py"}]}, {"expr": {"arguments": [], "func": {"name": "main", "node_type": "Name", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_if_4.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_if_4.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_if_4.py"}]}], "name": "test_if_4", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 7, "row_start": 1, "source_file_name": "test_if_4.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare

def test_if_5():
    prog_name = "test_if_5.py"
    folder = "if"

    raw_json = '{"nodes": [{"body": [{"body": [{"body": [{"expr": {"arguments": [{"node_type": "String", "source_refs": [{"col_end": 19, "col_start": 14, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_5.py"}], "string": "Hey"}], "func": {"name": "print", "node_type": "Name", "source_refs": [{"col_end": 20, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_5.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 20, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_5.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 20, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_if_5.py"}]}], "expr": {"left": {"boolean": true, "node_type": "Boolean", "source_refs": [{"col_end": 11, "col_start": 7, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_5.py"}]}, "node_type": "BinaryOp", "op": "And", "right": {"left": {"boolean": true, "node_type": "Boolean", "source_refs": [{"col_end": 20, "col_start": 16, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_5.py"}]}, "node_type": "BinaryOp", "op": "And", "right": {"left": {"boolean": false, "node_type": "Boolean", "source_refs": [{"col_end": 30, "col_start": 25, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_5.py"}]}, "node_type": "BinaryOp", "op": "And", "right": {"boolean": true, "node_type": "Boolean", "source_refs": [{"col_end": 39, "col_start": 35, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_5.py"}]}, "source_refs": [{"col_end": 39, "col_start": 7, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_5.py"}]}, "source_refs": [{"col_end": 39, "col_start": 7, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_5.py"}]}, "source_refs": [{"col_end": 39, "col_start": 7, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_if_5.py"}]}, "node_type": "ModelIf", "orelse": [], "source_refs": [{"col_end": 20, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 2, "source_file_name": "test_if_5.py"}]}, {"body": [{"expr": {"arguments": [{"node_type": "String", "source_refs": [{"col_end": 18, "col_start": 14, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_if_5.py"}], "string": "Hi"}], "func": {"name": "print", "node_type": "Name", "source_refs": [{"col_end": 19, "col_start": 8, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_if_5.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 19, "col_start": 8, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_if_5.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 19, "col_start": 8, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_if_5.py"}]}], "expr": {"left": {"boolean": false, "node_type": "Boolean", "source_refs": [{"col_end": 12, "col_start": 7, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_if_5.py"}]}, "node_type": "BinaryOp", "op": "Or", "right": {"left": {"boolean": false, "node_type": "Boolean", "source_refs": [{"col_end": 21, "col_start": 16, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_if_5.py"}]}, "node_type": "BinaryOp", "op": "Or", "right": {"left": {"boolean": false, "node_type": "Boolean", "source_refs": [{"col_end": 30, "col_start": 25, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_if_5.py"}]}, "node_type": "BinaryOp", "op": "Or", "right": {"boolean": true, "node_type": "Boolean", "source_refs": [{"col_end": 38, "col_start": 34, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_if_5.py"}]}, "source_refs": [{"col_end": 38, "col_start": 7, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_if_5.py"}]}, "source_refs": [{"col_end": 38, "col_start": 7, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_if_5.py"}]}, "source_refs": [{"col_end": 38, "col_start": 7, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_if_5.py"}]}, "node_type": "ModelIf", "orelse": [], "source_refs": [{"col_end": 19, "col_start": 4, "node_type": "SourceRef", "row_end": 6, "row_start": 5, "source_file_name": "test_if_5.py"}]}, {"body": [{"expr": {"arguments": [{"node_type": "String", "source_refs": [{"col_end": 21, "col_start": 14, "node_type": "SourceRef", "row_end": 9, "row_start": 9, "source_file_name": "test_if_5.py"}], "string": "Hello"}], "func": {"name": "print", "node_type": "Name", "source_refs": [{"col_end": 22, "col_start": 8, "node_type": "SourceRef", "row_end": 9, "row_start": 9, "source_file_name": "test_if_5.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 22, "col_start": 8, "node_type": "SourceRef", "row_end": 9, "row_start": 9, "source_file_name": "test_if_5.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 22, "col_start": 8, "node_type": "SourceRef", "row_end": 9, "row_start": 9, "source_file_name": "test_if_5.py"}]}], "expr": {"left": {"left": {"boolean": true, "node_type": "Boolean", "source_refs": [{"col_end": 11, "col_start": 7, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_if_5.py"}]}, "node_type": "BinaryOp", "op": "And", "right": {"boolean": false, "node_type": "Boolean", "source_refs": [{"col_end": 21, "col_start": 16, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_if_5.py"}]}, "source_refs": [{"col_end": 21, "col_start": 7, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_if_5.py"}]}, "node_type": "BinaryOp", "op": "Or", "right": {"boolean": true, "node_type": "Boolean", "source_refs": [{"col_end": 29, "col_start": 25, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_if_5.py"}]}, "source_refs": [{"col_end": 29, "col_start": 7, "node_type": "SourceRef", "row_end": 8, "row_start": 8, "source_file_name": "test_if_5.py"}]}, "node_type": "ModelIf", "orelse": [], "source_refs": [{"col_end": 22, "col_start": 4, "node_type": "SourceRef", "row_end": 9, "row_start": 8, "source_file_name": "test_if_5.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 22, "col_start": 0, "node_type": "SourceRef", "row_end": 9, "row_start": 1, "source_file_name": "test_if_5.py"}]}], "name": "test_if_5", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 9, "row_start": 1, "source_file_name": "test_if_5.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare

def test_import_1():
    prog_name = "test_import_1.py"
    folder = "import"

    raw_json = '{"nodes": [{"body": [{"body": [], "name": "sys", "node_type": "Module", "source_refs": [{"col_end": 10, "col_start": 0, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_import_1.py"}]}, {"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_1.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_1.py"}]}}, "node_type": "Assignment", "right": {"arguments": [{"attr": {"name": "argv", "node_type": "Name", "source_refs": [{"col_end": 20, "col_start": 12, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_1.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 20, "col_start": 12, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_1.py"}], "value": {"name": "sys", "node_type": "Name", "source_refs": [{"col_end": 15, "col_start": 12, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_1.py"}]}}], "func": {"name": "len", "node_type": "Name", "source_refs": [{"col_end": 21, "col_start": 8, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 21, "col_start": 8, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_1.py"}]}, "source_refs": [{"col_end": 21, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_1.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 21, "col_start": 0, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_import_1.py"}]}, {"expr": {"arguments": [], "func": {"name": "main", "node_type": "Name", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_import_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_import_1.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_import_1.py"}]}], "name": "test_import_1", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 7, "row_start": 1, "source_file_name": "test_import_1.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare

def test_import_2():
    prog_name = "test_import_2.py"
    folder = "import"

    raw_json = '{"nodes": [{"body": [{"body": [], "name": "s", "node_type": "Module", "source_refs": [{"col_end": 15, "col_start": 0, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_import_2.py"}]}, {"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_2.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_2.py"}]}}, "node_type": "Assignment", "right": {"arguments": [{"attr": {"name": "argv", "node_type": "Name", "source_refs": [{"col_end": 18, "col_start": 12, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_2.py"}]}, "node_type": "Attribute", "source_refs": [{"col_end": 18, "col_start": 12, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_2.py"}], "value": {"name": "sys", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_2.py"}]}}], "func": {"name": "len", "node_type": "Name", "source_refs": [{"col_end": 19, "col_start": 8, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_2.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 19, "col_start": 8, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_2.py"}]}, "source_refs": [{"col_end": 19, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_2.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 19, "col_start": 0, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_import_2.py"}]}, {"expr": {"arguments": [], "func": {"name": "main", "node_type": "Name", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_import_2.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_import_2.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_import_2.py"}]}], "name": "test_import_2", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 7, "row_start": 1, "source_file_name": "test_import_2.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare

def test_import_3():
    prog_name = "test_import_3.py"
    folder = "import"

    raw_json = '{"nodes": [{"body": [{"body": [], "name": "sys", "node_type": "Module", "source_refs": [{"col_end": 20, "col_start": 0, "node_type": "SourceRef", "row_end": 2, "row_start": 2, "source_file_name": "test_import_3.py"}]}, {"body": [{"expr": {"arguments": [{"node_type": "Number", "number": 0, "source_refs": [{"col_end": 10, "col_start": 9, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_3.py"}]}], "func": {"name": "exit", "node_type": "Name", "source_refs": [{"col_end": 11, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_3.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 11, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_3.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 11, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_import_3.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 11, "col_start": 0, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_import_3.py"}]}, {"expr": {"arguments": [], "func": {"name": "main", "node_type": "Name", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_import_3.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_import_3.py"}]}, "node_type": "Expr", "source_refs": [{"col_end": 6, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_import_3.py"}]}], "name": "test_import_3", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 7, "row_start": 1, "source_file_name": "test_import_3.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare

def test_for_1():
    prog_name = "test_for_1.py"
    folder = "loop"

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_for_1.py"}], "type": "integer", "val": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_for_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "List", "source_refs": [{"col_end": 19, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_for_1.py"}], "values": [{"node_type": "Number", "number": 1, "source_refs": [{"col_end": 10, "col_start": 9, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_for_1.py"}]}, {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 12, "col_start": 11, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_for_1.py"}]}, {"node_type": "Number", "number": 3, "source_refs": [{"col_end": 14, "col_start": 13, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_for_1.py"}]}, {"node_type": "Number", "number": 4, "source_refs": [{"col_end": 16, "col_start": 15, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_for_1.py"}]}, {"node_type": "Number", "number": 5, "source_refs": [{"col_end": 18, "col_start": 17, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_for_1.py"}]}]}, "source_refs": [{"col_end": 19, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_for_1.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}], "type": "integer", "val": {"name": "generated_index%", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 0, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}, {"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}], "type": "integer", "val": {"name": "i", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Subscript", "slice": {"name": "generated_index%", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}], "value": {"name": "y", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_for_1.py"}], "type": "integer", "val": {"name": "x", "node_type": "Name", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_for_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_for_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 8, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_for_1.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}], "type": "integer", "val": {"name": "generated_index%", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}}, "node_type": "Assignment", "right": {"left": {"name": "generated_index%", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}, "node_type": "BinaryOp", "op": "Add", "right": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}], "expr": {"left": {"name": "generated_index%", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}, "node_type": "BinaryOp", "op": "Lt", "right": {"arguments": [{"name": "y", "node_type": "Name", "source_refs": [{"col_end": 14, "col_start": 13, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_for_1.py"}]}], "func": {"name": "len", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}, "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}, "node_type": "Loop", "source_refs": [{"col_end": 13, "col_start": 4, "node_type": "SourceRef", "row_end": 5, "row_start": 4, "source_file_name": "test_for_1.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 13, "col_start": 0, "node_type": "SourceRef", "row_end": 5, "row_start": 2, "source_file_name": "test_for_1.py"}]}], "name": "test_for_1", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 5, "row_start": 1, "source_file_name": "test_for_1.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

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

    out_cast = cast.CAST([test_C])

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare

def test_while_1():
    prog_name = "test_while_1.py"
    folder = "loop"
    n1 = Number(1)
    n2 = Number(2)
    n3 = Number(3)
    v1 = Var(val=Name(name="b"), type="integer")
    v2 = Var(val=Name(name="i"), type="integer")
    v3 = Var(val=Name(name="a"), type="integer")
    a1 = Assignment(left=v1, right=List(values=[n1, n2, n3]))
    a2 = Assignment(left=v2, right=Number(0))

    loop_cond = BinaryOp(
        BinaryOperator.LT, Name("i"), Call(Name("len"), [Name("b")])
    )
    loop_assign = Assignment(v3, Subscript(Name("b"), Name("i")))
    loop_increment = Assignment(
        v2, BinaryOp(BinaryOperator.ADD, Name("i"), Number(1))
    )

    loop = Loop(expr=loop_cond, body=[loop_assign, loop_increment])

    f = FunctionDef(name="main", func_args=[], body=[a1, a2, loop])

    m = Module(name=prog_name, body=[f])
    C = cast.CAST([m])

    raw_json = '{"nodes": [{"body": [{"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_while_1.py"}], "type": "integer", "val": {"name": "b", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_while_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "List", "source_refs": [{"col_end": 15, "col_start": 8, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_while_1.py"}], "values": [{"node_type": "Number", "number": 1, "source_refs": [{"col_end": 10, "col_start": 9, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_while_1.py"}]}, {"node_type": "Number", "number": 2, "source_refs": [{"col_end": 12, "col_start": 11, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_while_1.py"}]}, {"node_type": "Number", "number": 3, "source_refs": [{"col_end": 14, "col_start": 13, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_while_1.py"}]}]}, "source_refs": [{"col_end": 15, "col_start": 4, "node_type": "SourceRef", "row_end": 3, "row_start": 3, "source_file_name": "test_while_1.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_while_1.py"}], "type": "integer", "val": {"name": "i", "node_type": "Name", "source_refs": [{"col_end": 5, "col_start": 4, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_while_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Number", "number": 0, "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_while_1.py"}]}, "source_refs": [{"col_end": 9, "col_start": 4, "node_type": "SourceRef", "row_end": 4, "row_start": 4, "source_file_name": "test_while_1.py"}]}, {"body": [{"left": {"node_type": "Var", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_while_1.py"}], "type": "integer", "val": {"name": "a", "node_type": "Name", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_while_1.py"}]}}, "node_type": "Assignment", "right": {"node_type": "Subscript", "slice": {"name": "i", "node_type": "Name", "source_refs": [{"col_end": 15, "col_start": 14, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_while_1.py"}]}, "source_refs": [{"col_end": 16, "col_start": 12, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_while_1.py"}], "value": {"name": "b", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_while_1.py"}]}}, "source_refs": [{"col_end": 16, "col_start": 8, "node_type": "SourceRef", "row_end": 6, "row_start": 6, "source_file_name": "test_while_1.py"}]}, {"left": {"node_type": "Var", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_while_1.py"}], "type": "integer", "val": {"name": "i", "node_type": "Name", "source_refs": [{"col_end": 9, "col_start": 8, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_while_1.py"}]}}, "node_type": "Assignment", "right": {"left": {"name": "i", "node_type": "Name", "source_refs": [{"col_end": 13, "col_start": 12, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_while_1.py"}]}, "node_type": "BinaryOp", "op": "Add", "right": {"node_type": "Number", "number": 1, "source_refs": [{"col_end": 17, "col_start": 16, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_while_1.py"}]}, "source_refs": [{"col_end": 17, "col_start": 12, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_while_1.py"}]}, "source_refs": [{"col_end": 17, "col_start": 8, "node_type": "SourceRef", "row_end": 7, "row_start": 7, "source_file_name": "test_while_1.py"}]}], "expr": {"left": {"name": "i", "node_type": "Name", "source_refs": [{"col_end": 11, "col_start": 10, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_while_1.py"}]}, "node_type": "BinaryOp", "op": "Lt", "right": {"arguments": [{"name": "b", "node_type": "Name", "source_refs": [{"col_end": 19, "col_start": 18, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_while_1.py"}]}], "func": {"name": "len", "node_type": "Name", "source_refs": [{"col_end": 20, "col_start": 14, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_while_1.py"}]}, "node_type": "Call", "source_refs": [{"col_end": 20, "col_start": 14, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_while_1.py"}]}, "source_refs": [{"col_end": 20, "col_start": 10, "node_type": "SourceRef", "row_end": 5, "row_start": 5, "source_file_name": "test_while_1.py"}]}, "node_type": "Loop", "source_refs": [{"col_end": 17, "col_start": 4, "node_type": "SourceRef", "row_end": 7, "row_start": 5, "source_file_name": "test_while_1.py"}]}], "func_args": [], "name": "main", "node_type": "FunctionDef", "source_refs": [{"col_end": 17, "col_start": 0, "node_type": "SourceRef", "row_end": 7, "row_start": 2, "source_file_name": "test_while_1.py"}]}], "name": "test_while_1", "node_type": "Module", "source_refs": [{"col_end": null, "col_start": null, "node_type": "SourceRef", "row_end": 9, "row_start": 1, "source_file_name": "test_while_1.py"}]}]}'

    filepath = f"{DATA_DIR}/{folder}/{prog_name}"

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

    out_cast = cast.CAST([test_C])

    # test_C.name = prog_name

    to_compare = json.dumps(out_cast.to_json_object(),sort_keys=True,indent=None) 

    assert raw_json == to_compare

    #assert C == cast.CAST([test_C])
