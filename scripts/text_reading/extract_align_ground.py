import argparse
import requests
import json
import os

webservice = "http://localhost:9000"

### The script is used to call various endpoints defined in /automates/automates/text_reading/webapp/app/controllers/HomeController.scala on individual files

# this endpoint requires science parse jar running
def call_pdf_to_mentions(doc_name, out_name):
    if not os.path.isfile(doc_name):
        raise RuntimeError(f"Document not found: {doc_name}")

    res = requests.post(
        f"{webservice}/pdf_to_mentions",
        headers={"Content-type": "application/json"},
        json={"pdf": doc_name, "outfile": f"{out_name}"},
    )
    print(f"HTTP {res} for /pdf_to_mentions on {doc_name}")


# SVO API has been disabled, so this cannot be currently used
def call_groundMentionsToSVO(mentions_name, out_name):
    if not os.path.isfile(mentions_name):
        raise RuntimeError(f"Mentions file not found: {mentions_name}")

    res = requests.post(
        f"{webservice}/groundMentionsToSVO",
        headers={"Content-type": "application/json"},
        json={"mentions": mentions_name},
    )

    print(f"HTTP {res} for /groundMentionsToSVO on {mentions_name}")
    json_dict = res.json()
    json.dump(json_dict, open(f"{out_name}.json", "w"))

# given a file of serialized mentions, produces a file with associated wikidata grounding
# before running, set toggle.groundToWiki in automates/automates/model_assembly/interfaces.py to True or groundToWiki in application.conf to true
def call_groundMentionsToWikidata(mentions_path, out_name):

    if not os.path.isfile(mentions_path):
        raise RuntimeError(f"Mentions file not found: {mentions_path}")

    res = requests.post(
        f"{webservice}/groundMentionsToWikidata",
        headers={"Content-type": "application/json"},
        json={"mentions": mentions_path},
    )

    print(f"HTTP {res} for /groundMentionsToWikidata on {mentions_path}")
    json_dict = res.json()
    json.dump(json_dict, open(f"{out_name}", "w"))


# replace sample text in this method ("text" in the post request) to return a file with serialized mentions for the text
def call_process_text(out_name):

    res = requests.post(
        f"{webservice}/process_text",
        headers={"Content-type": "application/json"},
        json={"text": "LAI is leaf area index."},
    )

    print(f"HTTP {res} for /process_text")
    json_dict = res.json()
    json.dump(json_dict, open(f"{out_name}", "w"))

# output serizlized mentions for the Science Parse json input
def call_json_doc_to_mentions(doc_name, out_name):

    res = requests.post(
        f"{webservice}/json_doc_to_mentions",
        headers={"Content-type": "application/json"},
        json={"json": doc_name, "outfile": f"{out_name}"},
    )
    print(f"HTTP {res} for /json_doc_to_mentions on {doc_name}")

# output serizlized mentions for the COSMOS json input
def call_cosmos_json_doc_to_mentions(doc_name, out_name):

    res = requests.post(
        f"{webservice}/cosmos_json_to_mentions",
        headers={"Content-type": "application/json"},
        json={"pathToCosmosJson": doc_name, "outfile": f"{out_name}"},
    )
    print(f"HTTP {res} for /cosmos_json_to_mentions on {doc_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="input file path")
    parser.add_argument("output_file", help="output file path")
    args = parser.parse_args()
    # replace the method below with any other method here to run different endpoints
    call_pdf_to_mentions(args.input_file, args.output_file)
