from typing import Dict, List, Tuple, Any, Set
import struct
from collections import OrderedDict, Counter
import pathlib
import os
import sys
import argparse
import uuid

# TODO: create batch processing mode

"""
Assumptions
(1) function names: common fns like printf are first-order tokens
    TODO: this will have to be generalized

References:
() Using python struct for decoding hex representations of values
    (particularly to float)
    - https://stackoverflow.com/questions/1592158/convert-hex-to-float
    - https://docs.python.org/3/library/struct.html
    - Interesting point about a hex value possibly containing two float reps
      https://stackoverflow.com/questions/44052818/how-to-convert-hex-to-ieee-floating-point-python
() IEEE-754 hex to decimal floating point converter: 
    https://babbage.cs.qc.cuny.edu/ieee-754.old/64bit.html
() Another hex to decimal (non-float) converter: 
    https://www.rapidtables.com/convert/number/hex-to-decimal.html
() Reference info for different instructions
    https://www.felixcloutier.com/x86/movsd
    https://www.felixcloutier.com/x86/fld
    https://www.felixcloutier.com/x86/cvtsi2sd
"""

# EXAMPLE_INSTRUCTIONS_FILE = \
#     'examples_ghidra_instructions/gcc/' \
#     'types_without_long_double__Linux-5.11.0-38-generic-x86_64-with-glibc2.31__gcc-10.1.0-instructions.txt'
# # 'types__Linux-5.11.0-38-generic-x86_64-with-glibc2.31__gcc-10.1.0-instructions.txt'
# # 'expr_00__Linux-5.11.0-38-generic-x86_64-with-glibc2.31__gcc-10.1.0-instructions.txt'


EXAMPLE_INSTRUCTIONS_FILE = \
    'expr_v2_perfect/expr_v2_0236641-small/' \
    'expr_v2_0236641__Linux-5.4.0-81-generic-x86_64-with-glibc2.31__gcc-10.1.0-instructions.txt'


class BiMap:
    def __init__(self, base='v'):
        self.gensym = GenSym(base=base)
        self.token_to_elm: OrderedDict[str, str] = OrderedDict()
        self.elm_to_token: Dict[str, str] = dict()
        self.elm_metadata: Dict[str, Any] = dict()

    def get_all_tokens(self):
        return set(self.token_to_elm.keys())

    def get_token(self, elm: str, metadata=None):
        if elm in self.elm_to_token:
            return self.elm_to_token[elm]
        else:
            new_gensym = self.gensym.get_name()
            self.token_to_elm[new_gensym] = elm
            self.elm_to_token[elm] = new_gensym
            if metadata:
                self.elm_metadata[new_gensym] = metadata
            return new_gensym

    def get_value(self, token: str):
        if token in self.elm_metadata:
            return self.token_to_elm[token], self.elm_metadata[token]
        else:
            return self.token_to_elm[token], None

    def print(self):
        for token, elm in self.token_to_elm.items():
            if token in self.elm_metadata:
                print(f'{token} : {elm} : {self.elm_metadata[token]}')
            else:
                print(f'{token} : {elm}')


class GenSym:
    def __init__(self, base='a'):
        self.var_counter = 0
        self.base = base

    def get_name(self):
        gensym = f'{self.base}{self.var_counter}'
        self.var_counter += 1
        return gensym


def parse_unicode_string_list(ustr):
    chunks = list()
    in_str = False
    str_start = None
    for i in range(1, len(ustr)):
        if ustr[i - 1] == 'u' and ustr[i] == '\'' and not in_str:
            in_str = True
            str_start = i + 1
        elif ustr[i - 1] != '\\' and ustr[i] == '\'' and in_str:
            in_str = False
            chunks.append(ustr[str_start: i])
    return chunks


def parse_fn_name_from_parsed_metadata(parsed_metadata: List):
    if parsed_metadata[0] == ':array' and len(parsed_metadata) == 3:
        target_string = parsed_metadata[2]
        if '(' in target_string:
            fn_name = target_string.split('(')[0].split(' ')[-1]
            return ':fn_name', fn_name
        else:
            raise Exception(f"ERROR parse_fn_name_from_parsed_metadata()\n"
                            f"target_string does not appear to contain a function signature"
                            f"target_string: {target_string}"
                            f"parsed_metadata: {parsed_metadata}")
    else:
        raise Exception(f"ERROR parse_fn_name_from_parsed_metadata()\n"
                        f"parsed_metadata is not an array of length 3:\n"
                        f"parsed_metadata: {parsed_metadata}")


def parse_hex_value_from_parsed_metadata(metadata, size: str):
    # print(f'parse_hex_value_from_parsed_metadata(): {metadata}')
    if len(metadata) == 3 and metadata[2].startswith('= ') and metadata[2][-1] == 'h':
        hex_str = metadata[2][2:-1]
        return ':interpreted_hex_float', hex_str, parse_hex_float_value(hex_str, size), size
    else:
        return None


def parse_string_value_from_parsed_metadata(metadata):
    if len(metadata) == 3 and metadata[0] == ':array' and metadata[1] == 'java.lang.String':
        return ':string', metadata[2]
    else:
        return None


def parse_hex_float_value(hex, size):
    if size == 'dword':
        return struct.unpack('!f', bytes.fromhex(hex))[0]
    elif size == 'qword':
        return struct.unpack('!d', bytes.fromhex(hex))[0]
    else:
        raise Exception(f'ERROR parse_hex_float_value(): Unhandled size {size}')


def parse_hex_value(value, size=None):
    # original code -- replaced in favor of 2's complement
    # return ':interpreted_hex', value, int(value, 16), size
    # if size:
    #     return ':interpreted_hex', value, int(value, 16), size
    # else:
    #     return ':raw_hex', value, int(value, 16), 'unknown'

    # new code that translate hex value -> binary (2's complement) -> decimal
    # need a dictionary that maps every float number into 4 bit binary number
    hex_to_bin = {"0": "0000", "1": "0001", "2": "0010", "3": "0011", "4": "0100",
                  "5": "0101", "6": "0110", "7": "0111", "8": "1000", "9": "1001",
                  "a": "1010", "b": "1011", "c": "1100", "d": "1101", "e": "1110",
                  "f": "1111"}
    result = ""
    # remove the initial 0x if it exists
    if value.startswith("-0x"):
        value = value[3:]
        result = -(int(value, 16))
        return ':interpreted_hex', value, result, size
    elif value.startswith("0x"):
        value = value[2:]
    # convert to lower case
    value = value.lower()
    # for each digit convert it to binary
    for item in value:
        result += hex_to_bin[item]
    # if the initial value is zero: it's a positive number
    if result[0] == "0":
        # convert it to integer
        result = int(result, 2)
    # else the number is negative, convert it differently
    else:
        # flip the bits
        temp = ''.join(['1' if i == '0' else '0' for i in result])
        # add 1 and convert to decimal => convert to decimal and add 1
        result = -(int(temp, 2) + 1)
    return ':interpreted_hex', value, result, size


def parse_metadata(metadata: str):
    if metadata.startswith('array'):
        parsed_metadata = [':array']
        t, rest = metadata[6:-1].split(',', maxsplit=1)
        parsed_metadata.append(t)

        elms = parse_unicode_string_list(rest.strip(' []'))
        for elm in elms:
            parsed_metadata.append(elm)

        # for elm in elms:
        #     if elm.startswith("u'"):
        #         elm = elm[2:-1]
        #     parsed_metadata.append(elm)

        return parsed_metadata
    else:
        return [':unparsed', metadata]


def parse_compound_instructions(instr_str: str):
    """
    OK, the following code is a hot mess...

    Assumptions: instruction string (instr_str) could
    (1) have an arbitrary number of infix binary '+'
    (2) have an arbitrary number of infix binary '*'
    (3) '*' is higher precedence than '+'
    :param instr_str:
    :return:
    """

    def flatten(lst):
        flat_list = list()
        for elm in lst:
            if isinstance(elm, list):
                for elm2 in elm:
                    flat_list.append(elm2)
            else:
                flat_list.append(elm)
        return flat_list

    def insert_infix(seq, val='+'):
        new_seq = list()
        for i, elm in enumerate(seq):
            new_seq.append(elm)
            if i < len(seq) - 1:
                new_seq.append(val)
        return new_seq

    def tokenize(_clause):
        if '*' in _clause:
            clause_times = [elm.strip(' ') for elm in _clause.split('*')]
            clause_times = insert_infix(clause_times, '*')
            return ['['] + clause_times + [']']
        else:
            return _clause

    clause_top = instr_str[1:-1]
    if '+' in clause_top:
        clause_plus = [elm.strip(' ') for elm in clause_top.split('+')]
        new_clause_plus = list()
        for elm in clause_plus:
            new_clause_plus.append(tokenize(elm))
        clause_plus = flatten(insert_infix(new_clause_plus, '+'))
        return ['['] + clause_plus + [']']
    else:
        return tokenize(clause_top)


def mytest_parse_compound_instructions(verbose_p=False):
    # another hot mess...
    def equal_list(lst1, lst2):
        if not isinstance(lst1, list) or not isinstance(lst2, list):
            return False
        elif len(lst1) != len(lst2):
            return False
        else:
            for i, (l1elm, l2elm) in enumerate(zip(lst1, lst2)):
                if l1elm != l2elm:
                    return False
        return True

    case1 = '[RDX*0x4]'
    ret = parse_compound_instructions(case1)
    assert equal_list(ret, ['[', 'RDX', '*', '0x4', ']'])
    if verbose_p:
        print(f'{case1}:', ret)

    case2 = '[RAX + -0x64]'
    ret = parse_compound_instructions(case2)
    assert equal_list(ret, ['[', 'RAX', '+', '-0x64', ']'])
    if verbose_p:
        print(f'{case2}:', ret)

    case3 = '[RSI + RCX*0x1]'
    ret = parse_compound_instructions(case3)
    assert equal_list(ret, ['[', 'RSI', '+', '[', 'RCX', '*', '0x1', ']', ']'])
    if verbose_p:
        print(f'{case3}:', ret)

    case4 = '[RSI]'
    ret = parse_compound_instructions(case4)
    assert ret == 'RSI'
    if verbose_p:
        print(f'{case4}:', ret)


# mytest_parse_compound_instructions()


class Function:
    def __init__(self, lines: List[str], instr_set: "InstructionSet"):
        self.instr_set = instr_set
        self.address: str = ''
        self.address_min: str = ''
        self.address_max: str = ''
        self.name: str = ''
        self.address_seq: List[str] = list()
        self.address_blocks: Dict[str, Tuple] = dict()
        self.tokens: OrderedDict[str, List] = OrderedDict()

        self.parse_from_lines(lines)

    def print_address_blocks(self, substitute_interpreted_values_p=False):
        print(f'START Address Blocks for function: {self.name} @ {self.address}')
        if substitute_interpreted_values_p:
            print(f'### <Address> : <Tokens_(with-interpreted-values)> : ([<Ghidra_Interpretation>], <Metadata>)')
        else:
            print(f'### <Address> : <Tokens> : ([<Ghidra_Interpretation>], <Metadata>)')
        for addr, rest in self.address_blocks.items():
            if addr in self.tokens:
                if substitute_interpreted_values_p:
                    token_or_value_list = list()
                    for token in self.tokens[addr]:
                        token_or_value_list.append(self.instr_set.get_token_or_interpreted_value(token))
                    print(f'{addr} : {token_or_value_list} : {rest}')
                else:
                    print(f'{addr} : {self.tokens[addr]} : {rest}')
            else:
                print(f'{addr} : {rest}')
        print(f'END Address Blocks for function {self.name} @ {self.address}')

    def parse_from_lines(self, lines):
        for line in lines:
            if line.startswith('>>> FUNCTION_START'):
                _, _, addr, fn_name = line.split(' ')
                self.address = addr
                self.name = fn_name
            elif line.startswith('addr_set_min'):
                _, addr = line.split(' ')
                self.address_min = addr
            elif line.startswith('addr_set_max'):
                _, addr = line.split(' ')
                self.address_max = addr
            else:
                addr_str, rest = line.split('::')
                addr = addr_str.strip(' ').split('x')[1]
                self.address_seq.append(addr)
                self.address_blocks[addr] = self.parse_line(rest.strip(' '))

    def parse_line(self, line):
        instr = list()
        rest = None
        if '>>>' in line:
            first, rest = line.split('>>>')
            line = first.strip(' ')
            rest = rest.strip(' ')
        line = line.split(' ', maxsplit=1)
        instr.append(line[0])
        if len(line) > 1:
            if ',' in line[1]:
                args = line[1].split(',')
                for arg in args:
                    instr.append(arg)
            else:
                instr.append(line[1])
        return instr, rest

    def tokenize(self):
        for addr in self.address_seq:
            tokens = list()
            elements, metadata = self.address_blocks[addr]
            if metadata:
                metadata = parse_metadata(metadata)
            ptr_size = None  # if this gets set, then use any values in place of ptr in tokens
            called_fn = None  # store whether a CALL with address/value has been interpreted
            for elm in elements:
                # Values
                if elm.startswith('0x') or elm.startswith('-0x'):
                    if metadata:
                        if 'CALL' in tokens:
                            # have already found a call, so metadata likely holds fn name
                            fn_name = parse_fn_name_from_parsed_metadata(metadata)
                            called_fn = fn_name
                            # tokens.append(self.instr_set.token_map_val.get_token(elm, metadata=fn_name))

                            # TODO: For now, using the fn_name directly as a token. Will need to generalize...
                            tokens.append(fn_name[1])
                        else:
                            # Has metadata, address appears to reference a known value
                            # Use values a metadata
                            # e.g., string as argument to printf

                            # attempt to parse string
                            parsed_string = parse_string_value_from_parsed_metadata(metadata)
                            if parsed_string is not None:
                                tokens.append(self.instr_set.token_map_val.get_token(elm, metadata=parsed_string))
                            else:
                                tokens.append(self.instr_set.token_map_val.get_token(elm, metadata=metadata))
                    else:
                        value = parse_hex_value(elm, size=ptr_size)
                        tokens.append(self.instr_set.token_map_val.get_token(elm, metadata=value))

                        # CTM 2021-10-28: for now, interpret all values as val, not val_other
                        # if ptr_size:
                        #     tokens.append(self.instr_set.token_map_val.get_token(elm, metadata=value))
                        # else:
                        #     tokens.append(self.instr_set.token_map_val_other.get_token(elm))
                # Address ptr
                elif ' ptr ' in elm:
                    ptr_size = elm.split(' ')[0]
                    if metadata:
                        if 'CALL' in tokens:
                            # have already found a call, so metadata likely holds fn name
                            fn_name = parse_fn_name_from_parsed_metadata(metadata)
                            called_fn = fn_name
                            # tokens.append(self.instr_set.token_map_val.get_token(elm, metadata=fn_name))

                            # TODO: For now, using the fn_name directly as a token. Will need to generalize...
                            tokens.append(fn_name[1])
                        else:
                            # no CALL, so check if note contain hex value: e.g.,
                            value = parse_hex_value_from_parsed_metadata(metadata, ptr_size)
                            tokens.append(self.instr_set.token_map_val.get_token(elm, metadata=value))
                    else:
                        tokens.append(self.instr_set.token_map_address.get_token(elm))

                elif elm.startswith('[') and elm.endswith(']') and len(elm) > 2:

                    # handle cases like: '[RDX*0x4]' or '[RAX + -0x64]' or '[RSI + RCX*0x1]'
                    compound_clause = parse_compound_instructions(elm)
                    if not isinstance(compound_clause, list):
                        compound_clause = [compound_clause]
                    for cc_elm in compound_clause:
                        if cc_elm.startswith('0x') or cc_elm.startswith('-0x'):
                            tokens.append(self.instr_set.token_map_val.get_token(elm, metadata=cc_elm))
                        else:
                            tokens.append(cc_elm)

                    # clause = elm[1:-1].split(' ')
                    # tokens.append('[')
                    # for celm in clause:
                    #     if celm.startswith('0x') or celm.startswith('-0x'):
                    #         value = parse_hex_value(celm, size=ptr_size)
                    #         tokens.append(self.instr_set.token_map_val.get_token(celm, metadata=value))
                    #     else:
                    #         tokens.append(celm)
                    # tokens.append(']')
                else:
                    # Does not appear to be a special value reference, use elm as token
                    tokens.append(elm)

            # handle clase where a CALL was observed but no address/value was interpreted as fn_name
            # This happens, e.g., in _init : CALL RAX >>> array(java.lang.String, [u'undefined __gmon_start__()'])
            if 'CALL' in tokens and called_fn is None and metadata:
                fn_name = parse_fn_name_from_parsed_metadata(metadata)
                print(f'WARNING: fn={self.name}, address={addr}, CALL to {fn_name} with no explicit token')

            self.tokens[addr] = tokens

            # TODO: for now, adding the sequence to the instr_set. May need to revisit this when handling multiple fns
            self.instr_set.token_seq += tokens

            self.instr_set.unique_tokens |= set(tokens)

    def get_tokens(self):
        token_seq = list()
        for _, block in self.tokens.items():
            token_seq += block
        return token_seq


class InstructionSet:
    def __init__(self):
        self.token_map_address: BiMap = BiMap('_a')
        self.token_map_val: BiMap = BiMap('_v')
        self.token_map_val_other: BiMap = BiMap('_o')
        self.token_seq: List[str] = list()  # TODO currently being set by Function.tokenize()
        self.unique_tokens: Set[str] = set()

        self.fn_by_address: Dict[str, Function] = dict()
        self.fn_address_by_name: Dict[str, str] = dict()

    def print_token_seq(self):
        tokens_str = f'{self.token_seq}'
        print(f"{tokens_str[1:-1]}")

    def get_non_generated_tokens(self):
        return self.unique_tokens \
               - self.token_map_address.get_all_tokens() \
               - self.token_map_val.get_all_tokens() \
               - self.token_map_val_other.get_all_tokens()

    def print_token_maps(self):
        token_address_size = len(self.token_map_address.get_all_tokens())
        print(f'START token_map_address {token_address_size}')
        self.token_map_address.print()
        print('END token_map_address')
        token_val_size = len(self.token_map_val.get_all_tokens())
        print(f'START token_map_val {token_val_size}')
        self.token_map_val.print()
        print('END token_map_val')
        token_val_other_size = len(self.token_map_val_other.get_all_tokens())
        print(f'START token_map_val_other {token_val_other_size}')
        self.token_map_val_other.print()
        print('END token_map_val_other')
        print('START token_stats')
        print(f'Token Sequence Length [{len(self.token_seq)}]')
        token_dist = Counter(self.token_seq)
        print(f'Token Distribution [{len(token_dist)}]: {token_dist}')
        # The following is redundant given the token_dist: the keys of token_dist *are* the unique tokens
        # print(f'Unique Tokens [{len(self.unique_tokens)}]: {self.unique_tokens}')
        print(f'Total Generated Tokens [{token_address_size + token_val_size + token_val_other_size}]')
        non_gen_tokens = self.get_non_generated_tokens()
        print(f'Non-generated Tokens [{len(non_gen_tokens)}]: {non_gen_tokens}')
        print('END token_stats')

    def get_token_or_interpreted_value(self, token: str):
        # TODO: this is very hacky...
        if token.startswith('_a'):
            tmap = self.token_map_address
        elif token.startswith('_v'):
            tmap = self.token_map_val
        elif token.startswith('_o'):
            tmap = self.token_map_val_other
        else:
            return token
        _, metadata = tmap.get_value(token)
        if metadata:
            if metadata[0] == ':interpreted_hex' or metadata[0] == ':interpreted_hex_float':
                return token, metadata[2]
            elif metadata[0] == ':string' or metadata[0] == ':fn_name':
                return token, metadata[1]
        else:
            return token

    def add_fn(self, fn: Function):
        self.fn_by_address[fn.address] = fn
        self.fn_address_by_name[fn.name] = fn.address

    def get_fn_by_name(self, name):
        return self.fn_by_address[self.fn_address_by_name[name]]


def extract_instructions(filepath):
    instruction_set = InstructionSet()
    lines = list()
    in_fn_p = False
    with open(filepath, 'r') as f:
        for line in f.readlines():
            line = line.strip('\n')
            if line.startswith('>>> FILE_START'):
                pass
            elif line.startswith('>>> FUNCTION_START'):
                in_fn_p = True
                lines.append(line)
            elif line.startswith('>>> FUNCTION_END'):
                instruction_set.add_fn(Function(lines, instruction_set))
                in_fn_p = False
                lines = list()
            elif in_fn_p:
                lines.append(line)
    return instruction_set


class TokenSet:
    def __init__(self):
        self.token_seqs: List[str] = list()
        self.token_seq_lengths: List[int] = list()
        self.token_address: Set[str] = set()
        self.token_val: Set[str] = set()
        self.token_val_other: Set[str] = set()

    def add(self, inst_set: InstructionSet):  # add(self, token_seq, token_address, token_val, token_val_other):
        self.token_seqs += inst_set.token_seq
        self.token_seq_lengths.append(len(inst_set.token_seq))
        self.token_address |= inst_set.token_map_address.get_all_tokens()
        self.token_val |= inst_set.token_map_val.get_all_tokens()
        self.token_val_other |= inst_set.token_map_val_other.get_all_tokens()

    def get_non_generated_tokens(self):
        return set(self.token_seqs) \
               - self.token_address \
               - self.token_val \
               - self.token_val_other

    def print(self):
        token_dist = Counter(self.token_seqs)
        print(f'Token Distribution [{len(token_dist)}]: {token_dist}')
        print(f'Token Sequence Lengths: {reversed(sorted(self.token_seq_lengths))}')
        # print(f'Token Sequence Lengths dist: {Counter(self.token_seq_lengths)}')
        token_address_size = len(self.token_address)
        token_val_size = len(self.token_val)
        token_val_other_size = len(self.token_val_other)
        non_gen_tokens = self.get_non_generated_tokens()
        print(f'Non-generated Tokens [{len(non_gen_tokens)}]: {non_gen_tokens}')
        print(f'Total Generated Tokens [{token_address_size + token_val_size + token_val_other_size}]')
        print(f'Token Address [{token_address_size}]: {self.token_address}')
        print(f'Token val [{token_val_size}]: {self.token_val}')
        print(f'Token val_other [{token_val_other_size}]: {self.token_val_other}')


def extract_tokens_from_instr_file(token_set, _src_filepath, _dst_filepath, num=0,
                                   execute_p=True, verbose_p=False):
    if not execute_p:
        print(f'{num} [TEST] tokenize {_src_filepath} -> {_dst_filepath}')
    else:
        if verbose_p:
            print(f'{num} [EXECUTE] tokenize {_src_filepath} -> {_dst_filepath}')

        inst_set = extract_instructions(_src_filepath)
        main_fn = inst_set.get_fn_by_name('main')
        main_fn.tokenize()

        token_set.add(inst_set)

        original_stdout = sys.stdout
        with open(_dst_filepath, 'w') as fout:
            sys.stdout = fout
            inst_set.print_token_seq()
            inst_set.print_token_maps()
            main_fn.print_address_blocks(substitute_interpreted_values_p=True)
            sys.stdout = original_stdout


def batch_process(execute_p: bool,
                  dst_dir: str,
                  instructions_root_dir: str,
                  instructions_file: str = ''):
    token_set = TokenSet()

    def get_dst_filepath(_src_filepath):
        _dst_filepath = os.path.join(dst_dir, os.path.basename(_src_filepath))
        return os.path.splitext(_dst_filepath)[0] + '__tokens.txt'

    if instructions_file != '':
        src_filepath = os.path.join(instructions_root_dir, instructions_file)
        if not os.path.isfile(src_filepath):
            raise Exception(f'ERROR: File not found: {src_filepath}')

        dst_filepath = get_dst_filepath(src_filepath)
        # print('src_filepath:', src_filepath)
        # print('dst_filepath:', dst_filepath)

        extract_tokens_from_instr_file(token_set, src_filepath, dst_filepath)

    else:
        i = 0
        for subdir, dirs, files in os.walk(instructions_root_dir):
            for file in files:
                src_filepath = subdir + os.sep + file
                if src_filepath.endswith('-instructions.txt'):
                    dst_filepath = get_dst_filepath(src_filepath)

                    extract_tokens_from_instr_file(token_set, src_filepath, dst_filepath,
                                                   num=i, execute_p=execute_p,
                                                   verbose_p=execute_p)
                    i += 1

    if execute_p:
        token_set_summary_filepath = os.path.join(dst_dir, 'tokens_summary.txt')
        if pathlib.Path(token_set_summary_filepath).is_file():
            token_set_summary_filepath += str(uuid.uuid4())
        original_stdout = sys.stdout
        with open(token_set_summary_filepath, 'w') as fout:
            sys.stdout = fout
            token_set.print()
            sys.stdout = original_stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--execute',
                        help='execute script (as opposed to running in test mode)',
                        action='store_true', default=False)
    parser.add_argument('-I', '--instructions_root_dir',
                        help='specify the instructions root directory; required',
                        type=str,
                        default='examples_ghidra_instructions/gcc')
    parser.add_argument('-i', '--instructions_file',
                        help='Optionally specify a specific Ghidra instructions file to process; '
                             'if left unspecified, then process whole instructions_root_dir directory',
                        type=str,
                        default='')
    parser.add_argument('-D', '--dst_dir',
                        help='directory where extracted token files will be saved',
                        type=str,
                        default='examples_tokenized')

    args = parser.parse_args()

    if not args.execute:
        print(f'Running in TEST mode: {args.instructions_root_dir} {args.dst_dir}')
    else:
        print(f'EXECUTE! {args.instructions_root_dir} {args.dst_dir}')

        # create destination root directory if does not already exist
        pathlib.Path(args.dst_dir).mkdir(parents=True, exist_ok=True)

    batch_process(execute_p=args.execute,
                  dst_dir=args.dst_dir,
                  instructions_root_dir=args.instructions_root_dir,
                  instructions_file=args.instructions_file)


if __name__ == '__main__':
    # test_parse_metadata()
    # test_get_fn_name_from_parsed_metadata()
    main()

# Tests -- TODO: ceate actual unit tests...

"""
def test_parse_metadata():
    print('TEST test_parse_metadata()')
    t1 = "array(java.lang.String, [u'= 00405010', u'= ??'])"
    print(parse_metadata(t1))
    t2 = "array(java.lang.String, [u'undefined __libc_start_main()'])"
    print(parse_metadata(t2))
    t3 = "array(java.lang.String, [u'= \"Answer: %g\\n\"'])"
    print(parse_metadata(t3))
    t4 = "array(java.lang.String, [u'int printf(char * __format, ...)'])"
    print(parse_metadata(t4))
    t5 = "something else"
    print(parse_metadata(t5))
    t6 = "array(java.lang.String, [u'= 40E75C29h'])"
    print(parse_metadata(t6))
    t7 = "array(java.lang.String, [u'= C056133333333333h'])"
    print(parse_metadata(t7))
"""

"""
def test_parse_fn_name_from_parsed_metadata():
    print('TEST parse_fn_name_from_parsed_metadata()')
    t1 = [':array', 'java.lang.String', 'undefined __libc_start_main()']
    print(parse_fn_name_from_parsed_metadata(t1))
    t2 = [':array', 'java.lang.String', 'int printf(char * __format, ...)']
    print(parse_fn_name_from_parsed_metadata(t2))
    t3 = [':array', 'java.lang.String', 'printf(char * __format, ...)']
    print(parse_fn_name_from_parsed_metadata(t3))
"""

"""
def unpack():
    print(int('7', 16))    # 7   : dword = int
    print(int('62', 16))   # 98  : qword = long
    print(int('11b', 16))  # 283 : qword = long

    # 7.23  : dword = float
    print(struct.unpack('!f', bytes.fromhex('40E75C29')))

    # -88.3 : qword = double
    print(struct.unpack('!d', bytes.fromhex('C056133333333333')))
"""

# Kinda cool, but didn't end up using:
# class bidict(dict):
#     def __init__(self, *args, **kwargs):
#         super(bidict, self).__init__(*args, **kwargs)
#         self.inverse = {}
#         for key, value in self.items():
#             self.inverse.setdefault(value,[]).append(key)
#
#     def __setitem__(self, key, value):
#         if key in self:
#             self.inverse[self[key]].remove(key)
#         super(bidict, self).__setitem__(key, value)
#         self.inverse.setdefault(value,[]).append(key)
#
#     def __delitem__(self, key):
#         self.inverse.setdefault(self[key],[]).remove(key)
#         if self[key] in self.inverse and not self.inverse[self[key]]:
#             del self.inverse[self[key]]
#         super(bidict, self).__delitem__(key)
