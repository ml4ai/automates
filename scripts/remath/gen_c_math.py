import numpy
import os
from pathlib import Path


# -----------------------------------------------------------------------------
# Primitive C types value ranges
# -----------------------------------------------------------------------------

RANGE_INT = (-32768, 32767)  # assuming 4 bit, otherwise same as long
RANGE_LONG = (-2147483648, 2147483647)
RANGE_LONG_LONG = (-9223372036854775808, 9223372036854775807)
RANGE_FLOAT = (1.17549E-38, 3.40282E+38)  # (1.E-38, 3.4E+38)
RANGE_DOUBLE = (2.22507E-308, 1.79769E+308)  # (2.3E-308, 1.7E+308)
RANGE_LONG_DOUBLE = (3.4E-4932, 1.1E+4932)
RANGES = (RANGE_INT, RANGE_LONG, RANGE_LONG_LONG, RANGE_FLOAT, RANGE_DOUBLE, RANGE_LONG_DOUBLE)


# -----------------------------------------------------------------------------
# Sample primitive C value
# -----------------------------------------------------------------------------

def sample_int():
    return str(numpy.random.randint(RANGE_LONG[0], RANGE_LONG[1]))


def sample_float():
    return str(numpy.random.uniform(-10, 10))


def test_sample_num():
    sample_i = [sample_int() for _ in range(10)]
    sample_f = [sample_float() for _ in range(10)]
    for i in range(10):
        print(f'{sample_i[i]} {sample_f[i]}')


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
# Parse c math.h fns from spec
# -----------------------------------------------------------------------------

def parse_cmath_fns():
    """
    Parse math_h_signatures.txt to extract indexed maps of math spec
    :return:
    """

    fns_by_name = dict()
    fns_by_type = dict()

    with open('math_h_signatures.txt', 'r') as fin:
        lines = fin.readlines()
        functions_in = False
        for line in lines:
            line = line.strip()
            if functions_in and line[0] != '#':
                return_val = line[:12].strip(' ')
                fn_component = line[12:].split('(')
                fn = fn_component[0]
                args = [arg.strip() for arg in fn_component[1][:-2].split(',')]
                types = tuple([return_val] + args)
                fns_by_name[fn] = types
                for t in types:
                    if t in fns_by_type:
                        fns_by_type[t].add(fn)
                    else:
                        fns_by_type[t] = {fn}
                # print(f'{return_val} :: {fn} :: {args}')
            if line == '## START functions':
                functions_in = True
            if line == '## END functions':
                functions_in = False

    # print('>>>>> fns_by_name:')
    # for k, v in fns_by_name.items():
    #     print(f'{k} : {v}')

    # print('\n>>>>> fns_by_type:')
    # for k, v in fns_by_type.items():
    #     print(f'{k} : {v}')

    return fns_by_name, fns_by_type


def collect_fns_except(fns_by_name, fns_by_type, exception_types):
    fns = set(list(fns_by_name))
    for t in exception_types:
        # print(f'{type} : {fns_by_type[type]}')
        fns -= fns_by_type[t]
    return fns


# -----------------------------------------------------------------------------
# Generators
# -----------------------------------------------------------------------------

def gen_c_main(body, includes=None):
    progn = list()
    if includes:
        for inc in includes:
            progn.append(inc)
    progn.append('int main() {')
    for line in body:
        progn.append(f'    {line}')
    progn.append('    return 0;')
    progn.append('}')
    return '\n'.join(progn)


# -----------------------------------------------------------------------------
# Generate math.h trivial programs

def gen_fn_all_literal_args(fn, type_return, type_args) -> str:
    new_var = VarGen()
    args = list()
    for t in type_args:
        if t in ('int', 'long', 'long long'):
            args.append(sample_int())
        else:
            args.append(sample_float())
    c_fn_string = f"{fn}({', '.join(args)})"
    c_fn_line = f"{type_return} {new_var.get_name()} = {c_fn_string}"
    return c_fn_line


def gen_fn_all_var_args(fn, type_return, type_args) -> list:
    new_var = VarGen()
    args = list()
    lines = list()
    for t in type_args:
        if t in ('int', 'long', 'long long'):
            val = sample_int()
        else:
            val = sample_float()
        var_name = new_var.get_name()
        lines.append(f'{t} {var_name} = {val};')
        args.append(var_name)

    # declare return variable
    return_var_name = new_var.get_name()
    lines.append(f'{type_return} {return_var_name};')

    c_fn_string = f"{fn}({', '.join(args)});"
    c_fn_line = f"{return_var_name} = {c_fn_string}"
    lines.append(c_fn_line)
    return lines


def gen_prog_fn_batch(root_dir, fn_list, fns_by_name, literals_only_p):
    # create root directory if does not already exist
    Path(root_dir).mkdir(parents=True, exist_ok=True)
    for fn in fn_list:
        fn_types = fns_by_name[fn]
        type_return = fn_types[0]
        type_args = fn_types[1:]
        if literals_only_p:
            fn_line = gen_fn_all_literal_args(fn, type_return, type_args)
            prog_string = gen_c_main([fn_line], includes=['#include <math.h>'])
        else:
            fn_lines = gen_fn_all_var_args(fn, type_return, type_args)
            prog_string = gen_c_main(fn_lines, includes=['#include <math.h>'])

        filename = f'{fn}.c'
        filepath = os.path.join(root_dir, filename)
        with open(filepath, 'w') as fout:
            fout.write(prog_string)


# -----------------------------------------------------------------------------
# Generate math.h trivial programs

def gen_arithmetic_op_primitives_examples():
    root_dir = 'primitive_op_examples'
    Path(root_dir).mkdir(parents=True, exist_ok=True)
    types = ('int', 'long', 'long long',
             'float', 'double', 'long double')

    def safe_name(s):
        return '_'.join(s.split(' '))

    for t in types:
        filepath = os.path.join(root_dir, f'add_{safe_name(t)}.c')
        lines = list()
        lines.append(f'{t} x0 = 1;')
        lines.append(f'{t} x1 = 2;')
        lines.append(f'{t} x2;')
        lines.append(f'{t} x2 = x0 + x1;')
        prog_string = gen_c_main(lines)
        with open(filepath, 'w') as fout:
            fout.write(prog_string)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    fns_by_name, fns_by_type = parse_cmath_fns()
    exception_types = ('int *', 'float *', 'double *', 'long double *', 'const char *')
    accepted_types = set(fns_by_type) - set(exception_types)
    accepted_fns = collect_fns_except(fns_by_name, fns_by_type, exception_types)
    for i, fn in enumerate(accepted_fns):
        print(f'[{i}] {fn} : {fns_by_name[fn]}')
    print(f'accepted_types: {accepted_types}')

    # test_sample_num()

    gen_prog_fn_batch('fn_all_literals', accepted_fns, fns_by_name, literals_only_p=True)
    gen_prog_fn_batch('fn_all_vars', accepted_fns, fns_by_name, literals_only_p=False)
    gen_arithmetic_op_primitives_examples()


# -----------------------------------------------------------------------------
# Top Level Script
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    main()
