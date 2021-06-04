import json
from typing import NewType, List, Tuple, Union
from dataclasses import dataclass, field, asdict


"""
Shared working examples:
gromet/
    docs/
        <date>-gromet-uml.{png,svg}
        <date>-TypedGrometElm-hierarchy-by-hand.pdf
        Conditional.pdf  # schematic of structural pattern for Conditional
        Loop.pdf         # schematic of structural pattern for Loop
    examples/
        <dated previous versions of examples>
        cond_ex1/        # example Function Network w/ Conditional
        Simple_SIR/
            Wiring diagrams and JSON for the following Model Framework types
              Function Network (FN)
              Bilayer
              Petri Net Classic (PetriNetClassic)
              Predicate/Transition (Pr/T) Petri Net (PrTNet)
        toy1/            # example Function Network (no Conditionals or Loops)

(UA:
Google Drive:ASKE-AutoMATES/ASKE-E/GroMEt-model-representation-WG/gromet/
    root of shared examples
Google Drive:ASKE-AutoMATES/ASKE-E/GroMEt-model-representation-WG/gromet-structure-visual
    TypedGrometElm-hierarchy-02.graffle
)


TODO: Side Effects
() mutations of globals
    (can happen in libraries)
() mutations of mutable variables
() mutations of referenced variables (C/C++, can't occur in Python)

Event-driven programming
() No static trace (directed edges from one fn to another), 
    so a generalization of side-effects
    Requires undirected, which corresponds to under-specification 
"""

# -----------------------------------------------------------------------------
# Model Framework Types
# -----------------------------------------------------------------------------

# Data:
# Float, Integer, Boolean

# Primitive term constructors (i.e., primitive operators):
# arithmetic: "+", "*", "-", "/", "exp", "log"
# boolean fn: "lt", "leq", "gr", "geq", "==", "!=", "and", "or", "not"

# Function Network (FunctionNetwork):
# Function, Expression, Predicate, Conditional, Loop,
# Junction, Port, Literal, Variable
# Types:
#   Ports: PortInput, PortOutput

# Bilayer
# Junction, Wire
# Types:
#  Junction: State, Flux, Tangent, Literal
#  Wire: W_in, W_pos, W_neg

# Petri Net Classic (PetriNetClassic)
# Junction, Wire, Literal
# Types:
#  Junction: State, Rate

# Predicate/Transition (Pr/T) Petri Net (PrTNet)
# Relation, Expression, Port, Literal
# Types:
#   Ports: Variable, Parameter
#   Wire: Undirected  (all wires are undirected, so not strictly required)
#   Relation: PrTNet, Event, Enable, Rate, Effect

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
    Implements __post_init__ that saves syntactic type (syntax)
        as GroMEt element class name.
    """
    syntax: str = field(init=False)

    def __post_init__(self):
        self.syntax = self.__class__.__name__


# --------------------
# Uid

# The purpose here is to provide a kind of "namespace" for the unique IDs
# that used to distinguish gromet model component instances.
# Currently making these str so I can give them arbitrary names as I
#   hand-construct example GroMEt instances, but these could be
#   sequential integers (as James uses) or uuids.

UidMetadatum = NewType('UidMetadatum', str)
UidType = NewType('UidType', str)
UidLiteral = NewType('UidLiteral', str)
UidPort = NewType('UidPort', str)
UidJunction = NewType('UidJunction', str)
UidWire = NewType('UidWire', str)

UidBox = NewType('UidBox', str)

UidOp = NewType('UidOp', str)  # Primitive operator name
UidFn = NewType('UidFn', str)  # Defined function name

UidVariable = NewType('UidVariable', str)
UidGromet = NewType('UidGromet', str)


# Explicit "reference" objects.
# Required when there is ambiguity about which type of uid reference
# is specified.

@dataclass
class RefFn(GrometElm):
    """
    Representation of an explicit reference to a defined box
    """
    name: UidFn


@dataclass
class RefOp(GrometElm):
    """
    Representation of an explicit reference to a primitive operator
    """
    name: UidOp


# --------------------
# Metadata

@dataclass
class Metadatum(GrometElm):
    """
    Metadatum base.
    """
    uid: UidMetadatum
    type: Union[UidType, None]


# TODO: add Metadatum subtypes
#       Will be based on: https://ml4ai.github.io/automates-v2/grfn_metadata.html


Metadata = NewType('Metadata', Union[List[Metadatum], None])


# --------------------
# Type


@dataclass
class Type:
    """
    Type Specification.
    Constructed as an expression of the GroMEt Type Algebra
    """
    type: str = field(init=False)

    def __post_init__(self):
        self.type = type(self).__name__


@dataclass
class TypeDeclaration(GrometElm):
    name: UidType
    type: Type
    metadata: Metadata

# TODO: GroMEt type algebra: "sublangauge" for specifying types


# Atomics

# Assumed "built-in" Atomic Types:
#   Any, Void (Nothing)
#   Number
#     Integer
#     Real
#       Float
#   Bool
#   Character
#   Symbol

# @dataclass
# class Atomic(Type):
#     pass


# Composites

# @dataclass
# class Composite(Type):
#     pass


# Algebra

@dataclass
class Prod(Type):
    """
    A Product type constructor.
    The elements of the element_type list are assumed to be
    present in each instance.
    """
    cardinality: Union[int, None]
    element_type: List[UidType]


@dataclass
class String(Prod):
    """
    A type representing a sequence (Product) of Characters.
    """
    element_type: List[UidType] = UidType("T:Character")


@dataclass
class Sum(Type):
    """
    A Sum type constructor.
    The elements of the element_type list are assumed to be variants
    forming a disjoint union; only one variant is actualized in each
    instance.
    """
    element_type: List[UidType]


@dataclass
class NamedAttribute(Type):
    """
    A named attribute of a Product composite type.
    """
    name: str
    element_type: UidType


# @dataclass
# class Map(Prod):
#     element_type: List[Tuple[UidType, UidType]]


# --------------------
# TypedGrometElm

@dataclass
class TypedGrometElm(GrometElm):
    """
    Base class for all Gromet Elements that may be typed.
    """
    type: Union[UidType, None]
    name: Union[str, None]
    metadata: Metadata


# --------------------
# Literal


@dataclass
class Literal(TypedGrometElm):
    """
    Literal base. (A kind of GAT Nullary Term Constructor)
    A literal is an instance of a Type
    """
    uid: Union[UidLiteral, None]  # allows anonymous literals
    value: 'Val'  # TODO


# TODO: "sublanguage" for specifying instances

@dataclass
class Val(GrometElm):
    val: Union[str, List[Union['Val', 'AttributeVal']]]


@dataclass
class AttributeVal(GrometElm):
    name: str
    val: Val


'''
Interval Number, Number, Number

Type: Pair = Prod(element_type[Int, String]) --> (<int>, <string>)
Literal: (type: "Pair", [3, "hello"])

Literal: (type: "Interval", [3, 6.7, 0.001])

SetIntegers = Prod(element_type=[Int])
SetIntegers10 = Prod(element_type=[Int], 10)
Literal: (type: "SetInt10", [1,2,3,3,4,52....])
'''


# --------------------
# Valued

@dataclass
class Valued(TypedGrometElm):
    """
    This class is never instantiated; it's purpose is to
        introduce attributes and a class-grouping into
        the class hierarchy.
    Typed Gromet Elements that may have a 'value'
    and the 'value_type' determines what types of values
    the element can have/carry.
    """
    value: Union[Literal, None]
    value_type: Union[UidType, None]


# --------------------
# Junction

@dataclass
class Junction(Valued):
    """
    Junction base.
    Junctions are "0-ary"
    """
    uid: UidJunction


# --------------------
# Port

@dataclass
class Port(Valued):
    """
    Port base.
    Ports are "1-ary" as they always *must* belong to a single Box
        -- you cannot have a Port without a host Box.
    Ports define an interface to a Box, whereby values may pass from
        outside of the Box into the internals of the Box.
    A Port may be optionally named (e.g., named argument)
    """
    uid: UidPort
    box: UidBox


@dataclass
class PortCall(Port):
    """
    "Outer" Port of an instance call to a Box definition.
    There will be a PortCall Port for every Port associated
        with the Box definition.
    """
    call: UidPort


# --------------------
# Wire

@dataclass
class Wire(Valued):
    """
    Wire base.
    Wires are "2-ary" as they connect up to two Valued elements,
        the 'src' and the 'tgt'.
        Despite the names, 'src' and 'tgt' are NOT inherently
            directed.
        Whether a Wire is directed depends on its 'type'
            within a Model Framework interpretation.
    All Wires have a 'value_type' (of the value they may carry).
    Optionally declared with a 'value', otherwise derived
        (from system dynamics).
    """
    uid: UidWire
    src: Union[UidPort, UidJunction, None]
    tgt: Union[UidPort, UidJunction, None]


# --------------------
# Box

@dataclass
class Box(TypedGrometElm):
    """
    Box base.
    A Box may have a name.
    A Box may have wiring (set of wiring connecting Ports of Boxes)
    """
    uid: UidBox
    ports: Union[List[UidPort], None]


@dataclass
class BoxCall(Box):
    """
    An instance "call" of a Box (the Box definition)
    """
    call: UidBox


@dataclass
class HasContents:
    """
    Mixin class, never instantiated.
    Bookkeeping for Box "contents" references.
        Natural to think of boxes "containing" (immediately
            contained) Boxes, Junctions and Wires that wire up
            the elements.
        This information functions like an index and
            supports easier identification of the elements
            that are the "top level contents" of a Box.
        Other Boxes do also have contents, but have special
            intended structure that is explicitly represented
    """
    wires: Union[List[UidWire], None]
    boxes: Union[List[UidBox], None]
    junctions: Union[List[UidJunction], None]


# @dataclass
# class BoxUndirected(Box):
#     """
#     Undirected Box base.
#     Unoriented list of Ports represent interface to Box
#     """
#
#     # NOTE: Redundant since Ports specify the Box they belong to.
#     # However, natural to think of boxes "having" Ports, and DirectedBoxes
#     # must specify the "face" their ports belong to, so for parity we'll
#     # have BoxUndirected also name their Ports
#     ports: Union[List[UidPort], None]
#
#
# @dataclass
# class BoxDirected(Box):
#     # NOTE: This is NOT redundant since Ports are not oriented,
#     # but DirectedBox has ports on a "orientation/face"
#     input_ports: Union[List[UidPort], None]
#     output_ports: Union[List[UidPort], None]


# Relations

@dataclass
class Relation(Box, HasContents):  # BoxUndirected
    """
    Base Relation
    """
    pass


# Functions

@dataclass
class Function(Box, HasContents):  # BoxDirected
    """
    Base Function
    Representations of general functions with contents wiring
        inputs to outputs.
    """
    pass


@dataclass
class Expr(GrometElm):
    """
    Assumption that may need revisiting:
      Expr's are assumed to always be declared inline as single
        instances, and may include Expr's in their args.
      Under this assumption, they do not require a uid or name
        -- they are always anonymous single instances.
    The call field of an Expr is a reference, either to
        (a) RefOp: primitive operator.
        (b) RefOp: an explicitly defined Box (e.g., a Function)
    The args field is a list of: UidPort reference, Literal or Expr
    """
    call: Union[RefFn, RefOp]
    args: Union[List[Union[UidPort, Literal, 'Expr']], None]


@dataclass
class Expression(Box):  # BoxDirected
    """
    A BoxDirected who's contents are an expression tree of Exp's.
    Assumptions:
      (1) Any "value" references in the tree will refer to the
        input Ports of the Expression. For this reason, there is
        no need for Wires.
      (2) An Expression always has only one output Port, but for
        parity with BoxDirected, the "output_ports" field name
        remains plural and is a List (of always one Port).
    """
    tree: Expr


@dataclass
class Predicate(Expression):
    """
    A Predicate is an Expression that has
        an assumed Boolean output Port
      (although we will not override the parent
       BoxDirected parent).
    """
    pass


@dataclass
class Conditional(Box):  # BoxDirected
    """
    Conditional
        ( TODO:
            Assumes no side effects.
            Assumes no breaks.
        )
    ( NOTE: the following notes make references to elements as they
            appear in Clay's gromet visual notation. )
    Terminology:
        *branch Predicate* (a type of Expression computing a
            boolean) represents the branch conditional test whose
            outcome determines whether the branch will be executed.
        *branch Function* represents the computation of anything in
            the branch
        A *branch* itself consists of a Tuple of:
                <Predicate>, <Function>, List[UidWire]
            The UidWire list denotes the set of wires relevant for
                completely wiring the branch Cond and Fn to the
                Conditional input and output Ports.
    Port conventions:
        Being a BoxDirected, a Conditional has a set of
            input and output Ports.
        *input* Ports capture any values of state/variables
            from the scope outside of the Conditional Box that
            are required by any branch Predicate or Function.
            (think of the input Ports as representing the relevant
            "variable environment" to the Conditional.)
        We can then think of each branch Function as a possible
            modification to the "variable environment" of the
            input Ports. When a branch Function is evaluated, it
            may preserve the values from some or all of the original
            input ports, or it may modify them, and/or it may
            introduce *new* variables resulting in corresponding
            new output Ports.
        From the perspective of the output Ports of the Conditional,
            we need to consider all of the possible new variable
            environment changes made by the selection of any branch.
            Doing so permits us to treat the Conditional as a modular
            building-block to other model structures.
            To achieve this, each branch Function must include in its
            output_ports a set of Ports that represent any of the
            "new variables" introduced by any branch Function.
            This allows us to have a single output_ports set for the
            entire Conditional, and whichever branch Function is
            evaluated, those Ports will be defined.
        NOTE: this does NOT mean those Ports are "Wired" and carry
            values; branch Function B1 may introduce a new variable
            "x" that branch Function B2 does not; B2 must still have
            a Port corresponding to "x", but it will not be Wired to
            anything -- it carries no value.
        Each branch Predicate has a single Boolean Port devoted to
            determining whether the branch is selected (when True).
    Definition: A Conditional is a...
        Sequence (List) of branches:
            Tuple[Predicate, Function, List[UidWire]]
        Each branch Predicate has a single boolean output Port
            whose state determines whether the branch Function
            will be evaluated to produce the state of the Conditional
            output Ports.
    Interpretation:
        GrFN provides unambiguous full data flow semantics.
        Here (for now), a gromet Conditional provides some abstraction
            away from pure data flow (but it is directly recoverable
            if desired).
        The interpretation convention:
            Branches are visited in order until the current branch
                Predicate evals to True
            If a branch Predicates evaluates to True, then branch
                Function takes the Conitional input_ports and sets
                determines the output_ports of the Conditional
                according to its internal components.
            If all no branch Predicate evaluats to True, then pass
                input Ports to outputs and new Ports have undefined
                values.
    """
    # branches is a List of
    #   ( <Predicate>1, <Function>, [<UidWire>+] )
    branches: List[Tuple[Union[Predicate, None], Function, List[UidWire]]]


@dataclass
class Loop(Box, HasContents):  # BoxDirected
    """
    Loop
        ( TODO:
            Assumes no side-effects.
            Assumes no breaks.
        )
    A BoxDirected that "loops" until an exit_condition (Predicate)
        is True.
        By "loop", you can think of iteratively making a copies of
            the Loop and wiring the previous Loop instance output_ports
            to the input_ports of the next Loop instance.
            (wiring of output-to-input Ports is done is order
             of the Ports).
    Definition / Terminology:
        A Loop has a *body* (because it is a Box), that
            represents the "body" of the loop.
        A Loop has an *exit_condition*, a Predicate that
            determines whether to evaluate the loop.
        A Loop has input_ports and output_ports (being
            a BoxDirected).
            A portion of the input_ports represent Ports
                set by the incoming external "environment"
                of the Loop.
            The remaining of the input_ports represent
                Ports to store state values that may be
                introduced within the Loop body
                but are not themselves initially used in
                (read by) the loop body wiring.
                In the initial evaluation of the loop,
                these Ports have no values; after one
                iteration of the Loop, these Ports
                may have their values assigned by the
                Loop body.
        Each input_port is "matched" to an output_port,
            based on the Port order within the input_ports
            and output_ports lists.
        A Loop has a *port_map* is a bi-directional map
            that pairs each Loop output Port with each Loop
            input Port, determining what the Loop input Port
            value will be based on the previous Loop iteration.
            Some input Port values will not be changed as a
            result of the Loop body, so these values "pass
            through" to that input's paired output.
            Others may be changed by the Loop body evaluation.
    Interpretation:
        The Loop exit_condition is evaluated at the very
            beginning before evaluating any of the Loop
            body wiring.
            IF True (the exit_condition evaluates to True),
                then the values of the Ports in input_ports
                are passed directly to their corresponding
                Ports in output_ports; The output_ports then
                represent the final value/state of the Loop
                output_ports.
            IF False (the exit_condition evaluates to False),
                then the Loop body wiring is evaluated to
                determine the state of each output Port value.
                The values of each output Port are then assined
                to the Port's corresponding input Port and
                the next Loop iteration is begun.
        This basic semantics supports both standard loop
            semantics:
            () while: the exit_condition is tested first.
            () repeat until: an initial input Port set to False
                make the initial exit_condition evaluation fail
                and is thereafter set to True in the Loop body.
    """
    exit_condition: Union[Predicate, None]


# Special forms for Pr/T (Predicate/Transition) Petri Nets, used by Galois

# @dataclass
# class CNFPredicate(Relation):
#     """
#     A Conjunctive Normal Form (CNF) Predicate.
#     Interpreted as a conjunction of Predicates:
#         All must be True for the CNFPredicate to be True.
#     """
#     terms: List[Predicate]
#
#
# @dataclass
# class PrTEvent(Box):
#     """
#     An Event in a Predicate/Transition (Pr/T) Petri Net: 'PTNet'.
#     All edges in a PrTEvent are undirected.
#     """
#     enable: CNFPredicate
#     rate: Relation
#     effect: Relation


# --------------------
# Variable

@dataclass
class Variable(TypedGrometElm):
    """
    A Variable is the locus of two representational roles:
        (a) denotes one or more elements that are Valued,
            i.e., carry a value (aka: states) and
        (b) denotes a modeled domain (world) state.
    Currently, (b) will be represented in Metadata.

    """
    uid: UidVariable
    states: List[Union[UidPort, UidWire, UidJunction]]


# --------------------
# Gromet top level

@dataclass
class Gromet(TypedGrometElm):
    uid: UidGromet
    root: Union[UidBox, None]
    types: Union[List[TypeDeclaration], None]
    literals: Union[List[Literal], None]
    junctions: Union[List[Junction], None]
    ports: Union[List[Port], None]
    wires: Union[List[Wire], None]
    boxes: List[Box]  # has to be one top-level Box
    variables: Union[List[Variable], None]


'''
@dataclass
class Measure(GrometElm):
    wire: Wire
    interval: ???: Tuple or Array
    type: Type  # Enum("instance", interval, steady_state)
'''


# -----------------------------------------------------------------------------
# Utils
# -----------------------------------------------------------------------------

def gromet_to_json(gromet: Gromet, tgt_file: Union[str, None] = None):
    if tgt_file is None:
        tgt_file = f"{gromet.name}_gromet_{gromet.type}.json"
    json.dump(asdict(gromet),  # gromet.to_dict(),
              open(tgt_file, "w"),
              indent=2)


# -----------------------------------------------------------------------------
# CHANGE LOG
# -----------------------------------------------------------------------------

"""
Changes 2021-05-27:
() Added the following mechanism by which a Box can be "called"
        in an arbitrary number of different contexts within the gromet.
    This include adding the following two TypedGrometElms:
    (1) BoxCall: A type of Box --- being a Box, the BoxCall itself has 
        it's own UidBox uid (to represent the instance) and its own 
        list of Ports (to wire it within a context). 
        The BoxCall adds a 'call' field that will consist of the UidBox 
            of another Box that will serve as the "definition" of the 
            BoxCall.
        An arbitrary number of different BoxCalls may "call" this 
            "definition" Box. There is nothing else about the 
            "definition" Box that makes it a definition -- just that 
            it is being called by a BoxCall.
        The BoxCall itself will have no internal contents, it's
            internals are defined by the "definition" Box.
        For each Port in the "definition" Box, BoxCall will have 
            a corresponding PortCall Port; this PortCall will reference 
            the "definition" Box Port. 
    (2) PortCall: A tye of Port -- being a Port, the PortCall has it's 
        own UidPort uid (to represent the instance), and adds a 'call' 
        field that will be the UidPort of the  Port on the "definition" 
        Box referenced by a BoxCall.
        The 'box' field of the PortCall will be the UidBox of the BoxCall
            instance.

Changes 2021-05-23:
() Added notes at top on Model Framework element Types
() Removed Event
() Wire tgt -> tgt

Changes 2021-05-21:
() Convention change: Model Framework typing will now be represented
    exclusively by the 'type' attribute of any TypedGrometElm.
    This is a much more clean way of separating syntax (the elements) from
        their semantics (how to interpret or differentially visualize).
    A Model Framework will designate what types are the TypedGrometElms may be. 
    For example, a Function Network will have 
        Port types: PortInput, PortOutput
        Wire types: WireDirected, WireUndirected
    For example, a Bilayer will have
        Port types: PortInput, PortOutput, PortRate
        Wire types: W_in, W_pos, W_neg
        Junction types; JunctionState, JunctionTangent
    In general, a Model Framework type will only be specified when
        a distinction between more than one type is needed.
() Changes to Wire:
    WireDirected and WireUndirected have been removed. All Wires have
        input -> src
        output -> tgt
        Despite the names, these are not necessarily directed, just in-principle
            distinction between the two.
        The 'type' determines whether a Wire has the property of being directed.
() Removed BoxDirected and BoxUndirected.
    The "facing" that Ports are associated with will now be represented
        in the Port 'type' Model Framework.
    Top-level Box now has 'ports' attribute. This is still required
        as we need to preserve information about ordering of Ports,
        both for positional arguments and for pairing inputs to outputs in Loop.
() Valued now includes 'value_type' attribute. 
    Previously was using Port, Junction and Wire 'type' to capture the 
        value type, but now the value type will be explicitly represented 
        by the value_type attribute.
    The 'type' attribute will instead be reserved for Model Framework type.
() Added 'name' to TypedGrometElm, so all children can be named
    The purpose of name: provide model domain-relevant identifier to model component 
() Metadatum is no longer a TypedGrometElm, just a GrometElm, as it is not
    itself a component of a model; it is data *about* a model component.
() Gromet object: added 'literals' and 'junctions' attributes
TODO:
    () Update docs to make explicit the convention for Port positional arguments
    () Update Loop docs to make explicit the convention for Port pairing

Changes 2021-05-17:
() FOR NOW: commenting out much of the Types, as likely source of
    confusion until sorted out.
() Added HasContents as a "mixin" that provides explicit lists
    of junctions, boxes, and wires.
    This is mixed-in to: Loop, Function and Relation.
() Added Valued class, a type of TypedGrometElm, that introduced
    the attributes of "value" (i.e., for things that can carry
    a value). This is now the parent to Junction, Port and Wire.
    This also distinguishes those classes from Box, which does
        not have a value, but is intended to transform or assert
        relationships between values.
() Changes to Loop:
    Removed "port_map" -- the pairing of input and output Ports
        is now based on the order of Ports in the input_ports and
        output_ports lists.
    Cleaned up documentation to reflect this.

Changes [2021-05-09 to 2021-05-16]:
() Added parent class TypedGrometElm inherited by any GrometElm that
    has a type. GrometElm's with types play general model structural roles,
    while other non-typed GrometElms add element-specific structure (such
    as Expr, RefFn, RefOp, Type, etc...)
() UidOp will now be reserved ONLY for primitive operators that are not
    explicitly defined within the gromet.
    All other "implementations" of transformations must have associated
        Box definitions with UidBox uids
() Introduced RefOp and RefFn to explicitly distinguish between the two
() Exp renamed to Expr
() Expr field "operator" -> "call", where type is now either RefOp or RefFn
() Expression changed from being a child of Function to being child of BoxDirected
() Changed Predicate to being an Expression
() Added Conditional, child of BoxDirected
() Added Loop, child of BoxDirected
() WireUndirected
    ports changed from List[Union[UidPort, UidJunction]]
    to Union[Tuple[UidPort, UidJunction],
             Tuple[UidJunction, UidPort],
             Tuple[UidPort, UidPort]]
    - should only have one pairwise connection per UndirectedWire

"""
