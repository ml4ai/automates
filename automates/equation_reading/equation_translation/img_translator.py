import requests
import json


def png2latex(input_path, output_path):
    """
    Calls the EqDecoder pipeline with a PNG image and returns JSON containing
    the tokenized latex output from OpenNMT.

    Args:
        input_path: [String] -- in the form: /path/to/input/<filename>.png
        output_path: [String] -- in the form: /path/to/output/
    Returns:
        output_file: [String] -- in the form: /path/to/output/<filename>.json
    """
    dir_path_index = input_path.rfind("/") + 1
    file_ending_index = input_path.rfind(".png")
    img_filename = input_path[dir_path_index:]

    res = requests.post(
        "http://localhost:8000/decode_equation/",
        files={"file": (img_filename, open(input_path, "rb"), "image/png")},
    )

    img_basename = img_filename[:file_ending_index]
    output_file = f"{output_path}/{img_basename}.json"
    json.dump(res.json(), open(output_file, "w"))
    return output_file
