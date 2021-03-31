from __future__ import annotations
from abc import ABC
from enum import Enum, auto, unique
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, List, Union, Callable, Type
from time import time

from .structures import MeasurementType, DataType

CategoricalTypes = Union[bool, str, int]
NumericalTypes = Union[int, float]


@unique
class MetadataType(Enum):
    NONE = auto()
    GRFN_CREATION = auto()
    EQUATION_EXTRACTION = auto()
    TEXT_EXTRACTION = auto()
    CODE_SPAN_REFERENCE = auto()
    CODE_COLLECTION_REFERENCE = auto()
    DOMAIN = auto()

    def __str__(self):
        return str(self.name).lower()

    @classmethod
    def from_str(cls, data: str):
        return getattr(MetadataType, data.upper())


@unique
class MetadataMethod(Enum):
    NONE = auto()
    TEXT_READING_PIPELINE = auto()
    EQUATION_READING_PIPELINE = auto()
    PROGRAM_ANALYSIS_PIPELINE = auto()
    CODE_ROLE_ASSIGNMENT = auto()

    def __str__(self):
        return str(self.name).lower()

    @classmethod
    def from_str(cls, data: str):
        return getattr(MetadataMethod, data.upper())


@unique
class SuperSet(Enum):
    ALL_BOOLS = auto()
    ALL_STRS = auto()

    def __str__(self):
        return str(self.name)

    @classmethod
    def from_data_type(cls, dtype: DataType):
        if dtype == DataType.BOOLEAN:
            return cls.ALL_BOOLS
        elif dtype == DataType.STRING:
            return cls.ALL_STRS
        else:
            raise ValueError(f"No implemented superset for type: {dtype}")

    @classmethod
    def ismember(cls, item: DataType, sset: SuperSet) -> bool:
        if sset == cls.ALL_BOOLS:
            return isinstance(item, DataType.BOOLEAN)
        elif sset == cls.ALL_STRS:
            return isinstance(item, DataType.STRING)
        else:
            raise TypeError(f"Unrecognized SuperSet type: {sset}")


class BaseMetadata(ABC):
    def to_dict(self) -> str:
        """Returns the contents of this metadata object as a JSON string."""
        return asdict(self)


@dataclass
class ProvenanceData(BaseMetadata):
    method: MetadataMethod
    timestamp: datetime

    @staticmethod
    def get_dt_timestamp() -> datetime:
        """Returns an datetime timestamp."""
        return datetime.fromtimestamp(time.time())


@dataclass
class TypedMetadata(BaseMetadata):
    type: MetadataType
    provenance: ProvenanceData

    @classmethod
    def from_dict(cls, data: dict) -> TypedMetadata:
        m_type = MetadataType.from_str(data["type"])
        if mdata_type == ""


@dataclass
class CodeSpan(BaseMetadata):
    line_begin: int
    line_end: int
    col_begin: int
    col_end: int


@dataclass
class CodeFileReference(BaseMetadata):
    uid: str
    name: str
    path: str


@dataclass
class DomainInterval(BaseMetadata):
    l_bound: NumericalTypes
    u_bound: NumericalTypes
    l_inclusive: bool
    u_inclusive: bool


@dataclass
class DomainSet(BaseMetadata):
    element_type: DataType
    superset: SuperSet
    predicate: Callable[[CategoricalTypes], bool]


DomainElement = Union[DomainInterval, DomainSet]


@dataclass
class CodeSpanReference(TypedMetadata):
    code_type: str
    code_file_reference_uid: str
    code_span: CodeSpan


@dataclass
class GrFNCreation(TypedMetadata):
    name: str


@dataclass
class CodeCollectionReference(TypedMetadata):
    global_reference_uid: str
    files: List[CodeFileReference]


# @dataclass
# class MeasurementType(TypedMetadata):
#     data_type: MeasurementType


# @dataclass
# class MeasurementScale(TypedMetadata):
#     measurement_scale: str


@dataclass
class Domain(TypedMetadata):
    data_type: DataType
    measurement_scale: MeasurementType
    elements: List[DomainElement]
