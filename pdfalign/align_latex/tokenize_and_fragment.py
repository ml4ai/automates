
import sys
import os
import re
import json
import subprocess
from glob import glob
from collections import namedtuple
from shutil import copytree, rmtree
import numpy as np
from lxml import etree
from pdf2image import convert_from_path
from latex_tokenizer import LatexTokenizer, CategoryCode
from arxiv_utils import find_main_tex_file

def tokens_to_string(tokens):
    s = ''
    for t in tokens:
        s += t.value
        if re.match(r'\\\w+', t.value) and t.code is None:
            # we need to introduce a space after control words
            # so that they don't get merged with text that may follow them
            s += ' '
    return s

def latex_strip(tokens):
    spaces = {'\\,', '\\:', '\\;', '\\!', '\\ ', '~', ' ', '\t'}
    # lstrip
    while tokens:
        if tokens[0].value in spaces:
            tokens.pop(0)
        else:
            break
    # rstrip
    while tokens:
        if tokens[-1].value in spaces:
            tokens.pop()
        else:
            break
    return tokens

def all_fragments(tokens):
    # return only fragments with balanced curly brackets
    # and strip whitespaces

    for i in range(len(tokens)):
        for j in range(i, len(tokens)):
            fragment = tokens[i:j+1]
            # count open and curly brackets
            opened = closed = 0


            for t in fragment:
                if t.code == CategoryCode.StartOfGroup:
                    opened += 1
                elif t.code == CategoryCode.EndOfGroup:
                    closed += 1
                    if closed > opened:
                        # we found a close curly bracket before an open one
                        break

            if closed == opened:
                yield tokens_to_string(latex_strip(fragment))

def get_frags(formula):
    tokens = list(LatexTokenizer(formula))
    frags = list(all_fragments(tokens))
    # for frag in frags:
    #     print(frag)
    return frags

if __name__ == '__main__':
    command = sys.argv[1]
    formula = sys.argv[2]
    # formula ="""\\f_{mn}\\big(z\\big)=\\left\\{\\begin{cases}{\\frac{\\operatorname{cosh}k_{mn}\\big(z+H\\big)}{\\operatorname{cosh}k_{mn}H}}&{\\mathrm{if}\\quadf_{mn}\\big(z\\big)<C_{f(z)}}\\{C_{f(z)}}&{\\mathrm{if}\\quadf_{mn}\\big(z\\big)\\geqC_{f(z)}}\\end{cases}\\right."""
    # tokens = list(LatexTokenizer(formula))
    # for t in tokens:
    #     print(t)

    if command == "get_fragments":
        punct = ["^", "=", "_", "+", ">", "<", "."]
        frags = get_frags(formula)
        for frag in frags:
            if frag[0] in punct or frag[-1] in punct or frag.startswith(")") or frag.endswith("("):
                break
            else:
                print(frag, end="\n")
