from __future__ import print_function

import os
import sys
import glob
from collections import namedtuple
from plasTeX.TeX import TeX
from plasTeX.Tokenizer import BeginGroup, EndGroup, EscapeSequence, Parameter



MacroDef = namedtuple('MacroDef', 'n_args definition')



def find_main_tex_file(dirname):
    r"""looks in a directory for a .tex file that contain the \documentclass directive"""
    # (from https://arxiv.org/help/faq/mistakes#wrongtex)
    #
    # Why does arXiv's system fail to recognize the main tex file?
    #
    # It is possible in writing your latex code to include your \documentclass directive
    # in a file other than the main .tex file. While this is perfectly reasonable for a human
    # who's compling to know which of the tex files is the main one (even when using something
    # obvious as the filename, such as ms.tex), our AutoTeX system will attempt to process
    # whichever file has the \documentclass directive as the main tex file.
    #
    # Note that the system does not process using Makefile or any other manifest-type files.
    for filename in glob.glob(os.path.join(dirname, '*.tex')):
        with open(filename) as f:
            for line in f:
                line = line.strip()
                if line.startswith(r'\documentclass'):
                    return filename



def maybe_add_extension(filename):
    """add .tex extension if needed"""
    if os.path.exists(filename):
        return filename
    elif os.path.exists(filename + '.tex'):
        return filename + '.tex'



def read_group(tokens):
    """read the content of a tex group, i.e., the text surrounded by curly brackets"""
    s = ''
    t = next(tokens)
    toks = [t]
    assert isinstance(t, BeginGroup)
    while True:
        t = next(tokens)
        toks.append(t)
        if isinstance(t, EndGroup):
            break
        s += t.data
    return s, toks



def is_begin_group(t):
    return isinstance(t, BeginGroup) or t == '['

def is_end_group(t):
    return isinstance(t, EndGroup) or t == ']'

def read_balanced_brackets(tokens):
    """
    returns the contents of a group (i.e. curly brackets)
    including the curly brackets
    may contain nested curly brackets
    """
    t = next(tokens)
    print("t: ", t)
    #print("tokens passed:", list(tokens))
    #assert isinstance(t, BeginGroup), t + " isn't a BeginGroup"
    assert is_begin_group(t), t + " isn't a BeginGroup, tokens passed:" + ",".join(list(tokens))
    n_open = 1
    capture = [t]
    while True:
        t = next(tokens)
        capture.append(t)
        # if isinstance(t, BeginGroup):
        if is_begin_group(t):
            n_open += 1
        # elif isinstance(t, EndGroup):
        elif is_end_group(t):
            n_open -= 1
        if n_open == 0:
            break
    return capture

def format_n_args(bracketed_tokens):
    return int(''.join(bracketed_tokens[1:-1]))

def maybe_expand_macro(token, tokens, macro_args, macro_lut):

    if not isinstance(token, EscapeSequence):
        # this is not a macro
        #print(token, "is not an EscapeSequence")
        yield token
    elif token.data not in macro_lut:
        # this isn't a macro either
        # print(token, "is not in macro_lut")
        yield token
    else:
        print(token, "IS in the macro_lut")
        macro_def = macro_lut[token.data]
        n_args = macro_def.n_args
        print("macro definition:", macro_def.definition)
        # note: consuming some tokens here fyi
        # macro_args = []
        # fixme I don't think I have the recursion right with this...
        # todo(marco): check the recursive reading of args - arg propogation
        for i in range(n_args):
            print("Reading arg", i)
            # trying to consume tokens to get the arguments, but we already have the arguments...
            if len(macro_args) < n_args:
                macro_args.append(read_balanced_brackets(tokens)[1:-1])
                print("macro_args:", macro_args)
        #todo(marco) - should this be an iterator?
        macro_iter = iter(macro_def.definition)
        for expanded in macro_iter:
            print("Looking at expanded:", expanded)
            if isinstance(expanded, Parameter):
                arg_index = int(next(macro_iter))
                print("found arg_index:", arg_index)
                supplied_arg_tokens = macro_args[arg_index - 1]
                for arg_t in supplied_arg_tokens:
                    yield arg_t
            else:
                for t in maybe_expand_macro(expanded, tokens, macro_args, macro_lut):
                    yield t




class LatexTokenizer:

    def __init__(self, filename):
        self.filename = filename
        self.macro_lut = {}
        self.tokens = list(self.itertokens())

    def __iter__(self):
        return iter(self.tokens)

    def itertokens(self):
        """read tex tokens, including imported files"""
        dirname = os.path.dirname(self.filename)
        tex = TeX(file=self.filename)
        tokens = tex.itertokens()
        try:
            while True:
                token = next(tokens)
                if token.data == 'input':
                    fname = os.path.join(dirname, read_group(tokens)[0])
                    fname = maybe_add_extension(fname)
                    for t in LatexTokenizer(fname):
                        yield t
                elif token.data == 'import':
                    # TODO handle \subimport, and also \import* and \subimport*
                    raise NotImplementedError("we don't handle \\import yet")
                elif token.data == 'include':
                    # TODO be aware of \includeonly
                    raise NotImplementedError("we don't handle \\include yet")
                elif token.data == 'newcommand':
                    print("found a NEW COMMAND!")
                    name = read_group(tokens)[0]
                    #name = name[1:] # drop backslash
                    print("   name:", name)
                    # check to see if this is followed by the
                    # n_args = 0 # TODO number of args
                    args_or_def = read_balanced_brackets(tokens)
                    if args_or_def[0] == '[': # n_args
                        n_args = format_n_args(args_or_def)
                        definition = read_balanced_brackets(tokens)
                    else:
                        n_args = 0
                        definition = args_or_def
                    # todo(marco): check -- maybe this shoulnd't be an iterator
                    definition = iter(definition[1:-1]) # drop brackets
                    self.macro_lut[name] = MacroDef(n_args, definition)
                else:
                    for t in maybe_expand_macro(token, tokens, [], self.macro_lut):
                        yield t
        except StopIteration:
            pass

    def equations(self):
        tokens = iter(self.tokens)
        try:
            while True:
                token = next(tokens)
                if token.data == 'begin':
                    group_name = read_group(tokens)[0]
                    if group_name in ('equation', 'equation*', 'align', 'align*'):
                        equation = []
                        while True:
                            t = next(tokens)
                            if t.data == 'end':
                                name, ts = read_group(tokens)
                                if name == group_name:
                                    break
                                else:
                                    equation.append(t)
                                    equation += ts
                            else:
                                equation.append(t)
                        yield (group_name, equation)
                # TODO add support for other math environments
        except StopIteration:
            pass



if __name__ == '__main__':
    for t in LatexTokenizer(find_main_tex_file(sys.argv[1])):
        print(type(t), repr(t))
