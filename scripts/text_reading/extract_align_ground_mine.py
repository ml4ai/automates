import requests
import json
import os

webservice = "http://localhost:9000"

# cur_dir = os.getcwd()
#cur_dir = "/home/alexeeva/Repos/automates/scripts/model_assembly/"
# automates_data = os.environ["AUTOMATES_DATA"]
# mini_spam = f"{automates_data}/Mini-SPAM"
# pet_grfns = f"{mini_spam}/grfns"
# pet_docs = f"{mini_spam}/docs/SPAM/PET"
# pet_eqns = f"{mini_spam}/eqns/SPAM/PET"


#def call_pdf_to_mentions(doc_name, out_name):
#    doc_file = "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/automates-related/Mini-SPAM-20200321T192737Z-001/Mini-SPAM/toRunSciParse/petpno_Penman.pdf"
#    if not os.path.isfile(doc_file):
#        raise RuntimeError(f"Document not found: {doc_name}")
#
#    res = requests.post(
#        f"{webservice}/pdf_to_mentions",
#        headers={"Content-type": "application/json"},
#        json={"pdf": doc_file, "outfile": "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/automates-related/Mini-SPAM-20200321T192737Z-001/Mini-SPAM/toRunSciParse/MASHA.json"},
#    )
#    print(f"HTTP {res} for /pdf_to_mentions on {doc_name}")


def call_align():
    # mentions_path =  "/home/alexeeva/Downloads/PT-mentions.json"
    # if not os.path.isfile(mentions_path):
    #     raise RuntimeError(f"Mentions not found: {mentions_name}")
    #
    # eqns_path = "/home/alexeeva/Downloads/PETPT_equations.txt"
    # if not os.path.isfile(eqns_path):
    #     raise RuntimeError(f"Equations not found: {eqn_name}")
    #
    # grfn_path = "/home/alexeeva/Downloads/PETPT_GrFN.json"
    # if not os.path.isfile(grfn_path):
    #     raise RuntimeError(f"GrFN not found: {grfn_name}")

    res = requests.post(
        f"{webservice}/align",
        headers={"Content-type": "application/json"},
        json={
            "pathToJson":"/Users/alexeeva/Desktop/automates-related/align_payload.json"
            # "pathToJson":"/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/automates-related/integration-wg-20201105T153355Z-001/integration-wg/SARS-CoV-1-double-epidemic/align_payload.json"
            # "pathToJson":"/home/alexeeva/Repos/automates/scripts/model_assembly/align_payload.json"
            # "pathToJson": "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/automates-related/petpno_penman_file/PNO-alignment-dataWithNewerMentionsAfterTRDebug.json",
            # "pathToJson":"/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/automates-related/petpno_penman_file/PNO-alignment-dataWithNewerMentionsAfterTRDebugWithoutSVO.json"
            # "equations": eqns_path,
            # "grfn": grfn_path,
        },
    )
    # print(f"HTTP {res} for /align on ({mentions_name}, {grfn_name})")
    json_dict = res.json()
    json.dump(json_dict, open("masha10.json", "w"), indent=4)

def call_alignMentionsFromTwoModels():
    print("running call align mentions")
    res = requests.post(
        f"{webservice}/alignMentionsFromTwoModels",
        headers={"Content-type": "application/json"},
        json={
            "pathToJson": "/home/alexeeva/Repos/automates/scripts/model_assembly/align_mentions_payload.json"
        },
    )
    # print(f"HTTP {res} for /align on ({mentions_name}, {grfn_name})")
    json_dict = res.json()
    json.dump(json_dict, open("masha_model_comparison1.json", "w"), indent=4)

def call_parquetJson_to_mentions():
    # mentions_path =  "/home/alexeeva/Downloads/PT-mentions.json"
    # if not os.path.isfile(mentions_path):
    #     raise RuntimeError(f"Mentions not found: {mentions_name}")
    #
    # eqns_path = "/home/alexeeva/Downloads/PETPT_equations.txt"
    # if not os.path.isfile(eqns_path):
    #     raise RuntimeError(f"Equations not found: {eqn_name}")
    #
    # grfn_path = "/home/alexeeva/Downloads/PETPT_GrFN.json"
    # if not os.path.isfile(grfn_path):
    #     raise RuntimeError(f"GrFN not found: {grfn_name}")


    res = requests.post(
        f"{webservice}/parquetJson_to_mentions",
        headers={"Content-type": "application/json"},
        json={
            "pathToJson": "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/automates-related/double_epidemic_model_COSMOS/documents/sample.json"
            # "pathToJson": "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/automates-related/petpno_penman_file/PNO-alignment-dataWithNewerMentionsAfterTRDebug.json",
            # "equations": eqns_path,
            # "grfn": grfn_path,
        },
    )
    # print(f"HTTP {res} for /align on ({mentions_name}, {grfn_name})")
    json_dict = res.json()
    json.dump(json_dict, open("masha9.json", "w"), indent=4)

def call_cosmos_json_to_mentions():
    outfile = "masha1.json"
    res = requests.post(
        f"{webservice}/cosmos_json_to_mentions",
        headers={"Content-type": "application/json"},
        json={
            "cosmos_file": "/Users/alexeeva/Desktop/automates-related/TWIST/cosmos/TWIST--COSMOS-data.json",
            "outfile": outfile
        },
    )

    # the method itself exports mentions
    # json_dict = res.json()
    # json.dump(json_dict, open(outfile, "w"), indent=4)



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


def call_groundMentionsToWikidata(mentions_name, out_name):
    mentions_path = f"{mentions_name}"

    if not os.path.isfile(mentions_path):
        raise RuntimeError(f"Mentions file not found: {mentions_name}")

    res = requests.post(
        f"{webservice}/groundMentionsToWikidata",
        headers={"Content-type": "application/json"},
        json={"mentions": mentions_path},
    )

    print(f"HTTP {res} for /groundMentionsToWikidata on {mentions_name}")
    json_dict = res.json()
    json.dump(json_dict, open(f"{out_name}", "w"))


if __name__ == "__main__":
    # call_pdf_to_mentions("petasce", "petpno")
    # call_align()
    # call_alignMentionsFromTwoModels()
    # call_cosmos_json_to_mentions()
    # call_parquetJson_to_mentions()
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
    # call_groundMentionsToSVO("CHIME-SIR-mentions", "CHIME-SIR-mentions-svo_grounding")
    # call_groundMentionsToWikidata("/Users/alexeeva/Repos/automates/automates/text_reading/masha1.json", "/Users/alexeeva/Repos/automates/automates/text_reading/masha1-wiki-groundings.json")
    call_groundMentionsToWikidata("/Users/alexeeva/Repos/automates/scripts/model_assembly/SIR-simple--mentions.json", "/Users/alexeeva/Repos/automates/scripts/model_assembly/SIR-simple--mentions-with-grounding.json")
    # call_groundMentionsToSVO("PT-mentions", "PT-svo_grounding")

    # call_pdf_to_mentions("petpno_Penman", "PNO-mentions")
    # call_pdf_to_mentions("petpen_PM", "PEN-mentions")
    # call_pdf_to_mentions("petdyn_modern", "DYN-mentions")
    #
    # call_groundMentionsToSVO("PNO-mentions", "PNO-svo_grounding")
    # call_groundMentionsToSVO("PEN-mentions", "PEN-svo_grounding")
    # call_groundMentionsToSVO("DYN-mentions", "DYN-svo_grounding")
