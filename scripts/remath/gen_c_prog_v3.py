# import os
# from pathlib import Path
from abc import ABC, abstractmethod
import random
from typing import Any, Union, Sequence, Set, List, Dict, Tuple
from dataclasses import dataclass
from collections import Counter

"""
Version 3

Supports
() expression trees
    () unary, binary operators
    () functions 
() functions
() globals

ASSUMPTIONS / OBSERVATIONS:
(1) Not using 'long double' type for now
    Doing so leads to binary handling of long double data that Ghidra 
      does not appear to be able to recover 
(2) GCC -O0 (lowest optimization) DOES indeed pre-compute values when 
      (primitive?) operators only involve literal values.
    GCC -O0 appears to NOT do this when at least one of the literal values
      is passed via a variable.
    For this reason, will introduce at least one literal-assigned variable
    for any operator (that is not otherwise fn of 
        See: expr_00.c
"""

# TODO:
#  NOTE: for now (in this version 3)
#    all introduced variables are assumed to be:
#    (a) declared ta the top of function body
#    (b) all var decls are assigned literals (to avoid, for now, ensuring there are no unassigned vars before access)
#  FOR A FUTURE VERSION (version 4):
#    we could relax both of the above assumptions by
#    (a) associating declarations at the closest control structure
#        within which the expr accesses the var
#    (b) for each use, trace path from useage backward and upward
#        to see if var gets set; if not, then decl needs value assignment
#        Any other decls could then remain unassigned until later...

# TODO:
#  (1) generate conditional conditions
#  (2) generate while loop conditions
#  (3) generate for loop conditions

# random.seed(a=6)

# https://codeforwin.org/2017/08/list-data-types-c-programming.html
# https://www.geeksforgeeks.org/c-data-types/


TAB_SIZE = 2
TAB_STR = ' '*TAB_SIZE


# -----------------------------------------------------------------------------
# VarGen - generate variable names
# -----------------------------------------------------------------------------

class VarGen:
    """
    Utility for generating new sequentially-numbered variable names
    of format: <base><count>
    """

    def __init__(self, base='x'):
        self.var_counter = 0
        self.base = base

    def get_name(self) -> str:
        """
        Generate the next sequentially-numbered variable
        :return:
        """
        vname = f'{self.base}{self.var_counter}'
        self.var_counter += 1
        return vname

    def is_var(self, _string: str) -> bool:
        """
        Test whether a provided string is an instance of a variable
        that has already been generated.
        :param _string:
        :return:
        """
        if not isinstance(_string, str):
            return False
        if _string.startswith(self.base):
            non_base = _string[len(self.base):]
            for c in non_base:
                if not c.isdigit():
                    return False
            if int(non_base) <= self.var_counter - 1:
                return True
        return False


# TODO: turn into proper unit test!
def mytest_var_gen():
    var_gen = VarGen()
    for i in range(10):
        var_gen.get_name()
    assert var_gen.is_var('x3') is True
    assert var_gen.is_var('x9') is True
    assert var_gen.is_var('x10') is False  # should only include 0-9
    assert var_gen.is_var('3') is False

    var_gen = VarGen('xy')
    for i in range(8):
        var_gen.get_name()
    assert var_gen.is_var('xy3') is True
    assert var_gen.is_var('xy7') is True
    assert var_gen.is_var('xy8') is False  # should only include 0-8
    assert var_gen.is_var('x3') is False
    assert var_gen.is_var('y3') is False
    assert var_gen.is_var('3') is False
    assert var_gen.is_var('x3y') is False


mytest_var_gen()


# -----------------------------------------------------------------------------
# TypeCats and Types
# -----------------------------------------------------------------------------

# ground_type: a specific legal c type
# typecat: a type category (and abstraction over a set of ground types)
# A map of typecat to ground_types.
# NOTE: The index order of the ground_types corresponds to their cast precedence.
#       Examples:
#         in typecat 'ANY', given arguments of 'int' and 'long', the return
#           ground_type is 'long' b/c 'int' is index 0 while 'long' is index 1
#         similarity (also in typecat 'ANY'), given 'long' and 'float', the return
#           ground_type is 'float' b/c 'float' index 3 > 'long' index 1
MAP_TYPECAT_TO_TYPE = \
    {'ANY': ('int', 'long', 'long long',
             'float', 'double'),  # 'long double'
     'REAL_FLOATING': ('float', 'double'),  # 'long double'
     'DOUBLE': ('double',),
     'NON_FLOAT': ('int', 'long', 'long long'),
     'INT': ('int',)}
TYPES = MAP_TYPECAT_TO_TYPE['ANY']
TYPECATS = tuple(MAP_TYPECAT_TO_TYPE.keys())


def sample_literal(literal_type, _map=None):
    if _map is None:
        _map = MAP_TYPECAT_TO_TYPE
    if 'REAL_FLOATING' in _map and literal_type in _map['REAL_FLOATING']:
        return random.uniform(-10, 10)
    elif 'DOUBLE' in _map and literal_type in _map['DOUBLE']:
        return random.uniform(-10, 10)
    elif 'NON_FLOAT' in _map and literal_type in _map['NON_FLOAT']:
        return random.randint(-100, 100)
    else:
        raise Exception(f"ERROR sample_literal():\n"
                        f"Unsupported type '{literal_type}'")


"""
Map type category to a priority score,
with 0 being lowest priority and 2 being highest.
"""
TYPE_PRIORITY = \
    {'ANY': 0,
     'REAL_FLOATING': 1,
     'DOUBLE': 2,
     'NON_FLOAT': 3,
     'INT': 4}


def get_type_priority(t: str) -> int:
    """
    Returns the type priority (integer) of t's type category
    :param t: a string representing a type category
    :return: integer representing the type priority
    """
    if t not in TYPE_PRIORITY:
        raise Exception(f'ERROR get_type_priority():\n'
                        f'type {t} is not handled\n{TYPE_PRIORITY}')
    else:
        return TYPE_PRIORITY[t]


def contract_type(target_type: str, other_type: str) -> str:
    """
    Returns the type with the highest priority.
    :param target_type: a string representing a type category
    :param other_type: a string representing a type category
    :return:
    """
    if get_type_priority(target_type) > get_type_priority(other_type):
        return target_type
    else:
        return other_type


def contract_list_to_target_type(target_type: str, other_types: Tuple[str]) -> Tuple[str]:
    """
    For each type category in other_types, computes the highest priority type
      compared to target_type, and returns these as a tuple.
    :param target_type: a string representing a type category
    :param other_types: a tuple of strings representing type categories
    :return: tuple of strings representing type categories
    """
    return tuple([contract_type(target_type, other_type) for other_type in other_types])


TYPE_STRING_FORMAT = \
    {'int': 'd', 'long': 'd', 'long long': 'd',
     'float': 'g', 'double': 'g', 'long double': 'g'}


# -----------------------------------------------------------------------------
# Operator Definitions
# -----------------------------------------------------------------------------

# Definitions of operator categories
# Each category is a dictionary that that maps:
#   <operator_string_name> : ( <type_signature>, <syntax>, optional: <include_library> )
#   <type_signature> := Tuple[ <return_type>, <arg1_type>, <arg2_type>, ... ]
#     NOTE: These type specifications are expressed as TYPECATS
#   <syntax> := 'INFIX' | 'PREFIX'
#     'INFIX' : <arg1> OP <arg2>
#     'PREFIX' : OP(<arg1>...)
#   <include_library> := String for the entire include line
# When <include_library> is not included, then assumed natively available.


OP_ARITHMETIC = \
    {'+': (('ANY', 'ANY', 'ANY'), 'INFIX', None),
     '-': (('ANY', 'ANY', 'ANY'), 'INFIX', None),
     '*': (('ANY', 'ANY', 'ANY'), 'INFIX', None),
     '/': (('ANY', 'ANY', 'ANY'), 'INFIX', None),
     }

# NOTE: Not supported by dynamic analysis
OP_ARITHMETIC_MOD = \
    {'%': (('INT', 'INT', 'INT'), 'INFIX', None), }

# NOTE: Not supported by dynamic analysis
OP_BITWISE_LOGICAL = \
    {'&': (('NON_FLOAT', 'NON_FLOAT', 'NON_FLOAT'), 'INFIX', None),  # bitwise AND
     '|': (('NON_FLOAT', 'NON_FLOAT', 'NON_FLOAT'), 'INFIX', None),  # bitwise inclusive OR
     '^': (('NON_FLOAT', 'NON_FLOAT', 'NON_FLOAT'), 'INFIX', None),  # bitwise exclusive OR
     }

OP_RELATIONS = \
    {'==': (('INT', 'ANY', 'ANY'), 'INFIX', None),
     '!=': (('INT', 'ANY', 'ANY'), 'INFIX', None),
     '>': (('INT', 'ANY', 'ANY'), 'INFIX', None),
     '<': (('INT', 'ANY', 'ANY'), 'INFIX', None),
     '>=': (('INT', 'ANY', 'ANY'), 'INFIX', None),
     '<=': (('INT', 'ANY', 'ANY'), 'INFIX', None),
    }

# logical operators
# https://stackoverflow.com/questions/39730583/return-value-of-a-boolean-expression-in-c
OP_LOGICAL = \
    {'!': (('INT', 'INT'), 'PREFIX', None),  # UNARY
     '&&': (('INT', 'INT', 'INT'), 'INFIX', None),  # BINARY
     '||': (('INT', 'INT', 'INT'), 'INFIX', None),  # BINARY
    }

# definitions for functions from math.h
OP_MATH_H = \
    {'sqrt': (('ANY', 'ANY'), 'PREFIX', '#include <math.h>'),  # double sqrt(double x);
     'sin': (('ANY', 'ANY'), 'PREFIX', '#include <math.h>'),  # double sin(double x);
     'fmin': (('ANY', 'ANY', 'ANY'), 'PREFIX', '#include <stdlib.h>'),  # any_type min (any_type a, any_type b);
     'fmax': (('ANY', 'ANY', 'ANY'), 'PREFIX', '#include <stdlib.h>'),  # any_type max (any_type a, any_type b);
     }   # double sin(double x);

# Definitions for functions from stdlib.h
OP_STDLIB_H = \
    {'abs': (('ANY', 'ANY'), 'PREFIX', '#include <stdlib.h>'),  # any_type abs (any_type);
     }


# NOTE: CTM 2022-05-10: turning off use of OP_STDLIB_H for now (need to figure out why `abs` does not show up as fn call)
# NOTE: type inspection warns that OP_MATH_H has a different value type signature
OP_DEFINITIONS = OP_ARITHMETIC | OP_MATH_H  # | OP_STDLIB_H

# Sequence of operators
OPS = tuple(OP_DEFINITIONS.keys())


def collect_ops_compatible_with_types():
    map_type_to_ops = dict()

    def add(t, op):
        if t in map_type_to_ops:
            map_type_to_ops[t].append(op)
        else:
            map_type_to_ops[t] = [op]

    # Build map of types to ops
    for t in TYPES:
        for op, (args, syntax, include) in OP_DEFINITIONS.items():
            return_type = args[0]
            if return_type in TYPECATS and t in MAP_TYPECAT_TO_TYPE[return_type]:
                add(t, op)
            elif t == return_type:
                add(t, op)

    # Build map of typecats to ops
    for tcat, ts in MAP_TYPECAT_TO_TYPE.items():
        tset = set()
        for t in ts:
            tset |= set(map_type_to_ops[t])
        map_type_to_ops[tcat] = sorted(list(tset))

    return map_type_to_ops


MAP_RETURN_TYPE_TO_OPS = collect_ops_compatible_with_types()


# MAP_RETURN_TYPE_TO_OPS
# <return_type> : list of <operator>
# MAP_OP_TO_TYPECATS
# <operator> : (<return_type>, <arg_type>, ...)
# MAP_TYPECAT_TO_TYPE
# <type_category> : list of <type>


# import sys
# print("TYPES")
# print(TYPES)
# print("TYPECATS")
# print(TYPECATS)
# print("MAP_TYPECAT_TO_TYPE")
# print(MAP_TYPECAT_TO_TYPE)
# print("OP_DEFINITIONS")
# print(OP_DEFINITIONS)
# print("OPS")
# print(OPS)
# print("MAP_RETURN_TYPE_TO_OPS")
# print(MAP_RETURN_TYPE_TO_OPS)
# sys.exit()


def debug_print_MAP_RETURN_TYPE_TO_OPS():
    print('\nMAP_RETURN_TYPE_TO_OPS:')
    for t, ops in MAP_RETURN_TYPE_TO_OPS.items():
        print(f'{t}: <{len(ops)}> {ops}')
    print()


# For debugging:
# def collect_ops_by_return_typecat(bin_ops):
#     map_return_typecat_to_op = dict()
#     for op, args in bin_ops.items():
#         if args[0] in map_return_typecat_to_op:
#             map_return_typecat_to_op[args[0]].append(op)
#         else:
#             map_return_typecat_to_op[args[0]] = list(op)
#     return map_return_typecat_to_op
#
#
# # Map from return type to BIN_OP
# MAP_RETURN_TYPECAT_TO_OP = collect_ops_by_return_typecat(MAP_OP_TO_ARGS)
#
# print("\nMAP_RETURN_TYPECAT_TO_OP:")
# for t, ops in MAP_RETURN_TYPECAT_TO_OP.items():
#     print(f'{t}: {ops}')


def sample_uniform_operator(op_set: Sequence[str]) -> Tuple[str, str, Tuple[str]]:
    """
    Given a sequence of operators (as strings), uniformly randomly choose
      one, retrieve it's type signature, and return a tuple representing:
        <operator_name[str]>, <return_type[str]>, list of <argument_type[str]>
    :param op_set: sequence of operators (as strings)
    :return: (<operator>, <return_type>, list of <argument_type>)
    """
    op = random.choice(op_set)
    args = OP_DEFINITIONS[op]
    return op, args[0], args[1:]


# -----------------------------------------------------------------------------
# Generator Config
# -----------------------------------------------------------------------------

@dataclass
class GeneratorConfig:
    """
    Version 3 Program Generation configuration
    Params defined as tuples represent range of <min>, <max>
    """
    map_typecat_to_type: Dict[str, Tuple]
    main_default_cli: bool   # whether main fn includes argc, argv

    globals_num: Tuple[int, int]
    globals_prob_set: float           # probability that global gets within each fn

    functions_num: Tuple[int, int]    # number of functions
    function_arguments_num: Tuple[int, int]  # number of function arguments
    functions_allow_recursive_calls: bool     # flag for whether to allow recursive calls

    expressions_num: Tuple[int, int]    # number of expressions per block
    operators_num: Tuple[int, int]      # number of operators per expression
    operators_primitive: Dict           # the primitive operators provided

    # probability of creating a new var (as opposed to: (a) using existing local or global or (b) inline literal)
    create_new_var_prob: float

    conditional_prob: float             # probability of creating conditionals
    conditionals_num: Tuple[int, int]   # when creating conditionals, how many?
    conditional_else_prob: float        # probability that a conditional has an else branch
    conditional_nesting_level: int      # 1 = no nesting, otherwise (>1) nesting up to level depth
    conditional_return_prob: float      # probability that a conditional branch has a return

    loop_prob: float                    # probability of creating loops
    loop_num: Tuple[int, int]           # when creating loops, how many?
    loop_for_prob: float                # probability that loop is a for-loop (otherwise while)
    loop_while_nesting_level: int       # 1 = no nesting, otherwise (>1) nesting up to level depth


CONFIG_1 = GeneratorConfig(
    map_typecat_to_type=MAP_TYPECAT_TO_TYPE,

    main_default_cli=False,  # flag for whether main includes default cli arguments: argc, argv

    globals_num=(0, 4),
    globals_prob_set=0.2,  # prob global gets set in each function

    functions_num=(1, 6),
    function_arguments_num=(1, 8),
    functions_allow_recursive_calls=True,  # flag for whether to allow recursive fn calls

    expressions_num=(1, 8),
    operators_num=(1, 6),
    operators_primitive=OP_DEFINITIONS,
    create_new_var_prob=0.2,

    conditional_prob=0,          # probability of creating conditionals
    conditionals_num=(4, 4),       # when creating conditionals, how many?
    conditional_else_prob=0.5,     # probability that a conditional has an else branch
    conditional_nesting_level=3,   # 1 = no nesting, otherwise (>1) nesting up to level depth
    conditional_return_prob=0.25,  # TODO: Not yet being used

    loop_prob=0,                 # probability of creating loops
    loop_num=(3, 3),               # when creating loops, how many?
    loop_for_prob=0.5,             # probability that loop is a for-loop (otherwise while)
    loop_while_nesting_level=3
)


"""
TODO 
() Think through when functions should be called: 
    only after defined, 
    OR anyone can call anyone :
        First define signatures, add to OP_DEFINITIONS, then expressions can call them.
        BUT, then need to ensure no disconnected calling networks
            - could do post-processing to ensure any function calls could then be traced back to main.

Globals 1 - create signature
    GeneratorConfig.globals_num
    generate global names
    sample type
    initially no literal assignments
    add each global to var set that can be accessed
Functions 1 - create signature
    Always create main
    GeneratorConfig.functions_num -- sample how many additional functions
    generate function name
    sample number of arguments: GeneratorConfig.function_arguments_num
    sample return type and argument types

Globals 2 - ensure each global is get by at least one function (could be any)
    
Functions 2 - fill out body
    generate expressions
        
    if self.globals_to_be_set is not empty:
        if self.globals_set_at_body_top is True (i.e., this is a main)
            then set global at the top of the body
        else:
            introduce anywhere where globals might be set.
Main 1
    Generate expressions
        
    Between each expression, check whether to set global

Do final pass: 

if Variable gets set, then don't need to 
do not access a global before it is set
"""


class VariableDecl:
    """
    Declaration of a Variable with an optional literal assignment
    """
    def __init__(self, name: str,
                 var_type: str = None,
                 var_value: Union[Any, None] = None,
                 var_type_ptr: Union[str, None] = None,
                 var_type_arr: bool = False,
                 is_arg: bool = False):
        self.name: str = name
        self.var_type: str = var_type  # the type of the variable
        self.var_type_ptr: Union[str, None] = var_type_ptr  # whether decl is a ptr (and what kind)
        self.var_type_arr: bool = var_type_arr  # whether decl is an array
        self.var_value: Union[str, None] = var_value  # a literal value assigned at declaration
        self.is_arg: bool = is_arg  # var is an argument (parameter) of a function, not to set value

        # <fn_name>: (<PNodeExpr>, <ExprTree.index_of_var_assignment>)
        self.get: Dict[str, List[Tuple['PNodeExpr', int]]] = dict()

        self.set: Dict[str, List['PNodeExpr']] = dict()  # <fn_name>: <PNodeExpr>)

    def __repr__(self):
        name = self.name
        if self.var_type_ptr:
            name = f'{self.var_type_ptr}{name}'
        if self.var_type_arr:
            name = f'{name}[]'
        if self.is_arg:
            return f'<VarDecl ARG {self.var_type} {name} = {self.var_value}>'
        else:
            return f'<VarDecl {self.var_type} {name} = {self.var_value}>'

    def update_get(self, function_name: str, pnode_expr: 'PNodeExpr', index_of_var_assignment: int):
        if function_name in self.get:
            self.get[function_name].append((pnode_expr, index_of_var_assignment))
        else:
            val: Tuple['PNodeExpr', int] = (pnode_expr, index_of_var_assignment)
            self.get[function_name] = list()
            self.get[function_name].append(val)

    def update_set(self, function_name: str, pnode_expr: 'PNodeExpr'):
        if function_name in self.set:
            self.set[function_name].append(pnode_expr)
        else:
            self.set[function_name] = list()
            self.set[function_name].append(pnode_expr)

    def to_c_string(self):
        name = self.name
        if self.var_type_ptr:
            name = f'{self.var_type_ptr}{name}'
        if self.var_type_arr:
            name = f'{name}[]'
        if self.var_value:
            return f'{self.var_type} {name} = {self.var_value}'
        else:
            return f'{self.var_type} {name}'


def op_def_dict_to_fn_spec_dict(op_def_dict: Dict):
    """
    Converts an operator definition dictionary into a dictionary with
        <fn_name> : <FunctionSpec>
    An operator definition dictionary has this schema:
        str:<op_name> : ( (str:<return_type>, str:<arg1_type>...), <syntax>, <include_library> )
    :param op_def_dict: An operator definition dictionary
    :return: function_spec_dictionary
    """
    function_specs_dict = dict()
    for fn_name, (signature, syntax, include_library) in op_def_dict.items():
        return_type = signature[0]
        args = list()
        arg_name_vargen = VarGen('a')
        for arg_type in signature[1:]:
            arg_name = arg_name_vargen.get_name()
            args.append(VariableDecl(arg_name, arg_type))
        function_specs_dict[fn_name] = FunctionSpec(
            name=fn_name, args=args,
            return_type=return_type,
            syntax=syntax,
            include_library=include_library
        )
    return function_specs_dict


# TODO Every function has
#  (1) a return (the current v3 default)
#  OR
#  (2) all conditional branches have returns (and no more expressions after the last conditional block)
class FunctionSpec:
    """
    Specification of a function
    """

    def __init__(self, name: str,
                 args: Union[List[VariableDecl], None],
                 return_type: str,
                 syntax: str = 'PREFIX',  # or 'INFIX' for some binary operators
                 include_library: Union[str, None] = None,
                 globals_to_be_get: Union[List[str], None] = None,
                 globals_to_be_set: Union[List[str], None] = None,
                 # globals_set_at_body_top: bool = False,
                 fns_to_call: Union[List[str], None] = None,
                 # body: 'FunctionBody' = None,
                 local_vargen: VarGen = None):
        self.name: str = name
        if local_vargen is None:
            self.local_vargen: VarGen = VarGen('x')
        else:
            self.local_vargen: VarGen = local_vargen
        if args:
            self.args: List[VariableDecl] = args
        else:
            self.args: List[VariableDecl] = list()
        self.return_type: str = return_type
        self.syntax: str = syntax
        self.include_library: str = include_library

        if globals_to_be_get is None:  # list of globals that need to be get
            self.globals_to_be_get: list = list()
        else:
            self.globals_to_be_get: list = globals_to_be_get

        if globals_to_be_set is None:  # list of globals that need to be set
            self.globals_to_be_set: list = list()
        else:
            self.globals_to_be_set: list = globals_to_be_set

        # TODO: Unclear this is needed
        #  flag for whether globals should be set at body top
        #  original idea was to at least use this in main, to ensure globals set early
        #  But unclear this is needed or useful.
        # self.globals_set_at_body_top: bool = globals_set_at_body_top

        # list of fns that must be called at least onc by this fn
        if fns_to_call is None:
            self.fns_to_call: list = list()
        else:
            self.fns_to_call: list = fns_to_call

        # self.body: FunctionBody = body
        self.called_by: Set[str] = set()  #

    def to_c_string_signature(self):
        arg_string = ''
        if self.args is not None:
            arg_string = ', '.join([arg.to_c_string() for arg in self.args])
        return f'{self.return_type} {self.name}({arg_string})'

    def pprint(self, indent=0):
        indent_str = TAB_STR*indent
        print(f'{indent_str}{self.to_c_string_signature()}')
        # if self.body:
        #     print(f'{indent_str}{self.to_c_string_signature()}')
        #     self.body.to_string()
        # else:
        #     print(f'{indent_str}{self.to_c_string_signature()}')
        indent_str = TAB_STR*(indent+1)
        if self.globals_to_be_get:
            print(f'{indent_str}globals_to_be_get: {self.globals_to_be_get}')
        if self.globals_to_be_set:
            print(f'{indent_str}globals_to_be_set: {self.globals_to_be_set}')
            # TODO possibly remove?: print(f'{indent_str}globals_set_at_body_top: {self.globals_set_at_body_top}')


class ExprTree:
    """
    An Expression Tree
    """
    def __init__(self, num_ops: int,
                 program_spec: 'ProgramSpec',
                 function_spec: 'FunctionSpec',
                 args_that_must_be_get: Union[List[VariableDecl], None] = None):
        self.program_spec: ProgramSpec = program_spec     # needed to access globals, functions, primitive operators

        # needed to access
        #   globals_to_be_get
        #   function_spec name (if not allowing recursive calls)
        #   fns_to_call : these fns must be called at least once during generation of expression tree
        self.function_spec: FunctionSpec = function_spec

        self.args_that_must_be_get = args_that_must_be_get

        self.num_ops: int = num_ops
        self.last_index: int = 0    # The highest index
        self.unassigned_indices: Set[int] = {0}  # indices that have not yet been assigned
        self.op_indices: Set[int] = set()        # indices of operators
        self.map_index_to_op: Dict[int, FunctionSpec] = dict()
        self.map_index_to_children: Dict[int, List[int]] = dict()   # map parent index to list of child indices
        self.map_index_to_op_arg: Dict[int, VariableDecl] = dict()  # map index to the argument decl of the operator
        self.map_index_to_var_assignments: Dict[int, VariableDecl] = dict()  # map index to variable decl
        self.map_index_to_literal_assignments: Dict[int, Any] = dict()   # map index to literal values
        # self.var_literal_assignments: List[Tuple[str, str, Any]] = list()  # (var_name, type, literal_value)

    def sample(self,
               fns_that_must_be_called: Union[List[str], None] = None,
               # args_that_must_be_get: Union[List[VariableDecl], None] = None
               ):
        """

        :param fns_that_must_be_called: list of any functions that *must* be called
        :return:
        """
        remaining_ops_to_assign = self.num_ops
        # First assign any functions that must be called
        if fns_that_must_be_called:
            remaining_ops_to_assign -= len(fns_that_must_be_called)
            if remaining_ops_to_assign < 0:
                raise Exception(f'ExprTree.sample(): remaining_ops_to_assing < 0, which should not happen'
                                f'  num_ops={self.num_ops}, fns_that_must_be_called={fns_that_must_be_called}')
            for fn_name in fns_that_must_be_called:
                idx = random.choice(list(self.unassigned_indices))  # sample index within ExprTree
                self.add_op_at(index=idx, op=self.program_spec.get_fn(fn_name))

        # Now assign any remaining operators (fns)
        for i in range(remaining_ops_to_assign):
            idx = random.choice(list(self.unassigned_indices))  # sample index within ExprTree
            if self.program_spec.params.functions_allow_recursive_calls:
                fn = self.program_spec.sample_fn()
            else:
                fn = self.program_spec.sample_fn(ignore={self.function_spec.name})
            self.add_op_at(index=idx, op=fn)

    def add_var_at(self, index: int, var_decl: VariableDecl):
        self.map_index_to_var_assignments[index] = var_decl
        self.unassigned_indices.remove(index)

    def add_literal_at(self, index: int, value: Any):
        self.map_index_to_literal_assignments[index] = value
        self.unassigned_indices.remove(index)

    def add_op_at(self, index: int, op: FunctionSpec):
        num_args = len(op.args)
        new_indices = list(range(self.last_index + 1, self.last_index + num_args + 1))

        # update mapping of new indices to the VariableDecl of operator args
        for i, idx in enumerate(new_indices):
            self.map_index_to_op_arg[idx] = op.args[i]

        self.last_index += num_args
        self.unassigned_indices |= set(new_indices)
        self.unassigned_indices.remove(index)
        self.op_indices.add(index)
        self.map_index_to_op[index] = op
        self.map_index_to_children[index] = new_indices

    def swap_new_op_at(self, index: int, new_op: FunctionSpec, verbose=False) -> Set[int]:
        """
        Helper to inset an op at an index that already has an op.
        The new op will now occupy the index of the existing (old) op
          and the old op will be set to be one of the children of
          the new op.
        :param index:
        :param new_op:
        :return: Set of new available (unassigned) children of new_op
        """
        if index not in self.op_indices:
            self.pprint()
            raise Exception(f'ExprTree.swap_new_op_at(): index={index} not in self.op_indices={self.op_indices}')
        else:
            num_args = len(new_op.args)

            new_child_indices = list(range(self.last_index + 1, self.last_index + num_args + 1))

            # update mapping of new indices to the VariableDecl of operator args
            for i, idx in enumerate(new_child_indices):
                self.map_index_to_op_arg[idx] = new_op.args[i]

            if verbose:
                print(f'new_child_indices={new_child_indices}')
            self.last_index += num_args

            old_op = self.map_index_to_op[index]
            old_op_new_index = random.choice(new_child_indices)
            self.op_indices.add(old_op_new_index)
            self.map_index_to_op[old_op_new_index] = old_op
            self.map_index_to_children[old_op_new_index] = self.map_index_to_children[index]
            self.map_index_to_children[index] = new_child_indices
            remaining_new_child_indices = set(new_child_indices)
            if verbose:
                print(f'remaining_new_child_indices: {remaining_new_child_indices}')
            remaining_new_child_indices.remove(old_op_new_index)
            if verbose:
                print(f'remaining_new_child_indices: {remaining_new_child_indices} (after removing {old_op_new_index})')
            self.unassigned_indices |= remaining_new_child_indices
            self.map_index_to_op[index] = new_op
            return remaining_new_child_indices

    def to_c_string(self, index=0):
        if index in self.map_index_to_op:
            op = self.map_index_to_op[index]
            if op.syntax == 'INFIX':
                return f'({self.to_c_string(self.map_index_to_children[index][0])} ' \
                       f'{op.name} ' \
                       f'{self.to_c_string(self.map_index_to_children[index][1])})'
            elif op.syntax == 'PREFIX':
                args = ', '.join([self.to_c_string(child_idx) for child_idx in self.map_index_to_children[index]])
                return f'{op.name}({args})'
        elif index in self.map_index_to_var_assignments:
            return f'{self.map_index_to_var_assignments[index].name}'
        elif index in self.map_index_to_literal_assignments:
            return f'{self.map_index_to_literal_assignments[index]}'
        else:
            return f'<_{index}>'  # '_' is for unassigned -- If appears here, expr tree is incomplete

    def to_string(self, index=0, semicolon: bool = False):
        eol = ''  # end of line: either nothing (default) or semicolon (when end of expression)
        if index == 0 and semicolon is True:
            eol = ';'
        if index in self.map_index_to_op:
            op = self.map_index_to_op[index]
            if op.syntax == 'INFIX':
                return f'({self.to_string(self.map_index_to_children[index][0])} ' \
                       f'{op.name} ' \
                       f'{self.to_string(self.map_index_to_children[index][1])}){eol}'
            elif op.syntax == 'PREFIX':
                args = ', '.join([self.to_string(child_idx) for child_idx in self.map_index_to_children[index]])
                return f'{op.name}({args}){eol}'
        elif index in self.map_index_to_var_assignments:
            return f'<v{index}={self.map_index_to_var_assignments[index].name}>'
        elif index in self.map_index_to_literal_assignments:
            return f'<val{index}={self.map_index_to_literal_assignments[index]}>'
        else:
            return f'<_{index}>'  # '_' is for unassigned

    def pprint(self):
        print(f'ExprTree {self}')
        print(f'    {self.to_string()}')
        print(f'    self.last_index: {self.last_index}')
        print(f'    self.unassigned_indices: {self.unassigned_indices}')
        print(f'    self.op_indices: {self.op_indices}')
        print(f'    self.map_index_to_op: {self.map_index_to_op}')
        print(f'    self.map_index_to_children: {self.map_index_to_children}')
        print(f'    self.map_index_to_var_assignments: {self.map_index_to_var_assignments}')
        print(f'    self.map_index_to_val_assignments: {self.map_index_to_literal_assignments}')


# TODO
class ProgramStats:
    """
    Summary statistics of generated program
    """
    def __init__(self, prog_spec: 'ProgramSpec' = None):
        self.num_globals = 0
        self.num_functions = 0


# TODO
class FunctionStats:
    """
    Summary statistics of FunctionBody
    """

    def __init__(self, fb: 'FunctionSpec' = None):
        self.num_args = 0
        self.num_expressions = 0
        self.num_operators = 0
        self.num_vars = 0
        self.num_inline_literals = 0
        self.num_global_gets = 0
        self.num_global_sets = 0
        self.num_loop_while = 0
        self.num_loop_for = 0
        self.num_cond_if = 0
        self.num_cond_if_else = 0


class ProgramSpec:
    """
    Specification of a Program
    """
    def __init__(self, params: GeneratorConfig,
                 globals_vargen: VarGen=None, function_name_vargen: VarGen=None):
        self.params: GeneratorConfig = params
        self.headers: List[str] = ['#include <stdio.h>', '#include <math.h>', '#include <stdlib.h>']
        self.globals_num = 0
        self.globals_vargen: VarGen = globals_vargen
        self.globals: Dict[str, VariableDecl] = dict()
        self.function_main: Union[FunctionSpec, None] = None
        self.function_main_body: Union[FunctionBody, None] = None
        self.function_name_vargen: VarGen = function_name_vargen
        self.functions_num = 0  # number of functions in addition to main
        self.functions: Dict[str, FunctionSpec] = dict()  # all defined fns (besides main)
        self.function_bodies: Dict[str, FunctionBody] = dict()  # all FunctionBody's corresponding to each defined fn
        self.functions_builtin: Dict[str, FunctionSpec] = dict()  # all built-in functions

    def sample_fn(self, ignore: Union[Set[str], None] = None) -> FunctionSpec:
        """
        Helper function to uniformly sample a function from the set of available functions
          that can be sampled, generally used as part of sampling expression trees (ExprTree).
        The source sample set is built from the built-in functions and any program-specific functions.
        The ignore set (if specified) is used to remove from consideration some functions.
          This is used depending on whether we allow recursive function calls.
        :param ignore: optional list of functions to remove from the set considered.
        :return: FunctionSpec of sampled fn
        """
        fns = self.functions_builtin | self.functions
        if ignore:
            fn_names = tuple(set(fns.keys()) - ignore)
        else:
            fn_names = tuple(fns.keys())
        fn_name = random.choice(fn_names)
        return fns[fn_name]

    def get_fn(self, fn_name: str) -> FunctionSpec:
        """
        Helper to retrieve FunctionSpec by name (str) irrespective of
          whether built-in or introduced (during sampling).
        :param fn_name: str of function name
        :return:
        """
        fns = self.functions_builtin | self.functions
        return fns[fn_name]

    def get_fns_with_num_args(self, num_args) -> List[FunctionSpec]:
        """
        Returns set of all FunctionSpecs with num_args number of arguments
        :param num_args: The number of arguments each FuncdtionSpec should have in set
        :return: Set of FunctionSpecs
        """
        fns = self.functions_builtin | self.functions
        return [fn_spec for fn_spec in fns.values() if len(fn_spec.args) == num_args]

    def sample_program_specific_fn(self, include_main_p: bool = True) -> str:
        """
        Uniformly randomly samples a function defined in the current program
        (including possibly main).
        :return: function name
        """
        if include_main_p:
            fns = ['main'] + list(self.functions.keys())
        else:
            fns = list(self.functions.keys())
        return random.choice(fns)

    def init_program_parameters(self):
        """
        Based on the GeneratorConfig parameters,
          sample the number of program-level components:
            number of globals
            number of functions in addition to main
        :return:
        """
        self.globals_num = random.randint(self.params.globals_num[0], self.params.globals_num[1])
        if self.globals_num > 0 and self.globals_vargen is None:
            self.globals_vargen = VarGen('g')
        self.functions_num = random.randint(self.params.functions_num[0], self.params.functions_num[1])
        if self.functions_num > 0 and self.function_name_vargen is None:
            self.function_name_vargen = VarGen('fn')
        if self.params.operators_primitive:
            self.functions_builtin = op_def_dict_to_fn_spec_dict(self.params.operators_primitive)

    def sample_create_globals(self):
        for gidx in range(self.globals_num):
            var_name = self.globals_vargen.get_name()
            var_type = random.choice(self.params.map_typecat_to_type['ANY'])
            var_value = sample_literal(var_type)
            self.globals[var_name] = VariableDecl(name=var_name, var_type=var_type, var_value=var_value)

    def choose_global(self) -> Union[VariableDecl, None]:
        if bool(self.globals):
            var_name_sample = random.choice(list(self.globals.keys()))
            return self.globals[var_name_sample]
        else:
            return None

    def sample_function_signatures(self):
        # create main function -- there will always be a main
        args = None
        if self.params.main_default_cli:
            args = [VariableDecl(name='argc', var_type='int', is_arg=True),
                    VariableDecl(name='argv', var_type='char', var_type_ptr='*', var_type_arr=True, is_arg=True)]
        self.function_main = FunctionSpec(
            name='main',
            args=args,
            return_type='int',
            # globals_set_at_body_top=True  # TODO: see above in FunctionSpec
        )
        # create other functions
        for fidx in range(self.functions_num):
            fun_name = self.function_name_vargen.get_name()
            num_args = random.randint(self.params.function_arguments_num[0],
                                      self.params.function_arguments_num[1])
            args = list()
            if num_args > 0:
                arg_name_vargen = VarGen('p')
                for aidx in range(num_args):
                    # TODO need to eventually generalize to allow for pointers
                    arg_name = arg_name_vargen.get_name()
                    arg_type = random.choice(self.params.map_typecat_to_type['ANY'])
                    args.append(VariableDecl(name=arg_name, var_type=arg_type, is_arg=True))

            fn_spec = FunctionSpec(
                name=fun_name,
                args=args,
                return_type=random.choice(self.params.map_typecat_to_type['ANY']),
                # globals_set_at_body_top=False  # TODO see above in FunctionSpec
            )

            # Ensure each function gets called in a way that eventually
            #   could affects main().
            #   This is accomplished by making sure each function will be
            #   called by an expression from some function already created
            #   (including possibly within main)
            # By sampling this call before setting to self.functions, then call
            #   to self.sample_user_defined_fn wil not include the new fun_name
            fn_that_calls_name = self.sample_program_specific_fn(include_main_p=True)
            if fn_that_calls_name == 'main':
                self.function_main.fns_to_call.append(fun_name)
            else:
                self.functions[fn_that_calls_name].fns_to_call.append(fun_name)

            self.functions[fun_name] = fn_spec

    def ensure_every_global_is_get_at_least_once(self):
        """
        For every global, ensure it is 'get' at least once by some function.
        :return:
        """
        function_names = ['main'] + list(self.functions.keys())
        for global_var in self.globals.keys():
            fn_name = random.choice(function_names)  # sample which fn will get global_var
            if fn_name == 'main':
                fn = self.function_main
            else:
                fn = self.functions[fn_name]
            fn.globals_to_be_get.append(global_var)

    def sample_global_literal_values(self):
        for global_var_decl in self.globals.values():
            global_var_decl.var_value = sample_literal(global_var_decl.var_type)

    def sample(self, verbose=False):
        """
        Top-level driver for sampling a program based on GeneratorConfig parameters.
        :return:
        """
        if verbose:
            print('ProgramSpec.sample()')
            print('  init_program_parameters()')
        self.init_program_parameters()
        if verbose:
            print('  sample_create_globals()')
        self.sample_create_globals()
        if verbose:
            print('  sample_function_signatures()')
        self.sample_function_signatures()
        if verbose:
            print('  ensure_every_global_is_get_at_least_once()')
        self.ensure_every_global_is_get_at_least_once()
        if verbose:
            print('  sample_global_literal_values()')
        self.sample_global_literal_values()
        if verbose:
            print('  Create and sample FunctionBody\'s')
        for i, (fn_name, fn_spec) in enumerate(self.functions.items()):
            if verbose:
                print(f'    {i} : {fn_name}')
            fb = FunctionBody(program_spec=self, function_spec=fn_spec)
            fb.sample()
            self.function_bodies[fn_name] = fb
        if verbose:
            print('  Create and sample main FunctionBody')
        fb = FunctionBody(program_spec=self, function_spec=self.function_main)
        fb.sample()
        self.function_main_body = fb
        if verbose:
            print('ProgramSpec.sample() : DONE')

    def to_c_string(self) -> List[str]:
        prog_str_list = list()
        # headers
        for header in self.headers:
            prog_str_list.append(header)
        prog_str_list.append('')
        # globals
        prog_str_list.append('// globals')
        for global_var_decl in self.globals.values():
            prog_str_list.append(global_var_decl.to_c_string() + ';')
        prog_str_list.append('')
        # function signatures
        prog_str_list.append('// function signatures')
        prog_str_list.append('')
        for fn_spec in self.functions.values():
            prog_str_list.append(fn_spec.to_c_string_signature() + ';')
        prog_str_list.append('')
        # functions
        prog_str_list.append('// functions')
        prog_str_list.append('')
        for function_body in self.function_bodies.values():
            prog_str_list += function_body.to_c_string()
            prog_str_list.append('')
        # main
        prog_str_list.append('// main')
        prog_str_list += self.function_main_body.to_c_string()
        return prog_str_list

    def pprint(self):
        print('ProgramSpec:')
        print(f'  headers={self.headers}')
        print(f'  globals={self.globals_num}, functions={self.functions_num}')
        print(f'  globals: {self.globals.items()}')
        print(f'  defined function signatures:')
        self.function_main.pprint(indent=4)
        for fn_spec in self.functions.values():
            fn_spec.pprint(indent=4)
        print(f'  built-in function signatures:')
        for fn_spec in self.functions_builtin.values():
            fn_spec.pprint(indent=4)


# -----------------------------------------------------------------------------
# FunctionBody generator
# -----------------------------------------------------------------------------

# TODO NOTE: there is a *lot* of repeated code here. Reduce with inheritance?


class Visitor(ABC):
    @abstractmethod
    def visit(self, obj: Any, context: Any):
        """
        Implements the visitor
        :return:
        """


class VisitorCollectElements(Visitor):

    def __init__(self, of_type: type = None):
        self.of_type = of_type
        self.elements = list()

    def visit(self, obj, context=None):
        if (self.of_type is not None and isinstance(obj, self.of_type)) \
                or self.of_type is None:
            self.elements.append((obj, context))

    def get_elements(self, with_context_p: bool = True) -> List:
        if with_context_p:
            return self.elements
        else:
            return [elm for (elm, context) in self.elements]


class FunctionBody:
    def __init__(self,
                 program_spec: ProgramSpec = None,
                 function_spec: FunctionSpec = None,
                 var_gen_expr: VarGen = None,
                 var_gen_other: VarGen = None):

        PNode.reset_pnode_index()

        self.program_spec: ProgramSpec = program_spec

        # Used to access
        #   fns_to_call
        self.function_spec: FunctionSpec = function_spec

        self.head: PNode = PNode()
        self.tail = self.head
        self.unassigned_pnodes: Set[PNode] = {self.head}
        self.nes_pnodes: Set[PNode] = set()  # PNodes that must be filled with expressions

        if var_gen_expr is None:
            self.var_gen_expr = VarGen('e')
        else:
            self.var_gen_expr = var_gen_expr

        if var_gen_other is None:
            self.var_gen_other = VarGen('v')
        else:
            self.var_gen_other = var_gen_other

        # collection of variable declarations; GCC stores all decls at FN level
        # this is initialized with the function argument list
        self.var_decls: List[VariableDecl] = list()
        if self.function_spec.args:
            self.var_decls = self.function_spec.args.copy()

    def sample(self, skip_sample_pnode_structure: bool = False):
        """
        Top-level method for driving expression tree sampling
          and completing variable declarations and assignments
        :return:
        """
        if not skip_sample_pnode_structure:
            self.sample_pnode_structure()
        pnode_exprs = self.collect_all_pnode_exprs(with_context_p=False)
        self.sample_expression_trees(pnode_exprs=pnode_exprs)
        for pnode_expr in pnode_exprs[1:]:
            self.ensure_expressions_affect_output(pnode_expr)
        self.ensure_function_args_used_at_least_once()
        for pnode_expr in pnode_exprs:
            self.ensure_expression_at_least_one_var_per_operator(pnode_expr)
        for pnode_expr in pnode_exprs:
            self.ensure_expression_fill_remaining_unassigned(pnode_expr)
        self.assign_literals_to_variable_decls()

    def create_and_add_new_var(self, new_var_name: str = None, can_set_literal: bool = False) -> VariableDecl:
        if new_var_name is None:
            new_var_name = self.var_gen_other.get_name()
        new_var_type = random.choice(self.program_spec.params.map_typecat_to_type['ANY'])
        new_var_decl = VariableDecl(name=new_var_name, var_type=new_var_type)
        # store the var decl in the FunctionBody.var_decls
        self.var_decls.append(new_var_decl)
        return new_var_decl

    def choose_var(self) -> Union[VariableDecl, None]:
        num_var_decls = len(self.var_decls)
        if self.program_spec.globals_num > 0 and num_var_decls == 0:
            return self.program_spec.choose_global()
        elif self.program_spec.globals_num == 0 and num_var_decls > 0:
            return random.choice(self.var_decls)
        elif self.program_spec.globals_num > 0:
            # if get here, then both global_num and num_var_decls are both > 0...
            total = self.program_spec.globals_num + num_var_decls
            prob_global = self.program_spec.globals_num / total
            if random.random() < prob_global:
                # choose a global
                return self.program_spec.choose_global()
            else:
                # choose another existing local var
                return random.choice(self.var_decls)
        else:
            return None

    # def choose_var(self) -> Union[VariableDecl, None]:
    #     total = self.program_spec.globals_num + len(self.var_decls)
    #     print(f'choose_var(): total: {total}')
    #     if total > 0:
    #         prob_global = self.program_spec.globals_num / total
    #         if random.random() < prob_global:
    #             # choose a global
    #             return self.program_spec.choose_global()
    #         else:
    #             # choose another existing local var
    #             if bool(self.var_decls):
    #                 return random.choice(self.var_decls)
    #             else:
    #                 return None
    #     else:
    #         return None

    def sample_pnode_structure(self, verbose: bool = False):

        if verbose:
            print(f'==================== FunctionBody.sample_pnode_structure()')
            print(f'========== Sample control structures')

        num_loops = 0
        if random.random() < self.program_spec.params.loop_prob:
            num_loops = random.randint(self.program_spec.params.loop_num[0],
                                       self.program_spec.params.loop_num[1])
        create_loop_tokens = ['LOOP']*num_loops
        if verbose:
            print(f'DEBUG: num_loops={num_loops}')

        num_conditionals = 0
        if random.random() < self.program_spec.params.conditional_prob:
            num_conditionals = random.randint(self.program_spec.params.conditionals_num[0],
                                              self.program_spec.params.conditionals_num[1])
        create_cond_tokens = ['COND']*num_conditionals
        if verbose:
            print(f'DEBUG: num_conditionals={num_conditionals}')

        create_tokens = create_loop_tokens + create_cond_tokens
        random.shuffle(create_tokens)
        if verbose:
            print(f'DEBUG: create_tokens: {create_tokens}')

        for i, token in enumerate(create_tokens):
            if verbose:
                print(f'---------- token: {token}')
            if len(self.unassigned_pnodes) == 0:
                print(f'create_tokens = {create_tokens}')
                raise Exception('FunctionBody.sample_pnode_structure() : self.unassigned_pnodes is empty!')
            pnode_to_swap = random.choice(list(self.unassigned_pnodes))
            if verbose:
                print(f'    node_to_swap: {pnode_to_swap}')
            if token == 'LOOP':
                if random.random() < self.program_spec.params.loop_for_prob:
                    if verbose:
                        print(f'    LOOP_FOR {i} {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')
                    PNodeLoopFor.swap(pnode_to_swap=pnode_to_swap, fn_body=self)
                else:
                    if verbose:
                        print(f'    LOOP_WHILE {i} {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')
                    PNodeLoopWhile.swap(pnode_to_swap=pnode_to_swap, fn_body=self)
            elif token == 'COND':
                if random.random() < self.program_spec.params.conditional_else_prob:
                    if verbose:
                        print(f'    COND_IF_ELSE {i} {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')
                    PNodeCondIfElse.swap(pnode_to_swap=pnode_to_swap, fn_body=self)
                else:
                    if verbose:
                        print(f'    COND_IF {i} {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')
                    PNodeCondIf.swap(pnode_to_swap=pnode_to_swap, fn_body=self)
            if verbose:
                print(f'    {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')

        # Sample expressions
        if verbose:
            print(f'========== Sample NES expressions')

        # Ensure tail is in NES
        self.nes_pnodes.add(self.tail)

        num_expressions = random.randint(self.program_spec.params.expressions_num[0],
                                         self.program_spec.params.expressions_num[1])

        if verbose:
            print(f'DEBUG: num_expressions={num_expressions}, num_nes={len(self.nes_pnodes)}')

        # Sample Expr for all NES PNodes
        num_nes_nodes = len(self.nes_pnodes)
        for i, pnode_to_swap in enumerate(list(self.nes_pnodes)):
            if verbose:
                print('-----------')
                print(f'    EXPR {i} {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')
                print(f'    NES node_to_swap: {pnode_to_swap}')
            PNodeExpr.swap(pnode_to_swap=pnode_to_swap, fn_body=self)
            if verbose:
                print(f'    {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')
            # self.pprint_depth_first()

        # Sample Expr any remaining unassigned PNodes
        if verbose:
            print(f'========== Sample remaining expressions')
        num_remaining_expressions = num_expressions - num_nes_nodes
        if verbose:
            print(f'DEBUG: num_remaining_expressions={num_remaining_expressions}')
        if num_remaining_expressions > 0:
            for i in range(num_remaining_expressions):
                if verbose:
                    print('-----------')
                    print(f'    EXPR {i} {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')
                pnode_to_swap = random.choice(list(self.unassigned_pnodes))
                if verbose:
                    print(f'    node_to_swap: {pnode_to_swap}')
                PNodeExpr.swap(pnode_to_swap=pnode_to_swap, fn_body=self)
                if verbose:
                    print(f'    {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')
                # self.pprint_depth_first()

        # Remove remaining unassigned ('production') PNodes
        self.remove_unassigned_pnodes()

    def collect_all_pnode_exprs(self, reverse: bool = True, with_context_p=True) -> List['PNodeExpr']:
        """
        Collect all PNodeExpr nodes and return as list (by default, in reverse order)
        :param reverse: Flag for whether to return list in reverse (default = True)
        :param with_context_p:
        :return:
        """
        vce = VisitorCollectElements(of_type=PNodeExpr)
        self.visit_depth_first_forward(vce)
        if with_context_p:
            pnode_exprs = vce.get_elements()
        else:
            pnode_exprs = [pnode for (pnode, context) in vce.get_elements()]
        if reverse:
            return list(reversed(pnode_exprs))
        else:
            return list(pnode_exprs)

    def sample_expression_trees(self, pnode_exprs: List['PNodeExpr'], verbose=False):
        if verbose:
            print(f'-- FunctionBody.sample_expression_trees(): Sample {len(pnode_exprs)} ExprTrees')

        num_exprs = len(pnode_exprs)

        # If there are fns_to_call, determine which expressions will call them
        expr_to_call_fns = dict()
        if self.function_spec.fns_to_call:
            for fn_to_call in self.function_spec.fns_to_call:
                expr_to_call_idx = random.randint(0, num_exprs)
                if expr_to_call_idx in expr_to_call_fns:
                    expr_to_call_fns[expr_to_call_idx].append(fn_to_call)
                else:
                    expr_to_call_fns[expr_to_call_idx] = [fn_to_call]

        # If there are FunctionSpec.args, determine which expressions will access them
        args_to_get = dict()
        if len(self.function_spec.args) > 0:
            for arg in self.function_spec.args:
                expr_to_get_idx = random.randint(0, num_exprs)
                if expr_to_get_idx in args_to_get:
                    args_to_get[expr_to_get_idx].append(arg)
                else:
                    args_to_get[expr_to_get_idx] = [arg]

        for i, pnode_expr in enumerate(pnode_exprs):
            num_ops = random.randint(self.program_spec.params.operators_num[0],
                                     self.program_spec.params.operators_num[1])

            # store the fns_that_must_be_called (if any) and
            #   adjust num_ops to be at least num of expr_to_call_fns
            fns_that_must_be_called = list()  # the fns that must be called in this expr
            if i in expr_to_call_fns:
                fns_that_must_be_called = expr_to_call_fns[i]
                num_ops = max(num_ops, len(fns_that_must_be_called))

            args_that_must_be_get = list()  # the arg VariableDecls that must be get in this expr
            if i in args_to_get:
                args_that_must_be_get = args_to_get[i]

            if verbose:
                print(f'    {i} num_ops={num_ops}')
                if i in expr_to_call_fns:
                    print(f'        expr_to_call_fns: {expr_to_call_fns[i]}')

            pnode_expr.expr_tree = ExprTree(num_ops=num_ops,
                                            program_spec=self.program_spec,
                                            function_spec=self.function_spec,
                                            args_that_must_be_get=args_that_must_be_get)
            pnode_expr.expr_tree.sample(fns_that_must_be_called)

            if verbose:
                print(f'        {pnode_expr.expr_tree.to_string()}')
                print(f'        ExprTree.unassigned_indices: {pnode_expr.expr_tree.unassigned_indices}')

    def ensure_expressions_affect_output(self, pnode_expr: 'PNodeExpr'):
        """
        TASK: ensure source PNodeExpr has an effect
              (i.e., its value gets used downstream or global set)
        if not tail:
            if there are globals
                determine whether to set the global --
                if so, set it
                set source PNodeExpr.expr_assignment_var = global var decl
            else:
                create a var decl for the source PNodeExpr
                    store the var decl in the FunctionBody.var_decls (using self.create_and_add_new_var())
                    store reference to the var decl in the source PNodeExpr.expr_assignment_var
                    Also store the reference within the VariableDecl.set
                collect the path from source PNodeExpr to tail (visit_forward_up)
                    sample a target PNodeExpr along that path
                    sample from target PnodeExpr.expr_tree.unassigned_indices that will be assigned var
                        (If no available unassigned_indices, add another binary operator to introduce one...)
                    store reference in var decl VariableDecl.get
        :param pnode_expr: The source PNodeExpr that is to affect the function output
        :return:
        """
        if self.program_spec.globals_num > 0 and random.random() < self.program_spec.params.globals_prob_set:
            # sample which global to set
            global_var = self.program_spec.choose_global()
            # assign the expr to a global
            pnode_expr.expr_assignment_var = global_var
            # record that global is set by pnode_expr
            global_var.update_set(self.function_spec.name, pnode_expr)
        else:
            # create var decl for expression (using self.var_gen_expr)
            new_var_name = self.var_gen_expr.get_name()
            new_var_decl = self.create_and_add_new_var(new_var_name=new_var_name, can_set_literal=False)
            new_var_decl.update_set(self.function_spec.name, pnode_expr)
            pnode_expr.expr_assignment_var = new_var_decl

            # get path from pnode_expr to tail via visit_forward_up
            v = VisitorCollectElements(of_type=PNodeExpr)
            pnode_expr.visit_forward_up(visitor=v)
            # don't include the current elements, which is index 0, start the list as index 1:...
            pnode_expr_list = v.get_elements(with_context_p=False)[1:]
            # print(pnode_expr_list)
            # sample target pnode_expr
            target_pnode_expr = random.choice(pnode_expr_list)
            # sample unassigned index in target_pnode_expr.expr_tree
            if len(target_pnode_expr.expr_tree.unassigned_indices):
                new_var_index_in_target = random.choice(list(target_pnode_expr.expr_tree.unassigned_indices))
            else:
                # choose an existing op to swap with new binary op, to make a new
                #   unassigned index available
                old_op_to_swap_index = random.choice(list(target_pnode_expr.expr_tree.op_indices))
                fn_binary_choice = random.choice(self.program_spec.get_fns_with_num_args(num_args=2))
                target_pnode_expr.expr_tree.swap_new_op_at(index=old_op_to_swap_index, new_op=fn_binary_choice)
                if len(target_pnode_expr.expr_tree.unassigned_indices):
                    new_var_index_in_target = random.choice(list(target_pnode_expr.expr_tree.unassigned_indices))
                else:
                    # We should not reach here -- if so, then there's a BUG in the logic...
                    target_pnode_expr.expr_tree.pprint()
                    raise Exception('FunctionBody.ensure_expressions_affect_output()\n'
                                    f'  {target_pnode_expr} has'
                                    f' no unassigned_indices: {target_pnode_expr.expr_tree.unassigned_indices}\n'
                                    f'  {target_pnode_expr.expr_tree.to_string()}'
                                    f'  BUT we just added one new bianry fn {fn_binary_choice.name} '
                                    f'at index {old_op_to_swap_index}')
            # assign the new_var_decl to the location in target_pnode_expr
            target_pnode_expr.expr_tree.add_var_at(new_var_index_in_target, new_var_decl)
            # store reference in var decl VariableDecl.get
            new_var_decl.update_get(self.function_spec.name, target_pnode_expr, new_var_index_in_target)

    def ensure_function_args_used_at_least_once(self):
        """
        TASK: ensure all function arguments are 'get' (used in expression trees) at least once
        :return:
        """
        # iterate through ExprTree's and if ExprTree has args_that_must_be_get
        pnode_exprs = self.collect_all_pnode_exprs(with_context_p=False)
        for pnode_expr in pnode_exprs:
            for arg_var_decl in pnode_expr.expr_tree.args_that_must_be_get:
                if not len(pnode_expr.expr_tree.unassigned_indices) > 0:
                    # if no remaining unassigned_indices...
                    #   introduce another binary operator and insert/swap it at some existing op
                    #   using ExprTree.introduce_new_op_at()
                    old_op_to_swap_index = random.choice(list(pnode_expr.expr_tree.op_indices))
                    fn_binary_choice = random.choice(self.program_spec.get_fns_with_num_args(num_args=2))
                    pnode_expr.expr_tree.swap_new_op_at(index=old_op_to_swap_index, new_op=fn_binary_choice)
                index = random.choice(list(pnode_expr.expr_tree.unassigned_indices))
                pnode_expr.expr_tree.add_var_at(index, arg_var_decl)
                arg_var_decl.update_get(self.function_spec.name, pnode_expr, index)

    def ensure_expression_at_least_one_var_per_operator(self, pnode_expr: 'PNodeExpr', verbose=False):
        """
        TASK: ensure at least one var for each operator argument
        For each operator (the indices are specified in ExprTree.op_indices),
          If there is not at least one child index (ExprTree.map_index_to_children)
            that is in ExprTree.map_index_to_var_assignments keys, then:
              Sample one of those values to assign to a VariableDecl by either:
              (1) sample from existing variables in FunctionBody.var_decls or globals:
                  (a) PNodeExpr.expr_tree.map_index_to_var_assignments[idx] = var_decl
                  (b) update VariableDecl.get
              or
              (2) create a new VariableDecl with a value
                  (a) Add to FunctionBody.var_decls
                  (b) update VariableDecl.get
        :param pnode_expr:
        :return:
        """
        if verbose:
            print('FunctionBody.ensure_expression_at_least_one_var_per_operator()')
        for op_idx in list(pnode_expr.expr_tree.op_indices):
            at_least_one = False
            candidate_indices = list()
            if verbose:
                print(f'>> {op_idx} {pnode_expr.expr_tree.map_index_to_children[op_idx]}')
            for child_idx in pnode_expr.expr_tree.map_index_to_children[op_idx]:
                if child_idx in pnode_expr.expr_tree.map_index_to_var_assignments.keys():
                    # there is at least one variable in argument
                    at_least_one = True
                elif child_idx in pnode_expr.expr_tree.op_indices:
                    # there is at least one operator call in argument
                    at_least_one = True
                else:
                    # neither a variable or operator call, so candidate to fill
                    candidate_indices.append(child_idx)
            if verbose:
                print(f'    at_least_one: {at_least_one} ; candidate_indices: {candidate_indices}')
            if at_least_one is False and len(candidate_indices) > 0:
                idx_for_var = random.choice(candidate_indices)
                if self.program_spec.globals_num + len(self.var_decls) == 0 \
                        or random.random() < self.program_spec.params.create_new_var_prob:
                    # create a new VariableDecl
                    new_var_name = self.var_gen_other.get_name()
                    new_var_decl = self.create_and_add_new_var(new_var_name=new_var_name, can_set_literal=True)
                    new_var_decl.update_get(self.function_spec.name, pnode_expr, idx_for_var)
                    pnode_expr.expr_tree.add_var_at(index=idx_for_var, var_decl=new_var_decl)
                else:
                    # choose an existing var
                    existing_var_decl = self.choose_var()
                    existing_var_decl.update_get(self.function_spec.name, pnode_expr, idx_for_var)
                    pnode_expr.expr_tree.add_var_at(index=idx_for_var, var_decl=existing_var_decl)

    def ensure_expression_fill_remaining_unassigned(self, pnode_expr: 'PNodeExpr'):
        """
        TASK: Fill remaining ExprTree.unassigned_indices with
        :param pnode_expr:
        :return:
        """
        for index in list(pnode_expr.expr_tree.unassigned_indices):
            if random.random() < self.program_spec.params.create_new_var_prob:
                # create new VariableDecl
                new_var_name = self.var_gen_other.get_name()
                new_var_decl = self.create_and_add_new_var(new_var_name=new_var_name)
                new_var_decl.update_get(self.function_spec.name, pnode_expr, index)
                pnode_expr.expr_tree.add_var_at(index=index, var_decl=new_var_decl)
            else:
                # assign inline-literal
                if index not in pnode_expr.expr_tree.map_index_to_op_arg:
                    raise Exception('FunctionBody.ensure_expression_fill_remaining_unassigned()\n'
                                    f'  Could not find index {index} in pnode_expr.expr_tree.map_index_to_op_arg: '
                                    f'{pnode_expr.expr_tree.map_index_to_op_arg}')
                arg_decl = pnode_expr.expr_tree.map_index_to_op_arg[index]
                value_type = arg_decl.var_type
                if arg_decl.var_type == 'ANY':
                    value_type = random.choice(MAP_TYPECAT_TO_TYPE['ANY'])
                if value_type not in MAP_TYPECAT_TO_TYPE['ANY']:
                    pnode_expr.expr_tree.pprint()
                    raise Exception('FunctionBody.ensure_expression_fill_remaining_unassigned()\n'
                                    f'  value_type={value_type} of index {index} not in MAP_TYPECAT_TO_TYPE["ANY"]: '
                                    f'{MAP_TYPECAT_TO_TYPE["ANY"]}')
                value = sample_literal(value_type)
                pnode_expr.expr_tree.add_literal_at(index, value)

    def assign_literals_to_variable_decls(self):
        for var_decl in self.var_decls:
            if not var_decl.is_arg:
                var_decl.var_value = sample_literal(var_decl.var_type)

    def remove_unassigned_pnodes(self):
        for pnode in list(self.unassigned_pnodes):
            pnode.remove(self)

    def visit_depth_first_forward(self, visitor: Visitor):
        self.head.visit_depth_first_forward(visitor)

    def to_string_depth_first_forward(self):
        l = [f'head:{self.head}', f'tail:{self.tail}']
        return l + self.head.to_string_depth_first_forward()

    def pprint_depth_first(self):
        print('\n'.join(self.to_string_depth_first_forward()))

    def to_c_string(self, level=1) -> List[str]:
        indent_str = TAB_STR * level
        fb_str_list = list()
        fb_str_list.append(self.function_spec.to_c_string_signature())
        fb_str_list.append('{')
        # local var decls -- iterate in random order
        shuffled_var_decls = self.var_decls.copy()
        random.shuffle(shuffled_var_decls)
        for var_decl in shuffled_var_decls:
            if not var_decl.is_arg:
                fb_str_list.append(indent_str + var_decl.to_c_string() + ';')
        if self.head:
            fb_str_list += self.head.to_c_string(level)
        fb_str_list.append('}')
        return fb_str_list


class PNode:
    global_pnode_index = 0

    @staticmethod
    def reset_pnode_index():
        PNode.global_pnode_index = 0

    @staticmethod
    def get_next_pnode_index():
        n = PNode.global_pnode_index
        PNode.global_pnode_index += 1
        return n

    def __init__(self, before: 'PNode' = None, after: 'PNode' = None, parent: 'PNode' = None):
        self.pnode_idx = PNode.get_next_pnode_index()
        self.before: PNode = before
        self.after: PNode = after
        self.parent: PNode = parent

        # NOTE: C makes all variable declarations at
        # bookkeeping of location in PNode structure for where variable will be declared
        # self.var_decls: List[VariableDecl] = list()

    def get_connectivity_str(self):
        b = '#'
        if self.before:
            b = f'{self.before.pnode_idx}'
        a = '#'
        if self.after:
            a = f'{self.after.pnode_idx}'
        p = '#'
        if self.parent:
            p = f'{self.parent.pnode_idx}'
        return f'{b},{p},{a}'

    def __repr__(self):
        return f'<{self.pnode_idx}:{self.get_connectivity_str()}>'

    def remove(self, fn_body: FunctionBody):
        if self.before is not None and self.after is not None:
            # between two existing terminals
            if self.parent is not None:
                raise Exception(f"PNode.remove(): unexpected parent: {self}")
            self.before.after = self.after
            self.after.before = self.before
        elif self.before is None and self.after is not None:
            # at start of chain (before is None but after is not)
            if self.parent:
                self.parent.swap_child_start(self, self.after)
            self.after.before = None
            if fn_body.head == self:
                fn_body.head = self.after
        elif self.after is None and self.before is not None:
            # at end of chain (after is None but before is not)
            if self.parent:
                self.parent.swap_child_end(self, self.before)
            self.before.after = None
            if fn_body.tail == self:
                fn_body.tail = self.before
        else:
            raise Exception(f"PNode.remove(): unexpected before/after pattern: {self}")
        fn_body.unassigned_pnodes.remove(self)
        del self

    # The following are needed for cases like PNodeCondIfElse that have
    # both an if_cond and an else_cond, so must separately determine

    def swap_child_start(self, pnode_to_swap: 'PNode', new_before: 'PNode'):
        """
        Each subtype to handle how they will swap a child_start.
        :param pnode_to_swap:
        :param new_before:
        :return:
        """

    def swap_child_end(self, pnode_to_swap: 'PNode', new_after: 'PNode'):
        """
        Each PNode subclass will implement how to swap child_end
        :param pnode_to_swap:
        :param new_after:
        :return:
        """

    def visit_depth_first_forward(self, visitor: Visitor):
        visitor.visit(self, None)
        if self.after:
            self.after.visit_depth_first_forward(visitor)

    def visit_forward_up(self, visitor: Visitor, level: int = 0, end_node: 'PNode' = None):
        visitor.visit(self, context=level)
        if self != end_node:
            if self.after:
                self.after.visit_forward_up(visitor, level, end_node)
            elif self.parent:
                self.parent.visit_forward_up(visitor, level + 1, end_node)

    def visit_backward_up(self, visitor: Visitor, level: int = 0, end_node: 'PNode' = None):
        visitor.visit(self, context=level)
        if self != end_node:
            if self.before:
                self.before.visit_backward_up(visitor, level, end_node)
            elif self.parent:
                self.parent.visit_backward_up(visitor, level + 1, end_node)

    def to_string_depth_first_forward(self, level: int = 0):
        indent_str = TAB_STR*level
        l = [f'{indent_str}{self}']
        if self.after:
            return l + self.after.to_string_depth_first_forward(level)
        else:
            return l

    def to_c_string(self, level: int) -> List[str]:
        """
        Must be implemented...
        :param level:
        :return:
        """
        raise Exception('PNode.to_c_string(): Should be more specific subtype of PNode')


def swap_finish(pnode_to_swap: PNode, new: PNode, fn_body: FunctionBody):
    if pnode_to_swap.before is None:
        if fn_body.head == pnode_to_swap:
            fn_body.head = new.before
    else:
        new.before.before = pnode_to_swap.before
        pnode_to_swap.before.after = new.before

    if pnode_to_swap.after is None:
        if fn_body.tail == pnode_to_swap:
            fn_body.tail = new.after
    else:
        new.after.after = pnode_to_swap.after
        pnode_to_swap.after.before = new.after

    if pnode_to_swap.parent is not None:
        pnode_to_swap.parent.swap_child_start(pnode_to_swap, new.before)
        pnode_to_swap.parent.swap_child_end(pnode_to_swap, new.after)

    fn_body.unassigned_pnodes.remove(pnode_to_swap)
    if pnode_to_swap in fn_body.nes_pnodes:
        fn_body.nes_pnodes.remove(pnode_to_swap)
    del pnode_to_swap


def swap_finish_no_after(pnode_to_swap: PNode, new: PNode, fn_body: FunctionBody):
    """
    This special version of 'swap_finish' assumes the pnode_to_swap.after is being consumed.
    This pattern is used by productions that only generate in the 'before' direction.
    Currently only Expr does this.
    :param pnode_to_swap:
    :param new:
    :param fn_body:
    :return:
    """
    if pnode_to_swap.before is None:
        if fn_body.head == pnode_to_swap:
            fn_body.head = new.before
    else:
        new.before.before = pnode_to_swap.before
        pnode_to_swap.before.after = new.before

    if pnode_to_swap.after is None:
        if fn_body.tail == pnode_to_swap:
            fn_body.tail = new
    else:
        new.after = pnode_to_swap.after   # difference from swap
        pnode_to_swap.after.before = new  # difference from swap

    if pnode_to_swap.parent is not None:
        pnode_to_swap.parent.swap_child_start(pnode_to_swap, new.before)
        pnode_to_swap.parent.swap_child_end(pnode_to_swap, new)  # difference from swap

    fn_body.unassigned_pnodes.remove(pnode_to_swap)
    if pnode_to_swap in fn_body.nes_pnodes:
        fn_body.nes_pnodes.remove(pnode_to_swap)
    del pnode_to_swap


class PNodeExpr(PNode):

    @staticmethod
    def swap(pnode_to_swap: PNode, fn_body: FunctionBody):
        """

        :param pnode_to_swap:
        :param fn_body:
        :return:
        """
        new = PNodeExpr()
        new.before = PNode(after=new)
        # print(f'    new: {new}')

        fn_body.unassigned_pnodes.add(new.before)

        swap_finish_no_after(pnode_to_swap=pnode_to_swap, new=new, fn_body=fn_body)

        return new

    def __init__(self, before: PNode = None, after: PNode = None, parent: PNode = None):
        self.expr_tree: Union[ExprTree, None] = None
        self.expr_assignment_var: VariableDecl = None
        super().__init__(before=before, after=after, parent=parent)

    def __repr__(self):
        return f'<Expr{self.pnode_idx}:{self.get_connectivity_str()}>'

    def visit_depth_first_forward(self, visitor: Visitor):
        visitor.visit(self)
        if self.after:
            self.after.visit_depth_first_forward(visitor)

    def to_string_depth_first_forward(self, level: int = 0):
        indent_str = TAB_STR*level
        l = [f'{indent_str}{self}']
        if self.after:
            return l + self.after.to_string_depth_first_forward(level)
        else:
            return l

    def to_c_string(self, level=0) -> List[str]:
        indent_str = TAB_STR * level
        str_list = list()
        if self.expr_assignment_var:
            str_list.append(indent_str + self.expr_assignment_var.name + ' = ' + self.expr_tree.to_c_string() + ';')
        else:
            # this occurs when the expression is the last in the body
            # print(f'PNodeExpr.to_c_string(): missing self.expr_assignment_var?: {self}')
            # print(self.expr_tree.to_c_string())
            # self.expr_tree.pprint()
            str_list.append(indent_str + 'return ' + self.expr_tree.to_c_string() + ';')
        if self.after:
            return str_list + self.after.to_c_string(level)
        else:
            return str_list


class PNodeControlWithBody(PNode, ABC):

    @staticmethod
    def swap(pnode_to_swap: PNode, fn_body: FunctionBody, new: PNode):
        """
        Swap an existing PNode with a new PNodeLoopWhile
        :param pnode_to_swap: existing (old) PNode
        :param new: new PNode -- must be assigned by subclass swap
        :param fn_body: the FunctionBody context
        :return:
        """
        # new = PNodeLoopWhile()
        new.before = PNode(after=new)
        new.after = PNode(before=new)

        body = PNode(parent=new)
        new.body_start = body
        new.body_end = body
        # print(f'    new: {new}')

        fn_body.unassigned_pnodes.add(new.before)
        fn_body.unassigned_pnodes.add(new.after)
        fn_body.unassigned_pnodes.add(body)
        fn_body.nes_pnodes.add(body)

        swap_finish(pnode_to_swap=pnode_to_swap, new=new, fn_body=fn_body)

        return new

    def __init__(self, before: PNode = None, after: PNode = None, parent: PNode = None):
        self.condition = None
        self.body_start = None
        self.body_end = None
        super().__init__(before=before, after=after, parent=parent)

    def swap_child_start(self, pnode_to_swap: PNode, new: PNode):
        if self.body_start == pnode_to_swap:
            self.body_start = new
            new.parent = self

    def swap_child_end(self, pnode_to_swap: PNode, new: PNode):
        if self.body_end == pnode_to_swap:
            self.body_end = new
            new.parent = self

    def visit_depth_first_forward(self, visitor: Visitor):
        visitor.visit(self)
        self.body_start.visit_depth_first_forward(visitor)
        if self.after:
            self.after.visit_depth_first_forward(visitor)

    def to_string_depth_first_forward(self, level: int = 0):
        indent_str = TAB_STR*level
        indent_str_body = TAB_STR*(level + 1)
        l = [f'{indent_str}{self}', f'{indent_str_body}<body>'] \
            + self.body_start.to_string_depth_first_forward(level + 2) \
            + [f'{indent_str_body}</body>', f'{indent_str}</{self}>']
        if self.after:
            return l + self.after.to_string_depth_first_forward(level)
        else:
            return l


class PNodeLoopWhile(PNodeControlWithBody):

    @staticmethod
    def swap(pnode_to_swap: PNode, fn_body: FunctionBody, new: PNode = None):
        """
        Swap an existing PNode with a new PNodeLoopWhile
        :param pnode_to_swap: existing (old) PNode
        :param fn_body: the FunctionBody context
        :param new: IGNORED
        :return:
        """
        new = PNodeLoopWhile()

        PNodeControlWithBody.swap(pnode_to_swap, fn_body, new)

        return new

    def __init__(self, before: PNode = None, after: PNode = None, parent: PNode = None):
        super().__init__(before=before, after=after, parent=parent)

    def __repr__(self):
        return f'<LoopWhile {self.pnode_idx}:{self.get_connectivity_str()}>'

    def to_c_string(self, level=0) -> List[str]:
        indent_str = TAB_STR * level
        str_list = list()
        str_list.append(indent_str + f'while({self.condition}) {{')
        if self.body_start:
            str_list += self.body_start.to_c_string(level + 1)
        str_list.append(indent_str + '}')
        if self.after:
            return str_list + self.after.to_c_string(level)
        else:
            return str_list


# TODO:
#  extend to allow multiple iterator variables, using comma operator
#  <initial> := <assignment_to_init_value> [ , <assignment_to_init_value> ]*
#  <test> := <conditional_expression>
#  <update> := <assignment_that_changes_var> [ , <assignment_to_init_value> ]*
#     <assignment_that_changes_var> := <var> = <var> <op> <value_or_expr> | <var> <assignment_op> <value_or_expr>
class PNodeLoopFor(PNodeControlWithBody):

    @staticmethod
    def swap(pnode_to_swap: PNode, fn_body: FunctionBody, new: PNode = None):
        """
        Swap an existing PNode with a new PNodeLoopFor
        :param pnode_to_swap: existing (old) PNode
        :param fn_body: the FunctionBody context
        :param new: IGNORED
        :return:
        """
        new = PNodeLoopFor()

        PNodeControlWithBody.swap(pnode_to_swap, fn_body, new)

        return new

    def __init__(self, before: PNode = None, after: PNode = None, parent: PNode = None):
        super().__init__(before=before, after=after, parent=parent)

    def __repr__(self):
        return f'<LoopFor {self.pnode_idx}:{self.get_connectivity_str()}>'

    def to_c_string(self, level=0) -> List[str]:
        indent_str = TAB_STR * level
        str_list = list()
        str_list.append(indent_str + f'for({self.condition}) {{')
        if self.body_start:
            str_list += self.body_start.to_c_string(level + 1)
        str_list.append(indent_str + '}')
        if self.after:
            return str_list + self.after.to_c_string(level)
        else:
            return str_list


class PNodeCondIf(PNodeControlWithBody):

    @staticmethod
    def swap(pnode_to_swap: PNode, fn_body: FunctionBody, new: PNode = None):
        new = PNodeCondIf()

        PNodeControlWithBody.swap(pnode_to_swap, fn_body, new)

        return new

    def __init__(self, before: PNode = None, after: PNode = None, parent: PNode = None):
        super().__init__(before=before, after=after, parent=parent)

    def __repr__(self):
        return f'<CondIf {self.pnode_idx}:{self.get_connectivity_str()}>'

    def to_string_depth_first_forward(self, level: int = 0):
        indent_str = TAB_STR*level
        indent_str_body = TAB_STR*(level + 1)
        l = [f'{indent_str}{self}>', f'{indent_str_body}<body_if>'] \
            + self.body_start.to_string_depth_first_forward(level + 2) \
            + [f'{indent_str_body}</body_if>', f'{indent_str}</{self}>']
        if self.after:
            return l + self.after.to_string_depth_first_forward(level)
        else:
            return l

    def to_c_string(self, level=0) -> List[str]:
        indent_str = TAB_STR * level
        str_list = list()
        str_list.append(indent_str + f'if({self.condition}) {{')
        if self.body_start:
            str_list += self.body_start.to_c_string(level + 1)
        str_list.append(indent_str + '}')
        if self.after:
            return str_list + self.after.to_c_string(level)
        else:
            return str_list


class PNodeCondIfElse(PNode):

    @staticmethod
    def swap(pnode_to_swap: PNode, fn_body: FunctionBody):
        new = PNodeCondIfElse()
        new.before = PNode(after=new)
        new.after = PNode(before=new)

        body_if = PNode(parent=new)
        new.body_if_start = body_if
        new.body_if_end = body_if
        body_else = PNode(parent=new)
        new.body_else_start = body_else
        new.body_else_end = body_else
        # print(f'    new: {new}')

        fn_body.unassigned_pnodes.add(new.before)
        fn_body.unassigned_pnodes.add(new.after)
        fn_body.unassigned_pnodes.add(body_if)
        fn_body.nes_pnodes.add(body_if)
        fn_body.unassigned_pnodes.add(body_else)
        fn_body.nes_pnodes.add(body_else)

        swap_finish(pnode_to_swap=pnode_to_swap, new=new, fn_body=fn_body)

        return new

    def __init__(self, before: PNode = None, after: PNode = None, parent: PNode = None):
        self.condition = None
        self.body_if_start = None
        self.body_if_end = None
        self.body_else_start = None
        self.body_else_end = None
        super().__init__(before=before, after=after, parent=parent)

    def __repr__(self):
        return f'<CondIfElse {self.pnode_idx}:{self.get_connectivity_str()}>'

    def swap_child_start(self, pnode_to_swap: PNode, new: PNode):
        if self.body_if_start == pnode_to_swap:
            self.body_if_start = new
            new.parent = self
        elif self.body_else_start == pnode_to_swap:
            self.body_else_start = new
            new.parent = self

    def swap_child_end(self, pnode_to_swap: PNode, new: PNode):
        if self.body_if_end == pnode_to_swap:
            self.body_if_end = new
            new.parent = self
        elif self.body_else_end == pnode_to_swap:
            self.body_else_end = new
            new.parent = self

    def visit_depth_first_forward(self, visitor: Visitor):
        visitor.visit(self)
        self.body_if_start.visit_depth_first_forward(visitor)
        self.body_else_start.visit_depth_first_forward(visitor)
        if self.after:
            self.after.visit_depth_first_forward(visitor)

    def to_string_depth_first_forward(self, level: int = 0):
        indent_str = TAB_STR*level
        indent_str_body = TAB_STR*(level + 1)
        l = [f'{indent_str}{self}', f'{indent_str_body}<if_cond>'] \
            + self.body_if_start.to_string_depth_first_forward(level + 2) \
            + [f'{indent_str_body}</if_cond>', f'{indent_str_body}<else_cond>'] \
            + self.body_else_start.to_string_depth_first_forward(level + 2) \
            + [f'{indent_str_body}</else_cond>', f'{indent_str}</{self}>']
        if self.after:
            return l + self.after.to_string_depth_first_forward(level)
        else:
            return l

    def to_c_string(self, level=0) -> List[str]:
        indent_str = TAB_STR * level
        str_list = list()
        str_list.append(indent_str + f'if({self.condition}) {{')
        if self.body_if_start:
            str_list += self.body_if_start.to_c_string(level + 1)
        str_list.append(indent_str + '} else {')
        if self.body_else_start:
            str_list += self.body_else_start.to_c_string(level + 1)
        str_list.append(indent_str + '}')
        if self.after:
            return str_list + self.after.to_c_string(level)
        else:
            return str_list


# -----------------------------------------------------------------------------
# Debug mini-tests
#   These are the start of what should be a more proper unit test suite...
# -----------------------------------------------------------------------------

def debug_generate_function_spec():
    prog = ProgramSpec(params=CONFIG_1)
    arg_name_vargen = VarGen('p')
    args = list()
    for aidx in range(4):
        # TODO need to eventually generalize to allow for pointers
        arg_name = arg_name_vargen.get_name()
        arg_type = random.choice(prog.params.map_typecat_to_type['ANY'])
        args.append(VariableDecl(name=arg_name, var_type=arg_type))
    fn_spec = FunctionSpec(
        name='fn_manual',
        args=args,
        return_type=random.choice(prog.params.map_typecat_to_type['ANY']),
        # globals_set_at_body_top=False  # TODO see above in FunctionSpec
    )
    return fn_spec


def debug_show_args_of_all_function_specs():
    prog = ProgramSpec(params=CONFIG_1)
    prog.sample()
    fns_dict = prog.functions_builtin | prog.functions
    for fn_name, fn_spec in fns_dict.items():
        print(f'{fn_name} : {fn_spec.args}')


def debug_generate_expr_tree(verbose=None):
    """
    Manually constructs an expression tree

    (fn0 <_0> (* <_1> <_2>) (max <_3> <_4>) (sqrt <_5>))

    :return:
    """
    prog = ProgramSpec(params=CONFIG_1)
    prog.sample()
    fn_manual = debug_generate_function_spec()
    if verbose:
        fn_manual.pprint()
    prog.functions[fn_manual.name] = fn_manual

    expr_tree = ExprTree(num_ops=4, program_spec=prog, function_spec=prog.functions['fn0'])

    if verbose:
        print(f'{prog.functions.keys()}')
        print(f'{prog.functions_builtin.keys()}')

    fn_times = prog.functions_builtin['*']
    # fn_times.pprint()
    fn_max = prog.functions_builtin['max']
    # fn_max.pprint()
    fn_sqrt = prog.functions_builtin['sqrt']
    # fn_sqrt.pprint()
    expr_tree.add_op_at(0, fn_manual)
    expr_tree.add_op_at(2, fn_times)
    expr_tree.add_op_at(3, fn_max)
    expr_tree.add_op_at(4, fn_sqrt)

    if verbose:
        expr_tree.pprint()

    return expr_tree


def debug_test_program_spec_get_fns_with_num_args():
    prog = ProgramSpec(params=CONFIG_1)
    prog.sample()
    print('All available 2-argument fns:')
    fns_with_2_args = prog.get_fns_with_num_args(num_args=2)
    for i, fn_spec in enumerate(fns_with_2_args):
        print(f'{i} : {fn_spec.name} : num_args={len(fn_spec.args)}')


def debug_test_expr_tree_swap_new_op_at():
    prog = ProgramSpec(params=CONFIG_1)
    prog.sample()

    expr_tree = debug_generate_expr_tree()
    expr_tree.pprint()

    fn_max = prog.get_fn('max')
    index = 2
    print(f'\nReplacing index {index} currently holding {expr_tree.map_index_to_op[index].name} with {fn_max.name}')
    expr_tree.swap_new_op_at(index=index, new_op=fn_max, verbose=True)

    print()
    expr_tree.pprint()

    fn_sqrt = prog.get_fn('sqrt')
    index = 4
    print(f'\nReplacing index {index} currently holding {expr_tree.map_index_to_op[index].name} with {fn_sqrt.name}')
    expr_tree.swap_new_op_at(index=index, new_op=fn_sqrt, verbose=True)

    print()
    expr_tree.pprint()


def debug_generate_function_body_pnode_structure():
    """
    Manually constructs a function body "sample"

    LoopFor_1
        Expr_1
        LoopFor_2
            Expr_3
            Expr_2
            condIfElse_1
                cond_if
                    Expr_4
                cond_else
                    Expr_5
            Expr_6
        LoopWhile_1
            CondIf_1
                Expr_7
            Expr_8
        Expr_9
    CondIf_2
        Expr_10
    Expr_11

    :return:
    """
    prog = ProgramSpec(params=CONFIG_1)
    prog.sample()
    fb = FunctionBody(program_spec=prog, function_spec=prog.functions['fn0'])

    for_loop_1 = PNodeLoopFor.swap(pnode_to_swap=fb.head, fn_body=fb)
    for_loop_2 = PNodeLoopFor.swap(pnode_to_swap=for_loop_1.body_start, fn_body=fb)
    while_loop_1 = PNodeLoopWhile.swap(pnode_to_swap=for_loop_2.after, fn_body=fb)
    cond_ifelse_1 = PNodeCondIfElse.swap(pnode_to_swap=for_loop_2.body_start, fn_body=fb)
    cond_if_1 = PNodeCondIf.swap(pnode_to_swap=while_loop_1.body_start, fn_body=fb)
    cond_if_2 = PNodeCondIf.swap(pnode_to_swap=for_loop_1.after, fn_body=fb)
    expr_1 = PNodeExpr.swap(pnode_to_swap=for_loop_2.before, fn_body=fb)
    expr_2 = PNodeExpr.swap(pnode_to_swap=cond_ifelse_1.before, fn_body=fb)
    expr_3 = PNodeExpr.swap(pnode_to_swap=expr_2.before, fn_body=fb)
    expr_4 = PNodeExpr.swap(pnode_to_swap=cond_ifelse_1.body_if_start, fn_body=fb)
    expr_5 = PNodeExpr.swap(pnode_to_swap=cond_ifelse_1.body_else_start, fn_body=fb)
    expr_6 = PNodeExpr.swap(pnode_to_swap=cond_ifelse_1.after, fn_body=fb)
    expr_7 = PNodeExpr.swap(pnode_to_swap=cond_if_1.body_start, fn_body=fb)
    expr_8 = PNodeExpr.swap(pnode_to_swap=cond_if_1.after, fn_body=fb)
    expr_9 = PNodeExpr.swap(pnode_to_swap=while_loop_1.after, fn_body=fb)
    expr_10 = PNodeExpr.swap(pnode_to_swap=cond_if_2.body_start, fn_body=fb)
    expr_11 = PNodeExpr.swap(pnode_to_swap=cond_if_2.after, fn_body=fb)

    # fb.pprint_depth_first()

    fb.remove_unassigned_pnodes()

    # print()
    # fb.pprint_depth_first()

    # print(f'{fb.head} {fb.tail} {fb.unassigned_pnodes} {fb.nes_pnodes}')

    # fb.index_pnodes(reset=True)
    # for idx, pnode in fb.tree_pnode_by_index.items():
    #     print(f'{idx}: {pnode}')

    return fb


def debug_test_visit_forward_and_backward_up():
    fb = debug_generate_function_body_pnode_structure()
    fb.pprint_depth_first()
    v1 = VisitorCollectElements(of_type=PNodeExpr)
    fb.visit_depth_first_forward(v1)
    elms = v1.get_elements()

    print('Forward up')
    for i, (elm, context) in enumerate(elms):
        v2 = VisitorCollectElements()
        elm.visit_forward_up(v2)
        print(f'{i}: {elm} : {list(v2.get_elements())}')

    print('\nBackward up')
    for i, (elm, context) in enumerate(elms):
        v2 = VisitorCollectElements()
        elm.visit_backward_up(v2)
        print(f'{i}: {elm} : {list(v2.get_elements())}')

    return fb


def debug_pprint_expression_trees(fb):
    print('\n>>> debug_pprint_expression_trees()')
    pnode_exprs = fb.collect_all_pnode_exprs(with_context_p=False)
    for i, pnode_expr in enumerate(pnode_exprs):
        print(f'{i} {pnode_expr} {pnode_expr.expr_assignment_var}')
        pnode_expr.expr_tree.pprint()
        # print(f'{i} {pnode_expr} : {pnode_expr.expr_assignment_var} '
        #       f': {pnode_expr.expr_tree.to_string()} '
        #       f': {pnode_expr.expr_tree.unassigned_indices}')


def debug_ensure_expression_at_least_one_var_per_operator():
    print('debug_ensure_expressions_affect_output()')
    prog = ProgramSpec(params=CONFIG_1)
    prog.sample()
    fb = FunctionBody(program_spec=prog, function_spec=prog.functions['fn0'])

    pnode_expr = PNodeExpr()
    expr_tree = debug_generate_expr_tree()
    pnode_expr.expr_tree = expr_tree
    fb.head = pnode_expr
    fb.tail = pnode_expr

    debug_pprint_expression_trees(fb)

    print('\ncall fb.ensure_expression_at_least_one_var_per_operator()')
    fb.ensure_expression_at_least_one_var_per_operator(pnode_expr=pnode_expr)

    debug_pprint_expression_trees(fb)


def debug_test_sample_expression_trees():
    fb = debug_generate_function_body_pnode_structure()
    pnode_exprs = fb.collect_all_pnode_exprs(with_context_p=False)

    print('\n>>> call sample_expression_trees:')
    fb.sample_expression_trees(pnode_exprs=pnode_exprs, verbose=True)

    debug_pprint_expression_trees(fb)

    print('\n>>> call ensure_expression_affect_output on each pnode:')
    for pnode_expr in pnode_exprs[1:]:
        # don't do for last expression (which is at the return)
        fb.ensure_expressions_affect_output(pnode_expr)

    debug_pprint_expression_trees(fb)

    print('\n>>> call ensure_function_args_used_at_least_once:')
    fb.ensure_function_args_used_at_least_once()

    debug_pprint_expression_trees(fb)

    print('\n>>> call ensure_expression_at_least_one_var_per_operator on each pnode:')
    for pnode_expr in pnode_exprs:
        # TODO: this does not seem to be working...
        fb.ensure_expression_at_least_one_var_per_operator(pnode_expr)

    debug_pprint_expression_trees(fb)

    print('\n>>> call ensure_expression_fill_remaining_unassigned on each pnode:')
    for pnode_expr in pnode_exprs:
        fb.ensure_expression_fill_remaining_unassigned(pnode_expr)

    debug_pprint_expression_trees(fb)

    fb.assign_literals_to_variable_decls()

    print('\nAll declared variables:')
    for i, var_decl in enumerate(fb.var_decls):
        print(f'  {i} : {var_decl}')


def debug_test_sample_and_complete_expression_trees():
    fb = debug_generate_function_body_pnode_structure()
    fb.sample(skip_sample_pnode_structure=True)

    debug_pprint_expression_trees(fb)

    print('\nAll declared variables:')
    for i, var_decl in enumerate(fb.var_decls):
        print(f'  {i} : {var_decl}')


def debug_test_program_spec_sample():
    prog = ProgramSpec(params=CONFIG_1)
    prog.sample(verbose=False)

    # print()

    # for fb in prog.function_bodies.values():
    #     print(f'----------------- {fb.function_spec.name}')
    #     fb.pprint_depth_first()
    # print(f'----------------- {fb.function_spec.name}')
    # prog.function_main_body.pprint_depth_first()
    #
    # print('=====================')

    print('\n'.join(prog.to_c_string()))

    # for i, (fn_name, fn_body) in enumerate(prog.function_bodies.items()):
    #     print(f'\n{i} : {fn_name}')
    #     # debug_pprint_expression_trees(fn_body)
    #     print(fn_body.to_string())


# -----------------------------------------------------------------------------
# Generate and save program
# -----------------------------------------------------------------------------

def generate_and_save_program(filepath: str) -> Tuple[ProgramSpec, str]:
    """
    Top-level fn to generate a new program and save it to file
    :param filepath:
    :return:
    """
    prog = ProgramSpec(params=CONFIG_1)
    prog.sample(verbose=False)
    sample_program_str = '\n'.join(prog.to_c_string())
    with open(filepath, 'w') as fout:
        fout.write(sample_program_str)
    return prog, sample_program_str


# -----------------------------------------------------------------------------
# Properties check
# -----------------------------------------------------------------------------

def check_properties():
    # every global is get at least once in some expression
    #   criteria set in: ProgramSpec.ensure_every_global_is_get_at_least_once()
    #   stored in: FunctionSpec.globals_to_be_get
    #   then satisfied by:
    # some globals have chance of being set
    #   criteria set in: ProgramSpec.
    #   stored in: FunctionSpec.globals_to_be_set
    # every introduced fn is called by another fn that leads to main
    #   criteria set in: ProgramSpec.sample_function_signatures(), which sets FunctionSpec.fns_to_call
    #   then satisfied by:
    #     FunctionBody.sample_expression_trees()
    #     ExprTree.sample()
    # every function argument parameter (VariableDecl) gets used in at least one ExprTree of FunctionBody
    #   criteria set by: the list of args in FunctionSpec
    #   then satisfied by:
    #     FunctionBody.sample_expression_trees():
    #       determines which expressions will 'get' args
    #     FunctionBody.ensure_function_args_used_at_least_once()
    #       assigns the arg param var decls to unassigned indices (or creates one via swap_new_op_at
    # at least one var per operator in each expression
    #   satisfied by FunctionBody.ensure_expression_at_least_one_var_per_operator()
    pass


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    prog = ProgramSpec(params=CONFIG_1)
    prog.sample()

    # prog.pprint()
    #
    # print()
    # print('Sample Expression:')
    # main_fn = prog.function_main
    # expr_tree = ExprTree(num_ops=4, program_spec=prog, function_spec=main_fn)
    # expr_tree.sample()
    # print(expr_tree.to_string())
    #
    # print()
    # print('Sample Block:')
    # block = Block(program_spec=prog)
    # block.sample()
    # print(block.to_string())
    #
    # print()
    # print('some fn samples:')
    # print(Counter([prog.sample_fn().name for i in range(10000)]))

    # print()
    # print('FunctionBody')
    # fb = FunctionBody(program_spec=prog)
    # fb.sample_pnode_structure()
    # print()
    # fb.pprint_depth_first()
    #
    # print()
    # print('visit_depth_first_forward')
    # v1 = VisitorCollectElements()
    # fb.visit_depth_first_forward(v1)
    # elms = v1.get_elements()
    # for i, elm in enumerate(elms):
    #     print(f'{i}: {elm}')
    #
    # print()
    # print('remove unassigned_pnodes')
    # fb.remove_unassigned_pnodes()
    #
    # print()
    # print('Review FunctionBody structure')
    # fb.pprint_depth_first()
    # print('-----')
    # v2 = VisitorCollectElements()
    # fb.visit_depth_first_forward(v2)
    # elms = v2.get_elements()
    # for i, elm in enumerate(elms):
    #     print(f'{i}: {elm}')
    #
    # print()
    # print('Collect only Exprs')
    # v3 = VisitorCollectElements(of_type=PNodeExpr)
    # fb.visit_depth_first_forward(v3)
    # elms = v3.get_elements()
    # for i, elm in enumerate(elms):
    #     print(f'{i}: {elm}')

    # fb = debug_generate_function_body()
    # fb.pprint_depth_first()

    # debug_show_args_of_all_function_specs()

    # debug_test_visit_forward_up()

    # debug_generate_expr_tree()
    # debug_test_program_spec_get_fns_with_num_args()
    # debug_test_expr_tree_swap_new_op_at()
    # debug_ensure_expression_at_least_one_var_per_operator()
    # debug_test_sample_expression_trees()
    # debug_test_sample_and_complete_expression_trees()
    debug_test_program_spec_sample()


# -----------------------------------------------------------------------------
# Top level
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

