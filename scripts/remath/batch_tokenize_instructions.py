from typing import Dict, List, Tuple, Any, Set
import struct
from collections import OrderedDict


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


EXAMPLE_INSTRUCTIONS_FILE = \
    'examples_ghidra_instructions/gcc/' \
    'types_without_long_double__Linux-5.11.0-38-generic-x86_64-with-glibc2.31__gcc-10.1.0-instructions.txt'
# 'types__Linux-5.11.0-38-generic-x86_64-with-glibc2.31__gcc-10.1.0-instructions.txt'
# 'expr_00__Linux-5.11.0-38-generic-x86_64-with-glibc2.31__gcc-10.1.0-instructions.txt'


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
            ptr_size = None   # if this gets set, then use any values in place of ptr in tokens
            called_fn = None  # store whether a CALL with address/value has been interpreted
            for elm in elements:
                # Values
                if elm.startswith('0x') or elm.startswith('-0x'):
                    if metadata:
                        if 'CALL' in tokens:
                            # have already found a call, so metadata likely holds fn name
                            fn_name = parse_fn_name_from_parsed_metadata(metadata)
                            called_fn = fn_name
                            tokens.append(self.instr_set.token_map_val.get_token(elm, metadata=fn_name))
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
                        if ptr_size:
                            tokens.append(self.instr_set.token_map_val.get_token(elm, metadata=value))
                        else:
                            tokens.append(self.instr_set.token_map_val_other.get_token(elm))
                # Address ptr
                elif ' ptr ' in elm:
                    ptr_size = elm.split(' ')[0]
                    if metadata:
                        if 'CALL' in tokens:
                            # have already found a call, so metadata likely holds fn name
                            fn_name = parse_fn_name_from_parsed_metadata(metadata)
                            called_fn = fn_name
                            tokens.append(self.instr_set.token_map_val.get_token(elm, metadata=fn_name))
                        else:
                            # no CALL, so check if note contain hex value: e.g.,
                            value = parse_hex_value_from_parsed_metadata(metadata, ptr_size)
                            tokens.append(self.instr_set.token_map_val.get_token(elm, metadata=value))
                    else:
                        tokens.append(self.instr_set.token_map_address.get_token(elm))
                else:
                    # Does not appear to be a special value reference, to use elm as token
                    tokens.append(elm)

            # handle clase where a CALL was observed but no address/value was interpreted as fn_name
            # This happens, e.g., in _init : CALL RAX >>> array(java.lang.String, [u'undefined __gmon_start__()'])
            if 'CALL' in tokens and called_fn is None and metadata:
                fn_name = parse_fn_name_from_parsed_metadata(metadata)
                print(f'WARNING: fn={self.name}, address={addr}, CALL to {fn_name} with no explicit token')

            self.tokens[addr] = tokens
            self.instr_set.unique_tokens |= set(tokens)

    def to_tokens(self):
        token_seq = list()
        for _, block in self.tokens.items():
            token_seq += block
        return token_seq


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


def parse_unicode_string_list(ustr):
    chunks = list()
    in_str = False
    str_start = None
    for i in range(1, len(ustr)):
        if ustr[i-1] == 'u' and ustr[i] == '\'' and not in_str:
            in_str = True
            str_start = i + 1
        elif ustr[i-1] != '\\' and ustr[i] == '\'' and in_str:
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
    if size:
        return ':interpreted_hex', value, int(value, 16), size
    else:
        return ':raw_hex', value


class InstructionSet:
    def __init__(self):
        self.token_map_address: BiMap = BiMap('_a')
        self.token_map_val: BiMap = BiMap('_v')
        self.token_map_val_other: BiMap = BiMap('_o')
        self.unique_tokens: Set[str] = set()

        self.fn_by_address: Dict[str, Function] = dict()
        self.fn_address_by_name: Dict[str, str] = dict()

    def get_non_generated_tokens(self):
        return self.unique_tokens \
               - self.token_map_address.get_all_tokens() \
               - self.token_map_val.get_all_tokens() \
               - self.token_map_val_other.get_all_tokens()

    def print_tokens(self):
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
        print(f'Total Generated Tokens [{token_address_size + token_val_size + token_val_other_size}]')
        non_gen_tokens = self.get_non_generated_tokens()
        print(f'Non-generated Tokens [{len(non_gen_tokens)}]: {non_gen_tokens}')
        print(f'Unique Tokens [{len(self.unique_tokens)}]: {self.unique_tokens}')

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
    inst_set = InstructionSet()
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
                inst_set.add_fn(Function(lines, inst_set))
                in_fn_p = False
                lines = list()
            elif in_fn_p:
                lines.append(line)
    return inst_set


def main():
    inst_set = extract_instructions(EXAMPLE_INSTRUCTIONS_FILE)
    main_fn = inst_set.get_fn_by_name('main')
    main_fn.tokenize()
    main_fn.print_address_blocks(substitute_interpreted_values_p=True)
    inst_set.print_tokens()
    tokens = main_fn.to_tokens()
    print(f'Tokens Sequence [{len(tokens)}]: {tokens}')


def unpack():
    print(int('7', 16))    # 7   : dword = int
    print(int('62', 16))   # 98  : qword = long
    print(int('11b', 16))  # 283 : qword = long

    # 7.23  : dword = float
    print(struct.unpack('!f', bytes.fromhex('40E75C29')))

    # -88.3 : qword = double
    print(struct.unpack('!d', bytes.fromhex('C056133333333333')))


if __name__ == '__main__':
    # test_parse_metadata()
    # test_get_fn_name_from_parsed_metadata()
    main()
    # print('------')
    # unpack()


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