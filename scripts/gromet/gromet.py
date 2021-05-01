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
    Has optional single input and (multiple) output Port(s).
    A directed Wire can only have a single source.
    The output Port(s) indicate "reads" of the Wire value (of which there
    can be zero or more).
    """
    input: Union[UidPort, None]
    output: Union[List[UidPort], None]


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
    wiring: Union[List[UidWire], None]
    metadata: Metadata


@dataclass_json
@dataclass
class UndirectedBox(Box):
    """
    Undirected Box base.
    Unoriented list of Ports represent interface to Box
    """
    ports: List[Port]


@dataclass_json
@dataclass
class DirectedBox(Box):
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
    type: Type
    wires: Union[List[Wire], Junction]
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


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------


def simple_sir_gromet() -> Gromet:
    wires = [
        # Var "S"
        WireDirected(uid=UidWire("W:S1"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:sir.in.S"),
                     output=[UidPort("P:infected_exp.in.S"),
                             UidPort("P:S_exp.in.S")]),
        # Var "I"
        WireDirected(uid=UidWire("W:I1"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:sir.in.I"),
                     output=[UidPort("P:infected_exp.in.I"),
                             UidPort("P:recovered_exp.in.I"),
                             UidPort("P:I_update_exp.in.I")]),
        # Var "R"
        WireDirected(uid=UidWire("W:R1"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:sir.in.R"),
                     output=[UidPort("P:infected_exp.in.R"),
                             UidPort("P:I_update_exp.in.R")]),
        # Var "beta"
        WireDirected(uid=UidWire("W:beta"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:sir.in.beta"),
                     output=[UidPort("P:infected_exp.in.beta")]),
        # Var "gamma"
        WireDirected(uid=UidWire("W:gamma"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:sir.in.gamma"),
                     output=[UidPort("P:recovered_exp.in.gamma")]),
        # Var "dt"
        WireDirected(uid=UidWire("W:dt"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:sir.in.dt"),
                     output=[UidPort("P:infected_exp.in.dt"),
                             UidPort("P:recovered_exp.in.dt")]),

        # Wire for Var "infected"
        WireDirected(uid=UidWire("W:infected"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:infected_exp.out.infected"),
                     output=[UidPort("P:S_update_exp.in.infected"),
                             UidPort("P:I_update_exp.in.infected")]),

        # Wire for Var "recovered"
        WireDirected(uid=UidWire("W:recovered"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:recovered_exp.out.recovered"),
                     output=[UidPort("P:I_update_exp.in.recovered"),
                             UidPort("P:R_update_exp.in.recovered")]),

        # part of Var "S"
        WireDirected(uid=UidWire("W:S2"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:S_update_exp.out.S"),
                     output=[UidPort("P:sir.out.S")]),

        # part of Var "I"
        WireDirected(uid=UidWire("W:I2"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:I_update_exp.out.I"),
                     output=[UidPort("P:sir.out.I")]),

        # part of Var "R"
        WireDirected(uid=UidWire("W:R2"), type=UidType("T:Float"), value=None, metadata=None,
                     input=UidPort("P:R_update_exp.out.R"),
                     output=[UidPort("P:sir.out.R")]),

    ]

    ports = [
        # The input ports to the 'sir' outer/parent Function
        Port(uid=UidPort("P:sir.in.S"), type=UidType("T:Float"), name="S", metadata=None),
        Port(uid=UidPort("P:sir.in.I"), type=UidType("T:Float"), name="I", metadata=None),
        Port(uid=UidPort("P:sir.in.R"), type=UidType("T:Float"), name="R", metadata=None),
        Port(uid=UidPort("P:sir.in.beta"), type=UidType("T:Float"), name="beta", metadata=None),
        Port(uid=UidPort("P:sir.in.gamma"), type=UidType("T:Float"), name="gamma", metadata=None),
        Port(uid=UidPort("P:sir.in.dt"), type=UidType("T:Float"), name="dt", metadata=None),
        # The output ports to the 'sir' outer/parent Function
        Port(uid=UidPort("P:sir.out.S"), type=UidType("T:Float"), name="S", metadata=None),
        Port(uid=UidPort("P:sir.out.I"), type=UidType("T:Float"), name="I", metadata=None),
        Port(uid=UidPort("P:sir.out.R"), type=UidType("T:Float"), name="R", metadata=None),

        # The input ports to the 'infected_exp' anonymous assignment Expression
        Port(uid=UidPort("P:infected_exp.in.S"), type=UidType("T:Float"), name="S", metadata=None),
        Port(uid=UidPort("P:infected_exp.in.I"), type=UidType("T:Float"), name="I", metadata=None),
        Port(uid=UidPort("P:infected_exp.in.R"), type=UidType("T:Float"), name="R", metadata=None),
        Port(uid=UidPort("P:infected_exp.in.beta"), type=UidType("T:Float"), name="beta", metadata=None),
        Port(uid=UidPort("P:infected_exp.in.dt"), type=UidType("T:Float"), name="dt", metadata=None),
        # The output ports to the 'infected_exp' anonymous assignment Expression
        Port(uid=UidPort("P:infected_exp.out.infected"), type=UidType("T:Float"), name="infected", metadata=None),

        # The input ports to the 'recovered_exp' anonymous assignment Expression
        Port(uid=UidPort("P:recovered_exp.in.I"), type=UidType("T:Float"), name="I", metadata=None),
        Port(uid=UidPort("P:recovered_exp.in.gamma"), type=UidType("T:Float"), name="gamma", metadata=None),
        Port(uid=UidPort("P:recovered_exp.in.dt"), type=UidType("T:Float"), name="dt", metadata=None),
        # The output ports to the 'recovered_exp' anonymous assignment Expression
        Port(uid=UidPort("P:recovered_exp.out.recovered"), type=UidType("T:Float"), name="recovered", metadata=None),

        # The input ports to the 'S_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:S_update_exp.in.S"), type=UidType("T:Float"), name="S", metadata=None),
        Port(uid=UidPort("P:S_update_exp.in.infected"), type=UidType("T:Float"), name="infected", metadata=None),
        # The output ports to the 'S_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:S_update_exp.out.S"), type=UidType("T:Float"), name="S", metadata=None),

        # The input ports to the 'I_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:I_update_exp.in.I"), type=UidType("T:Float"), name="I", metadata=None),
        Port(uid=UidPort("P:I_update_exp.in.infected"), type=UidType("T:Float"), name="infected", metadata=None),
        Port(uid=UidPort("P:I_update_exp.in.recovered"), type=UidType("T:Float"), name="recovered", metadata=None),
        # The output ports to the 'I_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:I_update_exp.out.I"), type=UidType("T:Float"), name="I", metadata=None),

        # The input ports to the 'R_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:R_update_exp.in.R"), type=UidType("T:Float"), name="R", metadata=None),
        Port(uid=UidPort("P:R_update_exp.in.recovered"), type=UidType("T:Float"), name="recovered", metadata=None),
        # The output ports to the 'R_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:R_update_exp.out.R"), type=UidType("T:Float"), name="R", metadata=None)
    ]

    # Expression 'infected_exp' (SIR-simple line 46) -- input: (S I R beta dt)
    # Exp's:
    # e1 : (* beta S I) -> e1
    e1 = Exp(operator=UidOp("*"),
             args=[UidPort("P:infected_exp.in.beta"),
                   UidPort("P:infected_exp.in.S"),
                   UidPort("P:infected_exp.in.I")])
    # e2 : (* e1 Literal(-1)) -> e2
    e2 = Exp(operator=UidOp("*"),
             args=[e1, Literal(uid=None, type=UidType("Float"), value="-1", metadata=None)])
    # e3 : (+ S I R) -> e3
    e3 = Exp(operator=UidOp("+"),
             args=[UidPort("P:infected_exp.in.S"),
                   UidPort("P:infected_exp.in.I"),
                   UidPort("P:infected_exp.in.R")])
    # e4 : (/ e2 e3) -> e4
    e4 = Exp(operator=UidOp("/"), args=[e2, e3])
    # e5 : (* e4 dt) -> e5
    e5 = Exp(operator=UidOp("*"), args=[e4, UidPort("P:infected_exp.in.dt")])
    # The anonymous Expression
    infected_exp = Expression(uid=UidBox("B:infected_exp"),
                              name=None,
                              input_ports=[UidPort("P:infected_exp.in.S"),
                                           UidPort("P:infected_exp.in.I"),
                                           UidPort("P:infected_exp.in.R"),
                                           UidPort("P:infected_exp.in.beta"),
                                           UidPort("P:infected_exp.in.dt")],
                              output_ports=[UidPort("P:infected_exp.out.infected")],
                              wiring=e5,
                              metadata=None)

    # Expression 'recovered_exp' (SIR-simple line 47) -- input: (gamma I dt)
    # Exp's:
    # e6 : (* gamma I) -> e6
    e6 = Exp(operator=UidOp("*"), args=[UidPort("P:sir.in.gamma"), UidPort("P:sir.in.I")])
    # e7 : (* e6 dt) -> e7
    e7 = Exp(operator=UidOp("*"), args=[e6, UidPort("P:sir.in.dt")])
    # The anonymous Expression
    recovered_exp = Expression(uid=UidBox("B:recovered_exp"),
                               name=None,
                               input_ports=[UidPort("P:recovered_exp.in.I"),
                                            UidPort("P:recovered_exp.in.gamma"),
                                            UidPort("P:recovered_exp.in.dt")],
                               output_ports=[UidPort("P:recovered_exp.out.infected")],
                               wiring=e7,
                               metadata=None)

    # Expression 'S_update_exp' (SIR-simple line 49) -- input: (S infected)
    # Exp's:
    # e8 : (- S infected) -> e8
    e8 = Exp(operator=UidOp("-"),
             args=[UidPort("P:S_update_exp.in.S"), UidPort("P:S_update_exp.in.infected")])
    # The anonymous Expression
    s_update_exp = Expression(uid=UidBox("B:S_update_exp"),
                              name=None,
                              input_ports=[UidPort("P:S_update_exp.in.S"),
                                           UidPort("P:S_update_exp.in.infected")],
                              output_ports=[UidPort("P:S_update_exp.out.S")],
                              wiring=e8,
                              metadata=None)

    # Expression 'I_update_exp' (SIR-simple line 50) -- input: (I infected recovered)
    # Exp's
    # e9 : (+ I infected) -> e9
    e9 = Exp(operator=UidOp("+"),
             args=[UidPort("P:I_update_exp.in.I"), UidPort("P:I_update_exp.in.infected")])
    # e10 : (- e9 recovered) -> e10
    e10 = Exp(operator=UidOp("-"),
              args=[e9, UidPort("P:I_update_exp.in.recovered")])
    # The anonymous Expression
    i_update_exp = Expression(uid=UidBox("B:I_update_exp"),
                              name=None,
                              input_ports=[UidPort("P:I_update_exp.in.I"),
                                           UidPort("P:I_update_exp.in.infected"),
                                           UidPort("P:I_update_exp.in.recovered")],
                              output_ports=[UidPort("P:I_update_exp.out.I")],
                              wiring=e10,
                              metadata=None)

    # Expression 'R_update_exp' (SIR-simple line 50) -- input: (R recovered)
    # Exp's
    # e11 : (+ R recovered) -> e11
    e11 = Exp(operator=UidOp("+"),
              args=[UidPort("P:R_update_exp.in.R"), UidPort("P:R_update_exp.in.recovered")])
    # The anonymous Expression
    r_update_exp = Expression(uid=UidBox("B:R_update_exp"),
                              name=None,
                              input_ports=[UidPort("P:R_update_exp.in.R"),
                                           UidPort("P:R_update_exp.in.recovered")],
                              output_ports=[UidPort("P:R_update_exp.out.R")],
                              wiring=e11,
                              metadata=None)

    sir = Function(uid=UidBox("B:sir"),
                   name=UidOp("sir"),
                   input_ports=[UidPort("P:sir.in.S"),
                                UidPort("P:sir.in.I"),
                                UidPort("P:sir.in.R"),
                                UidPort("P:sir.in.beta"),
                                UidPort("P:sir.in.gamma"),
                                UidPort("P:sir.in.dt")],
                   output_ports=[UidPort("P:sir.out.S"),
                                 UidPort("P:sir.out.I"),
                                 UidPort("P:sir.out.R")],
                   # this is redundant with having explicit top-level wires list
                   wiring=[UidWire("W:S1"), UidWire("W:I1"), UidWire("W:R1"),
                           UidWire("W:beta"), UidWire("W:gamma"), UidWire("W:dt"),
                           UidWire("W:infected"), UidWire("W:recovered"),
                           UidWire("W:S2"), UidWire("W:I2"), UidWire("W:R2")],
                   metadata=None)

    g = Gromet(
        uid=UidGromet("SimpleSIR"),
        name="SimpleSIR",
        framework_type="FunctionNetwork",
        root=sir.uid,
        types=None,
        ports=ports,
        wires=wires,
        boxes=[sir, infected_exp, recovered_exp,
               s_update_exp, i_update_exp, r_update_exp],
        variables=None,
        metadata=None
    )

    return g


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    gromet_to_json(simple_sir_gromet(), 'test.json')
    # gromet_to_json(simple_sir_gromet())
