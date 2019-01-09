from __future__ import print_function

import os
import sys
import glob
from plasTeX.TeX import TeX
from plasTeX.Tokenizer import BeginGroup, EndGroup



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



def extract_equations(tokens):
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



def tokenize(filename):
    """read tex tokens, including imported files"""
    dirname = os.path.dirname(filename)
    tex = TeX(file=filename)
    tokens = tex.itertokens()
    try:
        while True:
            token = next(tokens)
            if token.data == 'input':
                fname = os.path.join(dirname, read_group(tokens)[0])
                fname = maybe_add_extension(fname)
                for t in tokenize(fname):
                    yield t
            elif token.data == 'import':
                # TODO handle \subimport, and also \import* and \subimport*
                raise NotImplementedError("we don't handle \\import yet")
            elif token.data == 'include':
                # TODO be aware of \includeonly
                raise NotImplementedError("we don't handle \\include yet")
            else:
                yield token
    except StopIteration:
        pass



if __name__ == '__main__':
    for t in tokenize(find_main_tex_file(sys.argv[1])):
        print(type(t), repr(t))
