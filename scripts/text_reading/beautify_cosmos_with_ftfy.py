import argparse
import ftfy
import json
import os

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

        f = open(os.path.join(input_dir, input_file))
        loaded_json = json.load(f)

        # updating content with its ftfy-ied version
        for item in loaded_json:
            # print("item: ", item)
            item["content"] = ftfy.fix_text(item["content"])



        # the json file where the output must be stored
        # out_file = open("/Users/alexeeva/Desktop/testing_ftfy/tryExtracting/LPJmL_LPJmL4 – a dynamic global vegetation model with managed land – Part 1 Model description--COSMOS-data---OUT.json", "w")
        out_file_path = os.path.join(output_dir, input_file.replace("--COSMOS-data.json", "--pretty--COSMOS-data.json"))
        print("out file path: " + out_file_path)
        out_file = open(out_file_path, "w")
        json.dump(loaded_json, out_file)
