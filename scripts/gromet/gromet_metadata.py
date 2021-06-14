from typing import NewType, Union, List
from abc import ABC
from dataclasses import dataclass, field


# =============================================================================
# Uid
# =============================================================================

UidMetadatum = NewType('UidMetadatum', str)
UidDocumentReference = NewType('UidDocumentReference', str)

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
    """
    uid: UidDocumentReference
    global_reference_id: GlobalReferenceId
    cosmos_id: str  # ID of COSMOS component used to process document.
    cosmos_version_number: str  # Version number of COSMOS component.
    automates_id: str  # ID of AutoMATES component used to process document.
    automates_version_number: str  # Version number of AutoMATES component.
    bibjson: Bibjson


@dataclass
class TextualDocumentReferenceSet(Metadatum):
    """
    host: <gromet>
    A collection of references to textual documents
    (e.g., software documentation, scientific publications, etc.).
    """
    documents: List[TextualDocumentReference]


# =============================================================================
# CHANGE LOG
# =============================================================================

"""
Changes 2021-06-13:
() Started migration of GrFN metadata types to GroMEt metadatum types.
    () <Gromet>.TextualDocumentReferenceSet
    () 
"""
