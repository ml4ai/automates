# coding: utf-8

# flake8: noqa
"""
    GroMEt Metadata spec

    Grounded Model Exchange (GroMEt) Metadata schema specification  __Using Swagger to Generate Class Structure__  To automatically generate Python or Java models corresponding to this document, you can use [swagger-codegen](https://swagger.io/tools/swagger-codegen/). We can use this to generate client code based off of this spec that will also generate the class structure.  1. Install via the method described for your operating system    [here](https://github.com/swagger-api/swagger-codegen#Prerequisites).    Make sure to install a version after 3.0 that will support openapi 3. 2. Run swagger-codegen with the options in the example below.    The URL references where the yaml for this documentation is stored on    github. Make sure to replace CURRENT_VERSION with the correct version.    (The current version is `0.1.4`.)    To generate Java classes rather, change the `-l python` to `-l java`.    Change the value to the `-o` option to the desired output location.    ```    swagger-codegen generate -l python -o ./client -i https://raw.githubusercontent.com/ml4ai/automates-v2/master/docs/source/gromet_metadata_v{CURRENT_VERSION}.yaml    ``` 3. Once it executes, the client code will be generated at your specified    location.    For python, the classes will be located in    `$OUTPUT_PATH/swagger_client/models/`.    For java, they will be located in    `$OUTPUT_PATH/src/main/java/io/swagger/client/model/`  If generating GroMEt Metadata schema data model classes in SKEMA (AutoMATES), then after generating the above, follow the instructions here: ``` <automates>/automates/model_assembly/gromet/metadata/README.md ```   # noqa: E501

    OpenAPI spec version: 0.1.5
    Contact: claytonm@arizona.edu
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

# import models into model package
from automates.gromet.metadata.bibjson import Bibjson
from automates.gromet.metadata.code_file_reference import CodeFileReference
from automates.gromet.metadata.equation_definition import EquationDefinition
from automates.gromet.metadata.equation_extraction import EquationExtraction
from automates.gromet.metadata.equation_literal_value import EquationLiteralValue
from automates.gromet.metadata.gromet_creation import GrometCreation
from automates.gromet.metadata.literal_value import LiteralValue
from automates.gromet.metadata.metadata import Metadata
from automates.gromet.metadata.program_analysis_record_bookkeeping import ProgramAnalysisRecordBookkeeping
from automates.gromet.metadata.provenance import Provenance
from automates.gromet.metadata.source_code_collection import SourceCodeCollection
from automates.gromet.metadata.source_code_comment import SourceCodeComment
from automates.gromet.metadata.source_code_data_type import SourceCodeDataType
from automates.gromet.metadata.source_code_loop_init import SourceCodeLoopInit
from automates.gromet.metadata.source_code_loop_update import SourceCodeLoopUpdate
from automates.gromet.metadata.source_code_port_default_val import SourceCodePortDefaultVal
from automates.gromet.metadata.source_code_port_keyword_arg import SourceCodePortKeywordArg
from automates.gromet.metadata.source_code_reference import SourceCodeReference
from automates.gromet.metadata.text_description import TextDescription
from automates.gromet.metadata.text_extraction import TextExtraction
from automates.gromet.metadata.text_extraction_metadata import TextExtractionMetadata
from automates.gromet.metadata.text_grounding import TextGrounding
from automates.gromet.metadata.text_literal_value import TextLiteralValue
from automates.gromet.metadata.text_units import TextUnits
from automates.gromet.metadata.textual_document_collection import TextualDocumentCollection
from automates.gromet.metadata.textual_document_reference import TextualDocumentReference
