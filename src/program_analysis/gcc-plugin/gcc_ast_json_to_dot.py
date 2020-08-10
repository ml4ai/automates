import json
import sys
import os

AST_FUNCTIONS_KEY = "functions"
BASIC_BLOCKS_KEY = "basicBlocks"

def open_dot_file(filename):
    base = os.path.splitext(filename)[0]
    return open(base + ".dot", "w")

def write_basic_block(f, bb):
    f.write(str(bb["index"]) + "[ ]")

    for edge in bb["edges"]:
        f.write(str(edge["source"]) + " -> " + str(edge["target"]))

def write_ast_function(f, function):
    f.write("digraph \"" + function["name"] + "_" + str(function["id"]) + "\" {\n")
    f.write("A -> B\n")
    # print parameters

    # variable declarations

    # basic blocks
    for bb in function[BASIC_BLOCKS_KEY]:
        write_basic_block(f, bb)

    f.write("}\n")

def write_ast_functions(f, ast_json):
    for func in ast_json[AST_FUNCTIONS_KEY]:
        write_ast_function(f, func)


def write_ast_dot(f, ast_json):
    write_ast_functions(f, ast_json)

if len(sys.argv) < 2:
    print("Pass in gcc plugin AST file as argument.")
    sys.exit(1)
filename = sys.argv[1]

f = open(filename)
ast_json = json.load(f)
f.close()

f = open_dot_file(filename)
write_ast_dot(f, ast_json)
f.close()