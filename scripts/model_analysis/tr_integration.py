import requests
import json
import os

webservice = "http://localhost:9000"

cur_dir = os.getcwd()
# automates_data = os.environ["AUTOMATES_DATA"]
# pet_docs = f"{automates_data}/Mini-SPAM/docs/SPAM/PET"
# pet_eqns = f"{automates_data}/Mini-SPAM/eqns/SPAM/PET"


def test_pdf_to_mentions():
    res = requests.post(
        f"{webservice}/pdf_to_mentions",
        headers={"Content-type": "application/json"},
        json={
            "pdf": f"{pet_docs}/petpt_2012.pdf",
            "outfile": f"{cur_dir}/PT-mentions.json",
        },
    )
    print(res)
    # mentions = res.json()
    # mentions = json_dict["mentions"]
    # json.dump(mentions, open("PT-mentions.json", "w"))


def test_align():
    # NOTE: relies upon test_pdf_to_mentions being run previously
    # mentions = json.load(open("PT-mentions.json", "r"))
    # mentions["outfile"] = f"{cur_dir}/PT-alignment.json"
    # json.dump(mentions, open("PT-mentions.json", "w"))

    res = requests.post(
        f"{webservice}/align",
        headers={"Content-type": "application/json"},
        json={
            "mentions": "/home/alexeeva/Downloads/PT-mentions.json",
            "equations": "/home/alexeeva/Repos/automates/scripts/model_analysis/PETPT_equations.txt",
            "grfn": "/home/alexeeva/Repos/automates/scripts/model_analysis/PETPT_GrFN.json",
        },
    )
    print("Done")
    print(res)
    json_dict = res.json()
    json.dump(json_dict, open("PT-alignment.json", "w"))


def test_groundMentionsToSVO():
    # NOTE: relies upon test_pdf_to_mentions being run previously
    res = requests.post(
        f"{webservice}/groundMentionsToSVO",
        headers={"Content-type": "application/json"},
        json={"mentions": f"{cur_dir}/PT-mentions.json"},
    )

    print(res)
    json_dict = res.json()
    json.dump(json_dict, open("PT-ground-SVO.json", "w"))


if __name__ == "__main__":
    # test_pdf_to_mentions()
    test_align()
    # test_groundMentionsToSVO()
