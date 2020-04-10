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
    doc_file = f"{pet_docs}/{doc_name}.pdf"
    if not os.path.isfile(doc_file):
        raise RuntimeError(f"Document not found: {doc_name}")

    res = requests.post(
        f"{webservice}/pdf_to_mentions",
        headers={"Content-type": "application/json"},
        json={"pdf": doc_file, "outfile": f"{cur_dir}/{out_name}.json"},
    )
    print(f"HTTP {res} for /pdf_to_mentions on {doc_name}")


def call_align(mentions_name, eqn_path, eqn_name, grfn_name, out_name):
    mentions_path = f"{cur_dir}/{mentions_name}.json"
    if not os.path.isfile(mentions_path):
        raise RuntimeError(f"Mentions not found: {mentions_name}")

    eqns_path = f"{pet_eqns}/{eqn_path}/{eqn_name}.txt"
    if not os.path.isfile(eqns_path):
        raise RuntimeError(f"Equations not found: {eqn_name}")

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


def call_groundMentionsToSVO(mentions_name, out_name):
    mentions_path = f"{cur_dir}/{mentions_name}.json"
    if not os.path.isfile(mentions_path):
        raise RuntimeError(f"Mentions file not found: {mentions_name}")

    res = requests.post(
        f"{webservice}/groundMentionsToSVO",
        headers={"Content-type": "application/json"},
        json={"mentions": mentions_path},
    )

    print(f"HTTP {res} for /groundMentionsToSVO on {mentions_name}")
    json_dict = res.json()
    json.dump(json_dict, open(f"{out_name}.json", "w"))


if __name__ == "__main__":
    # call_pdf_to_mentions("petasce", "ASCE-mentions")
    # call_align(
    #     "ASCE-mentions",
    #     "PETASCE",
    #     "PETASCE_equations",
    #     "PETASCE_GrFN",
    #     "ASCE-alignment",
    # )
    #
    # call_pdf_to_mentions("petpt_2012", "PT-mentions")
    # call_align(
    #     "PT-mentions", "PETPT", "PETPT_equations", "PETPT_GrFN", "PT-alignment"
    # )
    #
    # call_groundMentionsToSVO("ASCE-mentions", "ASCE-svo_grounding")
    # call_groundMentionsToSVO("PT-mentions", "PT-svo_grounding")

    # call_pdf_to_mentions("petpno_Penman", "PNO-mentions")
    # call_pdf_to_mentions("petpen_PM", "PEN-mentions")
    # call_pdf_to_mentions("petdyn_modern", "DYN-mentions")

    call_groundMentionsToSVO("PNO-mentions", "PNO-svo_grounding")
    call_groundMentionsToSVO("PEN-mentions", "PEN-svo_grounding")
    call_groundMentionsToSVO("DYN-mentions", "DYN-svo_grounding")
