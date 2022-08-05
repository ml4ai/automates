# coding: utf-8

# flake8: noqa
"""
    Grounded Model Exchange (GroMEt) schema for Function Networks

    This document defines the GroMEt Function Network data model. Note that Metadata is defined in separate spec.  __Using Swagger to Generate Class Structure__  To automatically generate Python or Java models corresponding to this document, you can use [swagger-codegen](https://swagger.io/tools/swagger-codegen/). This can be used to generate the client code based off of this spec, and in the process this will generate the data model class structure.  1. Install via the method described for your operating system    [here](https://github.com/swagger-api/swagger-codegen#Prerequisites).    Make sure to install a version after 3.0 that will support openapi 3. 2. Run swagger-codegen with the options in the example below.    The URL references where the yaml for this documentation is stored on    github. Make sure to replace CURRENT_VERSION with the correct version.    To generate Java classes rather, change the `-l python` to `-l java`.    Change the value to the `-o` option to the desired output location.    ```    swagger-codegen generate -l python -o ./client -i https://raw.githubusercontent.com/ml4ai/automates-v2/master/docs/source/gromet_FN_v{CURRENT_VERSION}.yaml    ``` 3. Once it executes, the client code will be generated at your specified    location.    For python, the classes will be located in    `$OUTPUT_PATH/swagger_client/models/`.    For java, they will be located in    `$OUTPUT_PATH/src/main/java/io/swagger/client/model/`  If generating GroMEt schema data model classes in SKEMA (AutoMATES), then afer generating the above, follow the instructions here: ``` <automates>/automates/model_assembly/gromet/model/README.md ```   # noqa: E501

    OpenAPI spec version: 0.1.2
    Contact: claytonm@arizona.edu
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

# import models into model package
from automates.model_assembly.gromet.model.function_type import FunctionType
from automates.model_assembly.gromet.model.gromet_box import GrometBox
from automates.model_assembly.gromet.model.gromet_box_conditional import GrometBoxConditional
from automates.model_assembly.gromet.model.gromet_box_function import GrometBoxFunction
from automates.model_assembly.gromet.model.gromet_box_loop import GrometBoxLoop
from automates.model_assembly.gromet.model.gromet_fn import GrometFN
from automates.model_assembly.gromet.model.gromet_fn_module import GrometFNModule
from automates.model_assembly.gromet.model.gromet_port import GrometPort
from automates.model_assembly.gromet.model.gromet_type import GrometType
from automates.model_assembly.gromet.model.gromet_wire import GrometWire
from automates.model_assembly.gromet.model.import_reference import ImportReference
from automates.model_assembly.gromet.model.import_type import ImportType
from automates.model_assembly.gromet.model.literal_value import LiteralValue
# from automates.model_assembly.gromet.model.metadata import Metadata
from automates.model_assembly.gromet.model.source_type import SourceType
from automates.model_assembly.gromet.model.typed_value import TypedValue
