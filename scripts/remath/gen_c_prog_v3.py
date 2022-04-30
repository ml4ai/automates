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


def sample_literal(t, _map=None):
    if _map is None:
        _map = MAP_TYPECAT_TO_TYPE
    if 'REAL_FLOATING' in _map and t in _map['REAL_FLOATING']:
        return random.uniform(-10, 10)
    elif 'DOUBLE' in _map and t in _map['DOUBLE']:
        return random.uniform(-10, 10)
    elif 'NON_FLOAT' in _map and t in _map['NON_FLOAT']:
        return random.randint(-100, 100)
    else:
        raise Exception(f"ERROR sample_literal():\n"
                        f"Unsupported type '{t}'")


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
     }   # double sin(double x);

# Definitions for functions from stdlib.h
OP_STDLIB_H = \
    {'abs': (('ANY', 'ANY'), 'PREFIX', '#include <stdlib.h>'),  # any_type abs (any_type);
     'min': (('ANY', 'ANY', 'ANY'), 'PREFIX', '#include <stdlib.h>'),  # any_type min (any_type a, any_type b);
     'max': (('ANY', 'ANY', 'ANY'), 'PREFIX', '#include <stdlib.h>'),  # any_type max (any_type a, any_type b);
     }


# NOTE: type inspection warns that OP_MATH_H has a different value type signature
OP_DEFINITIONS = OP_ARITHMETIC | OP_MATH_H | OP_STDLIB_H

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
#
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
    expressions_num: Tuple[int, int]  # number of expressions per block
    operators_num: Tuple[int, int]    # number of operators per expression
    operators_primitive: Dict  # the primitive operators provided

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
    main_default_cli=True,
    globals_num=(4, 4),
    globals_prob_set=0.8,  # prob global gets set in each function
    functions_num=(2, 2),
    function_arguments_num=(8, 8),
    functions_allow_recursive_calls=True,
    expressions_num=(8, 8),
    operators_num=(4, 4),
    operators_primitive=OP_DEFINITIONS,

    conditional_prob=1.0,          # probability of creating conditionals
    conditionals_num=(4, 4),       # when creating conditionals, how many?
    conditional_else_prob=0.5,     # probability that a conditional has an else branch
    conditional_nesting_level=3,   # 1 = no nesting, otherwise (>1) nesting up to level depth
    conditional_return_prob=0.25,

    loop_prob=1.0,                 # probability of creating loops
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
    def __init__(self, name: str, var_type: str,
                 var_value: Union[str, None] = None,
                 var_type_ptr: Union[str, None] = None,
                 var_type_arr: bool = False):
        self.name = name
        self.var_type = var_type
        self.var_type_ptr = var_type_ptr
        self.var_type_arr = var_type_arr
        self.var_value = var_value
        self.accessed: Set[str] = set()  # names of fns (including main) that access the global
        self.set: Set[str] = set()  # names of fns (including main) that set the global

    def __repr__(self):
        name = self.name
        if self.var_type_ptr:
            name = f'{self.var_type_ptr}{name}'
        if self.var_type_arr:
            name = f'{name}[]'
        if self.var_type_ptr:
            return f'<VarDecl {self.var_type} {name} = {self.var_value}>'
        else:
            return f'<VarDecl {self.var_type} {name} = {self.var_value}>'

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


# TODO: Way to get expressions through conditionals:
#  Have expression_var (the variable the expression value is set to) be
#  defined outside of the conditional, and then it get updates in either conditional branch,
#  and then used after the conditionals
class BlockSpec:
    def __init__(self, var_env: List[str], parent: Union["BlockSpec", None] = None,
                 level: int = 1):
        self.level: int = level
        self.parent: Union[BlockSpec, None] = parent
        self.var_env: List[str] = var_env
        self.expressions: Dict[int, Union[ExprTree, ConditionalSpec, LoopWhileSpec, LoopForSpec]] = list()

    def sample(self, function_spec: "FunctionSpec", program_spec: "ProgramSpec"):
        # sample how many expressions will be in this block
        num_expressions = random.randint(program_spec.params.expressions_num[0],
                                         program_spec.params.expressions_num[1])
        for i in range(num_expressions):
            # sample how many operators will be in this expression
            num_ops = random.randint(program_spec.params.operators_num[0],
                                     program_spec.params.operators_num[1])
            # sample the expression tree
            expr = ExprTree(num_ops=num_ops, function_spec=function_spec, program_spec=program_spec)
            self.expressions[i] = expr
            # self.expr_var[i] = None

    def to_string(self):
        indent = ' '*(self.level * TAB_SIZE)
        lines = list()
        for expr in self.expressions.values():
            lines.append(f'{indent}{expr.to_string()}')
        return '\n'.join(lines)


class ConditionalSpec(BlockSpec):
    def __init__(self, var_env: List[str], parent: BlockSpec = None,
                 condition: "ExprTree" = None,
                 if_cond: BlockSpec = None,
                 else_cond: BlockSpec = None,
                 level: int = 0):
        self.condition: ExprTree = condition
        self.if_cond: BlockSpec = if_cond
        self.else_cond: BlockSpec = else_cond
        super(BlockSpec, self).__init__(var_env=var_env, parent=parent, level=level)


class LoopWhileSpec(BlockSpec):
    def __init__(self, var_env: List[str], parent: BlockSpec = None,
                 condition: "ExprTree" = None,
                 body: BlockSpec = None,
                 level: int = 0):
        self.condition: ExprTree = condition
        self.body: Union[BlockSpec, None] = body
        super(BlockSpec, self).__init__(var_env=var_env, parent=parent, level=level)


# TODO: finish
#  extend to allow multiple iterator variables, using comma operator
#  <initial> := <assignment_to_init_value> [ , <assignment_to_init_value> ]*
#  <test> := <conditional_expression>
#  <update> := <assignment_that_changes_var> [ , <assignment_to_init_value> ]*
#     <assignment_that_changes_var> := <var> = <var> <op> <value_or_expr> | <var> <assignment_op> <value_or_expr>
class LoopForSpec:
    def __init__(self):
        # Here the condition is a for-loop decl: (<initial>; <test>; <update>)
        self.condition = None
        self.body: BlockSpec = None


# TODO Every function has
#  (1) a return
#  OR
#  (2) all conditional branches have returns (and no more expressions after the last conditional block)
class FunctionSpec:
    """
    Specification of a function
    """

    @staticmethod
    def op_def_dict_to_fn_spec_dict(op_def_dict: Dict):
        """
        This static method converts an operator definition dictionary into
          a dictionary with
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

    def __init__(self, name: str,
                 args: Union[List[VariableDecl], None],
                 return_type: str,
                 syntax: str = 'PREFIX',  # or 'INFIX' for some binary operators
                 include_library: Union[str, None] = None,
                 globals_to_be_get: Union[List[str], None] = None,
                 globals_to_be_set: Union[List[str], None] = None,
                 globals_set_at_body_top: bool = False,
                 body: BlockSpec = None,
                 local_vargen: VarGen = None):
        self.name = name
        if local_vargen is None:
            self.local_vargen = VarGen('x')
        else:
            self.local_vargen = local_vargen
        self.args = args
        self.return_type = return_type
        self.syntax = syntax
        self.include_library = include_library
        if globals_to_be_get is None:  # list of globals that need to be get
            self.globals_to_be_get = list()
        else:
            self.globls_to_be_get = globals_to_be_get
        if globals_to_be_set is None:  # list of globals that need to be set
            self.globals_to_be_set = list()
        else:
            self.globals_to_be_set = globals_to_be_set
        self.globals_set_at_body_top = globals_set_at_body_top  # flag for whether globals should be set at body top
        self.body = body
        self.called_by: Set[str] = set()  #

    def to_c_string_signature(self):
        arg_string = ''
        if self.args is not None:
            arg_string = ', '.join([arg.to_c_string() for arg in self.args])
        return f'{self.return_type} {self.name}({arg_string})'

    def pprint(self, indent=0):
        indent_str = ' '*indent
        if self.body:
            print(f'{indent_str}{self.to_c_string_signature()}')
            self.body.to_string()
        else:
            print(f'{indent_str}{self.to_c_string_signature()}')
        indent_str = ' '*(indent+2)
        if self.globals_to_be_get:
            print(f'{indent_str}globals_to_be_get: {self.globals_to_be_get}')
        if self.globals_to_be_set:
            print(f'{indent_str}globals_to_be_set: {self.globals_to_be_set}')
            print(f'{indent_str}globals_set_at_body_top: {self.globals_set_at_body_top}')


class Block:
    def __init__(self, expr_vargen: VarGen = None,
                 program_spec: "ProgramSpec" = None,
                 function_spec: "FunctionSpec" = None):
        self.program_spec: ProgramSpec = program_spec
        self.function_spec: FunctionSpec = function_spec
        if expr_vargen is None:
            self.expr_vargen = VarGen('e')
        else:
            self.expr_vargen = expr_vargen
        self.last_index: int = 0
        self.unassigned_indices: set[int] = {0}
        self.elm_indices: Set[int] = set()
        self.map_index_to_elm: Dict[int, str] = dict()
        self.map_index_to_children: Dict[int, List[int]] = dict()

    def sample(self):

        # (assign <before> <ExprTree> <after>)
        # (loop_while <before> <body> <after>)
        # (cond_if <before> <if_cond> <after>)
        # (cond_if_else <before> <if_cond> <else_cond> <after>)

        num_conditionals = 0
        if random.random() < self.program_spec.params.conditional_prob:
            num_conditionals = random.randint(self.program_spec.params.conditionals_num[0],
                                              self.program_spec.params.conditionals_num[1])

        print(f'DEBUG: num_conditionals={num_conditionals}')
        for i in range(num_conditionals):
            idx = random.choice(list(self.unassigned_indices))
            if random.random() < self.program_spec.params.conditional_else_prob:
                self.add_elm_at(index=idx, elm='cond_if_else', num_args=4)
            else:
                self.add_elm_at(index=idx, elm='cond_if', num_args=3)

        num_loop_while = 0
        if random.random() < self.program_spec.params.loop_prob:
            num_loop_while = random.randint(self.program_spec.params.loop_num[0],
                                            self.program_spec.params.loop_num[1])

        print(f'DEBUG: num_loop_while={num_loop_while}')
        for i in range(num_loop_while):
            idx = random.choice(list(self.unassigned_indices))
            self.add_elm_at(index=idx, elm='loop_while', num_args=3)

        num_expressions = random.randint(self.program_spec.params.expressions_num[0],
                                         self.program_spec.params.expressions_num[1])

        print(f'DEBUG: num_expressions={num_expressions}')
        for i in range(num_expressions):
            idx = random.choice(list(self.unassigned_indices))
            num_ops = random.randint(self.program_spec.params.operators_num[0],
                                     self.program_spec.params.operators_num[1])
            expr = ExprTree(num_ops=num_ops,
                            program_spec=self.program_spec,
                            function_spec=self.function_spec)
            expr.sample()
            self.add_elm_at(index=idx, elm=expr, num_args=1)

    def add_elm_at(self, index: int, elm: str, num_args: int):
        new_indices = list(range(self.last_index + 1, self.last_index + num_args + 1))
        self.last_index += num_args
        self.unassigned_indices |= set(new_indices)
        self.unassigned_indices.remove(index)
        self.elm_indices.add(index)
        self.map_index_to_elm[index] = elm
        self.map_index_to_children[index] = new_indices

    def to_string(self, index=0):
        if index in self.map_index_to_elm:
            elm = self.map_index_to_elm[index]
            if elm == 'loop_while':
                return f's:{self.to_string(self.map_index_to_children[index][0])}, ' \
                       f'(loop_while {self.to_string(self.map_index_to_children[index][1])}), ' \
                       f'e:{self.to_string(self.map_index_to_children[index][2])}'
            elif elm == 'cond_if':
                return f's:{self.to_string(self.map_index_to_children[index][0])}, ' \
                       f'(cond_if b1:{self.to_string(self.map_index_to_children[index][1])}), ' \
                       f'e:{self.to_string(self.map_index_to_children[index][2])}'
            elif elm == 'cond_if_else':
                return f's:{self.to_string(self.map_index_to_children[index][0])}, ' \
                       f'(cond_if_else b1:{self.to_string(self.map_index_to_children[index][1])}' \
                       f' b2:{self.to_string(self.map_index_to_children[index][2])}), ' \
                       f'e:{self.to_string(self.map_index_to_children[index][3])}'
            elif isinstance(elm, ExprTree) :
                return f'{self.to_string(self.map_index_to_children[index][0])}, ' \
                       f'({elm.to_string()})'
        else:
            return f'<{index}>'


class ExprTree:
    """
    An Expression Tree
    """
    def __init__(self, num_ops: int, function_spec: "FunctionSpec", program_spec: "ProgramSpec"):
        self.program_spec: ProgramSpec = program_spec     # needed to access globals, functions, primitive operators
        self.function_spec: FunctionSpec = function_spec  # needed to access globals_to_be_get
        self.num_ops: int = num_ops
        self.last_index: int = 0    # The highest index
        self.unassigned_indices: Set[int] = {0}  # indices that have not yet been assigned
        self.op_indices: Set[int] = set()        # indices of operators
        self.map_index_to_op: Dict[int, FunctionSpec] = dict()
        self.map_index_to_children: Dict[int, List[int]] = dict()   # map parent index to list of child indices
        self.value_assignments: Dict[int, Any] = dict()             # map index to literal or variable value
        self.var_literal_assignments: List[Tuple[str, str, Any]] = list()  # (var_name, type, literal_value)

    def sample(self):
        for i in range(self.num_ops):
            idx = random.choice(list(self.unassigned_indices))  # sample index within ExprTree
            fn = self.program_spec.sample_fn()
            self.add_op_at(index=idx, op=fn)

    def add_op_at(self, index: int, op: FunctionSpec):
        num_args = len(op.args)
        new_indices = list(range(self.last_index + 1, self.last_index + num_args + 1))
        self.last_index += num_args
        self.unassigned_indices |= set(new_indices)
        self.unassigned_indices.remove(index)
        self.op_indices.add(index)
        self.map_index_to_op[index] = op
        self.map_index_to_children[index] = new_indices

    def to_string(self, index=0):
        eol = ''  # end of line: either nothing (default) or semicolon (when end of expression)
        if index == 0:
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
        else:
            return f'<val {index}>'


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
        self.globals = dict()
        self.function_main: Union[FunctionSpec, None] = None
        self.function_name_vargen: VarGen = function_name_vargen
        self.functions_num = 0  # number of functions in addition to main
        self.functions: Dict[str, FunctionSpec] = dict()  # all defined fns (besides main)
        self.functions_builtin: Dict[str, FunctionSpec] = dict()  # all built-in functions

    def sample_fn(self, remove: Union[Set[str], None] = None):
        fns = self.functions_builtin | self.functions
        if remove:
            fn_names = tuple(set(fns.keys()) - remove)
        else:
            fn_names = tuple(fns.keys())
        fn_name = random.choice(fn_names)
        return fns[fn_name]

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
            self.functions_builtin = \
                FunctionSpec.op_def_dict_to_fn_spec_dict(self.params.operators_primitive)

    def sample_globals(self):
        for gidx in range(self.globals_num):
            var_name = self.globals_vargen.get_name()
            var_type = random.choice(self.params.map_typecat_to_type['ANY'])
            self.globals[var_name] = VariableDecl(name=var_name, var_type=var_type)

    def sample_function_signatures(self):
        # create main function -- there will always be a main
        args = None
        if self.params.main_default_cli:
            args = [VariableDecl(name='argc', var_type='int'),
                    VariableDecl(name='argv', var_type='char', var_type_ptr='*', var_type_arr=True)]
        self.function_main = FunctionSpec(
            name='main',
            args=args,
            return_type='int',
            globals_set_at_body_top=True  # main always sets all globals at the top
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
                    args.append(VariableDecl(name=arg_name, var_type=arg_type))
            fn_spec = FunctionSpec(
                name=fun_name,
                args=args,
                return_type=random.choice(self.params.map_typecat_to_type['ANY']),
                globals_set_at_body_top=False  # non-main may set globals anywhere
            )
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

    def sample(self):
        """
        Top-level driver for sampling a program based on GeneratorConfig parameters.
        :return:
        """
        self.init_program_parameters()
        self.sample_globals()
        self.sample_function_signatures()
        self.ensure_every_global_is_get_at_least_once()

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
    def visit(self, obj):
        """
        Implements the visitor
        :return:
        """


class VisitorCollectElements(Visitor):

    def __init__(self):
        self.elements = list()

    def visit(self, obj):
        self.elements.append(obj)

    def get_elements(self):
        return self.elements


class FunctionBody:
    def __init__(self,
                 program_spec: ProgramSpec = None,
                 function_spec: FunctionSpec = None,
                 expr_vargen: VarGen = None):

        PNode.reset_pnode_index()

        self.program_spec: ProgramSpec = program_spec
        self.function_spec: FunctionSpec = function_spec
        if expr_vargen is None:
            self.expr_vargen = VarGen('e')
        else:
            self.expr_vargen = expr_vargen

        self.head: PNode = PNode()
        self.tail = self.head
        self.unassigned_pnodes: Set[PNode] = {self.head}
        self.nes_pnodes: Set[PNode] = set()  # PNodes that must be filled with expressions

    def sample(self):

        print(f'==================== Sample control structures')

        num_loops = 0
        if random.random() < self.program_spec.params.loop_prob:
            num_loops = random.randint(self.program_spec.params.loop_num[0],
                                       self.program_spec.params.loop_num[1])
        create_loop_tokens = ['LOOP']*num_loops
        print(f'DEBUG: num_loops={num_loops}')

        num_conditionals = 0
        if random.random() < self.program_spec.params.conditional_prob:
            num_conditionals = random.randint(self.program_spec.params.conditionals_num[0],
                                              self.program_spec.params.conditionals_num[1])
        create_cond_tokens = ['COND']*num_conditionals
        print(f'DEBUG: num_conditionals={num_conditionals}')

        create_tokens = create_loop_tokens + create_cond_tokens
        random.shuffle(create_tokens)
        print(f'DEBUG: create_tokens: {create_tokens}')

        for i, token in enumerate(create_tokens):
            print(f'----------- token: {token}')
            pnode_to_swap = random.choice(list(self.unassigned_pnodes))
            print(f'    node_to_swap: {pnode_to_swap}')
            if token == 'LOOP':
                if random.random() < self.program_spec.params.loop_for_prob:
                    print(f'    LOOP_FOR {i} {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')
                    PNodeLoopFor.swap(pnode_to_swap=pnode_to_swap, fn_body=self)
                else:
                    print(f'    LOOP_WHILE {i} {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')
                    PNodeLoopWhile.swap(pnode_to_swap=pnode_to_swap, fn_body=self)
            elif token == 'COND':
                if random.random() < self.program_spec.params.conditional_else_prob:
                    print(f'    COND_IF {i} {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')
                    PNodeCondIfElse.swap(pnode_to_swap=pnode_to_swap, fn_body=self)
                else:
                    print(f'    COND_IF_ELSE {i} {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')
                    PNodeCondIf.swap(pnode_to_swap=pnode_to_swap, fn_body=self)
            print(f'    {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')

        # Sample expressions
        print(f'==================== Sample NES expressions')

        # Ensure tail is in NES
        self.nes_pnodes.add(self.tail)

        num_expressions = random.randint(self.program_spec.params.expressions_num[0],
                                         self.program_spec.params.expressions_num[1])

        print(f'DEBUG: num_expressions={num_expressions}, num_nes={len(self.nes_pnodes)}')

        # Sample Expr for all NES PNodes
        num_nes_nodes = len(self.nes_pnodes)
        for i, pnode_to_swap in enumerate(list(self.nes_pnodes)):

            # TODO
            num_ops = random.randint(self.program_spec.params.operators_num[0],
                                     self.program_spec.params.operators_num[1])

            print('-----------')
            print(f'    EXPR {i} {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')

            print(f'    NES node_to_swap: {pnode_to_swap}')
            PNodeExpr.swap(pnode_to_swap=pnode_to_swap, fn_body=self)
            print(f'    {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')

            # self.pprint_depth_first()

        # Sample Expr any remaining unassigned PNodes
        print(f'==================== Sample remaining expressions')
        num_remaining_expressions = num_expressions - num_nes_nodes
        print(f'DEBUG: num_remaining_expressions={num_remaining_expressions}')
        if num_remaining_expressions > 0:
            for i in range(num_remaining_expressions):

                # TODO
                num_ops = random.randint(self.program_spec.params.operators_num[0],
                                         self.program_spec.params.operators_num[1])

                print('-----------')
                print(f'    EXPR {i} {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')

                pnode_to_swap = random.choice(list(self.unassigned_pnodes))
                print(f'    node_to_swap: {pnode_to_swap}')
                PNodeExpr.swap(pnode_to_swap=pnode_to_swap, fn_body=self)
                print(f'    {self.head} {self.tail} {self.unassigned_pnodes} {self.nes_pnodes}')

                # self.pprint_depth_first()

    def visit_depth_first_forward(self, visitor: Visitor):
        self.head.visit_depth_first_forward(visitor)

    def to_string_depth_first_forward(self):
        l = [f'head:{self.head}', f'tail:{self.tail}']
        return l + self.head.to_string_depth_first_forward()

    def pprint_depth_first(self):
        print('\n'.join(self.to_string_depth_first_forward()))


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
        print(f'    new: {new}')

        fn_body.unassigned_pnodes.add(new.before)

        swap_finish_no_after(pnode_to_swap=pnode_to_swap, new=new, fn_body=fn_body)

        # if pnode_to_swap.before is None:
        #     if fn_body.head == pnode_to_swap:
        #         fn_body.head = new.before
        # else:
        #     new.before.before = pnode_to_swap.before
        #     pnode_to_swap.before.after = new.before
        #
        # if pnode_to_swap.after is None:
        #     if fn_body.tail == pnode_to_swap:
        #         fn_body.tail = new
        # if pnode_to_swap.after is not None:
        #     new.after = pnode_to_swap.after
        #     pnode_to_swap.after.before = new
        #
        # if pnode_to_swap.parent is not None:
        #     # new.parent = pnode_to_swap.parent
        #     pnode_to_swap.parent.swap_child_start(pnode_to_swap, new.before)
        #     pnode_to_swap.parent.swap_child_end(pnode_to_swap, new)
        #
        # fn_body.unassigned_pnodes.remove(pnode_to_swap)
        # if pnode_to_swap in fn_body.nes_pnodes:
        #     fn_body.nes_pnodes.remove(pnode_to_swap)
        # del pnode_to_swap

    def __init__(self, before: PNode = None, after: PNode = None, parent: PNode = None):
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
        print(f'    new: {new}')

        fn_body.unassigned_pnodes.add(new.before)
        fn_body.unassigned_pnodes.add(new.after)
        fn_body.unassigned_pnodes.add(body)
        fn_body.nes_pnodes.add(body)

        swap_finish(pnode_to_swap=pnode_to_swap, new=new, fn_body=fn_body)

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

    #     new.before = PNode(after=new)
    #     new.after = PNode(before=new)
    #
    #     body = PNode(parent=new)
    #     new.body_start = body
    #     new.body_end = body
    #     print(f'    new: {new}')
    #
    #     fn_body.unassigned_pnodes.add(new.before)
    #     fn_body.unassigned_pnodes.add(new.after)
    #     fn_body.unassigned_pnodes.add(body)
    #     fn_body.nes_pnodes.add(body)
    #
    #     swap_finish(pnode_to_swap=pnode_to_swap, new=new, fn_body=fn_body)
    #
    #     # if pnode_to_swap.before is None:
    #     #     # new.before = PNode(after=new)
    #     #     # fn_body.unassigned_pnodes.add(new.before)
    #     #     if fn_body.head == pnode_to_swap:
    #     #         fn_body.head = new.before
    #     # else:
    #     #     new.before.before = pnode_to_swap.before
    #     #     pnode_to_swap.before.after = new.before
    #     #
    #     # if pnode_to_swap.after is None:
    #     #     # new.after = PNode(before=new)
    #     #     # fn_body.unassigned_pnodes.add(new.after)
    #     #     if fn_body.tail == pnode_to_swap:
    #     #         fn_body.tail = new.after
    #     # else:
    #     #     new.after.after = pnode_to_swap.after
    #     #     pnode_to_swap.after.before = new.after
    #     #
    #     # if pnode_to_swap.parent is not None:
    #     #     # new.parent = pnode_to_swap.parent
    #     #     pnode_to_swap.parent.swap_child_start(pnode_to_swap, new.before)
    #     #     pnode_to_swap.parent.swap_child_end(pnode_to_swap, new.after)
    #     #
    #     # fn_body.unassigned_pnodes.remove(pnode_to_swap)
    #     # if pnode_to_swap in fn_body.nes_pnodes:
    #     #     fn_body.nes_pnodes.remove(pnode_to_swap)
    #     # del pnode_to_swap

    def __init__(self, before: PNode = None, after: PNode = None, parent: PNode = None):
        # self.condition = None
        # self.body_start = None
        # self.body_end = None
        super().__init__(before=before, after=after, parent=parent)

    def __repr__(self):
        return f'<LoopWhile {self.pnode_idx}:{self.get_connectivity_str()}>'

    # def swap_child_start(self, pnode_to_swap: PNode, new: PNode):
    #     if self.body_start == pnode_to_swap:
    #         self.body_start = new
    #         new.parent = self
    #
    # def swap_child_end(self, pnode_to_swap: PNode, new: PNode):
    #     if self.body_end == pnode_to_swap:
    #         self.body_end = new
    #         new.parent = self
    #
    # def visit_depth_first_forward(self, visitor: Visitor):
    #     visitor.visit(self)
    #     self.body_start.visit_depth_first_forward(visitor)
    #     if self.after:
    #         self.after.visit_depth_first_forward(visitor)

    # def to_string_depth_first_forward(self, level: int = 0):
    #     indent_str = TAB_STR*level
    #     indent_str_body = TAB_STR*(level + 1)
    #     l = [f'{indent_str}{self}', f'{indent_str_body}<body>'] \
    #         + self.body_start.to_string_depth_first_forward(level + 2) \
    #         + [f'{indent_str_body}</body>', f'{indent_str}</{self}>']
    #     if self.after:
    #         return l + self.after.to_string_depth_first_forward(level)
    #     else:
    #         return l


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

    #     new.before = PNode(after=new)
    #     new.after = PNode(before=new)
    #
    #     body = PNode(parent=new)
    #     new.body_start = body
    #     new.body_end = body
    #     print(f'    new: {new}')
    #
    #     fn_body.unassigned_pnodes.add(new.before)
    #     fn_body.unassigned_pnodes.add(new.after)
    #     fn_body.unassigned_pnodes.add(body)
    #     fn_body.nes_pnodes.add(body)
    #
    #     swap_finish(pnode_to_swap=pnode_to_swap, new=new, fn_body=fn_body)
    #
    #     # if pnode_to_swap.before is None:
    #     #     if fn_body.head == pnode_to_swap:
    #     #         fn_body.head = new.before
    #     # else:
    #     #     new.before.before = pnode_to_swap.before
    #     #     pnode_to_swap.before.after = new.before
    #     #
    #     # if pnode_to_swap.after is None:
    #     #     if fn_body.tail == pnode_to_swap:
    #     #         fn_body.tail = new.after
    #     # else:
    #     #     new.after.after = pnode_to_swap.after
    #     #     pnode_to_swap.after.before = new.after
    #     #
    #     # if pnode_to_swap.parent is not None:
    #     #     pnode_to_swap.parent.swap_child_start(pnode_to_swap, new.before)
    #     #     pnode_to_swap.parent.swap_child_end(pnode_to_swap, new.after)
    #     #
    #     # fn_body.unassigned_pnodes.remove(pnode_to_swap)
    #     # if pnode_to_swap in fn_body.nes_pnodes:
    #     #     fn_body.nes_pnodes.remove(pnode_to_swap)
    #     # del pnode_to_swap

    def __init__(self, before: PNode = None, after: PNode = None, parent: PNode = None):
        # self.condition = None
        # self.body_start = None
        # self.body_end = None
        super().__init__(before=before, after=after, parent=parent)

    def __repr__(self):
        return f'<LoopFor {self.pnode_idx}:{self.get_connectivity_str()}>'

    # def swap_child_start(self, pnode_to_swap: PNode, new: PNode):
    #     if self.body_start == pnode_to_swap:
    #         self.body_start = new
    #         new.parent = self
    #
    # def swap_child_end(self, pnode_to_swap: PNode, new: PNode):
    #     if self.body_end == pnode_to_swap:
    #         self.body_end = new
    #         new.parent = self
    #
    # def visit_depth_first_forward(self, visitor: Visitor):
    #     visitor.visit(self)
    #     self.body_start.visit_depth_first_forward(visitor)
    #     if self.after:
    #         self.after.visit_depth_first_forward(visitor)
    #
    # def to_string_depth_first_forward(self, level: int = 0):
    #     indent_str = TAB_STR*level
    #     indent_str_body = TAB_STR*(level + 1)
    #     l = [f'{indent_str}{self}', f'{indent_str_body}<body>'] \
    #         + self.body_start.to_string_depth_first_forward(level + 2) \
    #         + [f'{indent_str_body}</body>', f'{indent_str}</{self}>']
    #     if self.after:
    #         return l + self.after.to_string_depth_first_forward(level)
    #     else:
    #         return l


class PNodeCondIf(PNodeControlWithBody):

    @staticmethod
    def swap(pnode_to_swap: PNode, fn_body: FunctionBody, new: PNode = None):
        new = PNodeCondIf()

        PNodeControlWithBody.swap(pnode_to_swap, fn_body, new)

    #     new.before = PNode(after=new)
    #     new.after = PNode(before=new)
    #
    #     body = PNode(parent=new)
    #     new.body_if_start = body
    #     new.body_if_end = body
    #     print(f'    new: {new}')
    #
    #     fn_body.unassigned_pnodes.add(new.before)
    #     fn_body.unassigned_pnodes.add(new.after)
    #     fn_body.unassigned_pnodes.add(body)
    #     fn_body.nes_pnodes.add(body)
    #
    #     swap_finish(pnode_to_swap=pnode_to_swap, new=new, fn_body=fn_body)
    #
    #     # if pnode_to_swap.before is None:
    #     #     if fn_body.head == pnode_to_swap:
    #     #         fn_body.head = new.before
    #     # else:
    #     #     new.before.before = pnode_to_swap.before
    #     #     pnode_to_swap.before.after = new.before
    #     #
    #     # if pnode_to_swap.after is None:
    #     #     if fn_body.tail == pnode_to_swap:
    #     #         fn_body.tail = new.after
    #     # else:
    #     #     new.after.after = pnode_to_swap.after
    #     #     pnode_to_swap.after.before = new.after
    #     #
    #     # if pnode_to_swap.parent is not None:
    #     #     pnode_to_swap.parent.swap_child_start(pnode_to_swap, new.before)
    #     #     pnode_to_swap.parent.swap_child_end(pnode_to_swap, new.after)
    #     #
    #     # fn_body.unassigned_pnodes.remove(pnode_to_swap)
    #     # if pnode_to_swap in fn_body.nes_pnodes:
    #     #     fn_body.nes_pnodes.remove(pnode_to_swap)
    #     # del pnode_to_swap

    def __init__(self, before: PNode = None, after: PNode = None, parent: PNode = None):
        # self.condition = None
        # self.body_if_start = None
        # self.body_if_end = None
        super().__init__(before=before, after=after, parent=parent)

    def __repr__(self):
        return f'<CondIf {self.pnode_idx}:{self.get_connectivity_str()}>'

    # def swap_child_start(self, pnode_to_swap: PNode, new: PNode):
    #     if self.body_if_start == pnode_to_swap:
    #         self.body_if_start = new
    #         new.parent = self
    #
    # def swap_child_end(self, pnode_to_swap: PNode, new: PNode):
    #     if self.body_if_end == pnode_to_swap:
    #         self.body_if_end = new
    #         new.parent = self
    #
    # def visit_depth_first_forward(self, visitor: Visitor):
    #     visitor.visit(self)
    #     self.body_if_start.visit_depth_first_forward(visitor)
    #     if self.after:
    #         self.after.visit_depth_first_forward(visitor)

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
        print(f'    new: {new}')

        fn_body.unassigned_pnodes.add(new.before)
        fn_body.unassigned_pnodes.add(new.after)
        fn_body.unassigned_pnodes.add(body_if)
        fn_body.nes_pnodes.add(body_if)
        fn_body.unassigned_pnodes.add(body_else)
        fn_body.nes_pnodes.add(body_else)

        swap_finish(pnode_to_swap=pnode_to_swap, new=new, fn_body=fn_body)

        # if pnode_to_swap.before is None:
        #     if fn_body.head == pnode_to_swap:
        #         fn_body.head = new.before
        # else:
        #     new.before.before = pnode_to_swap.before
        #     pnode_to_swap.before.after = new.before
        #
        # if pnode_to_swap.after is None:
        #     if fn_body.tail == pnode_to_swap:
        #         fn_body.tail = new.after
        # else:
        #     new.after.after = pnode_to_swap.after
        #     pnode_to_swap.after.before = new.after
        #
        # if pnode_to_swap.parent is not None:
        #     pnode_to_swap.parent.swap_child_start(pnode_to_swap, new.before)
        #     pnode_to_swap.parent.swap_child_end(pnode_to_swap, new.after)
        #
        # fn_body.unassigned_pnodes.remove(pnode_to_swap)
        # if pnode_to_swap in fn_body.nes_pnodes:
        #     fn_body.nes_pnodes.remove(pnode_to_swap)
        # del pnode_to_swap

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


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    prog = ProgramSpec(params=CONFIG_1)
    # prog.sample()
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

    print()
    print('FunctionBody')
    fb = FunctionBody(program_spec=prog)
    fb.sample()
    print()
    fb.pprint_depth_first()

    print()
    print('visit_depth_first_forward')
    v1 = VisitorCollectElements()
    fb.visit_depth_first_forward(v1)
    elms = v1.get_elements()
    for i, elm in enumerate(elms):
        print(f'{i}: {elm}')


# -----------------------------------------------------------------------------
# Top level
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

