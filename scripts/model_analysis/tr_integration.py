import requests
import json

# from delphi.GrFN.networks import GroundedFunctionNetwork


def main():
    webservice = "http://localhost:9000"
    mini_spam = "/Users/phein/Google Drive/ASKE-AutoMATES/Data/Mini-SPAM"
    pet_docs = f"{mini_spam}/docs/SPAM/PET"
    pet_eqns = f"{mini_spam}/eqns/SPAM/PET"
    petpt_grfn = json.load(open(f"PETPT_GrFN.json", "r"))
    petpt_grfn = json.dumps(petpt_grfn)
    # res = requests.post(
    #     "%s/pdf_to_mentions" % webservice,
    #     headers={"Content-type": "application/json"},
    #     json={"pdf": f"{pet_docs}/petpt_2012.pdf"},
    # )
    # json_dict = res.json()
    # mentions = json_dict["mentions"]
    mentions = json.load(open("PT-mentions.json", "r"))
    print(type(mentions))
    print(mentions[0])

    res = requests.post(
        f"{webservice}/align",
        headers={"Content-type": "application/json"},
        json={
            "mentions": "/Users/phein/repos/aske/automates/scripts/model_analysis/PT-mentions.json",
            "equations": f"{pet_eqns}/PETPT/PETPT_equations.txt",
            "grfn": petpt_grfn,
        },
    )
    print(res)
    json_dict = res.json()
    json.dump(json_dict, open("PT-alignment.json", "w"))


if __name__ == "__main__":
    main()
