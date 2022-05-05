from __future__ import annotations
from abc import ABC, abstractclassmethod, abstractmethod
from copy import deepcopy
from enum import Enum, auto, unique
from dataclasses import dataclass
from datetime import datetime
from typing import List, Union, Type, Dict
from time import time

from ..utils.misc import uuid

CategoricalTypes = Union[bool, str, int]
NumericalTypes = Union[int, float]


class MissingEnumError(Exception):
    pass


class AutoMATESBaseEnum(Enum):
    def __str__(self):
        return str(self.name).lower()

    @abstractclassmethod
    def from_str(cls, child_cls: Type, data: str):
        try:
            return getattr(child_cls, data.upper())
        except AttributeError:
            raise MissingEnumError(
                f"No matching value found in {child_cls.__name__} for {data}"
            )


@unique
class MetadataType(AutoMATESBaseEnum):
    NONE = auto()
    GRFN_CREATION = auto()
    EQUATION_EXTRACTION = auto()
    TEXT_EXTRACTION = auto()
    CODE_SPAN_REFERENCE = auto()
    CODE_COLLECTION_REFERENCE = auto()
    DOMAIN = auto()
    FROM_SOURCE = auto()

    @classmethod
    def from_str(cls, data: str):
        return super().from_str(cls, data)

    @classmethod
    def get_metadata_class(cls, mtype: MetadataType) -> TypedMetadata:
        if mtype == cls.GRFN_CREATION:
            return GrFNCreation
        elif mtype == cls.CODE_SPAN_REFERENCE:
            return CodeSpanReference
        elif mtype == cls.CODE_COLLECTION_REFERENCE:
            return CodeCollectionReference
        elif mtype == cls.DOMAIN:
            return Domain
        elif mtype == cls.FROM_SOURCE:
            return VariableFromSource
        else:
            raise MissingEnumError(
                "Unhandled MetadataType to TypedMetadata conversion " + f"for: {mtype}"
            )


@unique
class MetadataMethod(AutoMATESBaseEnum):
    NONE = auto()
    TEXT_READING_PIPELINE = auto()
    EQUATION_READING_PIPELINE = auto()
    PROGRAM_ANALYSIS_PIPELINE = auto()
    MODEL_ASSEMBLY_PIPELINE = auto()
    CODE_ROLE_ASSIGNMENT = auto()

    @classmethod
    def from_str(cls, data: str):
        return super().from_str(cls, data)


@unique
class MeasurementType(AutoMATESBaseEnum):
    # NOTE: Refer to this stats data type blog post:
    # https://towardsdatascience.com/data-types-in-statistics-347e152e8bee

    # NOTE: the ordering of the values below is incredibly important!!
    UNKNOWN = 0  # used for instances where the measurement scale is unknown
    NONE = 1  # Used for undefined variable types
    CATEGORICAL = 2  # Labels used to represent a quality
    BINARY = 3  # Categorical measure with *only two* categories
    NOMINAL = 4  # Categorical measure with *many* categories
    ORDINAL = 5  # Categorical measure with many *ordered* categories
    NUMERICAL = 6  # Numbers used to express a quantity
    DISCRETE = 7  # Numerical measure with *countably infinite* options
    CONTINUOUS = 8  # Numerical measure w/ *uncountably infinite* options
    INTERVAL = 9  # Continuous measure *without* an absolute zero
    RATIO = 10  # Continuous measure *with* an absolute zero

    @classmethod
    def from_name(cls, name: str):
        name = name.lower()
        if name == "float":
            return cls.CONTINUOUS
        elif name == "string":
            return cls.NOMINAL
        elif name == "boolean":
            return cls.BINARY
        elif name == "integer":
            return cls.DISCRETE
        # TODO remove array after updating for2py to use list type
        elif any(name == x for x in ["none", "list", "array", "object"]):
            return cls.NONE
        elif name == "unknown":
            return cls.UNKNOWN
        else:
            raise ValueError(f"MeasurementType unrecognized name: {name}")

    @classmethod
    def from_str(cls, data: str):
        return super().from_str(cls, data)

    @classmethod
    def isa_categorical(cls, item: MeasurementType) -> bool:
        return any(
            [item == x for x in range(cls.CATEGORICAL.value, cls.NUMERICAL.value)]
        )

    @classmethod
    def isa_numerical(cls, item: MeasurementType) -> bool:
        return any([item == x for x in range(cls.NUMERICAL.value, cls.RATIO.value + 1)])


@unique
class LambdaType(AutoMATESBaseEnum):
    ASSIGN = auto()
    LITERAL = auto()
    CONDITION = auto()
    DECISION = auto()
    INTERFACE = auto()
    EXTRACT = auto()
    PACK = auto()
    OPERATOR = auto()
    LOOP_TOP_INTERFACE = auto()

    def __str__(self):
        return str(self.name)

    def shortname(self):
        if (self == LambdaType.LOOP_TOP_INTERFACE):
            return "LTI"
        return self.__str__()[0]

    @classmethod
    def get_lambda_type(cls, type_str: str, num_inputs: int):
        if type_str == "assign":
            if num_inputs == 0:
                return cls.LITERAL
            return cls.ASSIGN
        elif type_str == "condition":
            return cls.CONDITION
        elif type_str == "decision":
            return cls.DECISION
        elif type_str == "interface":
            return cls.INTERFACE
        elif type_str == "pack":
            return cls.PACK
        elif type_str == "extract":
            return cls.EXTRACT
        elif type_str == "loop_top_interface":
            return cls.LOOP_TOP_INTERFACE
        else:
            raise ValueError(f"Unrecognized lambda type name: {type_str}")

    @classmethod
    def from_str(cls, data: str):
        return super().from_str(cls, data)


@unique
class DataType(AutoMATESBaseEnum):
    BOOLEAN = auto()
    STRING = auto()
    INTEGER = auto()
    SHORT = auto()
    LONG = auto()
    FLOAT = auto()
    DOUBLE = auto()
    ARRAY = auto()
    LIST = auto()
    STRUCT = auto()
    UNION = auto()
    OBJECT = auto()
    NONE = auto()
    UNKNOWN = auto()

    @classmethod
    def from_str(cls, data: str):
        return super().from_str(cls, data)


@unique
class CodeSpanType(AutoMATESBaseEnum):
    IDENTIFIER = auto()
    BLOCK = auto()

    @classmethod
    def from_str(cls, data: str):
        return super().from_str(cls, data)


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
    @abstractmethod
    def to_dict(self) -> str:
        """Returns the contents of this metadata object as a JSON string."""
        return NotImplemented


@dataclass
class ProvenanceData(BaseMetadata):
    method: MetadataMethod
    timestamp: datetime

    @staticmethod
    def get_dt_timestamp() -> datetime:
        """Returns an datetime timestamp."""
        return datetime.fromtimestamp(time())

    @classmethod
    def from_data(cls, data: dict) -> ProvenanceData:
        return cls(MetadataMethod.from_str(data["method"]), data["timestamp"])

    def to_dict(self):
        return {"method": str(self.method), "timestamp": str(self.timestamp)}


@dataclass
class TypedMetadata(BaseMetadata):
    type: MetadataType
    provenance: ProvenanceData

    @abstractclassmethod
    def from_data(cls, data):
        data = deepcopy(data)
        mtype = MetadataType.from_str(data["type"])
        provenance = ProvenanceData.from_data(data["provenance"])
        ChildMetadataClass = MetadataType.get_metadata_class(mtype)
        data.update({"type": mtype, "provenance": provenance})
        return ChildMetadataClass.from_data(data)

    def to_dict(self):
        return {
            "type": str(self.type),
            "provenance": self.provenance.to_dict(),
        }


@dataclass
class CodeSpan(BaseMetadata):
    line_begin: int
    line_end: int
    col_begin: int
    col_end: int

    @classmethod
    def from_source_ref(cls, source_ref: Dict[str, int]) -> CodeSpan:
        def get_ref_with_default(ref: str) -> Union[int, None]:
            return source_ref[ref] if ref in source_ref else None

        return cls(
            get_ref_with_default("line_begin"),
            get_ref_with_default("line_end"),
            get_ref_with_default("col_start"),
            get_ref_with_default("col_end"),
        )

    @classmethod
    def from_data(cls, data: dict) -> CodeSpan:
        if data == {} or data is None:
            return None
        else:
            return cls(**data)

    def to_dict(self):
        return {
            "line_begin": self.line_begin,
            "line_end": self.line_end,
            "col_begin": self.col_begin,
            "col_end": self.col_end,
        }


@dataclass
class CodeFileReference(BaseMetadata):
    uid: str
    name: str
    path: str

    @classmethod
    def from_str(cls, filepath: str) -> CodeFileReference:
        split_point = filepath.rfind("/")
        dirpath = filepath[: split_point + 1]
        filename = filepath[split_point + 1 :]
        return cls(str(uuid.uuid4()), filename, dirpath)

    @classmethod
    def from_data(cls, data: dict) -> CodeFileReference:
        return cls(**data)

    def to_dict(self):
        return {"uid": self.uid, "name": self.name, "path": self.path}


@dataclass
class DomainInterval(BaseMetadata):
    l_bound: NumericalTypes
    u_bound: NumericalTypes
    l_inclusive: bool
    u_inclusive: bool

    @classmethod
    def from_data(cls, data: dict) -> DomainInterval:
        return cls(**data)

    def to_dict(self):
        return {
            "l_bound": str(self.l_bound),
            "u_bound": str(self.u_bound),
            "l_inclusive": self.l_inclusive,
            "u_inclusive": self.u_inclusive,
        }


@dataclass
class DomainSet(BaseMetadata):
    superset: SuperSet
    predicate: str

    @classmethod
    def from_data(cls, data: dict) -> DomainSet:
        return cls(SuperSet.from_str(data["superset"]), data["predicate"])

    def to_dict(self):
        return {"superset": str(self.superset), "predicate": self.predicate}


DomainElement = Union[DomainInterval, DomainSet]


@dataclass
class CodeSpanReference(TypedMetadata):
    code_type: CodeSpanType
    code_file_reference_uid: str
    code_span: CodeSpan

    @classmethod
    def from_air_data(cls, data: dict) -> CodeSpanReference:
        return cls(
            MetadataType.CODE_SPAN_REFERENCE,
            ProvenanceData(
                MetadataMethod.PROGRAM_ANALYSIS_PIPELINE,
                ProvenanceData.get_dt_timestamp(),
            ),
            CodeSpanType.from_str(data["code_type"]),
            data["file_uid"],
            CodeSpan.from_source_ref(data["source_ref"]),
        )

    @classmethod
    def from_data(cls, data: dict) -> CodeSpanReference:
        return cls(
            data["type"],
            data["provenance"],
            CodeSpanType.from_str(data["code_type"]),
            data["code_file_reference_uid"],
            CodeSpan.from_data(data["code_span"]),
        )

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                "code_type": str(self.code_type),
                "code_file_reference_uid": self.code_file_reference_uid,
                "code_span": self.code_span.to_dict(),
            }
        )
        return data


@unique
class VariableCreationReason(AutoMATESBaseEnum):
    UNKNOWN = auto()
    LOOP_ITERATION = auto()
    TUPLE_DECONSTRUCTION = auto()
    INLINE_EXPRESSION_EXPANSION = auto()
    INLINE_CALL_RESULT = auto()
    COMPLEX_RETURN_EXPR = auto()
    CONDITION_RESULT = auto()
    LOOP_EXIT_VAR = auto()
    LITERAL_FUNCTION_ARG = auto()
    TOP_IFACE_INTRO = auto()
    BOT_IFACE_INTRO = auto()
    FUNC_RET_VAL = auto()
    FUNC_ARG = auto()
    COND_VAR = auto()
    DUP_GLOBAL = auto()
    DUMMY_ASSIGN = auto()

    def __str__(self):
        return str(self.name)

    @classmethod
    def from_str(cls, data: str):
        return super().from_str(cls, data)


@dataclass
class VariableFromSource(TypedMetadata):
    from_source: bool
    creation_reason: VariableCreationReason

    @classmethod
    def from_air_data(cls, data: dict) -> VariableFromSource:
        return cls(
            MetadataType.FROM_SOURCE,
            ProvenanceData(
                MetadataMethod.PROGRAM_ANALYSIS_PIPELINE,
                ProvenanceData.get_dt_timestamp(),
            ),
            CodeSpanType.from_str(data["code_type"]),
            data["file_uid"],
            CodeSpan.from_source_ref(data["source_ref"]),
        )

    @classmethod
    def from_data(cls, data: dict) -> VariableFromSource:
        return cls(
            data["type"],
            data["provenance"],
            data["from_source"] or data["from_source"] == "True",
            VariableCreationReason.from_str(data["creation_reason"]),
        )

    @classmethod
    def from_ann_cast_data(cls, data: dict) -> VariableFromSource:
        return cls(
            data["type"],
            data["provenance"],
            data["from_source"] or data["from_source"] == "True",
            data["creation_reason"],
        )

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                "from_source": str(self.from_source),
                "creation_reason": str(self.creation_reason),
            }
        )
        return data


@dataclass
class GrFNCreation(TypedMetadata):
    name: str

    @classmethod
    def from_name(cls, filepath: str) -> GrFNCreation:
        filename = filepath[filepath.rfind("/") + 1 :]
        return cls(
            MetadataType.GRFN_CREATION,
            ProvenanceData(
                MetadataMethod.MODEL_ASSEMBLY_PIPELINE,
                ProvenanceData.get_dt_timestamp(),
            ),
            filename,
        )

    @classmethod
    def from_data(cls, data: dict) -> GrFNCreation:
        return cls(**data)

    def to_dict(self):
        data = super().to_dict()
        data.update({"name": self.name})
        return data


@dataclass
class CodeCollectionReference(TypedMetadata):
    global_reference_uid: str
    files: List[CodeFileReference]

    @classmethod
    def from_sources(cls, sources: List[str]) -> CodeCollectionReference:
        return cls(
            MetadataType.CODE_COLLECTION_REFERENCE,
            ProvenanceData(
                MetadataMethod.PROGRAM_ANALYSIS_PIPELINE,
                ProvenanceData.get_dt_timestamp(),
            ),
            str(uuid.uuid4()),
            [CodeFileReference.from_str(fpath) for fpath in sources],
        )

    @classmethod
    def from_data(cls, data: dict) -> CodeCollectionReference:
        return cls(
            data["type"],
            data["provenance"],
            data["global_reference_uid"],
            [CodeFileReference.from_data(d) for d in data["files"]],
        )

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                "global_reference_uid": self.global_reference_uid,
                "files": [code_file.to_dict() for code_file in self.files],
            }
        )
        return data


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

    @classmethod
    def from_data(cls, data: dict) -> Domain:
        mtype = MeasurementType.from_str(data["measurement_scale"])
        if MeasurementType.isa_categorical(mtype):
            els = [DomainSet.from_data(dom_el) for dom_el in data["elements"]]
        elif MeasurementType.isa_numerical(mtype):
            els = [DomainInterval.from_data(dom_el) for dom_el in data["elements"]]
        else:
            els = []
        return cls(
            data["type"],
            data["provenance"],
            DataType.from_str(data["data_type"]),
            mtype,
            els,
        )

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                "data_type": str(self.data_type),
                "measurement_scale": str(self.measurement_scale),
                "elements": [dom_el.to_dict() for dom_el in self.elements],
            }
        )
        return data
