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
        self, mentions_path: str, eqns_path: str, air_path: str
    ) -> dict:
        if not os.path.isfile(mentions_path):
            raise RuntimeError(f"Mentions not found: {mentions_path}")

        if not os.path.isfile(eqns_path):
            raise RuntimeError(f"Equations not found: {eqns_path}")

        if not os.path.isfile(air_path):
            raise RuntimeError(f"AIR not found: {air_path}")

        if not mentions_path.endswith(".json"):
            raise ValueError("/align expects mentions to be a JSON file")

        if not eqns_path.endswith(".txt"):
            raise ValueError("/align expects equations to be a text file")

        if not air_path.endswith(".json"):
            raise ValueError("/align expects AIR to be a JSON file")

        air_data = json.load(open(air_path, "r"))
        air_variables = list(
            set(
                [
                    {"name": "::".join(v["name"].split("::")[:-1]) + "::0"}
                    for v in air_data["variables"]
                ]
            )
        )
        payload = {
            "mentions": mentions_path,
            "equations": eqns_path,
            "source_code": {
                "variables": air_variables,
                "comments": air_data["source_comments"],
            },
            "toggles": {"groundToSVO": False, "appendToGrFN": False},
            "arguments": {"maxSVOgroundingsPerVar": 5},
        }
        payload_path = "align_payload.json"
        json.dump(payload, open("payload_path", "w"))

        res = requests.post(
            f"{self.webservice}/align",
            headers={"Content-type": "application/json"},
            json={"pathToJson": payload_path},
        )
        print(f"HTTP {res} for /align on:\n\t{mentions_path}\n\t{air_path}\n")
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
