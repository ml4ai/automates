import os
import json
import requests
import argparse

def system_to_json(root_path: str, system_filepaths: str, system_name: str) -> str:
    files=[]
    blobs=[]

    with open(system_filepaths, "r") as f:
        files = f.readlines()
    files = [file.strip() for file in files]
    
    for file_path in files:
        full_path = os.path.join(root_path, file_path)
        with open(full_path, "r") as f:
            blobs.append(f.read())
    
    root_name = os.path.basename(os.path.normpath(root_path))

    return json.dumps({"files":files, "blobs":blobs, "system_name": system_name, "root_name":root_name})
    
parser = argparse.ArgumentParser()
parser.add_argument("host", type=str)
parser.add_argument("port", type=str)

parser.add_argument("root_path", type=str)
parser.add_argument("system_filepaths", type=str)
parser.add_argument("system_name", type=str)

args = parser.parse_args()

url = f"http://{args.host}:{args.port}"
data = system_to_json(args.root_path, args.system_filepaths, args.system_name)
response = requests.post(url, data=data)

print(data)
with open(f"{args.system_name}--Gromet-FN-auto.json", "w") as f:
    f.write(response.json())
