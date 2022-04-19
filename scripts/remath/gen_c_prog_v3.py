# import os
# from pathlib import Path
import random
from typing import Union, Sequence, Set, List, Dict, Tuple
from dataclasses import dataclass

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
    main_cli: bool   # whether main fn includes argc, argv
    num_globals: Tuple[int, int]
    prob_global_set: float            # probability that each global gets set in each fn
    num_functions: Tuple[int, int]    # number of functions
    num_function_arguments: Tuple[int, int]  # number of function arguments
    allow_recursive_function_calls: bool     # flag for whether to allow recursive calls
    num_expressions: Tuple[int, int]  # number of expressions per block
    num_operators: Tuple[int, int]    # number of operators per expression


CONFIG_1 = GeneratorConfig(
    map_typecat_to_type=MAP_TYPECAT_TO_TYPE,
    main_cli=True,
    num_globals=(4, 4),
    prob_global_set=0.8,
    num_functions=(2, 2),
    num_function_arguments=(8, 8),
    allow_recursive_function_calls=True,
    num_expressions=(4, 4),
    num_operators=(4, 4)
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
    GeneratorConfig.num_globals
    generate global names
    types initially ANY
    initially no literal assignments
    add each global to var set that can be accessed
Functions 1 - create signature
    GeneratorConfig.num_functions
    generate function name
    sample number of arguments: GeneratorConfig.num_function_arguments
    return type and argument types all initially ANY
    sample globals: for each global, determine whether *set*
        acc'd to: GeneratorConfig.prob_global_set
        record fn-name in
    add new fn to OP_DEFINITIONS
Functions 2 - fill out body
    create expressions
    TODO: When sampling operations, possibly too sparse; maybe post-process to ensure
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


class BlockSpec:
    def __init__(self):
        pass

    def pprint(self):
        pass


class FunctionSpec:
    """
    Specification of a function
    """
    def __init__(self, name: str, args: Union[List[VariableDecl], None],
                 return_type: str, body: BlockSpec = None,
                 local_vargen: VarGen = None):
        self.name = name
        if local_vargen is None:
            self.local_vargen = VarGen('x')
        else:
            self.local_vargen = local_vargen
        self.args = args
        self.return_type = return_type
        self.body = body
        self.called_by: Set[str] = set()  #

    def to_c_string_signature(self):
        arg_string = ''
        if self.args is not None:
            arg_string = ', '.join([arg.to_c_string() for arg in self.args])
        return f'{self.return_type} {self.name}({arg_string})'

    def pprint(self):
        if self.body:
            print(self.to_c_string_signature())
            self.body.pprint()
        else:
            print(self.to_c_string_signature())


class ProgramSpec:
    """
    Specification of a Program
    """
    def __init__(self, params: GeneratorConfig,
                 globals_vargen=None, function_name_vargen=None):
        self.params = params
        self.headers: Set[str] = set()
        self.num_globals = 0
        self.globals_vargen: VarGen = globals_vargen
        self.globals = dict()
        self.function_name_vargen: VarGen = function_name_vargen
        self.num_functions = 0
        self.functions: Dict[str, FunctionSpec] = dict()
        # self.expressions: Dict[int, ExprTreeSample] = dict()

    def sample_program_parameters_from_params(self):
        """
        Based on the GeneratorConfig parameters,
          sample the number of program-level components:
            number of globals
            number of functions
        :return:
        """
        self.num_globals = random.randint(self.params.num_globals[0], self.params.num_globals[1])
        if self.num_globals > 0 and self.globals_vargen is None:
            self.globals_vargen = VarGen('g')
        self.num_functions = random.randint(self.params.num_functions[0], self.params.num_functions[1])
        if self.num_functions > 0 and self.function_name_vargen is None:
            self.function_name_vargen = VarGen('fn')

    def sample_globals(self):
        for gidx in range(self.num_globals):
            var_name = self.globals_vargen.get_name()
            var_type = 'ANY'
            self.globals[var_name] = VariableDecl(name=var_name, var_type=var_type)

    def sample_function_signatures(self):
        # create main function
        args = None
        if self.params.main_cli:
            args = [VariableDecl(name='argc', var_type='int'),
                    VariableDecl(name='argv', var_type='char', var_type_ptr='*', var_type_arr=True)]
        self.functions['main'] = FunctionSpec(
            name='main',
            args=args,
            return_type='int'
        )
        # create other functions
        for fidx in range(self.num_functions):
            fun_name = self.function_name_vargen.get_name()
            num_args = random.randint(self.params.num_function_arguments[0],
                                      self.params.num_function_arguments[1])
            args = list()
            if num_args > 0:
                arg_name_vargen = VarGen('p')
                for aidx in range(num_args):
                    # TODO need to eventually generalize to allow for pointers
                    arg_name = arg_name_vargen.get_name()
                    args.append(VariableDecl(name=arg_name, var_type='ALL'))
            fn_spec = FunctionSpec(
                name=fun_name,
                args=args,
                return_type='ANY'
            )
            self.functions[fun_name] = fn_spec

    def sample(self):
        """
        Top-level driver for sampling a program based on GeneratorConfig parameters.
        :return:
        """
        self.sample_program_parameters_from_params()
        self.sample_globals()
        self.sample_function_signatures()

    def pprint(self):
        print('ProgramSpec:')
        print(f'  globals={self.num_globals}, functions={self.num_functions}')
        print(f'  globals: {self.globals.items()}')
        for fn_spec in self.functions.values():
            fn_spec.pprint()


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    prog = ProgramSpec(params=CONFIG_1)
    prog.sample()
    prog.pprint()


# -----------------------------------------------------------------------------
# Top level
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

