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

class TextualDocumentReference(object):
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
        'uid': 'str',
        'global_reference_id': 'str',
        'cosmos_id': 'str',
        'cosmos_version_number': 'str',
        'skema_id': 'str',
        'skema_version_number': 'str',
        'bibjson': 'Bibjson'
    }

    attribute_map = {
        'uid': 'uid',
        'global_reference_id': 'global_reference_id',
        'cosmos_id': 'cosmos_id',
        'cosmos_version_number': 'cosmos_version_number',
        'skema_id': 'skema_id',
        'skema_version_number': 'skema_version_number',
        'bibjson': 'bibjson'
    }

    def __init__(self, uid=None, global_reference_id=None, cosmos_id=None, cosmos_version_number=None, skema_id=None, skema_version_number=None, bibjson=None):  # noqa: E501
        """TextualDocumentReference - a model defined in Swagger"""  # noqa: E501
        self._uid = None
        self._global_reference_id = None
        self._cosmos_id = None
        self._cosmos_version_number = None
        self._skema_id = None
        self._skema_version_number = None
        self._bibjson = None
        self.discriminator = None
        self.uid = uid
        self.global_reference_id = global_reference_id
        if cosmos_id is not None:
            self.cosmos_id = cosmos_id
        if cosmos_version_number is not None:
            self.cosmos_version_number = cosmos_version_number
        if skema_id is not None:
            self.skema_id = skema_id
        if skema_version_number is not None:
            self.skema_version_number = skema_version_number
        if bibjson is not None:
            self.bibjson = bibjson

    @property
    def uid(self):
        """Gets the uid of this TextualDocumentReference.  # noqa: E501

        Unique identifier of the DocumentReference  # noqa: E501

        :return: The uid of this TextualDocumentReference.  # noqa: E501
        :rtype: str
        """
        return self._uid

    @uid.setter
    def uid(self, uid):
        """Sets the uid of this TextualDocumentReference.

        Unique identifier of the DocumentReference  # noqa: E501

        :param uid: The uid of this TextualDocumentReference.  # noqa: E501
        :type: str
        """
        if uid is None:
            raise ValueError("Invalid value for `uid`, must not be `None`")  # noqa: E501

        self._uid = uid

    @property
    def global_reference_id(self):
        """Gets the global_reference_id of this TextualDocumentReference.  # noqa: E501

        Identifier of source document.<br> Rank preference of identifier type:<br> (1) DOI (digital object identifier) recognized by COSMOS<br> (2) PMID (Pubmed ID) or other DOI<br> (3) aske_id (ASKE unique identifier)   # noqa: E501

        :return: The global_reference_id of this TextualDocumentReference.  # noqa: E501
        :rtype: str
        """
        return self._global_reference_id

    @global_reference_id.setter
    def global_reference_id(self, global_reference_id):
        """Sets the global_reference_id of this TextualDocumentReference.

        Identifier of source document.<br> Rank preference of identifier type:<br> (1) DOI (digital object identifier) recognized by COSMOS<br> (2) PMID (Pubmed ID) or other DOI<br> (3) aske_id (ASKE unique identifier)   # noqa: E501

        :param global_reference_id: The global_reference_id of this TextualDocumentReference.  # noqa: E501
        :type: str
        """
        if global_reference_id is None:
            raise ValueError("Invalid value for `global_reference_id`, must not be `None`")  # noqa: E501

        self._global_reference_id = global_reference_id

    @property
    def cosmos_id(self):
        """Gets the cosmos_id of this TextualDocumentReference.  # noqa: E501

        ID of COSMOS component used to process document.  # noqa: E501

        :return: The cosmos_id of this TextualDocumentReference.  # noqa: E501
        :rtype: str
        """
        return self._cosmos_id

    @cosmos_id.setter
    def cosmos_id(self, cosmos_id):
        """Sets the cosmos_id of this TextualDocumentReference.

        ID of COSMOS component used to process document.  # noqa: E501

        :param cosmos_id: The cosmos_id of this TextualDocumentReference.  # noqa: E501
        :type: str
        """

        self._cosmos_id = cosmos_id

    @property
    def cosmos_version_number(self):
        """Gets the cosmos_version_number of this TextualDocumentReference.  # noqa: E501

        Version number of COSMOS component.  # noqa: E501

        :return: The cosmos_version_number of this TextualDocumentReference.  # noqa: E501
        :rtype: str
        """
        return self._cosmos_version_number

    @cosmos_version_number.setter
    def cosmos_version_number(self, cosmos_version_number):
        """Sets the cosmos_version_number of this TextualDocumentReference.

        Version number of COSMOS component.  # noqa: E501

        :param cosmos_version_number: The cosmos_version_number of this TextualDocumentReference.  # noqa: E501
        :type: str
        """

        self._cosmos_version_number = cosmos_version_number

    @property
    def skema_id(self):
        """Gets the skema_id of this TextualDocumentReference.  # noqa: E501

        ID of SKEMA component used to process document.  # noqa: E501

        :return: The skema_id of this TextualDocumentReference.  # noqa: E501
        :rtype: str
        """
        return self._skema_id

    @skema_id.setter
    def skema_id(self, skema_id):
        """Sets the skema_id of this TextualDocumentReference.

        ID of SKEMA component used to process document.  # noqa: E501

        :param skema_id: The skema_id of this TextualDocumentReference.  # noqa: E501
        :type: str
        """

        self._skema_id = skema_id

    @property
    def skema_version_number(self):
        """Gets the skema_version_number of this TextualDocumentReference.  # noqa: E501

        Version number of SKEMA component.  # noqa: E501

        :return: The skema_version_number of this TextualDocumentReference.  # noqa: E501
        :rtype: str
        """
        return self._skema_version_number

    @skema_version_number.setter
    def skema_version_number(self, skema_version_number):
        """Sets the skema_version_number of this TextualDocumentReference.

        Version number of SKEMA component.  # noqa: E501

        :param skema_version_number: The skema_version_number of this TextualDocumentReference.  # noqa: E501
        :type: str
        """

        self._skema_version_number = skema_version_number

    @property
    def bibjson(self):
        """Gets the bibjson of this TextualDocumentReference.  # noqa: E501


        :return: The bibjson of this TextualDocumentReference.  # noqa: E501
        :rtype: Bibjson
        """
        return self._bibjson

    @bibjson.setter
    def bibjson(self, bibjson):
        """Sets the bibjson of this TextualDocumentReference.


        :param bibjson: The bibjson of this TextualDocumentReference.  # noqa: E501
        :type: Bibjson
        """

        self._bibjson = bibjson

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
        if issubclass(TextualDocumentReference, dict):
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
        if not isinstance(other, TextualDocumentReference):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
