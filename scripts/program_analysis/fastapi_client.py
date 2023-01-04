import os
import json
import requests
import argparse

def module_to_json(root_path: str, system_filepaths: str, system_name: str) -> str:
    files=[]
    blobs=[]

    with open(system_filepaths, "r") as f:
        files = f.readlines()
    files = [file.strip() for file in files]
    
    for file_path in files:
        full_path = os.path.join(root_path, file_path)
        with open(full_path, "r") as f:
            blobs.append(f.read())
    
    return json.dumps({"files":files, "blobs":blobs, "name": system_name})
    
parser = argparse.ArgumentParser()
parser.add_argument("host", type=str)
parser.add_argument("port", type=str)

parser.add_argument("root_path", type=str)
parser.add_argument("system_filepaths", type=str)
parser.add_argument("system_name", type=str)

args = parser.parse_args()

url = f"http://{args.host}:{args.port}"
data = module_to_json(args.root_path, args.system_filepaths, args.system_name)
with open("test.json", "w") as f:
    f.write(data)
x = requests.post(url, data=data)
print(x.text)