import os
# from pathlib import Path
import random
from typing import Set, List, Dict, Tuple
from dataclasses import dataclass

"""
ASSUMPTIONS / OBSERVATIONS:
(1) Not using 'long double' type for now
    Doing so leads to binary handling of long double data that Ghidra 
      does not appear to be able to recover 
(2) GCC DOES indeed pre-compute values when (primitive?) operators only
    involve literal values.
    GCC appears to NOT do this when at least one of the literal values
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

    def __init__(self):
        self.var_counter = 0

    def get_name(self, base='x'):
        vname = f'{base}{self.var_counter}'
        self.var_counter += 1
        return vname


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
     'NON_FLOAT': ('int', 'long', 'long long'),
     'INT': ('int',)}
TYPES = MAP_TYPECAT_TO_TYPE['ANY']
TYPECATS = tuple(MAP_TYPECAT_TO_TYPE.keys())


def sample_literal(t):
    if t in MAP_TYPECAT_TO_TYPE['REAL_FLOATING']:
        return random.uniform(-10, 10)
    elif t in MAP_TYPECAT_TO_TYPE['NON_FLOAT']:
        return random.randint(-100, 100)
    else:
        raise Exception(f"ERROR sample_literal():\n"
                        f"Unsupported type '{t}'")


TYPE_PRIORITY = \
    {'ANY': 0,
     'NON_FLOAT': 1,
     'INT': 2}


def get_type_priority(t):
    if t not in TYPE_PRIORITY:
        raise Exception(f'ERROR get_type_priority():\n'
                        f'type {t} is not handled\n{TYPE_PRIORITY}')
    else:
        return TYPE_PRIORITY[t]


def contract_type(target_type: str, other_type: str) -> str:
    if get_type_priority(target_type) > get_type_priority(other_type):
        return target_type
    else:
        return other_type


def contract_list_to_target_type(target_type: str, other_types: Tuple[str]) -> Tuple[str]:
    return tuple([contract_type(target_type, other_type) for other_type in other_types])


TYPE_STRING_FORMAT = \
    {'int': 'd', 'long': 'd', 'long long': 'd',
     'float': 'g', 'double': 'g', 'long double': 'g'}


# -----------------------------------------------------------------------------
# Operators
# -----------------------------------------------------------------------------

# Assumptions:
# (1) All are binary operators
# (2) All typing is in terms of typecats
MAP_OP_TO_TYPECATS = \
    {'+': ('ANY', 'ANY', 'ANY'),
     '-': ('ANY', 'ANY', 'ANY'),
     '*': ('ANY', 'ANY', 'ANY'),
     '/': ('ANY', 'ANY', 'ANY'),
     '%': ('INT', 'INT', 'INT'),
     # bitwise logical operators
     '&': ('NON_FLOAT', 'NON_FLOAT', 'NON_FLOAT'),  # bitwise AND
     '|': ('NON_FLOAT', 'NON_FLOAT', 'NON_FLOAT'),  # bitwise inclusive OR
     '^': ('NON_FLOAT', 'NON_FLOAT', 'NON_FLOAT')   # bitwise exclusive OR
     }

# Sequence of operators
OPS = tuple(MAP_OP_TO_TYPECATS.keys())


def collect_ops_compatible_with_types():
    map_type_to_ops = dict()

    def add(t, op):
        if t in map_type_to_ops:
            map_type_to_ops[t].append(op)
        else:
            map_type_to_ops[t] = [op]

    # Build map of types to ops
    for t in TYPES:
        for op, args in MAP_OP_TO_TYPECATS.items():
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


def sample_uniform_operator(op_set):
    op = random.choice(op_set)
    args = MAP_OP_TO_TYPECATS[op]
    return op, args[0], args[1:]


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

@dataclass
class SampleParameters:
    # Range of number of expressions
    min_expressions: int
    max_expressions: int
    # Range of number of operators in expression
    min_ops: int  # minimum operations per expression
    max_ops: int  # maximum operations per expression

    # Probability of assigning an expression variable to an unassigned index in an expression
    p_assign_expr_var: float
    # A "literal variable" is a variable that is declared and assigned a literal.
    # This is the probability of assigning a literal variable to an unassigned index in an expression
    p_assign_literal_var: float


EXAMPLE_PARAMS = \
    SampleParameters(min_expressions=1, max_expressions=6,
                     min_ops=1, max_ops=6,
                     p_assign_expr_var=0.2,
                     p_assign_literal_var=0.2)


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

class ExprSeqSample:
    def __init__(self, params: SampleParameters, var_gen: VarGen):
        self.params = params
        self.var_gen = var_gen
        # map of expr_index [int] to an expression [ExprTreeSample]
        self.expressions: Dict[int, ExprTreeSample] = dict()
        # map of expr_index [int] to the variable its return value is assigned to [str]
        self.expr_var: Dict[int, str] = dict()
        # map of variable to the index in an expr that it has been assigned to: (<expr_index>, <var_index>)
        self.expr_index_var_assignments: Dict[str, List[Tuple[int, int]]] = dict()

    def add_var_to_expr_index_var_assignments(self, variable, expr_index, var_index):
        if variable in self.expr_index_var_assignments:
            self.expr_index_var_assignments[variable].append((expr_index, var_index))
        else:
            self.expr_index_var_assignments[variable] = [ (expr_index, var_index) ]

    def get_unassigned_expr_vars(self) -> List[Tuple[int, int, str]]:  # Dict[str, List[Tuple[int, int]]]:
        unassigned_expr_vars: List[Tuple[int, int, str]] = list()  # Dict[str, List[Tuple[int, int]]] = dict()
        for expr_idx, expr in self.expressions.items():
            for var_type, var_idx in expr.get_unassigned_types():
                unassigned_expr_vars.append((expr_idx, var_idx, var_type))
        return unassigned_expr_vars

    def get_expr_vars_by_typecats(self, start_index) -> Dict[str, List[str]]:
        map_typecat_to_var: Dict[str, List[str]] = dict()
        for expr_idx in range(start_index, len(self.expressions)):
            expr_return_type = self.expressions[expr_idx].index_type[0]
            if expr_return_type in map_typecat_to_var:
                map_typecat_to_var[expr_return_type].append(self.expr_var[expr_idx])
            else:
                map_typecat_to_var[expr_return_type] = [self.expr_var[expr_idx]]
        return map_typecat_to_var

    def sample(self, verbose_p=False):
        num_expressions = random.randint(self.params.min_expressions, self.params.max_expressions)
        if verbose_p:
            print(f'- ExprSeqSample.sample() : num_expressions={num_expressions}')
        target_typecat = 'ANY'
        next_var = self.var_gen.get_name()  # get variable that expression will be assigned to
        for i in range(num_expressions):
            if verbose_p:
                print(f'-- expression {i}')
            num_ops = random.randint(self.params.min_ops, self.params.max_ops)
            expr = ExprTreeSample(num_ops=num_ops, init_typecat=target_typecat)
            self.expressions[i] = expr
            self.expr_var[i] = next_var
            expr.sample(verbose_p=verbose_p)

            if i < num_expressions - 1:
                unassigned_expr_vars = self.get_unassigned_expr_vars()
                # sample an unassigned var out of all of the unassigned vars in all of the expressions
                expr_idx, var_idx, var_typecat = random.choice(unassigned_expr_vars)
                expr_with_var = self.expressions[expr_idx]
                # generate the next var name that will be set as the expr_with_var's and be the assigned the next expr
                next_var = self.var_gen.get_name()
                # set the next_var as the value of the var_idx
                # remove the var_idx from the expr_with_var's unassigned_indices
                #expr_with_var.value_assignments[var_idx] = next_var
                #expr_with_var.unassigned_indices.remove(var_idx)
                expr_with_var.assign_value(var_idx, next_var)
                # record the (expr_index, var_index) to which a var has been assigned
                self.add_var_to_expr_index_var_assignments(next_var, expr_idx, var_idx)
                # the new target_typecat is the typecat of the var we're setting
                target_typecat = var_typecat

    def reuse_exprs_for_vars(self, verbose_p=False):
        for expr_idx in range(0, len(self.expressions) - 1):
            current_expr = self.expressions[expr_idx]
            map_typecat_to_var = self.get_expr_vars_by_typecats(start_index=expr_idx + 1)
            unassigned_indices = sorted(list(current_expr.unassigned_indices))
            for unassigned_index in unassigned_indices:
                current_expr_unassigned_index_type = current_expr.index_type[unassigned_index]
                if current_expr_unassigned_index_type in map_typecat_to_var:
                    # possibly assign unassigned_index to var
                    if random.random() < self.params.p_assign_expr_var:
                        var = random.choice(map_typecat_to_var[current_expr_unassigned_index_type])
                        current_expr.assign_value(unassigned_index, var)
                        # record the (expr_index, var_index) to which a var has been assigned
                        self.add_var_to_expr_index_var_assignments(var, expr_idx, unassigned_index)
                        if verbose_p:
                            print(f'>>> reuse_exprs_for_vars(): Assigning expr={expr_idx} index={unassigned_index} to {var}')

    def backward_propagate_ground_type_choices(self):
        # iterate from last expression in expression sequence to first, to ensure
        # proper propagation of ground_types (ensuring any ground_types of expr
        # variables (i.e., the ground_types associated with an expression return type)
        # are assigned before backward-propagating the ground type for the expressoin
        # that has the variable in one of its indices.
        for expr_index in reversed(range(len(self.expressions))):
            expr = self.expressions[expr_index]
            expr.backward_propagate_ground_type_choices(0)

            # now assign ground_type of expr return value to all expressions with indices
            # that have been assigned an expr variable
            expr_var = self.expr_var[expr_index]
            expr_var_type = expr.index_type[0]  # get the type of the root index (the return of expr)
            if expr_var in self.expr_index_var_assignments:
                for assigned_expr_idx, var_idx in self.expr_index_var_assignments[expr_var]:
                    assigned_expr = self.expressions[assigned_expr_idx]
                    assigned_expr.index_type[var_idx] = expr_var_type

    def assign_literals(self):
        for expr_index in range(len(self.expressions)):
            self.expressions[expr_index].assign_literals()

    def to_expression_str_list(self):
        lines = list()
        for expr_index in reversed(range(len(self.expressions))):
            lines.append(f'{self.expressions[expr_index].index_type[0]} {self.expr_var[expr_index]} '
                         f'= {self.expressions[expr_index].to_infix_expression()};')
        return lines

    def to_program_str(self):
        progn = list()
        # if includes:
        #     for inc in includes:
        #         progn.append(inc)
        progn.append('#include <stdio.h>')
        progn.append('int main() {')
        for line in self.to_expression_str_list():
            progn.append(f'    {line}')
        return_type = self.expressions[0].index_type[0]
        format_str = TYPE_STRING_FORMAT[return_type]
        progn.append(f'    printf("Answer: %{format_str}\\n", x0);')
        progn.append('    return 0;')
        progn.append('}')
        return '\n'.join(progn)

    def print(self, header=None):
        if header:
            print(f'{header}')
        print(f'params: {self.params}')
        for expr_idx, expr in self.expressions.items():
            expr.print(header=f'-- Expression {expr_idx} assigned to var {self.expr_var[expr_idx]}')

    def backward_propagate_ground_type_choices_DEBUG(self):
        expr_idx = 4
        expr = self.expressions[expr_idx]
        expr.backward_propagate_ground_type_choices(0)
        expr.print(header=f'-- Expression {expr_idx} assigned to var {self.expr_var[expr_idx]}')

        expr_var = self.expr_var[expr_idx]
        expr_var_type = expr.index_type[0]
        if expr_var in self.expr_index_var_assignments:
            for assigned_expr_idx, var_idx in self.expr_index_var_assignments[expr_var]:
                print(f'>>> setting expr={assigned_expr_idx} var_idx={var_idx} to --> {expr_var_type}')
                assigned_expr = self.expressions[assigned_expr_idx]
                assigned_expr.index_type[var_idx] = expr_var_type
                assigned_expr.print(header=f'---- {assigned_expr_idx}')
        print('<<<<<<< DONE')


def sample_expr_seq():
    var_gen = VarGen()
    expr_seq = ExprSeqSample(params=EXAMPLE_PARAMS, var_gen=var_gen)
    expr_seq.sample(verbose_p=False)
    expr_seq.reuse_exprs_for_vars(verbose_p=False)

    # expr_seq.print(header='\n -------- Expressions before backward_propagate:')
    # print(f'expr_seq.expr_index_var_assignments: {expr_seq.expr_index_var_assignments}')

    expr_seq.backward_propagate_ground_type_choices()

    # TODO: create literal variables for at least one of any binary fn that has unassigned values
    # TODO: reuse some literal variables

    # finally, inline assign literals to all remaining unassigned indices
    expr_seq.assign_literals()

    # expr_seq.print(header='\n -------- Final Expressions:')

    # print()
    print(expr_seq.to_program_str())


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

class ExprTreeSample:
    def __init__(self, num_ops: int, init_typecat='ANY'):
        self.num_ops = num_ops
        self.last_index = 0                  # The highest index (used to support incremental generation/expansion)
        self.unassigned_indices = {0}        # [int]
        self.op_indices = set()              # [int]
        self.index_op = dict()               # map of index [int] to op [str]
        self.index_type = {0: init_typecat}  # map of index [int] to type [str]
        self.index_children = dict()         # map of index [int] to list of next indices [List[int]]
        self.value_assignments = dict()      # map of index [int] to values (literals, variables)

    def get_unassigned_types(self) -> List[Tuple[str, int]]:
        return [(self.index_type[index], index) for index in sorted(list(self.unassigned_indices))]

    def sample(self, verbose_p=False):
        for i in range(self.num_ops):
            idx = random.choice(sorted(list(self.unassigned_indices)))
            return_type = self.index_type[idx]
            op, _, arg_types = sample_uniform_operator(MAP_RETURN_TYPE_TO_OPS[return_type])
            # NOTE:
            #   immediately contract types
            #   (rather than calling forward_propagate_type_constraints
            #   after tree constructed)
            contracted_arg_types = contract_list_to_target_type(return_type, arg_types)
            self.add_op_at(index=idx, op=op, arg_types=contracted_arg_types)
        if verbose_p:
            self.print(header=f'---- ExprTreeSample.sample() 0: num_ops={self.num_ops}')
        # self.forward_propagate_type_constraints(0)
        # if verbose_p:
        #     self.print(header=f'---- ExprTreeSample.sample() 1: forward_propagate_constraints')
        # self.backward_propagate_ground_type_choices(0)
        # if verbose_p:
        #     self.print(header=f'---- ExprTreeSample.sample() 2: backward_propagate_ground_type_choices')

    def add_op_at(self, index: int, op: str, arg_types: Tuple, verbose_p=False):  # return_type: str,
        if verbose_p:
            print(f'add_op_at(index={index}, op={op}, args={arg_types})')  # return_type={return_type},
        new_indices = list(range(self.last_index + 1, self.last_index + len(arg_types) + 1))
        self.last_index += len(arg_types)
        self.unassigned_indices |= set(new_indices)
        self.unassigned_indices.remove(index)
        self.op_indices.add(index)
        self.index_op[index] = op
        # self.index_type[index] = return_type
        for idx, arg_type in zip(new_indices, arg_types):
            self.index_type[idx] = arg_type
        self.index_children[index] = new_indices

    def assign_value(self, index, value):
        if index not in sorted(list(self.unassigned_indices)):
            raise Exception(f'ERROR ExprTreeSample.assign_value():\n'
                            f'Attempting to assign value {value} to index {index} '
                            f'not in unassigned:\n{self.unassigned_indices}')
        elif index in self.value_assignments:
            raise Exception(f'ERROR ExprTreeSampleassign_value():\n'
                            f'Attempting to assign value {value} to index {index} '
                            f'already assigned to {self.value_assignments[index]}')
        else:
            self.value_assignments[index] = value
            self.unassigned_indices.remove(index)

    # NOTE: deprecating: now doing this per new sample
    #       in self.sample
    #           right after sample_uniform_operator, now calling contracted_arg_types
    #           to propagate parent constraints forward...
    # def contract_child_type_by_index(self, parent_idx, child_idx):
    #     parent_priority = get_type_priority(self.index_type[parent_idx])
    #     child_priority = get_type_priority(self.index_type[child_idx])
    #     if parent_priority > child_priority:
    #         return self.index_type[parent_idx]
    #     else:
    #         return self.index_type[child_idx]
    #
    # def forward_propagate_type_constraints(self, parent_index):
    #     if parent_index in self.index_children:
    #         for child_index in self.index_children[parent_index]:
    #             self.index_type[child_index] = self.contract_child_type_by_index(parent_index, child_index)
    #             self.forward_propagate_type_constraints(child_index)

    def get_return_ground_type(self, op: str, arg_types: List[str]) -> str:
        """
        Given list of specific ground_types, select the appropriate cast type.
        TODO: Currently the assumption is that we select the return ground_type
            based on comparing the cast precedence the ground_types of the op
            arguments within the context of the op return typecat,
            so only using op to get the op return typecat;
            In the future, may allow for departure from this scheme per operator
        :param op: operator
        :param arg_types: list of specific ground_types provided as args to op
        :return: ground_type for the op return value
        """
        return_typecat = MAP_OP_TO_TYPECATS[op][0]
        return_types = MAP_TYPECAT_TO_TYPE[return_typecat]
        # print(f'>>>> DEBUG return_typecat={return_typecat}, return_types={return_types}, arg_types={arg_types}')
        cast_priority = max([return_types.index(arg_type) for arg_type in arg_types])
        return return_types[cast_priority]

    def backward_propagate_ground_type_choices(self, index):
        if index in sorted(list(self.unassigned_indices)):
            chosen_type = random.choice(MAP_TYPECAT_TO_TYPE[self.index_type[index]])
            self.index_type[index] = chosen_type
            return chosen_type
        elif index in self.value_assignments:
            # print(f'>>>> DEBUG backward_propagate_ground_type_choices: ASSIGNED {index} {self.index_type[index]} {self.value_assignments[index]}')
            return self.index_type[index]
        else:
            arg_ground_types = [self.backward_propagate_ground_type_choices(child_idx)
                                for child_idx in self.index_children[index]]
            # print(f'>>> index={index} self.index_children[index]={self.index_children[index]}')
            return_ground_type = self.get_return_ground_type(self.index_op[index], arg_ground_types)
            self.index_type[index] = return_ground_type
            return return_ground_type

    def assign_literals(self):
        for index in sorted(list(self.unassigned_indices)):
            t = self.index_type[index]
            self.assign_value(index, sample_literal(t))

    def to_prefix_expression(self, index=0):
        if index in self.value_assignments:
            return f'{self.value_assignments[index]}'
        else:
            expr = ['(', self.index_op[index]]
            for child_index in self.index_children[index]:
                expr.append(self.to_prefix_expression(child_index))
            expr.append(')')
            return ' '.join(expr)

    def to_infix_expression(self, index=0):
        if index in self.value_assignments:
            return f'{self.value_assignments[index]}'
        else:
            return f'({self.to_infix_expression(self.index_children[index][0])} ' \
                   f'{self.index_op[index]} ' \
                   f'{self.to_infix_expression(self.index_children[index][1])})'

    def print(self, header=None):
        if header:
            print(f'{header}')
        print(f'num_ops:            {self.num_ops}')
        print(f'last_index:         {self.last_index}')
        print(f'unassigned_indices: {self.unassigned_indices}')
        print(f'op_indices:         {self.op_indices}')
        print(f'index_op:           {self.index_op}')
        print(f'index_type:         {self.index_type}')
        print(f'index_children:     {self.index_children}')
        print(f'value_assignments:  {self.value_assignments}')


"""
def test_expr_tree_sample_1():
    num_ops = 5  # TODO: make this a random variable
    expr = ExprTreeSample(num_ops=num_ops)

    # 0, 1, 2
    print('-- 0')
    expr.add_op_at(index=0, op='op1', return_type='op1.NON_FLOAT', arg_types=('op1.NON_FLOAT1', 'op1.NON_FLOAT2'),
                   verbose_p=True)
    expr.print()
    # 3, 4
    print('-- 1')
    expr.add_op_at(index=2, op='op2', return_type='op2.int', arg_types=('op2.int1', 'op2.int2'), verbose_p=True)
    expr.print()
    # 5, 6
    print('-- 2')
    expr.add_op_at(index=3, op='op3', return_type='op3.int', arg_types=('op3.int1', 'op3.int2'), verbose_p=True)
    expr.print()
    # 7, 8
    print('-- 3')
    expr.add_op_at(index=1, op='op4', return_type='op4.long', arg_types=('op4.int1', 'op4.long2'), verbose_p=True)
    expr.print()
"""


def sample_expr_tree(num_ops):
    expr = ExprTreeSample(num_ops=num_ops)
    expr.sample()
    expr.print(header='\n-- 0: sample')
    expr.backward_propagate_ground_type_choices(0)
    expr.print(header='\n-- 1: backward_propagate_ground_type_choices')
    expr.assign_literals()
    expr.print(header='\n-- 2: assign literals')
    print(expr.to_prefix_expression(0))
    print(expr.to_infix_expression(0))


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

def gen_prog() -> str:
    return ''


def gen_prog_batch(n=1):
    root_dir = 'sample_expressions'
    # TODO
    # Path(root_dir).mkdir(parents=True, exist_ok=True)
    for i in range(n):
        sig_digits = len(str(n))
        filename = f'source_{i}.c'.zfill(sig_digits)
        filepath = os.path.join(root_dir, filename)
        prog_str = gen_prog()
        with open(filepath, 'w') as fout:
            fout.write(prog_str)


def main():
    gen_prog_batch(n=1)
    x = ((((14 - (-10 % 16)) & 63) ^ -91) - (((5.849503665497089 - -5.358216134466982) * 9.065075755655059) / -0.6929482786805892))


if __name__ == "__main__":
    sample_expr_seq()
    # sample_expr_tree(8)
    # test_expr_tree_sample_1()
    # main()
    # print(collections.Counter([sample_uniform_operator() for i in range(100000)]))
