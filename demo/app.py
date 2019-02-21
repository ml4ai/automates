import os
import sys
import ast
import json
from uuid import uuid4
import subprocess as sp
import importlib
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
    submit = SubmitField("Submit", render_kw={"class":"btn btn-primary"})


SECRET_KEY = "secret!"
# mandatory
CODEMIRROR_LANGUAGES = ["fortran"]
# optional
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
                    "shape": "roundrectangle",
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


def get_cyjs_elementsJSON_from_ScopeTree(A, lambdas) -> str:
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


@app.route("/")
def index():
    form = MyForm()
    if form.validate_on_submit():
        text = form.source_code.data
    return render_template("index.html", form=form, code='')


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
    filename=f"input_code_{str(uuid4())}"
    input_code_tmpfile = f"/tmp/automates/{filename}.f"
    with open(input_code_tmpfile, "w") as f:
        f.write("".join(lines))
    root = Scope.from_fortran_file(input_code_tmpfile, tmpdir="/tmp/automates")
    scopetree_graph = root.to_agraph()

    sys.path.insert(0, "/tmp/automates")
    lambdas = f"{filename}_lambdas"
    scopeTree_elementsJSON = get_cyjs_elementsJSON_from_ScopeTree(
        scopetree_graph, importlib.__import__(lambdas)
    )
    programAnalysisGraph = ProgramAnalysisGraph.from_agraph(
        scopetree_graph,
        importlib.__import__(lambdas)
    )
    program_analysis_graph_elementsJSON = programAnalysisGraph.cyjs_elementsJSON()
    os.remove(input_code_tmpfile)
    os.remove(f"/tmp/automates/{lambdas}.py")

    return render_template(
        "index.html",
        form=form,
        code=code,
        scopeTree_elementsJSON=scopeTree_elementsJSON,
        program_analysis_graph_elementsJSON=program_analysis_graph_elementsJSON,
    )


if __name__ == "__main__":
    app.run()
