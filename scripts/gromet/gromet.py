import json
from typing import NewType, List, Tuple, Union
from dataclasses import dataclass, field, asdict


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

# The following gromet spec as a "grammar" is not guaranteed to
#   be unambiguous.
# For this reason, adding explicit "gromet_element" field that
#   represents the Type of GroMEt syntactic element


@dataclass
class GrometElm(object):
    """
    Base class for all Gromet Elements.
    Implements __post_init__ that saves gromet_elm class name.
    """
    gromet_elm: str = field(init=False)

    def __post_init__(self):
        self.gromet_elm = type(self).__name__


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

# either a primitive operator or a named fn
# OR, perhaps just use UidBox for all Op, Functions, etc... ?
UidOp = NewType('UidFn', str)

UidVariable = NewType('UidVariable', str)
UidGromet = NewType('UidGromet', str)


# --------------------
# Metadata

@dataclass
class Metadatum(GrometElm):
    """
    Metadatum base.
    """
    uid: UidMetadatum


# TODO: add Metadatum subtypes
#       Will be based on: https://ml4ai.github.io/automates-v2/grfn_metadata.html


Metadata = NewType('Metadata', Union[List[Metadatum], None])


# --------------------
# Type


@dataclass
class TypeDeclaration(GrometElm):
    name: UidType
    metadata: Metadata


@dataclass
class Type:
    """
    Type Specification.
    Constructed as an expression of the GroMEt Type Algebra
    """
    type: str = field(init=False)

    def __post_init__(self):
        self.type = type(self).__name__


# TODO: GroMEt type algebra: "sublangauge" for specifying types


# Atomics

@dataclass
class Atomic(Type):
    pass


@dataclass
class Any(Atomic):
    pass


@dataclass
class Nothing(Atomic):
    pass


@dataclass
class Number(Atomic):
    pass


@dataclass
class Integer(Number):
    pass


@dataclass
class Real(Number):
    pass


@dataclass
class Float(Real):
    pass


@dataclass
class Boolean(Atomic):
    pass


@dataclass
class Character(Atomic):
    pass


@dataclass
class Symbol(Atomic):
    pass


# Composites

@dataclass
class Composite(Type):
    pass


# Algebra

@dataclass
class Prod(Composite):
    element_type: List[UidType]
    cardinality: Union[int, None]


@dataclass
class String(Prod):
    element_type: List[UidType] = (UidType("Character"),)


@dataclass
class Sum(Composite):
    element_type: List[UidType]


@dataclass
class NamedAttribute(Composite):
    name: str
    element_type: UidType


@dataclass
class Map(Prod):
    element_type: List[Tuple[UidType, UidType]]


# --------------------
# Literal


@dataclass
class Literal(GrometElm):
    """
    Literal base.
    A literal is an instances of Types
    """
    uid: Union[UidLiteral, None]  # allows anonymous literals
    type: UidType
    value: 'Val'  # TODO
    metadata: Metadata


# TODO: "sublanguage" for specifying instances

@dataclass
class Val(GrometElm):
    val: Union[str, List['Val', 'AttributeVal']]


@dataclass
class AttributeVal(GrometElm):
    name: str
    val: Val

# --------------------
# Port

@dataclass
class Port(GrometElm):
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
# Wire

@dataclass
class Wire(GrometElm):
    """
    Wire base.
    All Wires have a Type (of the value they may carry).
    Optionally declared with a value, otherwise derived (from system dynamics).
    """
    uid: UidWire
    type: UidType
    value: Union[Literal, None]
    metadata: Metadata


@dataclass
class WireDirected(Wire):
    """
    Directed Wire base.
    Has optional single input and single output Port.
    """
    input: Union[UidPort, None]
    output: Union[UidPort, None]


@dataclass
class WireUndirected(Wire):
    """
    Undirected Wire base.
    Assumption: that Undirected Wire could connect zero or more Ports
    and possibly one Junction. (This implementation does not enforce this assumption)
    """
    ports: List[Union[UidPort, UidJunction]]


# --------------------
# Junction

@dataclass
class Junction(GrometElm):
    """
    Junction base.
    (Junctions are nullary)
    """
    uid: UidJunction
    type: UidType
    metadata: Metadata


# --------------------
# Box

@dataclass
class Box(GrometElm):
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


@dataclass
class BoxUndirected(Box):
    """
    Undirected Box base.
    Unoriented list of Ports represent interface to Box
    """

    # NOTE: Redundant since Ports specify the Box they belong to.
    # However, natural to think of boxes "having" Ports, and DirectedBoxes
    # must specify the "face" their ports belong to, so for parity we'll
    # have BoxUndirected also name their Ports
    ports: Union[List[UidPort], None]


@dataclass
class BoxDirected(Box):
    # NOTE: This is NOT redundant since Ports are not oriented,
    # but DirectedBox has ports on a "orientation/face"
    input_ports: Union[List[UidPort], None]
    output_ports: Union[List[UidPort], None]


# Relations

@dataclass
class Relation(BoxUndirected):
    """
    Base Relation
    TODO: what is its semantics?
    """
    pass


# Functions

@dataclass
class Function(BoxDirected):
    """
    Base Function
    Representations of general functions, primitive operators, predicates and loops.
    """
    name: Union[UidOp, None]


@dataclass
class Exp(GrometElm):
    """
    Assumption that may need revisiting:
      Exp's are assumed to always be declared inline as single instances,
      and may themselves include Exp's in their args.
      Under this assumption, they do not require a uid or name
      -- they are always single instance.
    The operator field of an Expression denotes a fn call reference,
    which is either
        (a) primitive operator.
        (b) a named Function
    The args field is a list of either UidPort reference, Literal or Exp
    """
    operator: UidOp
    args: Union[List[Union[UidPort, Literal, 'Exp']], None]


@dataclass
class Expression(Function):
    """
    A Function who's wiring is an expression tree of Exp's.
    Assumptions:
      (1) Any "variable" references in the tree will refer to the
        input Ports of the Expression. For this reason, there is
        no need for Wires.
      (2) An Expression always has only one output Port, but for
        parity with Function, the output_ports field name remains
        plural while it's value is no longer a list.
    """
    wiring: Exp
    output_ports: UidPort  # forces output to be a single Port


@dataclass
class Predicate(Function):
    """
    Function that has only one output port.
    The Port type MUST be Boolean (although not enforced in this
    implementation)
    """
    output_ports: UidPort  # forces output to be a single Port


@dataclass
class Loop(Function):
    """
    Function that loops until exit Predicate is True.
    NOTE: Must have one output Port for every input Port,
      to enable output Port values to set input Port values
      at next iteration through the loop.
    In general, there are two cases:
      (1) input Port values is altered along a path that
        eventually arrives at the corresponding output Port
        that is then the updated value that will be used as
        input in the next trip through the loop
      (2) input Port value is not updated within the loop;
        in this case, there will be a directed Wire that
        connects the input Port directly to it's corresponding
        output Port.
    portmap: a list of pairs of:
         ( <output UidPort>, <input UidPort> )
        That is, it specifies the map
          From output ports (previous iteration)
          To input ports (next iteration).
      The portmap is essentially a list of anonymous Wires
    """
    portmap: List[Tuple[UidPort, UidPort]]
    exit: Predicate


# --------------------
# Variable

@dataclass
class Variable(GrometElm):
    """
    A Variable is the locus of two representational roles:
        (a) denotes one or more Wires (that carry a value) or Junction and
        (b) denotes a modeled domain (world) state.
    (b) currently is represented in Metadata.

    """
    uid: UidVariable
    name: str
    type: UidType
    wires: Union[List[UidWire], Junction]
    metadata: Metadata


# --------------------
# Gromet top level

@dataclass
class Gromet(GrometElm):
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
    json.dump(asdict(gromet),  # gromet.to_dict(),
              open(dst_file, "w"),
              indent=2)


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    t = Type(uid=UidType("myType"), name="myType", metadata=None)
    print(json.dumps(asdict(t)))

    lit = Literal(uid=UidLiteral("myLiteral"), type=UidType("myType"),
                  value="infty", metadata=None)
    print(json.dumps(asdict(lit)))

    p = Port(uid=UidPort("myPort"), box=UidBox("myBox"), type=UidType("Int"),
             name="myPort", metadata=None)
    print(json.dumps(asdict(p)))

    w = Wire(uid=UidWire("myWire"), type=UidType("Float"), value=None,
             metadata=None)
    print(json.dumps(asdict(w)))

    wd = WireDirected(uid=UidWire("myDirectedWire"), type=UidType("Float"), value=None,
                      input=UidPort("inPort"),
                      output=UidPort("outPort"),
                      metadata=None)
    print(json.dumps(asdict(wd)))

    wu = WireUndirected(uid=UidWire("myUndirectedWire"), type=UidType("Float"), value=None,
                        ports=[UidPort("p1"), UidPort("p2")],
                        metadata=None)
    print(json.dumps(asdict(wu)))

    j = Junction(uid=UidJunction("myJunction"), type=UidType("Float"), metadata=None)
    print(json.dumps(asdict(j)))

    b = Box(uid=UidBox("myBox"), name="aBox", wiring=[UidWire("myWire")], metadata=None)
    print(json.dumps(asdict(b)))

    bu = BoxUndirected(uid=UidBox("myBoxUndirected"), name="aBox", wiring=[UidWire("myWire")],
                       ports=[UidPort("myPort")], metadata=None)
    print(json.dumps(asdict(bu)))

    bd = BoxDirected(uid=UidBox("myBoxDirected"), name="aBox",
                     wiring=[UidWire("myWire")],
                     input_ports=[UidPort("in1"), UidPort("in2")],
                     output_ports=[UidPort("out1"), UidPort("out2")],
                     metadata=None)
    print(json.dumps(asdict(bd)))

    r = Relation(uid=UidBox("myRelation"), name="aBox", wiring=[UidWire("myWire")],
                 ports=[UidPort("p1"), UidPort("p2")], metadata=None)
    print(json.dumps(asdict(r)))

    f = Function(uid=UidBox("myFunction"), name=UidOp("aBox"),
                 wiring=[UidWire("myWire")],
                 input_ports=[UidPort("in1"), UidPort("in2")],
                 output_ports=[UidPort("out1"), UidPort("out2")],
                 metadata=None)
    print(json.dumps(asdict(f)))

    exp = Exp(operator=UidOp("myExp"),
              args=[UidPort("p1"), UidPort("p2")])
    print(json.dumps(asdict(exp)))

    e = Expression(uid=UidBox("myExpression"), name=UidOp("aBox"),
                   wiring=exp,
                   input_ports=[UidPort("in1"), UidPort("in2")],
                   output_ports=UidPort("out"),
                   metadata=None)
    print(json.dumps(asdict(e)))

    pred = Predicate(uid=UidBox("myPredicate"), name=UidOp("aBox"),
                     wiring=[UidWire("myWire")],
                     input_ports=[UidPort("in1"), UidPort("in2")],
                     output_ports=UidPort("outBooleanPort"),
                     metadata=None)
    print(json.dumps(asdict(pred)))

    loop = Loop(uid=UidBox("myLoop"), name=UidOp("myLoop"),
                input_ports=[UidPort("in1"), UidPort("in2")],
                output_ports=[UidPort("out1"), UidPort("out2")],
                wiring=[UidWire("wire_from_in1_to_out_1"),
                        UidWire("wire_from_in2_to_out_2")],
                portmap=[(UidPort("out1"), UidPort("in1")),
                         (UidPort("out2"), UidPort("in2"))],
                exit=pred,
                metadata=None)
    print(json.dumps(asdict(loop), indent=2))

    v = Variable(uid=UidVariable("myVariable"),
                 name="nameOfMyVar",
                 type=UidType("myType"),
                 wires=[UidWire("wire1"), UidWire("wire2")],
                 metadata=None)
    print(json.dumps(asdict(v)))

    g = Gromet(
        uid=UidGromet("myGromet"),
        name="myGromet",
        framework_type="FunctionNetwork",
        root=b.uid,
        types=[t],
        ports=[p],
        wires=[w, wd, wu],
        boxes=[b, bd, bu],
        variables=[v],
        metadata=None
    )
    print(json.dumps(asdict(g), indent=2))
