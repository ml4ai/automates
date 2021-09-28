import argparse
import json
import os

import ftfy

parser = argparse.ArgumentParser()
parser.add_argument("cosmos_dir", help="path to cosmos json file to prettify")
parser.add_argument("output_dir")
args = parser.parse_args()
input_dir = args.cosmos_dir
output_dir = args.output_dir


for input_file in os.listdir(input_dir):
    print(input_file)
    if input_file.endswith("--COSMOS-data.json"):
        print("using file")

        with open(os.path.join(input_dir, input_file)) as infile:
            loaded_json = json.load(infile)

            # updating content with its ftfy-ied version
            for item in loaded_json:
                # print("item: ", item)
                item["content"] = ftfy.fix_text(item["content"])



            # the json file where the output must be stored
            out_file_path = os.path.join(output_dir, input_file.replace("--COSMOS-data.json", "--pretty--COSMOS-data.json"))
            print("out file path: " + out_file_path)
            with open(out_file_path, "w") as out_file:
                json.dump(loaded_json, out_file)
