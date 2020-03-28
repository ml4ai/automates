import requests
import json

webservice = "http://localhost:9000"

# TODO: update this to no longer depend on my google drive path
mini_spam = "/Users/phein/Google Drive/ASKE-AutoMATES/Data/Mini-SPAM"
cur_dir = "/Users/phein/repos/aske/automates/scripts/model_analysis"

pet_docs = f"{mini_spam}/docs/SPAM/PET"
pet_eqns = f"{mini_spam}/eqns/SPAM/PET"


def test_pdf_to_mentions():
    res = requests.post(
        f"{webservice}/pdf_to_mentions",
        headers={"Content-type": "application/json"},
        json={"pdf": f"{pet_docs}/petpt_2012.pdf"},
    )
    print(res)
    json_dict = res.json()
    mentions = json_dict["mentions"]
    json.dump(mentions, open("PT-mentions.json", "w"))


def test_align():
    # NOTE: relies upon test_pdf_to_mentions being run previously
    petpt_grfn = json.load(open("PETPT_GrFN.json", "r"))
    res = requests.post(
        f"{webservice}/align",
        headers={"Content-type": "application/json"},
        json={
            "mentions": f"{cur_dir}/PT-mentions.json",
            "equations": f"{pet_eqns}/PETPT/PETPT_equations.txt",
            "grfn": petpt_grfn,
        },
    )
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
    test_pdf_to_mentions()
    test_align()
    # test_groundMentionsToSVO()
