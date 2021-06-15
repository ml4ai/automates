from flask import Flask, Blueprint, json, request, jsonify

from automates.apps.automates.model.result.api_response import ApiResponse
from automates.apps.automates.translation_driver import translate_c, translate_fortran
from automates.apps.automates.extract_driver import extract_io_from_grfn, extract_io_from_grfn_json
from automates.apps.automates.execute_driver import execute_grfn_json

# Create app and blueprint objects
app = Flask(__name__)
bp_api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

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
        return ApiResponse(200, "", f"Unable to process source code of type {source_language}")

    output_model = body["output_model"]
    if  output_model == "GRFN":
        return jsonify({
            "grfn": grfn_result.to_dict(),
            "variable_io": extract_io_from_grfn(grfn_result)
        })
    else:
        return ApiResponse(200, "", f"Unable to process output of type {output_model}")
    

@bp_api_v1.route("/extract/variable_io", methods=["POST"])
def extract_variable_io():
    # TODO validate body using marshmellow
    body = request.json
    grfn_json = body["grfn"]
    io = extract_io_from_grfn_json(grfn_json)
    return jsonify(io)


@bp_api_v1.route("/execute/grfn", methods=["POST"])
def execute_grfn():
    body = request.json
    grfn_json = body["grfn"]
    input_json = body["inputs"]
    execution_results = execute_grfn_json(grfn_json, input_json)
    return jsonify(execution_results)

# Register API blueprints
app.register_blueprint(bp_api_v1)
