from flask import Flask, Blueprint, json, request, jsonify

from automates.apps.automates.model.result.api_response import ApiResponse
from automates.apps.automates.translation_driver import translate_c, translate_fortran
from automates.apps.automates.extract_driver import (
    extract_io_from_grfn,
    extract_io_from_grfn_json,
    extract_expr_trees_from_grfn_json,
    extract_model_dynamics_from_grfn_json,
)
from automates.apps.automates.execute_driver import (
    execute_grfn_json,
    execute_gromet_experiment_json,
)

# Create app and blueprint objects
app = Flask(__name__)
bp_api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")


@app.route("/")
def hello_world():
    return "Success"


@bp_api_v1.route("/translate", methods=["POST"])
def translate():
    # TODO validate body using marshmellow
    body = request.json

    source_language = body["source_language"]
    grfn_result = None
    if source_language == "c":
        grfn_result = translate_c(body)
    elif source_language == "fortran":
        grfn_result = translate_fortran(body)
    else:
        return ApiResponse(
            400, "", f"Unable to process source code of type {source_language}"
        )

    output_model = body["output_model"]
    if output_model == "GRFN":
        return jsonify(
            {
                "grfn": grfn_result.to_dict(),
                "variable_io": extract_io_from_grfn(grfn_result),
            }
        )
    else:
        return ApiResponse(400, "", f"Unable to process output of type {output_model}")


@bp_api_v1.route("/extract/variable_io", methods=["POST"])
def extract_variable_io():
    # TODO validate body using marshmellow
    body = request.json
    res = {}
    if "grfn" in body:
        grfn_json = body["grfn"]
        res = extract_io_from_grfn_json(grfn_json)
    else:
        res = {
            "code": 400,
            "type": "Bad request.",
            "message": 'No "grfn" field was provided in input.',
        }
    return jsonify(res)


@bp_api_v1.route("/extract/expr_trees", methods=["POST"])
def extract_expr_trees():
    # TODO validate body using marshmellow
    body = request.json
    res = {}
    if "grfn" in body:
        grfn_json = body["grfn"]
        res = extract_expr_trees_from_grfn_json(grfn_json)
    else:
        res = {
            "code": 400,
            "type": "Bad request.",
            "message": 'No "grfn" field was provided in input.',
        }
    return jsonify(res)


@bp_api_v1.route("/extract/dynamics", methods=["POST"])
def extract_dynamics():
    # TODO validate body using marshmellow
    body = request.json
    res = {}
    if "grfn" in body:
        grfn_json = body["grfn"]
        res = extract_model_dynamics_from_grfn_json(grfn_json)
    else:
        res = {
            "code": 400,
            "type": "Bad request.",
            "message": 'No "grfn" field was provided in input.',
        }
    return jsonify(res)


@bp_api_v1.route("/execute/grfn", methods=["POST"])
def execute_grfn():
    body = request.json
    grfn_json = body["grfn"]
    input_json = body["inputs"]

    outputs_json = []
    if "outputs" in body:
        outputs_json = body["outputs"]

    execution_results = execute_grfn_json(grfn_json, input_json, outputs_json)
    return jsonify(execution_results)


@bp_api_v1.route("/execute/gromet_experiment", methods=["POST"])
def execute_gromet_experiment():
    """

    Returns:
        [type]: [description]
    """
    experiment_json = request.json
    experiment_results = execute_gromet_experiment_json(experiment_json)
    return jsonify(experiment_results)


# Register API blueprints
app.register_blueprint(bp_api_v1)
