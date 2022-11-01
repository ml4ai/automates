# coding: utf-8

"""
    Grounded Model Exchange (GroMEt) schema for Function Networks

    This document defines the GroMEt Function Network data model. Note that Metadata is defined in separate spec.  __Using Swagger to Generate Class Structure__  To automatically generate Python or Java models corresponding to this document, you can use [swagger-codegen](https://swagger.io/tools/swagger-codegen/). This can be used to generate the client code based off of this spec, and in the process this will generate the data model class structure.  1. Install via the method described for your operating system    [here](https://github.com/swagger-api/swagger-codegen#Prerequisites).    Make sure to install a version after 3.0 that will support openapi 3. 2. Run swagger-codegen with the options in the example below.    The URL references where the yaml for this documentation is stored on    github. Make sure to replace CURRENT_VERSION with the correct version.    (The current version is `0.1.4`.)    To generate Java classes rather, change the `-l python` to `-l java`.    Change the value to the `-o` option to the desired output location.    ```    swagger-codegen generate -l python -o ./client -i https://raw.githubusercontent.com/ml4ai/automates-v2/master/docs/source/gromet_FN_v{CURRENT_VERSION}.yaml    ``` 3. Once it executes, the client code will be generated at your specified    location.    For python, the classes will be located in    `$OUTPUT_PATH/swagger_client/models/`.    For java, they will be located in    `$OUTPUT_PATH/src/main/java/io/swagger/client/model/`  If generating GroMEt schema data model classes in SKEMA (AutoMATES), then afer generating the above, follow the instructions here: ``` <automates>/automates/model_assembly/gromet/model/README.md ```   # noqa: E501

    OpenAPI spec version: 0.1.5
    Contact: claytonm@arizona.edu
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six
from automates.gromet.fn.gromet_object import GrometObject  # noqa: F401,E501

class GrometPort(GrometObject):
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
        'id': 'int',
        'name': 'str',
        'box': 'int'
    }
    if hasattr(GrometObject, "swagger_types"):
        swagger_types.update(GrometObject.swagger_types)

    attribute_map = {
        'id': 'id',
        'name': 'name',
        'box': 'box'
    }
    if hasattr(GrometObject, "attribute_map"):
        attribute_map.update(GrometObject.attribute_map)

    def __init__(self, id=None, name=None, box=None, *args, **kwargs):  # noqa: E501
        """GrometPort - a model defined in Swagger"""  # noqa: E501
        self._id = None
        self._name = None
        self._box = None
        self.discriminator = None
        if id is not None:
            self.id = id
        if name is not None:
            self.name = name
        if box is not None:
            self.box = box
        GrometObject.__init__(self, *args, **kwargs)

    @property
    def id(self):
        """Gets the id of this GrometPort.  # noqa: E501

        The Port id is a natural number that represent the order of the Port on the Box. This enables the following: (1) BoxFunctions with FN context will be able to unambiguously match the \"calling\" BoxFunction Port Inputs (pif) (and Port Outputs, pof) to their corresonding Outer Port Inputs (opi) (and Outer Port Outputs, opo) based in the ordering of the ids of each Port. (2) Loop Port Input (pil) id ordering will match the Loop Port Output (pol) as well as the ordering of the Port Inputs and Port Outputs of the calling loop body Function.   # noqa: E501

        :return: The id of this GrometPort.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this GrometPort.

        The Port id is a natural number that represent the order of the Port on the Box. This enables the following: (1) BoxFunctions with FN context will be able to unambiguously match the \"calling\" BoxFunction Port Inputs (pif) (and Port Outputs, pof) to their corresonding Outer Port Inputs (opi) (and Outer Port Outputs, opo) based in the ordering of the ids of each Port. (2) Loop Port Input (pil) id ordering will match the Loop Port Output (pol) as well as the ordering of the Port Inputs and Port Outputs of the calling loop body Function.   # noqa: E501

        :param id: The id of this GrometPort.  # noqa: E501
        :type: int
        """

        self._id = id

    @property
    def name(self):
        """Gets the name of this GrometPort.  # noqa: E501


        :return: The name of this GrometPort.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this GrometPort.


        :param name: The name of this GrometPort.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def box(self):
        """Gets the box of this GrometPort.  # noqa: E501

        Index to the Box that the Port belongs to.  # noqa: E501

        :return: The box of this GrometPort.  # noqa: E501
        :rtype: int
        """
        return self._box

    @box.setter
    def box(self, box):
        """Sets the box of this GrometPort.

        Index to the Box that the Port belongs to.  # noqa: E501

        :param box: The box of this GrometPort.  # noqa: E501
        :type: int
        """

        self._box = box

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
        if issubclass(GrometPort, dict):
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
        if not isinstance(other, GrometPort):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
