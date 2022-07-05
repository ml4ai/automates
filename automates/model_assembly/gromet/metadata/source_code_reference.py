# coding: utf-8

"""
    GroMEt Metadata spec

    Grounded Model Exchange (GroMEt) Metadata schema specification  __Using Swagger to Generate Class Structure__  To automatically generate Python or Java models corresponding to this document, you can use [swagger-codegen](https://swagger.io/tools/swagger-codegen/). We can use this to generate client code based off of this spec that will also generate the class structure.  1. Install via the method described for your operating system    [here](https://github.com/swagger-api/swagger-codegen#Prerequisites).    Make sure to install a version after 3.0 that will support openapi 3. 2. Run swagger-codegen with the options in the example below.    The URL references where the yaml for this documentation is stored on    github. Make sure to replace CURRENT_VERSION with the correct version.    To generate Java classes rather, change the `-l python` to `-l java`.    Change the value to the `-o` option to the desired output location.    ```    swagger-codegen generate -l python -o ./client -i https://raw.githubusercontent.com/ml4ai/automates-v2/master/docs/source/gromet_metadata_v{CURRENT_VERSION}.yaml    ``` 3. Once it executes, the client code will be generated at your specified    location.    For python, the classes will be located in    `$OUTPUT_PATH/swagger_client/models/`.    For java, they will be located in    `$OUTPUT_PATH/src/main/java/io/swagger/client/model/`  If generating GroMEt Metadata schema data model classes in SKEMA (AutoMATES), then afer generating the above, follow the instructions here: ``` <automates>/automates/model_assembly/gromet/metadata/README.md ```   # noqa: E501

    OpenAPI spec version: 0.1.0
    Contact: claytonm@email.arizona.edu
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six
import Metadata  # noqa: F401,E501

class SourceCodeReference(Metadata):
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
        'code_file_reference_uid': 'str',
        'line_begin': 'int',
        'line_end': 'int',
        'col_begin': 'int',
        'col_end': 'int'
    }
    if hasattr(Metadata, "swagger_types"):
        swagger_types.update(Metadata.swagger_types)

    attribute_map = {
        'metadata_type': 'metadata_type',
        'code_file_reference_uid': 'code_file_reference_uid',
        'line_begin': 'line_begin',
        'line_end': 'line_end',
        'col_begin': 'col_begin',
        'col_end': 'col_end'
    }
    if hasattr(Metadata, "attribute_map"):
        attribute_map.update(Metadata.attribute_map)

    def __init__(self, metadata_type='source_code_reference', code_file_reference_uid=None, line_begin=None, line_end=None, col_begin=None, col_end=None, *args, **kwargs):  # noqa: E501
        """SourceCodeReference - a model defined in Swagger"""  # noqa: E501
        self._metadata_type = None
        self._code_file_reference_uid = None
        self._line_begin = None
        self._line_end = None
        self._col_begin = None
        self._col_end = None
        self.discriminator = None
        if metadata_type is not None:
            self.metadata_type = metadata_type
        self.code_file_reference_uid = code_file_reference_uid
        self.line_begin = line_begin
        if line_end is not None:
            self.line_end = line_end
        if col_begin is not None:
            self.col_begin = col_begin
        if col_end is not None:
            self.col_end = col_end
        Metadata.__init__(self, *args, **kwargs)

    @property
    def metadata_type(self):
        """Gets the metadata_type of this SourceCodeReference.  # noqa: E501


        :return: The metadata_type of this SourceCodeReference.  # noqa: E501
        :rtype: str
        """
        return self._metadata_type

    @metadata_type.setter
    def metadata_type(self, metadata_type):
        """Sets the metadata_type of this SourceCodeReference.


        :param metadata_type: The metadata_type of this SourceCodeReference.  # noqa: E501
        :type: str
        """

        self._metadata_type = metadata_type

    @property
    def code_file_reference_uid(self):
        """Gets the code_file_reference_uid of this SourceCodeReference.  # noqa: E501

        uid for the source code file CodeFileReference  # noqa: E501

        :return: The code_file_reference_uid of this SourceCodeReference.  # noqa: E501
        :rtype: str
        """
        return self._code_file_reference_uid

    @code_file_reference_uid.setter
    def code_file_reference_uid(self, code_file_reference_uid):
        """Sets the code_file_reference_uid of this SourceCodeReference.

        uid for the source code file CodeFileReference  # noqa: E501

        :param code_file_reference_uid: The code_file_reference_uid of this SourceCodeReference.  # noqa: E501
        :type: str
        """
        if code_file_reference_uid is None:
            raise ValueError("Invalid value for `code_file_reference_uid`, must not be `None`")  # noqa: E501

        self._code_file_reference_uid = code_file_reference_uid

    @property
    def line_begin(self):
        """Gets the line_begin of this SourceCodeReference.  # noqa: E501

        The line number where the identifier name string occurs  # noqa: E501

        :return: The line_begin of this SourceCodeReference.  # noqa: E501
        :rtype: int
        """
        return self._line_begin

    @line_begin.setter
    def line_begin(self, line_begin):
        """Sets the line_begin of this SourceCodeReference.

        The line number where the identifier name string occurs  # noqa: E501

        :param line_begin: The line_begin of this SourceCodeReference.  # noqa: E501
        :type: int
        """
        if line_begin is None:
            raise ValueError("Invalid value for `line_begin`, must not be `None`")  # noqa: E501

        self._line_begin = line_begin

    @property
    def line_end(self):
        """Gets the line_end of this SourceCodeReference.  # noqa: E501

        The line number where the identifier name string occurs  # noqa: E501

        :return: The line_end of this SourceCodeReference.  # noqa: E501
        :rtype: int
        """
        return self._line_end

    @line_end.setter
    def line_end(self, line_end):
        """Sets the line_end of this SourceCodeReference.

        The line number where the identifier name string occurs  # noqa: E501

        :param line_end: The line_end of this SourceCodeReference.  # noqa: E501
        :type: int
        """

        self._line_end = line_end

    @property
    def col_begin(self):
        """Gets the col_begin of this SourceCodeReference.  # noqa: E501

        The start column of the identifier name string instance  # noqa: E501

        :return: The col_begin of this SourceCodeReference.  # noqa: E501
        :rtype: int
        """
        return self._col_begin

    @col_begin.setter
    def col_begin(self, col_begin):
        """Sets the col_begin of this SourceCodeReference.

        The start column of the identifier name string instance  # noqa: E501

        :param col_begin: The col_begin of this SourceCodeReference.  # noqa: E501
        :type: int
        """

        self._col_begin = col_begin

    @property
    def col_end(self):
        """Gets the col_end of this SourceCodeReference.  # noqa: E501

        The end column of the identifier name string instance  # noqa: E501

        :return: The col_end of this SourceCodeReference.  # noqa: E501
        :rtype: int
        """
        return self._col_end

    @col_end.setter
    def col_end(self, col_end):
        """Sets the col_end of this SourceCodeReference.

        The end column of the identifier name string instance  # noqa: E501

        :param col_end: The col_end of this SourceCodeReference.  # noqa: E501
        :type: int
        """

        self._col_end = col_end

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
        if issubclass(SourceCodeReference, dict):
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
        if not isinstance(other, SourceCodeReference):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
