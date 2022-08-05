from automates.model_assembly.gromet.metadata import (
    # Bibjson,
    # CodeFileReference,
    # EquationDefinition,
    # EquationExtraction,
    # EquationParameter,
    # GrometCreation,
    # LiteralValue,
    # Metadata,
    # Provenance,
    # SourceCodeCollection,
    # SourceCodeDataType,
    # SourceCodeLoopInit,
    # SourceCodeLoopUpdate,
    # SourceCodeReference,
    # TextDefinition,
    # TextExtraction,
    # TextParameter,
    TextualDocumentCollection,
    # TextualDocumentReference,
)

import os
from automates.program_analysis.JSON2GroMEt.json2gromet import JsonToGromet


# NOTE: Update ROOT_ASKEM_DATA path to local version
ROOT_ASKEM_DATA = '/Users/claytonm/My Drive/ASKEM-SKEMA/data'
ROOT_CHIME_SIR_GROMET = \
    os.path.join(ROOT_ASKEM_DATA,
                 'epidemiology/CHIME/CHIME_SIR_model/gromet/FN_0.1.2/CHIME_SIR_while--Gromet-FN-auto.json')


def add_metadata():
    gromet = JsonToGromet(ROOT_CHIME_SIR_GROMET)
    dir(gromet)


add_metadata()
