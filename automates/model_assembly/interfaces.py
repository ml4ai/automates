import os
import json
from typing import List, Dict, NoReturn

import requests


class TextReadingInterface:
    def __init__(self, addr):
        self.webservice = addr

    def extract_mentions(self, doc_path: str, out_path: str) -> dict:
        if not os.path.isfile(doc_path):
            raise RuntimeError(f"Document not found: {doc_path}")

        if not out_path.endswith(".json"):
            raise ValueError("/pdf_to_mentions requires an JSON output file")

        if doc_path.endswith(".pdf"):
            res = requests.post(
                f"{self.webservice}/pdf_to_mentions",
                headers={"Content-type": "application/json"},
                json={"pdf": doc_path, "outfile": out_path},
            )
            print(f"HTTP {res} for /pdf_to_mentions on {doc_path}")

        elif doc_path.endswith("--COSMOS-data.json"):
            res = requests.post(
                f"{self.webservice}/cosmos_json_to_mentions",
                headers={"Content-type": "application/json"},
                json={"pathToCosmosJson": doc_path, "outfile": out_path},
            )
            print(f"HTTP {res} for /cosmos_json_to_mentions on {doc_path}")
        elif doc_path.endswith(".json"):
            res = requests.post(
                f"{self.webservice}/json_doc_to_mentions",
                headers={"Content-type": "application/json"},
                json={"json": doc_path, "outfile": out_path},
            )
            print(f"HTTP {res} for /json_doc_to_mentions on {doc_path}")

        else:
            raise ValueError(f"Unknown input document extension in file {doc_path} (pdf or json expected)")

        return json.load(open(out_path, "r"))

    def get_link_hypotheses(
        self,
        mentions_path: str,
        eqns_path: str,
        grfn_path: str,
        comments_path: str,
        wikidata_path: str
    ) -> dict:
        if not os.path.isfile(mentions_path):
            raise RuntimeError(f"Mentions not found: {mentions_path}")

        if not os.path.isfile(eqns_path):
            raise RuntimeError(f"Equations not found: {eqns_path}")

        if not os.path.isfile(grfn_path):
            raise RuntimeError(f"GrFN not found: {grfn_path}")

        if not os.path.isfile(comments_path):
            raise RuntimeError(f"Comments not found: {comments_path}")

        if not mentions_path.endswith(".json"):
            raise ValueError("/align expects mentions to be a JSON file")

        if not eqns_path.endswith(".txt"):
            raise ValueError("/align expects equations to be a text file")

        if not grfn_path.endswith(".json"):
            raise ValueError("/align expects GrFN to be a JSON file")

        if not comments_path.endswith(".json"):
            raise ValueError("/align expects comments to be a JSON file")

        grfn_data = json.load(open(grfn_path, "r"))

        unique_var_names = list(
            {
                "::".join(var_def["identifier"].split("::")[:-1]) + "::0"
                for var_def in grfn_data["variables"]
            }
        )
        variables = [{"name": var_name} for var_name in unique_var_names]

        equations = list()
        with open(eqns_path, "r") as infile:
            for eqn_line in infile.readlines():
                equations.append(eqn_line.strip())

        payload = {
            "mentions": mentions_path,
            "documents": mentions_path,
            "equations": equations,
            "source_code": {
                "variables": variables,
                "comments": json.load(open(comments_path, "r")),
            },
            "toggles": {"groundToSVO": False, "groundToWiki": False, "saveWikiGroundings": False, "appendToGrFN": False},
            "arguments": {"maxSVOgroundingsPerVar": 5},
            "wikidata": wikidata_path
        }
        payload_path = f"{os.getcwd()}/align_payload.json"
        json.dump(payload, open(payload_path, "w"))

        res = requests.post(
            f"{self.webservice}/align",
            headers={"Content-type": "application/json"},
            json={"pathToJson": payload_path},
        )
        print(f"HTTP {res} for /align on:\n\t{mentions_path}\n\t{grfn_path}\n")
        json_dict = res.json()
        return json_dict

    def ground_to_SVO(self, mentions_path: str) -> dict:
        if not os.path.isfile(mentions_path):
            raise RuntimeError(f"Mentions file not found: {mentions_path}")

        if not mentions_path.endswith(".json"):
            raise ValueError(
                "/groundMentionsToSVO expects mentions to be a JSON file"
            )

        res = requests.post(
            f"{self.webservice}/groundMentionsToSVO",
            headers={"Content-type": "application/json"},
            json={"mentions": mentions_path},
        )

        print(f"HTTP {res} for /groundMentionsToSVO on {mentions_path}")
        json_dict = res.json()
        return json_dict


class EquationReadingInterface:
    # TODO: define this for interface to EqDec and Cosmos equation-detection
    pass


class CosmosInterface:
    def __init__(self):
        pass

    def convert_parquet_collection(self, parquet_filenames: List[str]) -> Dict:
        pass

    def find_parquet_files(self, outdir_path: str) -> List:
        return [
            os.path.join(outdir_path, fname)
            for fname in os.listdir(outdir_path)
            if fname.endswith(".parquet")
        ]

    def parquet2dict(self, parquet_file) -> Dict:
        pass

    def parquet2Json(self, parquet_file) -> str:
        pass

    def parquet2JsonFile(self, parquet_file, json_filename) -> NoReturn:
        pass
