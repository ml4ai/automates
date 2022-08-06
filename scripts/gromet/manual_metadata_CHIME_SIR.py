from automates.model_assembly.gromet.metadata import (
    # Bibjson,
    # CodeFileReference,
    # EquationDefinition,
    # EquationExtraction,
    # EquationParameter,
    # GrometCreation,
    # LiteralValue,
    # Metadata,
    Provenance,
    # SourceCodeCollection,
    # SourceCodeDataType,
    # SourceCodeLoopInit,
    # SourceCodeLoopUpdate,
    # SourceCodeReference,
    # TextDefinition,
    # TextExtraction,
    # TextParameter,
    TextualDocumentCollection,
    TextualDocumentReference,
)

from automates.program_analysis.JSON2GroMEt.json2gromet import json_to_gromet
from automates.utils.fold import dictionary_to_gromet_json, del_nulls

import os
import pprint


# NOTE: Update ROOT_ASKEM_DATA path to local version
ROOT_ASKEM_DATA = '/Users/claytonm/My Drive/ASKEM-SKEMA/data'

ROOT_CHIME_SIR_GROMET = \
    os.path.join(ROOT_ASKEM_DATA,
                 'epidemiology/CHIME/CHIME_SIR_model/gromet/FN_0.1.2')

PATH_CHIME_SIR_GROMET = \
    os.path.join(ROOT_CHIME_SIR_GROMET,
                 'CHIME_SIR_while_loop--Gromet-FN-auto.json')

PATH_CHIME_SIR_GROMET_V2 = \
    os.path.join(ROOT_CHIME_SIR_GROMET,
                 'CHIME_SIR_while_loop--Gromet-FN-auto_v2.json')

PATH_CHIME_SIR_GROMET_MLINK = \
    os.path.join(ROOT_CHIME_SIR_GROMET,
                 'CHIME_SIR_while_loop--Gromet-FN-auto-manual-link.json')

PATH_CHIME_SIR_GROMET_NO_METADATA = \
    os.path.join(ROOT_CHIME_SIR_GROMET,
                 'CHIME_SIR_while--Gromet-FN-auto_no_metadata.json')

ROOT_CHIME_SVIIvR_GROMET = \
    os.path.join(ROOT_ASKEM_DATA,
                 'epidemiology/CHIME/CHIME_SVIIvR_model/gromet/FN_0.1.2/CHIME_SIR_while--Gromet-FN-auto.json')


def generate_textual_document_collection_CHIME_docs():
    # print('\ngenerate_gromet_textual_document_collection(): TextualDocumentCollection')
    tdc = TextualDocumentCollection(
        provenance=Provenance(method="skema_text_reading",
                              timestamp="2022-07-21T11:12:28Z"),
        documents=[
            TextualDocumentReference(
                uid="",
                global_reference_id="askem_8832",
                bibjson={
                    "title": "CHIME: COVID-19 Hospital Impact for Epidemics - Online Documentation",
                    "author": [
                        {"name": "Jason Lubken"},
                        {"name": "Marieke Jackson"},
                        {"name": "Michael Chow"}
                    ],
                    "type": "web_documentation",
                    "website": {
                        "type": "url",
                        "location": "https://code-for-philly.gitbook.io/chime/"
                    },
                    "timestamp": "2021-01-19T21:08",
                    "link": [
                        {"type": "gdrive",
                         "location": "https://drive.google.com/file/d/122LEBSEMF9x-3r3tWbF6YQ9xeV4I_9Eh/view?usp=sharing"
                         }
                    ],
                    "identifier": [
                        {"type": "aske_id", "id": "8467496e-3dfb-4efd-9061-433fef1b92de"}
                    ]
                }
            )
        ]
    )
    return tdc


def add_metadata_CHIME_SIR():
    gromet_fn_module = json_to_gromet(PATH_CHIME_SIR_GROMET)

    # add the textual_document_collection for the CHIME webdoc
    tdc_chime_docs = generate_textual_document_collection_CHIME_docs()
    gromet_fn_module.metadata.append(tdc_chime_docs)

    # pprint.pprint(gromet_fn_module.metadata)
    # print(gromet_fn_module.fn)
    # print(len(gromet_fn_module.attributes))

    # adapted from lines 88-90 in run_ann_cast_pipeline.py
    with open(f"{PATH_CHIME_SIR_GROMET_MLINK}", "w") as f:
        gromet_fn_module_dict = gromet_fn_module.to_dict()
        f.write(dictionary_to_gromet_json(del_nulls(gromet_fn_module_dict)))

    gromet_fn_module_2 = json_to_gromet(PATH_CHIME_SIR_GROMET_MLINK)
    print(gromet_fn_module_2)


def read_write_read():
    gromet_fn_module = json_to_gromet(PATH_CHIME_SIR_GROMET)
    with open(f"{PATH_CHIME_SIR_GROMET_V2}", "w") as f:
        gromet_fn_module_dict = gromet_fn_module.to_dict()
        f.write(dictionary_to_gromet_json(del_nulls(gromet_fn_module_dict)))
    gromet_fn_module_2 = json_to_gromet(PATH_CHIME_SIR_GROMET_V2)
    print(gromet_fn_module_2)


# add_metadata_CHIME_SIR()

read_write_read()
