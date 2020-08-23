
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
from align_eq_bb import all_fragments

def get_frags(formula):
    tokens = list(LatexTokenizer(formula))
    frags = list(all_fragments(tokens))
    # for frag in frags:
    #     print(frag)
    return frags

def is_balanced(s):
    return is_balanced_delim(s, '(', ')') and is_balanced_delim(s, '[', ']')

def is_balanced_delim(s, open_delim, close_delim):
    n_open = 0
    for c in s:
        if c == open_delim:
            n_open += 1
        elif c == close_delim:
            n_open -= 1
        if n_open < 0:
            return False
    return n_open == 0


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
        for frag in set(frags):
            if len(frag) == 0 or frag[0] in punct or frag[-1] in punct or not is_balanced(frag):
                continue
            else:
                print(frag)

