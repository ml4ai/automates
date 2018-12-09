import os
import ast
import subprocess as sp
import json
from pprint import pprint
from delphi.program_analysis.autoTranslate.scripts import (
    f2py_pp,
    translate,
    get_comments,
    pyTranslate,
    genPGM,
)
from delphi.utils.fp import flatten
from delphi.program_analysis.scopes import Scope
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from flask_codemirror.fields import CodeMirrorField
from wtforms.fields import SubmitField
from flask_codemirror import CodeMirror


class MyForm(FlaskForm):
    source_code = CodeMirrorField(
        language="fortran", config={"lineNumbers": "true", "viewportMargin": 800}
    )
    submit = SubmitField("Submit")


SECRET_KEY = "secret!"
# mandatory
CODEMIRROR_LANGUAGES = ["fortran"]
# optional
CODEMIRROR_THEME = "3024-day"
CODEMIRROR_ADDONS = (("display", "placeholder"),)

app = Flask(__name__)
app.config.from_object(__name__)
codemirror = CodeMirror(app)

os.environ["CLASSPATH"] = (
    os.getcwd() + "/../../delphi/delphi/program_analysis/autoTranslate/bin/*"
)


def get_cluster_nodes(A):
    cluster_nodes=[]
    for subgraph in A.subgraphs():
        cluster_nodes.append(
            {
                "data": {
                    "id": subgraph.name,
                    "label": subgraph.name.replace("cluster_",""),
                    "shape": "rectangle",
                    "parent": A.name,
                    "color": subgraph.graph_attr['border_color'],
                    'textValign': 'top',
                }
            }
        )
        cluster_nodes.append(get_cluster_nodes(subgraph))

    return cluster_nodes


def to_cyjs_elements_json_str(A) -> dict:
    elements = {
        "nodes": [
            {
                "data": {
                    "id": n,
                    "label": n.attr["label"],
                    "parent": n.attr["parent"],
                    "shape": n.attr["shape"],
                    "color": n.attr["color"],
                    'textValign': 'center',
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
    preprocessed_fortran_file = "preprocessed_code.f"
    return render_template("index.html", form=form)


@app.route("/processCode", methods=["POST"])
def processCode():
    form = MyForm()
    code = form.source_code.data
    lines = [
        line + "\n"
        for line in [line for line in code.split("\n")]
        if line != ""
    ]
    preprocessed_fortran_file = "preprocessed_code.f"

    with open(preprocessed_fortran_file, "w") as f:
        f.write(f2py_pp.process(lines))

    xml_string = sp.run(
        [
            "java",
            "fortran.ofp.FrontEnd",
            "--class",
            "fortran.ofp.XMLPrinter",
            "--verbosity",
            "0",
            preprocessed_fortran_file,
        ],
        stdout=sp.PIPE,
    ).stdout

    trees = [ET.fromstring(xml_string)]
    comments = get_comments.get_comments(preprocessed_fortran_file)
    outputDict = translate.analyze(trees, comments)
    pySrc = pyTranslate.create_python_string(outputDict)
    asts = [ast.parse(pySrc)]
    pgm_dict = genPGM.create_pgm_dict(
        "crop_yield_lambdas.py", asts, "crop_yield.json"
    )
    root = Scope.from_dict(pgm_dict)
    A = root.to_agraph()
    elements = to_cyjs_elements_json_str(A)

    return render_template("index.html", form=form, elementsJSON=elements)


if __name__ == "__main__":
    app.run()
