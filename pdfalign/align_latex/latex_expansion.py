from collections import namedtuple
from latex_tokenizer import *

MacroDef = namedtuple('MacroDef', 'n_args definition')

def build_macro_lut(tokens):
    tokens = iter(tokens)
    macro_lut = dict()
    while True:
        try:
            token = next(tokens)
            if token.value == '\\newcommand':
                name = read_macro_name(tokens)
                args_or_def = read_balanced_brackets(tokens)
                if args_or_def[0].value == '[':
                    n_args = int(next(tokens).value)
                    next(tokens) # closing square bracket
                    definition = read_balanced_brackets(tokens)
                else:
                    n_args = 0
                    definition = args_or_def
                macro_lut[name] = MacroDef(n_args, definition[1:-1])
        except StopIteration:
            return macro_lut

def expand_tokens(tokens, macro_lut):
    return list(iter_tokens(tokens, macro_lut))

def iter_tokens(tokens, macro_lut):
    tokens = iter(tokens)
    while True:
        try:
            token = next(tokens)
            for t in maybe_expand_macro(token, tokens, macro_lut):
                yield t
        except StopIteration:
            break

def maybe_expand_macro(token, tokens, macro_lut):
    if not token.value.startswith('\\'):
        # this is not a macro
        yield token
    elif token.value not in macro_lut:
        # we haven't seen this macro's definition
        yield token
    else:
        macro_def = macro_lut[token.value]
        # consume args
        macro_args = [read_balanced_brackets(tokens)[1:-1] for i in range(macro_def.n_args)]
        # expand macro
        expanded = expand_macro(macro_def, macro_args)
        # try to expand recursively
        for t in expanded:
            for t2 in maybe_expand_macro(t, expanded, macro_lut):
                yield t2

def expand_macro(macro_def, macro_args):
    for expanded in macro_def.definition:
        if expanded.value.startswith('#'):
            arg_index = int(expanded.value[1:])
            supplied_arg_tokens = macro_args[arg_index-1]
            for arg_t in supplied_arg_tokens:
                yield arg_t
        else:
            yield expanded

def read_balanced_brackets(tokens):
    """
    returns the contents of a group (i.e. curly brackets)
    including the curly brackets
    may contain nested curly brackets
    """
    n_open = 0
    capture = []
    while True:
        t = next(tokens)
        capture.append(t)
        if t.code == CategoryCode.StartOfGroup:
            n_open += 1
        elif t.code == CategoryCode.EndOfGroup:
            n_open -= 1
        if n_open == 0:
            break
    return capture

def read_macro_name(tokens):
    group = read_balanced_brackets(tokens)
    return ''.join(t.value for t in group[1:-1])
