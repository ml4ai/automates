import json
from typing import NewType, List, Tuple, Union
from dataclasses import dataclass
from dataclasses_json import dataclass_json


# REQUIREMENTS:
# dataclasses-json
#   Install with: `pip install dataclasses-json`
#   This package provides decorator that makes native dataclasses JSON-serializable

# TODO: Method for hacking inherited constant values
# https://stackoverflow.com/questions/51575931/class-inheritance-in-python-3-7-dataclasses
# TODO: Use the above to explicitly annotate Gromet syntax type names into JSON
#       OR: Get fancy and create a custom decorator!


"""
GroMEt is the bytecode for the expression of multi-framework model semantics

The GroMEt bytecode is expressed in a syntax that makes explicit the semantics
  of the model, in a structure aimed at enabling algebraic operations

Directed GroMET is the bytecode for causal/influence paths / data flow semantics

Functions are Directed Boxes that represent directed paths in the general
  case of a (directed) graph
Expression Boxes represent a special kind of Box whose internal 'wiring' are
  guaranteed to be (must be) a tree, where any references to variables
  (value sources) are via the input ports to the Expression.
  The internal wiring is thus a recursive list of input ports and Exp
     where Exp is an expression consisting of a single operator (primitive
     or Box name) and arguments (positionally presented) to the operator
  An Expression has a single output port that passes the result of the top Exp
"""

# -----------------------------------------------------------------------------
# GroMEt syntactic types
# -----------------------------------------------------------------------------

# The following gromet spec as a "grammar" is ambiguous: there are children
#   that could be one of several types
# For this reason, need to have an explicit "gromet_element" field that
#   represents the Type of GroMEt syntactic element

# Here's a so-far failed attempt to provide a top level class that could
# automatically add the class name as a field to any inheriting GroMEt element.
# The problem
#   If you don't provide default assignment (None), then serializing
#      won't include the field
#      BUT: then all inheriting dataclasses MUST also all provide default values!
#   If you remove the default assignment, then the constructor REQUIRES
#      requires you specify teh gromet_class manuall, which defeats the purpose...

# @dataclass_json
# @dataclass
# class GrometElm:
#     gromet_class: str = None
#
#     def __post_init__(self):
#         self.gromet_class = type(self).__name__
#         print(f"My field is {type(self).__name__}")


# --------------------
# Uid

# The purpose here is to provide a kind of "namespace" for the unique IDs
# that used to distinguish gromet model component instances.
# I'm currently making these str so I can give them arbitrary names as I
#   hand-construct example GroMEt instances, but these could be
#   sequential integers (as James uses) or uuids.

UidMetadatum = NewType('UidMetadatum', str)
UidType = NewType('UidType', str)
UidLiteral = NewType('UidLiteral', str)
UidPort = NewType('UidPort', str)
UidJunction = NewType('UidJunction', str)
UidWire = NewType('UidWire', str)
UidBox = NewType('UidBox', str)
UidOp = NewType('UidFn', str)  # either a primitive operator or a named fn (Box)
UidVariable = NewType('UidVariable', str)
UidGromet = NewType('UidGromet', str)


# --------------------
# Metadata


@dataclass_json
@dataclass
class Metadatum:
    """
    Metadatum base.
    """
    uid: UidMetadatum


# TODO: add Metadatum subtypes
#       Will be based on: https://ml4ai.github.io/automates-v2/grfn_metadata.html


Metadata = NewType('Metadata', Union[List[Metadatum], None])


# --------------------
# Type

@dataclass_json
@dataclass
class Type:
    """
    Type Specification.
    Constructed as an expression of the GroMEt Type Algebra
    """
    uid: UidType
    name: str
    metadata: Metadata


# TODO: GroMEt type algebra: "sublangauge" for specifying types


# --------------------
# Literal

@dataclass_json
@dataclass
class Literal:
    """
    Literal base.
    A literal is an instances of Types
    """
    uid: Union[UidLiteral, None]  # allows anonymous literals
    type: UidType
    value: str  # TODO
    metadata: Metadata


# TODO: "sublanguage" for specifying instances


# --------------------
# Wire

@dataclass_json
@dataclass
class Wire:
    """
    Wire base.
    All Wires have a Type (of the value they may carry).
    Optionally declared with a value, otherwise derived (from system dynamics).
    """
    uid: UidWire
    type: UidType
    value: Union[Literal, None]
    metadata: Metadata


@dataclass_json
@dataclass
class WireDirected(Wire):
    """
    Directed Wire base.
    Has optional single input and single output Port.
    """
    input: Union[UidPort, None]
    output: Union[UidPort, None]


@dataclass_json
@dataclass
class WireUndirected(Wire):
    """
    Undirected Wire base.
    Assumption: that Undirected Wire could connect zero or more Ports
    and possibly one Junction. (This implementation does not enforce this assumption)
    """
    ports: List[Union[UidPort, UidJunction]]


# --------------------
# Port

@dataclass_json
@dataclass
class Port:
    """
    Port base.
    (Ports are nullary, but always must belong to a single Box)
    Port may be named (e.g., named argument)
    """
    uid: UidPort
    box: UidBox
    type: UidType
    name: Union[str, None]
    metadata: Metadata


# --------------------
# Junction

@dataclass_json
@dataclass
class Junction:
    """
    Junction base.
    (Junctions are nullary)
    """
    uid: UidPort
    type: UidType
    metadata: Metadata


# --------------------
# Box

@dataclass_json
@dataclass
class Box:
    """
    Box base.
    A Box may have a name
    A Bpx may have wiring (set of wiring connecting Ports of Boxes)
    """
    uid: UidBox
    name: Union[str, None]

    # NOTE: Redundant since Wiring specified Port, which in turn specifies Box
    # However, natural to think of boxes "containing" (immediately contained) wires
    wiring: Union[List[UidWire], None]

    metadata: Metadata


@dataclass_json
@dataclass
class UndirectedBox(Box):
    """
    Undirected Box base.
    Unoriented list of Ports represent interface to Box
    """

    # NOTE: Redundant since Ports specified Box they belong to.
    # However, natural to think of boxes "having" Ports, to
    # per below, DirectedBox "orients" ports
    ports: List[Port]


@dataclass_json
@dataclass
class DirectedBox(Box):
    # NOTE: This is NOT redundant since Ports are not oriented,
    # but DirectedBox has ports on a "orientation/face"
    input_ports: List[UidPort]
    output_ports: List[UidPort]


### Relations

@dataclass_json
@dataclass
class Relation(UndirectedBox):
    """
    Base Relation
    TODO: what is its semantics?
    """
    pass


### Functions

@dataclass_json
@dataclass
class Function(DirectedBox):
    """
    Base Function
    Representations of general functions, primitive operators, predicates and loops.
    """
    name: Union[UidOp, None]


@dataclass_json
@dataclass
class Exp:
    """
    The operator field of an Expression denotes a fn call reference,
    which is either
        (a) primitive operator.
        (b) a named Function (Box)
    """
    operator: UidOp
    args: List[Union[UidPort, 'Exp']]


@dataclass_json
@dataclass
class Expression(Function):
    """

    """
    wiring: Exp


@dataclass_json
@dataclass
class Predicate(Function):
    """
    Function that has only one output port.
    The Port type must be Boolean (although not enforced in this implementation)
    """
    output_ports: Port


@dataclass_json
@dataclass
class Loop(Function):
    """
    Function that loops until exit Predicate is True.
    portmap maps output ports (previous iteration) to input ports (next iteration)
    """
    portmap: List[Tuple[UidPort, UidPort]]
    exit: Predicate


# --------------------
# Variable

@dataclass_json
@dataclass
class Variable:
    """
    A Variable is the locus of two representational roles:
        (a) denotes one or more Wires (that carry a value) or Junction and
        (b) denotes a modeled domain (world) state.
    (b) currently is represented in Metadata.

    """
    name: str
    type: UidType
    wires: Union[List[UidWire], Junction]
    metadata: Metadata


# --------------------
# Gromet top level

@dataclass_json
@dataclass
class Gromet:
    uid: UidGromet
    name: Union[str, None]
    framework_type: str
    root: Union[UidBox, None]
    types: Union[List[Type], None]
    ports: Union[List[Port], None]
    wires: Union[List[Wire], None]
    boxes: List[Box]
    variables: Union[List[Variable], None]
    metadata: Metadata


# -----------------------------------------------------------------------------
# Utils
# -----------------------------------------------------------------------------

def gromet_to_json(gromet: Gromet, dst_file: Union[str, None] = None):
    if dst_file is None:
        dst_file = f"{gromet.name}.json"
    json.dump(gromet.to_dict(),
              open(dst_file, "w"),
              indent=2)


