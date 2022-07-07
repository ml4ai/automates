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
from .metadata import Metadata  # noqa: F401,E501

class GrometCreation(Metadata):
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
        'timestamp': 'str'
    }
    if hasattr(Metadata, "swagger_types"):
        swagger_types.update(Metadata.swagger_types)

    attribute_map = {
        'metadata_type': 'metadata_type',
        'timestamp': 'timestamp'
    }
    if hasattr(Metadata, "attribute_map"):
        attribute_map.update(Metadata.attribute_map)

    def __init__(self, metadata_type='gromet_creation', timestamp=None, *args, **kwargs):  # noqa: E501
        """GrometCreation - a model defined in Swagger"""  # noqa: E501
        self._metadata_type = None
        self._timestamp = None
        self.discriminator = None
        if metadata_type is not None:
            self.metadata_type = metadata_type
        self.timestamp = timestamp
        Metadata.__init__(self, *args, **kwargs)

    @property
    def metadata_type(self):
        """Gets the metadata_type of this GrometCreation.  # noqa: E501


        :return: The metadata_type of this GrometCreation.  # noqa: E501
        :rtype: str
        """
        return self._metadata_type

    @metadata_type.setter
    def metadata_type(self, metadata_type):
        """Sets the metadata_type of this GrometCreation.


        :param metadata_type: The metadata_type of this GrometCreation.  # noqa: E501
        :type: str
        """

        self._metadata_type = metadata_type

    @property
    def timestamp(self):
        """Gets the timestamp of this GrometCreation.  # noqa: E501

        Creation timestamp  # noqa: E501

        :return: The timestamp of this GrometCreation.  # noqa: E501
        :rtype: str
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Sets the timestamp of this GrometCreation.

        Creation timestamp  # noqa: E501

        :param timestamp: The timestamp of this GrometCreation.  # noqa: E501
        :type: str
        """
        if timestamp is None:
            raise ValueError("Invalid value for `timestamp`, must not be `None`")  # noqa: E501

        self._timestamp = timestamp

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
        if issubclass(GrometCreation, dict):
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
        if not isinstance(other, GrometCreation):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
