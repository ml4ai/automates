# coding: utf-8

"""
    GroMEt Metadata spec

    Grounded Model Exchange (GroMEt) Metadata schema specification  __Using Swagger to Generate Class Structure__  To automatically generate Python or Java models corresponding to this document, you can use [swagger-codegen](https://swagger.io/tools/swagger-codegen/). We can use this to generate client code based off of this spec that will also generate the class structure.  1. Install via the method described for your operating system    [here](https://github.com/swagger-api/swagger-codegen#Prerequisites).    Make sure to install a version after 3.0 that will support openapi 3. 2. Run swagger-codegen with the options in the example below.    The URL references where the yaml for this documentation is stored on    github. Make sure to replace CURRENT_VERSION with the correct version.    (The current version is `0.1.4`.)    To generate Java classes rather, change the `-l python` to `-l java`.    Change the value to the `-o` option to the desired output location.    ```    swagger-codegen generate -l python -o ./client -i https://raw.githubusercontent.com/ml4ai/automates-v2/master/docs/source/gromet_metadata_v{CURRENT_VERSION}.yaml    ``` 3. Once it executes, the client code will be generated at your specified    location.    For python, the classes will be located in    `$OUTPUT_PATH/swagger_client/models/`.    For java, they will be located in    `$OUTPUT_PATH/src/main/java/io/swagger/client/model/`  If generating GroMEt Metadata schema data model classes in SKEMA (AutoMATES), then afer generating the above, follow the instructions here: ``` <automates>/automates/model_assembly/gromet/metadata/README.md ```   # noqa: E501

    OpenAPI spec version: 0.1.5
    Contact: claytonm@email.arizona.edu
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six
from automates.gromet.metadata.metadata import Metadata  # noqa: F401,E501

class SourceCodeCollection(Metadata):
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
        'name': 'str',
        'global_reference_id': 'str',
        'files': 'list[CodeFileReference]'
    }
    if hasattr(Metadata, "swagger_types"):
        swagger_types.update(Metadata.swagger_types)

    attribute_map = {
        'metadata_type': 'metadata_type',
        'name': 'name',
        'global_reference_id': 'global_reference_id',
        'files': 'files'
    }
    if hasattr(Metadata, "attribute_map"):
        attribute_map.update(Metadata.attribute_map)

    def __init__(self, metadata_type='source_code_collection', name=None, global_reference_id=None, files=None, *args, **kwargs):  # noqa: E501
        """SourceCodeCollection - a model defined in Swagger"""  # noqa: E501
        self._metadata_type = None
        self._name = None
        self._global_reference_id = None
        self._files = None
        self.discriminator = None
        if metadata_type is not None:
            self.metadata_type = metadata_type
        if name is not None:
            self.name = name
        if global_reference_id is not None:
            self.global_reference_id = global_reference_id
        if files is not None:
            self.files = files
        Metadata.__init__(self, *args, **kwargs)

    @property
    def metadata_type(self):
        """Gets the metadata_type of this SourceCodeCollection.  # noqa: E501


        :return: The metadata_type of this SourceCodeCollection.  # noqa: E501
        :rtype: str
        """
        return self._metadata_type

    @metadata_type.setter
    def metadata_type(self, metadata_type):
        """Sets the metadata_type of this SourceCodeCollection.


        :param metadata_type: The metadata_type of this SourceCodeCollection.  # noqa: E501
        :type: str
        """

        self._metadata_type = metadata_type

    @property
    def name(self):
        """Gets the name of this SourceCodeCollection.  # noqa: E501

        Code Collection name  # noqa: E501

        :return: The name of this SourceCodeCollection.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this SourceCodeCollection.

        Code Collection name  # noqa: E501

        :param name: The name of this SourceCodeCollection.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def global_reference_id(self):
        """Gets the global_reference_id of this SourceCodeCollection.  # noqa: E501

        URL (e.g., GitHub url), or aske_id   # noqa: E501

        :return: The global_reference_id of this SourceCodeCollection.  # noqa: E501
        :rtype: str
        """
        return self._global_reference_id

    @global_reference_id.setter
    def global_reference_id(self, global_reference_id):
        """Sets the global_reference_id of this SourceCodeCollection.

        URL (e.g., GitHub url), or aske_id   # noqa: E501

        :param global_reference_id: The global_reference_id of this SourceCodeCollection.  # noqa: E501
        :type: str
        """

        self._global_reference_id = global_reference_id

    @property
    def files(self):
        """Gets the files of this SourceCodeCollection.  # noqa: E501


        :return: The files of this SourceCodeCollection.  # noqa: E501
        :rtype: list[CodeFileReference]
        """
        return self._files

    @files.setter
    def files(self, files):
        """Sets the files of this SourceCodeCollection.


        :param files: The files of this SourceCodeCollection.  # noqa: E501
        :type: list[CodeFileReference]
        """

        self._files = files

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
        if issubclass(SourceCodeCollection, dict):
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
        if not isinstance(other, SourceCodeCollection):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
