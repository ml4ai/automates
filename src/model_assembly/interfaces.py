import os
import json

import requests


class TextReadingInterface:
    def __init__(self, addr):
        self.webservice = addr

    def extract_mentions(self, doc_path: str, out_path: str) -> dict:
        if not os.path.isfile(doc_path):
            raise RuntimeError(f"Document not found: {doc_path}")

        if not out_path.endswith(".json"):
            raise ValueError("/pdf_to_mentions requires an JSON output file")

        res = requests.post(
            f"{self.webservice}/pdf_to_mentions",
            headers={"Content-type": "application/json"},
            json={"pdf": doc_path, "outfile": out_path},
        )
        print(f"HTTP {res} for /pdf_to_mentions on {doc_path}")
        return json.load(open(out_path, "r"))

    def get_link_hypotheses(
        mentions_path: str, eqns_path: str, air_path: str
    ) -> dict:
        if not os.path.isfile(mentions_path):
            raise RuntimeError(f"Mentions not found: {mentions_path}")

        if not os.path.isfile(eqns_path):
            raise RuntimeError(f"Equations not found: {eqns_path}")

        grfn_path = f"{pet_grfns}/{grfn_name}.json"
        if not os.path.isfile(grfn_path):
            raise RuntimeError(f"GrFN not found: {grfn_name}")

        res = requests.post(
            f"{webservice}/align",
            headers={"Content-type": "application/json"},
            json={
                "mentions": mentions_path,
                "equations": eqns_path,
                "grfn": grfn_path,
            },
        )
        print(f"HTTP {res} for /align on ({mentions_name}, {grfn_name})")
        json_dict = res.json()
        json.dump(json_dict, open(f"{out_name}.json", "w"))


class EquationReadingInterface:
    # TODO: define this for interface to EqDec and Cosmos equation-detection
    pass
