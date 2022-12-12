# coding: utf-8

"""
    GroMEt Metadata spec

    Grounded Model Exchange (GroMEt) Metadata schema specification  __Using Swagger to Generate Class Structure__  To automatically generate Python or Java models corresponding to this document, you can use [swagger-codegen](https://swagger.io/tools/swagger-codegen/). We can use this to generate client code based off of this spec that will also generate the class structure.  1. Install via the method described for your operating system    [here](https://github.com/swagger-api/swagger-codegen#Prerequisites).    Make sure to install a version after 3.0 that will support openapi 3. 2. Run swagger-codegen with the options in the example below.    The URL references where the yaml for this documentation is stored on    github. Make sure to replace CURRENT_VERSION with the correct version.    (The current version is `0.1.4`.)    To generate Java classes rather, change the `-l python` to `-l java`.    Change the value to the `-o` option to the desired output location.    ```    swagger-codegen generate -l python -o ./client -i https://raw.githubusercontent.com/ml4ai/automates-v2/master/docs/source/gromet_metadata_v{CURRENT_VERSION}.yaml    ``` 3. Once it executes, the client code will be generated at your specified    location.    For python, the classes will be located in    `$OUTPUT_PATH/swagger_client/models/`.    For java, they will be located in    `$OUTPUT_PATH/src/main/java/io/swagger/client/model/`  If generating GroMEt Metadata schema data model classes in SKEMA (AutoMATES), then after generating the above, follow the instructions here: ``` <automates>/automates/model_assembly/gromet/metadata/README.md ```   # noqa: E501

    OpenAPI spec version: 0.1.5
    Contact: claytonm@arizona.edu
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six
from automates.gromet.metadata.metadata import Metadata  # noqa: F401,E501

class ProgramAnalysisRecordBookkeeping(Metadata):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'metadata_type': 'str',
        'type_name': 'str',
        'field_declarations': 'object',
        'method_declarations': 'list[str]'
    }
    if hasattr(Metadata, "swagger_types"):
        swagger_types.update(Metadata.swagger_types)

    attribute_map = {
        'metadata_type': 'metadata_type',
        'type_name': 'type_name',
        'field_declarations': 'field_declarations',
        'method_declarations': 'method_declarations'
    }
    if hasattr(Metadata, "attribute_map"):
        attribute_map.update(Metadata.attribute_map)

    def __init__(self, metadata_type='program_analysis_record_bookkeeping', type_name=None, field_declarations=None, method_declarations=None, *args, **kwargs):  # noqa: E501
        """ProgramAnalysisRecordBookkeeping - a model defined in Swagger"""  # noqa: E501
        self._metadata_type = None
        self._type_name = None
        self._field_declarations = None
        self._method_declarations = None
        self.discriminator = None
        if metadata_type is not None:
            self.metadata_type = metadata_type
        if type_name is not None:
            self.type_name = type_name
        if field_declarations is not None:
            self.field_declarations = field_declarations
        if method_declarations is not None:
            self.method_declarations = method_declarations
        Metadata.__init__(self, *args, **kwargs)

    @property
    def metadata_type(self):
        """Gets the metadata_type of this ProgramAnalysisRecordBookkeeping.  # noqa: E501


        :return: The metadata_type of this ProgramAnalysisRecordBookkeeping.  # noqa: E501
        :rtype: str
        """
        return self._metadata_type

    @metadata_type.setter
    def metadata_type(self, metadata_type):
        """Sets the metadata_type of this ProgramAnalysisRecordBookkeeping.


        :param metadata_type: The metadata_type of this ProgramAnalysisRecordBookkeeping.  # noqa: E501
        :type: str
        """

        self._metadata_type = metadata_type

    @property
    def type_name(self):
        """Gets the type_name of this ProgramAnalysisRecordBookkeeping.  # noqa: E501


        :return: The type_name of this ProgramAnalysisRecordBookkeeping.  # noqa: E501
        :rtype: str
        """
        return self._type_name

    @type_name.setter
    def type_name(self, type_name):
        """Sets the type_name of this ProgramAnalysisRecordBookkeeping.


        :param type_name: The type_name of this ProgramAnalysisRecordBookkeeping.  # noqa: E501
        :type: str
        """

        self._type_name = type_name

    @property
    def field_declarations(self):
        """Gets the field_declarations of this ProgramAnalysisRecordBookkeeping.  # noqa: E501

        dictionary of key=field_name, val=method_name  # noqa: E501

        :return: The field_declarations of this ProgramAnalysisRecordBookkeeping.  # noqa: E501
        :rtype: object
        """
        return self._field_declarations

    @field_declarations.setter
    def field_declarations(self, field_declarations):
        """Sets the field_declarations of this ProgramAnalysisRecordBookkeeping.

        dictionary of key=field_name, val=method_name  # noqa: E501

        :param field_declarations: The field_declarations of this ProgramAnalysisRecordBookkeeping.  # noqa: E501
        :type: object
        """

        self._field_declarations = field_declarations

    @property
    def method_declarations(self):
        """Gets the method_declarations of this ProgramAnalysisRecordBookkeeping.  # noqa: E501

        array of method names associted with a type  # noqa: E501

        :return: The method_declarations of this ProgramAnalysisRecordBookkeeping.  # noqa: E501
        :rtype: list[str]
        """
        return self._method_declarations

    @method_declarations.setter
    def method_declarations(self, method_declarations):
        """Sets the method_declarations of this ProgramAnalysisRecordBookkeeping.

        array of method names associted with a type  # noqa: E501

        :param method_declarations: The method_declarations of this ProgramAnalysisRecordBookkeeping.  # noqa: E501
        :type: list[str]
        """

        self._method_declarations = method_declarations

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(ProgramAnalysisRecordBookkeeping, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, ProgramAnalysisRecordBookkeeping):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
