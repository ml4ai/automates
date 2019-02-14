import os
import sys
import ast
import json
import subprocess as sp
from pprint import pprint
from delphi.translators.for2py.scripts import (
    f2py_pp,
    translate,
    get_comments,
    pyTranslate,
    genPGM,
)
from delphi.utils.fp import flatten
from delphi.GrFN.scopes import Scope
from delphi.GrFN.ProgramAnalysisGraph import ProgramAnalysisGraph
import delphi.paths
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from flask_codemirror.fields import CodeMirrorField
from wtforms.fields import SubmitField
from flask_codemirror import CodeMirror
import inspect
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from sympy import sympify, latex, symbols


class MyForm(FlaskForm):
    source_code = CodeMirrorField(
        language="fortran",
        config={"lineNumbers": "true", "viewportMargin": 800},
    )
    submit = SubmitField("Submit")


SECRET_KEY = "secret!"
# mandatory
CODEMIRROR_LANGUAGES = ["fortran"]
# optional
CODEMIRROR_THEME = "monokai"
CODEMIRROR_ADDONS = (("display", "placeholder"),)

app = Flask(__name__)
app.config.from_object(__name__)
codemirror = CodeMirror(app)


def get_cluster_nodes(A):
    cluster_nodes = []
    for subgraph in A.subgraphs():
        cluster_nodes.append(
            {
                "data": {
                    "id": subgraph.name,
                    "label": subgraph.name.replace("cluster_", ""),
                    "shape": "rectangle",
                    "parent": A.name,
                    "color": subgraph.graph_attr["border_color"],
                    "textValign": "top",
                    "tooltip": None,
                }
            }
        )
        cluster_nodes.append(get_cluster_nodes(subgraph))

    return cluster_nodes


def get_tooltip(n, lambdas):
    if n.attr["node_type"] == "ActionNode":
        x = getattr(lambdas, n.attr["lambda_fn"], None)
        if x is None:
            return "None"
        else:
            src = inspect.getsource(x)
            src_lines = src.split("\n")
            symbs = src_lines[0].split("(")[1].split(")")[0].split(", ")
            ltx = (
                src_lines[0]
                .split("__lambda__")[1]
                .split("(")[0]
                .replace("_", "\_")
                + " = "
                + latex(
                    sympify(src_lines[1][10:].replace("math.exp", "e^"))
                ).replace("_", "\_")
            )
            return f"\({ltx}\)"
    else:
        return json.dumps({"index": n.attr["index"]}, indent=2)


def to_cyjs_elements_json_str(A) -> dict:
    sys.path.insert(0, "/tmp/")
    import lambdas

    lexer = PythonLexer()
    formatter = HtmlFormatter()
    elements = {
        "nodes": [
            {
                "data": {
                    "id": n,
                    "label": n.attr["label"],
                    "parent": n.attr["parent"],
                    "shape": n.attr["shape"],
                    "color": n.attr["color"],
                    "textValign": "center",
                    "tooltip": get_tooltip(n, lambdas)
                    # "tooltip": highlight(get_tooltip(n, lambdas), lexer, formatter),
                }
            }
            for n in A.nodes()
        ]
        + flatten(get_cluster_nodes(A)),
        "edges": [
            {
                "data": {
                    "id": f"{edge[0]}_{edge[1]}",
                    "source": edge[0],
                    "target": edge[1],
                }
            }
            for edge in A.edges()
        ],
    }
    json_str = json.dumps(elements, indent=2)
    return json_str

def to_cyjs_elements_json_str_2(A) -> dict:

    elements = {
        "nodes": [
            {
                "data": {
                    "id": n[0],
                    "label": n[0],
                    "parent": "petpt",
                    "shape": "ellipse",
                    "color": 'black',
                    "textValign": "center",
                    "tooltip":'None',
                }
            }
            for n in A.nodes(data=True)
        ],
        "edges": [
            {
                "data": {
                    "id": f"{edge[0]}_{edge[1]}",
                    "source": edge[0],
                    "target": edge[1],
                }
            }
            for edge in A.edges()
        ],
    }
    json_str = json.dumps(elements, indent=2)
    return json_str


@app.route("/")
def index():
    form = MyForm()
    if form.validate_on_submit():
        text = form.source_code.data
    return render_template("index.html", form=form)


@app.route("/processCode", methods=["POST"])
def processCode():
    form = MyForm()
    code = form.source_code.data
    if code == "":
        return render_template("index.html", form=form)
    lines = [
        line.replace("\r", "") + "\n"
        for line in [line for line in code.split("\n")]
        if line != ""
    ]
    input_code_tmpfile = "/tmp/input_code.f"
    with open(input_code_tmpfile, 'w') as f:
        f.write("".join(lines))
    root=Scope.from_fortran_file(input_code_tmpfile)
    A = root.to_agraph()
    elements = to_cyjs_elements_json_str(A)
    A = ProgramAnalysisGraph.from_fortran_file(input_code_tmpfile)
    os.remove(input_code_tmpfile)
    elements2 = to_cyjs_elements_json_str_2(A)

    return render_template("index.html", form=form, elementsJSON=elements,
            elementsJSON2 = elements2)


if __name__ == "__main__":
    app.run()
