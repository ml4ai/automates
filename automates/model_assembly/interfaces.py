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
        self,
        mentions_path: str,
        eqns_path: str,
        grfn_path: str,
        comments_path: str,
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
        variables = list(
            set(
                [
                    {
                        "name": "::".join(v["identifier"].split("::")[:-1])
                        + "::0"
                    }
                    for v in grfn_data["variables"]
                ]
            )
        )
        payload = {
            "mentions": mentions_path,
            "equations": eqns_path,
            "source_code": {
                "variables": variables,
                "comments": json.load(open(comments_path, "r")),
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
