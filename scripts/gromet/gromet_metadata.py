from typing import NewType, Union, List
from abc import ABC
from dataclasses import dataclass, field
import datetime
import pytz


"""
Metadatum types:
(*) <Any>.CodeSpanReference
(*) <Gromet>.ModelInterface  # designates variables, parameters, initial_conditions
(*) <Gromet>.TextualDocumentReferenceSet
(*) <Gromet>.CodeCollectionReference
(*) <Box>.EquationDefinition
(*) <Variable>.TextDefinition
(*) <Variable>.TextParameter
() <Variable>.EquationParameter

INDRA Metadatum types:
() <Junction>.ReactionReference
() <Junction>.IndraAgentReferenceSet
"""


# =============================================================================
# Uid
# =============================================================================

# The following also get defined in gromet.py, which imports this file...
UidVariable = NewType('UidVariable', str)
UidJunction = NewType('UidJunction', str)

UidMetadatum = NewType('UidMetadatum', str)
UidDocumentReference = NewType('UidDocumentReference', str)
UidCodeFileReference = NewType('UidCodeFileReference', str)

# ISO 8601 Extended format: YYYY-MM-DDTHH:mm:ss:ffffff_ZZZ±zzzz
# where
# YYYY : 4-digit year
# MM   : 2-digit month (January is 01, December is 12)
# DD   : 2-digit date (0 to 31)
# -    : Date delimiters
# T    : Indicates the start of time
# HH   : 24-digit hour (0 to 23)
# mm   : Minutes (0 to 59)
# ss   : Seconds (0 to 59)
# ffffff  : Microseconds (0 to 999)
# :    : Time delimiters
# _    : Time zone delimiter
# ZZZ  : Three-letter timezone
# zzzz : 4 number UTC timezone offset
Datetime = NewType('Datetime', str)

TZ_PDT = pytz.timezone('US/Pacific')
TZ_MST = pytz.timezone('US/Arizona')
TZ_MDT = pytz.timezone('US/Mountain')
TZ_CDT = pytz.timezone('US/Central')
TZ_EDT = pytz.timezone('US/Eastern')
# for tz in pytz.common_timezones:
#     print(tz)


# TODO Description of method that produced the metadata
# Some descriptor that enables identifying process by which metadata was created
# There will generally be a set of 1 or more methods that may generate
# each Metadatum type
# For example: AutoMATES program analysis creates code_span metadata.
MetadatumMethod = NewType('MetadatumMethod', str)


# -----------------------------------------------------------------------------

def get_current_datetime(tz=TZ_MST) -> Datetime:
    """
    Utility for getting a GroMEt formatted current datetime string.
    String is in Datetime ISO 8601 Extended format format (see comment above)
        YYYY-MM-DDTHH:mm:ss:ffffff_ZZZ±zzzz
    (helpful resource https://pythonhosted.org/pytz/)
    :tz: Specify pytz timezone
    :return: Datetime
    """
    now = tz.localize(datetime.datetime.now())
    return Datetime(now.strftime("%Y-%m-%dT%H:%M:%S:%f_%Z%z"))


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
      TextualDocumentReference for the document from which this
      text definition was extracted.
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
    file_id: UidCodeFileReference
    line_begin: int
    line_end: Union[int, None]   # None if one one line
    col_begin: Union[int, None]  # None if multi-line
    col_end: Union[int, None]    # None if single char or multi-line


# =============================================================================
# Metadata host: <Gromet>
# metadata associated with a top-level <Gromet> object
# =============================================================================

# -----------------------------------------------------------------------------
# ModelInterface
# -----------------------------------------------------------------------------

@dataclass
class ModelInterface(Metadatum):
    """
    Explicit definition of model interface.
    The interface identifies explicit roles of these variables
    'variables': All model variables (anything that can be measured)
    'parameters': Variables that are generally set to explicit values
        (either by default or in experiment spec).
        Often these remain constant during execution/simultation,
        although they may be updated by the model during
        execution/simulation depending on conditions.
    'initial_conditions': Variables that typically take an initial
        value but then update during execution/simulation
    TODO: will want to later introduce experiment spec concept
            of intervention clamping (keeping parameters/variables
            throughout irrespective of original model variable
            value update structure).
    """
    variables: List[Union[UidVariable, UidJunction]]
    parameters: List[Union[UidVariable, UidJunction]]
    initial_conditions: List[Union[UidVariable, UidJunction]]


# -----------------------------------------------------------------------------
# TextualDocumentReferenceSet
# -----------------------------------------------------------------------------

# GlobalReferenceId: Identifier of source document.
# Rank preference of identifier type:
#  (1) 'DOI' (digital objectd identifier) recognize by COSMOS
#  (2) 'PMID' (Pubmed ID) or other DOI
#  (3) 'aske_id' (ASKE unique identifier)
@dataclass
class GlobalReferenceId:
    type: str
    id: str


@dataclass
class BibjsonAuthor:
    name: str


@dataclass
class Bibjson:
    """
    Placeholder for bibjson JSON object; format described in:
        http://okfnlabs.org/bibjson/
    """
    title: str
    author: List[BibjsonAuthor]
    type: str
    website: dict
    timestamp: str
    file: str
    file_url: str
    identifier: List[dict]


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

# -----------------------------------------------------------------------------
# EquationDefinition
# -----------------------------------------------------------------------------

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

# -----------------------------------------------------------------------------
# TextDefinition
# -----------------------------------------------------------------------------

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


# -----------------------------------------------------------------------------
# TextParameter
# -----------------------------------------------------------------------------

@dataclass
class TextParameter(Metadatum):
    """
    host: <Variable>
    Association of parameter values extracted from text.
    """
    text_extraction: TextExtraction
    variable_identifier: str
    value: str  # eventually Literal?


# -----------------------------------------------------------------------------
# EquationParameter
# -----------------------------------------------------------------------------

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
# Metadata host: <Junction>
# metadata associated with a Junction
# =============================================================================

# -----------------------------------------------------------------------------
# INDRA Metadatums
# -----------------------------------------------------------------------------

@dataclass
class ReactionReference(Metadatum):
    """
    host: <Junction> : PNC Rate
    """
    indra_stmt_hash: str
    reaction_rule: str
    is_reverse: bool


IndraAgent = NewType('IndraAgent', dict)


@dataclass
class IndraAgentReferenceSet(Metadatum):
    """
    host: <Junction> : PNC State
    """
    indra_agent_references: List[IndraAgent]


# =============================================================================
# =============================================================================
# CHANGE LOG
# =============================================================================
# =============================================================================

"""
Changes 2021-06-10:
() Started migration of GrFN metadata types to GroMEt metadatum types.
"""
