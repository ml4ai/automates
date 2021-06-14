from typing import NewType, Union, List
from abc import ABC
from dataclasses import dataclass, field


"""
Metadatum types:
() <Any>.CodeSpanReference
() <Gromet>.TextualDocumentReferenceSet
() <Gromet>.CodeCollectionReference
() <Box>.EquationDefinition
() <Variable>.TextDefinition
() <Variable>.TextParameter
() <Variable>.EquationParameter
"""


# =============================================================================
# Uid
# =============================================================================

# This also gets defined in gromet.py, which imports this file...
UidVariable = NewType('UidVariable', str)

UidMetadatum = NewType('UidMetadatum', str)
UidDocumentReference = NewType('UidDocumentReference', str)
UidCodeFileReference = NewType('UidCodeFileReference', str)

# ISO 8601 Extended format: YYYY-MM-DDTHH:mm:ss:sssZ
# where
# YYYY : 4-digit year
# MM   : 2-digit month (January is 01, December is 12)
# DD   : 2-digit date (0 to 31)
# -    : Date delimiters
# T    : Indicates the start of time
# HH   : 24-digit hour (0 to 23)
# mm   : Minutes (0 to 59)
# ss   : Seconds (0 to 59)
# sss  : Milliseconds (0 to 999)
# :    : Time delimiters
# Z    : Indicates UTC time zone -- this will always be present
Datetime = NewType('Datetime', str)

# TODO Description of method that produced the metadata
# Some descriptor that enables identifying process by which metadata was created
# There will generally be a set of 1 or more methods that may generate
# each Metadatum type
# For example: AutoMATES program analysis creates code_span metadata.
MetadatumMethod = NewType('MetadatumMethod', str)


# =============================================================================
# Metadatum
# =============================================================================

@dataclass
class MetadatumElm(ABC):
    """
    Base class for all Gromet Metadatum types.
    Implements __post_init__ that saves syntactic type (syntax)
        as GroMEt element class name.
    """
    metadata_type: str = field(init=False)

    def __post_init__(self):
        self.metadata_type = self.__class__.__name__


@dataclass
class Provenance(MetadatumElm):
    """
    Provenance of metadata
    """
    method: MetadatumMethod
    timestamp: Datetime


@dataclass
class Metadatum(MetadatumElm, ABC):
    """
    Metadatum base.
    """
    uid: UidMetadatum
    provenance: Provenance


# TODO: add Metadatum subtypes
#       Will be based on: https://ml4ai.github.io/automates-v2/grfn_metadata.html


Metadata = NewType('Metadata', Union[List[Metadatum], None])


# =============================================================================
# Metadata components
# =============================================================================

@dataclass
class TextExtraction:
    """
    Text extraction.
    'document_reference_uid' should match the uid of a
      TextualDocumentReference.
    COSMOS within-document reference coordinates to the span of text.
      'block' is found on a 'page'
      'char_begin' and 'char_end' are relative to the 'block'.
    """
    document_reference_uid: UidDocumentReference
    page: int
    block: int
    char_begin: int
    char_end: int


@dataclass
class EquationExtraction:
    """
    'document_reference_uid' should match the uid of a
      TextualDocumentReference.
    'equation_number' is 0-indexed, relative order of equation
      as identified in the document.
    """
    document_reference_uid: UidDocumentReference
    equation_number: int
    equation_source_latex: str  # latex
    equation_source_mml: str    # MathML


@dataclass
class CodeFileReference:
    """
    'name': filename
    'path': Assume starting from root of code collection
    """
    uid: UidCodeFileReference
    name: str
    path: str


# =============================================================================
# Metadata host: <Any>
# metadata that may be associated with any GroMEt element
# =============================================================================

# -----------------------------------------------------------------------------
# CodeSpanReference
# -----------------------------------------------------------------------------

@dataclass
class CodeSpanReference(Metadatum):
    """
    host: <Any>
    Code span references may be associated with any GroMEt object.
    'code_type': One of 'IDENTIFIER', 'CODE_BLOCK'
    code span coordinates are relative to the source file
        (denoted by the file_id)
    """
    code_type: str  # 'IDENTIFIER', 'CODE_BLOCK'
    file_id: CodeFileReference
    line_begin: int
    line_end: int
    col_begin: int
    col_end: int


# =============================================================================
# Metadata host: <Gromet>
# metadata associated with a top-level <Gromet> object
# =============================================================================

# -----------------------------------------------------------------------------
# TextualDocumentReferenceSet
# -----------------------------------------------------------------------------

# GlobalReferenceId: Identifier of source document.
# Rank preference of identifier type:
#  (1) DOI (digital objectd identifier) recognize by COSMOS
#  (2) PMID (Pubmed ID) or other DOI
#  (3) aske_id (ASKE unique identifier)
GlobalReferenceId = NewType('GlobalReferenceId', str)


@dataclass
class Bibjson:
    """
    Placeholder for bibjson JSON object; format described in:
        http://okfnlabs.org/bibjson/
    """
    pass


@dataclass
class TextualDocumentReference:
    """
    Reference to an individual document
    'cosmos_id': ID of COSMOS component used to process document.
    'cosmos_version_number': Version number of COSMOS component.
    'automates_id': ID of AutoMATES component used to process document.
    'automates_version_number': Version number of AutoMATES component.
    """
    uid: UidDocumentReference
    global_reference_id: GlobalReferenceId
    cosmos_id: str
    cosmos_version_number: str
    automates_id: str
    automates_version_number: str
    bibjson: Bibjson


@dataclass
class TextualDocumentReferenceSet(Metadatum):
    """
    host: <Gromet>
    A collection of references to textual documents
    (e.g., software documentation, scientific publications, etc.).
    """
    documents: List[TextualDocumentReference]


# -----------------------------------------------------------------------------
# CodeCollectionReference
# -----------------------------------------------------------------------------

@dataclass
class CodeCollectionReference(Metadatum):
    """
    host: <Gromet>
    Reference to a code collection (i.e., repository)
    """
    global_reference_id: GlobalReferenceId
    file_ids: List[CodeFileReference]


# =============================================================================
# Metadata host: <Box>
# metadata associated with a Box
# =============================================================================

@dataclass
class EquationDefinition(Metadatum):
    """
    host: <Box>
    Association of an equation extraction with a Box
        (e.g., Function, Expression, Relation).
    """
    equation_extraction: EquationExtraction


# =============================================================================
# Metadata host: <Variable>
# metadata associated with a Variable
# =============================================================================

@dataclass
class TextDefinition(Metadatum):
    """
    host: <Variable>
    Association of text definition of host derived from text source.
    'variable_identifier': char/string representation of the variable.
    'variable_definition': text definition of the variable.
    """
    text_extraction: TextExtraction
    variable_identifier: str
    variable_definition: str


@dataclass
class TextParameter(Metadatum):
    """
    host: <Variable>
    Association of parameter values extracted from text.
    """
    variable_identifier: str
    value: str  # eventually Literal?


@dataclass
class EquationParameter(Metadatum):
    """
    host: <Variable>
    Association of parameter value extracted from equation.
    """
    equation_extraction: EquationExtraction
    variable_uid: UidVariable
    value: str  # eventually Literal?


# =============================================================================
# =============================================================================
# CHANGE LOG
# =============================================================================
# =============================================================================

"""
Changes 2021-06-10:
() Started migration of GrFN metadata types to GroMEt metadatum types.
"""
