import os
import sys
from plasTeX.TeX import TeX
from plasTeX.Tokenizer import BeginGroup, EndGroup



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
            if token.data == 'begin': #and read_group(tokens)[0] == 'equation':
                group_name = read_group(tokens)[0]
                if group_name in ('equation', 'equation*'):
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
                    yield equation
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
                path = read_group(tokens)[0]
                name = read_group(tokens)[0]
                fname = maybe_add_extension(os.path.join(path, name))
                for t in tokenize(fname):
                    yield t
            elif token.data == 'include':
                # TODO be aware of \includeonly
                fname = maybe_add_extension(read_group(tokens)[0])
                for t in tokenize(fname):
                    yield t
            else:
                yield token
    except StopIteration:
        pass



if __name__ == '__main__':
    for t in tokenize(sys.argv[1]):
        print type(t), repr(t)
