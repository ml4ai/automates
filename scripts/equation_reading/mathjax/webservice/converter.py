import requests
import json
import argparse


def main(args):
    # Define the webservice address
    webservice = "http://localhost:8081"

    # Load the LaTeX string data
    latex_strs = json.load(open(args.infile, "r"))

    # Translate and save each LaTeX string using the NodeJS service for MathJax
    if args.bulk:
        res = requests.post(
            f"{webservice}/bulk_tex2mml",
            headers={"Content-type": "application/json"},
            json={"TeX_data": json.dumps(latex_strs)},
        )
        # Save the MML text response to our list
        mml_strs = res.json()
    else:
        mml_strs = list()
        for latex in latex_strs:
            res = requests.post(
                f"{webservice}/tex2mml",
                headers={"Content-type": "application/json"},
                json={"tex_src": json.dumps(latex)},
            )
            # Save the MML text response to our list
            mml_strs.append(res.text)

    # Dump the MathML strings to JSON
    json.dump(mml_strs, open(args.outfile, "w"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Enable convserion of LaTeX to MathML"
    )
    parser.add_argument(
        "-i",
        "--infile",
        type=str,
        required=True,
        help="Filepath to a JSON file containing LaTeX equation strings",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        type=str,
        required=True,
        help="Filepath to a JSON file to use for storing translated MathML",
    )
    parser.add_argument(
        "-b",
        "--bulk",
        action="store_true",
        default=False,
        help="If True, send all LaTeX equations in a single request",
    )

    args = parser.parse_args()
    main(args)
