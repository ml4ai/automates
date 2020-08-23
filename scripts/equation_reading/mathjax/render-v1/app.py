from flask import Flask, render_template, jsonify, request
import json

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/load_data")
def load_data():
    filepath = request.args.get("filepath", 0, type=str)
    return jsonify(json.load(open(filepath, "r")))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
