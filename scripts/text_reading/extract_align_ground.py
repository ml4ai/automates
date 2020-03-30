import requests
import json
import os

webservice = "http://localhost:9000"

cur_dir = os.getcwd()
automates_data = os.environ["AUTOMATES_DATA"]
mini_spam = f"{automates_data}/Mini-SPAM"
pet_grfns = f"{mini_spam}/grfns"
pet_docs = f"{mini_spam}/docs/SPAM/PET"
pet_eqns = f"{mini_spam}/eqns/SPAM/PET"


def call_pdf_to_mentions(doc_name, out_name):
    res = requests.post(
        f"{webservice}/pdf_to_mentions",
        headers={"Content-type": "application/json"},
        json={
            "pdf": f"{pet_docs}/{doc_name}.pdf",
            "outfile": f"{cur_dir}/{out_name}.json",
        },
    )
    print(f"HTTP {res} for /pdf_to_mentions on doc_name")


def call_align(doc_name, eqn_path, eqn_name, grfn_name, out_name):
    res = requests.post(
        f"{webservice}/align",
        headers={"Content-type": "application/json"},
        json={
            "mentions": f"{cur_dir}/{doc_name}.json",
            "equations": f"{pet_eqns}/{eqn_path}/{eqn_name}.txt",
            "grfn": f"{pet_grfns}/{grfn_name}.json",
        },
    )
    print(f"HTTP {res} for /align on ({doc_name}, {grfn_name})")
    json_dict = res.json()
    json.dump(json_dict, open(f"{out_name}.json", "w"))


def call_groundMentionsToSVO(mentions_name, out_name):
    # NOTE: relies upon call_pdf_to_mentions being run previously
    res = requests.post(
        f"{webservice}/groundMentionsToSVO",
        headers={"Content-type": "application/json"},
        json={"mentions": f"{cur_dir}/{mentions_name}.json"},
    )

    print(f"HTTP {res} for /groundMentionsToSVO on {mentions_name}")
    json_dict = res.json()
    json.dump(json_dict, open(f"{out_name}.json", "w"))


if __name__ == "__main__":
    call_pdf_to_mentions("petasce", "ASCE-mentions")
    call_align(
        "petasce", "PETASCE", "PETASCE_equations", "PETASCE", "ASCE-alignment"
    )

    call_pdf_to_mentions("petpt_2012", "PT-mentions")
    call_align(
        "petpt_2012", "PETPT", "PETPT_equations", "PETPT", "PT-alignment"
    )

    call_groundMentionsToSVO("ASCE-mentions", "ASCE-svo_grounding")
    call_groundMentionsToSVO("PT-mentions", "PT-svo_grounding")
