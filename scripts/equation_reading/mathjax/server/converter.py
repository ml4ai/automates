import requests
import json


def main():

    webservice = "http://localhost:5000"

    latex_strs = json.load(open("static/data/latex_data_dev.json", "r"))
    mml_strs = list()
    for latex in latex_strs:
        res = requests.post(
            f"{webservice}/tex_to_mml",
            headers={"Content-type": "application/json"},
            json={"pdf": doc_file, "outfile": f"{cur_dir}/{out_name}.json"},
        )

    json.dump(mml_strs, open("static/data/mml.json", "w"))


if __name__ == "__main__":
    main()
