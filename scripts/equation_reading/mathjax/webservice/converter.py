import requests
import json


def main():
    # Define the webservice address
    webservice = "http://localhost:8081"

    # Load the LaTeX string data
    latex_strs = json.load(open("latex_data_dev.json", "r"))

    # Translate and save each LaTeX string using the NodeJS service for MathJax
    mml_strs = list()
    for latex in latex_strs:
        res = requests.get(f"{webservice}/TeX2MML", params={"tex_src": latex},)
        # Save the MML text response to our list
        mml_strs.append(res.text)

    # Dump the MathML strings to JSON
    json.dump(mml_strs, open("mml.json", "w"))


if __name__ == "__main__":
    main()
