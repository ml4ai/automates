import requests
import json

# from delphi.GrFN.networks import GroundedFunctionNetwork


def main():
    webservice = "http://localhost:9000"
    mini_spam = "/Users/phein/Google Drive/ASKE-AutoMATES/Data/Mini-SPAM"
    pet_docs = f"{mini_spam}/docs/SPAM/PET"
    pet_eqns = f"{mini_spam}/eqns/SPAM/PET"
    petpt_grfn = f"PETPT_GrFN.json"
    # res = requests.post(
    #     "%s/pdf_to_mentions" % webservice,
    #     headers={"Content-type": "application/json"},
    #     json={"pdf": f"{pet_docs}/petpt_2012.pdf"},
    # )
    # json_dict = res.json()
    # mentions = json_dict["mentions"]
    pdf_json = json.load(open("PT-mentions.json", "r"))
    mentions = pdf_json["mentions"]

    res = requests.post(
        f"{webservice}/align",
        headers={"Content-type": "application/json"},
        json={
            "mentions": mentions,
            "equations": f"PETPT_equations.txt",
            "grfn": "PETPT_GrFN.json",
        },
    )
    print(res)
    json_dict = res.json()
    json.dump(json_dict, open("PT-alignment.json", "w"))


if __name__ == "__main__":
    main()
