#!/usr/bin/env python

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
from latex_expansion import build_macro_lut, expand_tokens
from arxiv_utils import find_main_tex_file



DPI = 200



MATHCOLOR_MACRO = r"""
\usepackage{xcolor}
\definecolor{myred}{rgb}{1,0,0}
\definecolor{mygreen}{rgb}{0,1,0}
\definecolor{myblue}{rgb}{0,0,1}
\definecolor{mycyan}{rgb}{0,1,1}
\definecolor{mymagenta}{rgb}{1,0,1}
\definecolor{myyellow}{rgb}{1,1,0}
\makeatletter
\def\mathcolor#1#{\@mathcolor{#1}}
\def\@mathcolor#1#2#3{%
  \protect\leavevmode
  \begingroup
    \color#1{#2}#3%
  \endgroup
}
\makeatother
"""



DEFAULT_COLORS = [
   'myred', 'mygreen', 'myblue', 'mycyan', 'mymagenta', 'myyellow'
    # 'brown', 'lime', 'olive', 'orange', 'pink', 'purple', 'teal', 'violet',
]



AABB = namedtuple('AABB', 'xmin ymin xmax ymax')



def all_colorizations(tokens, colors=DEFAULT_COLORS):
    # make string for whole equation
    equation = tokens_to_string(tokens)
    # iterate over unique stripped fragments
    for fragment in sorted(set(all_fragments(tokens))):
        # skip if the fragment is empty or if it is the entire equation
        if fragment != '' and fragment != equation:
            yield (fragment, colorize(equation, fragment, colors))



def colorize(equation, fragment, colors=DEFAULT_COLORS):
    i = 0
    def mathcolor(m):
        nonlocal i
        color = colors[i % len(colors)]
        lookbehind = m.group(1)
        match = m.group(2)
        if match[0].isalpha() and len(lookbehind) > 0:
            return m.group()
        else:
            i += 1
            return '{\\mathcolor{' + color + '}{' + match + '}}'
    pattern = r'((?:\\[a-zA-Z]*)?)(' + re.escape(fragment) + ')'
    return re.sub(pattern, mathcolor, equation)



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



def read_equation_annotations(ann_file):
    with open(ann_file) as f:
        annotations = json.load(f)
        return [a['equation'] for a in annotations]



def get_equation_approx_location(annotations):
    # first annotation, first component, first token, first char
    synctex = annotations[0][0][0]['chars'][0]['synctex']
    filename = make_relative_path(synctex['input'])
    line = synctex['line']
    return (filename, line)



# This function is only meant to make a relative path for latex files
# that belong to an arxiv paper. It assumes that the paper id is somewhere
# in the path, and starts the path immediately after that.
def make_relative_path(filename):
    match = re.search(r'\d+\.\d+/(.+)', filename)
    if match:
        return match.group(1)



def find_equation(filename, line, macro_lut={}):
    line -= 1 # line provided is one-based but we want zero-based
    pattern = r'\\begin\s*\{(equation\*?)\}(.+?)\\end\s*\{\1\}'
    with open(filename) as f:
        text = f.read()
        for m in re.finditer(pattern, text, re.MULTILINE | re.DOTALL):
            start = text[:m.start()].count('\n')
            end = text[:m.end()].count('\n')
            if start <= line <= end:
                return m.group(2).strip()
        # if we're here it means the regex failed
        # let's try the macro expansion approach
        orig_line = text.splitlines()[line]
        expanded_line = tokens_to_string(expand_tokens(LatexTokenizer(orig_line), macro_lut))
        match = re.search(pattern, expanded_line, re.MULTILINE | re.DOTALL)
        if match:
            return match.group(2).strip()
        # if we're here then we didn't found an equation



def replace_in_file(filename, pattern, replacement):
    with open(filename) as f:
        text = f.read()
    text = re.sub(re.escape(pattern), lambda m: replacement, text)
    with open(filename, 'w') as f:
        f.write(text)



def inject_macro(filename, macro=MATHCOLOR_MACRO):
    with open(filename) as f:
        text = f.read()
    text = re.sub(r'\\documentclass(?:\s*\[[^]]+])?\s*\{[^}]+}', lambda m: m.group() + f'\n{macro}\n', text)
    with open(filename, 'w') as f:
        f.write(text)



def run_command(cmd, dirname, log_fn):
    with open(log_fn, 'w') as logfile:
        p = subprocess.Popen(cmd, stdout=logfile, stderr=subprocess.STDOUT, cwd=dirname)
        p.communicate()
        return p.wait()



def render_tex(filename, outdir='build', keep_intermediate=False):
    """render latex document"""
    dirname = os.path.dirname(filename)
    basename = os.path.basename(filename)
    logfile = os.path.join(dirname, outdir, 'latexmk.logfile')
    os.makedirs(os.path.dirname(logfile))
    # we use -halt-on-error so that the latexmk dies if an error is encountered
    # so that we can move on to the next tex file
    # synctex=0 is no synctex, synctex=1 means synctex compressed, -1 would be synctex w/o compression
    command = ['latexmk', '-halt-on-error', '-synctex=1', '-outdir=' + outdir, '-pdf', basename]
    return_code = run_command(command, dirname, logfile)
    # we can remove the intermediate files generated by latexmk to save storage space
    if not keep_intermediate:
        # use -c to delete intermediate files, not the pdf
        command = ['latexmk', '-c', '-outdir=' + outdir]
        run_command(command, dirname, '/dev/null')
    if return_code == 0:
        pdf_name = os.path.join(dirname, outdir, os.path.splitext(basename)[0] + '.pdf')
    else:
        pdf_name = None
    return pdf_name



def get_bboxes_from_component(component, eq_aabb, dpi):
    # component comes directly from the pdfalign annotations
    # eq_aabb is the AABB of the equation (already size corrected)
    # dpi is whatever dpi we're using
    for token in component:
        for char in token['chars']:
            xmin = int(max(char['xmin'] * dpi, eq_aabb.xmin))
            ymin = int(max(char['ymin'] * dpi, eq_aabb.ymin))
            xmax = int(min(char['xmax'] * dpi, eq_aabb.xmax))
            ymax = int(min(char['ymax'] * dpi, eq_aabb.ymax))
            yield AABB(xmin, ymin, xmax, ymax)



def match_component(page, eq_aabb, comp_aabbs, color_to_match):
    # make equation mask
    eq_mask = np.zeros(page.shape[:2], dtype=bool)
    eq_mask[eq_aabb.ymin:eq_aabb.ymax+1, eq_aabb.xmin:eq_aabb.xmax+1] = True
    # make mask for annotations only
    comp_mask = np.zeros(page.shape[:2], dtype=bool)
    for aabb in comp_aabbs:
        comp_mask[aabb.ymin:aabb.ymax+1, aabb.xmin:aabb.xmax+1] = True
    # make mask for given color
    color_mask = mask_maker(page, color_to_match)
    # make mask for blackish pixels
    other_mask = mask_maker(page, 'black')
    for c in DEFAULT_COLORS:
        other_mask = np.logical_or(other_mask, mask_maker(page, c))
    other_mask = np.logical_and(other_mask, np.logical_not(color_mask))
    # calc precision, recall, and f1
    eq_other_mask = np.logical_and(eq_mask, other_mask)
    eq_color_mask = np.logical_and(eq_mask, color_mask)
    tp_mask = np.logical_and(eq_color_mask, comp_mask)
    fp_mask = np.logical_and(eq_color_mask, np.logical_not(comp_mask))
    fn_mask = np.logical_and(eq_other_mask, comp_mask)
    tp = np.count_nonzero(tp_mask)
    fp = np.count_nonzero(fp_mask)
    fn = np.count_nonzero(fn_mask)
    if tp == 0:
        return 0, 0, 0
    p = tp / (tp + fp)
    r = tp / (tp + fn)
    if p + r == 0:
        return p, r, 0
    f1 = 2 * p * r / (p + r)
    return (p, r, f1)



def mask_maker(img, color):
    if color == 'black':
        return np.all(img < 50, axis=2)
    elif color == 'myred':
        return np.logical_and(np.logical_and(img[...,0] > 200, img[...,1] < 100), img[...,2] < 100)
    elif color == 'mygreen':
        return np.logical_and(np.logical_and(img[...,0] < 100, img[...,1] > 200), img[...,2] < 100)
    elif color == 'myblue':
        return np.logical_and(np.logical_and(img[...,0] < 100, img[...,1] < 100), img[...,2] > 200)
    elif color == 'mycyan': # green + blue
        return np.logical_and(np.logical_and(img[...,0] < 100, img[...,1] > 200), img[...,2] > 200)
    elif color == 'mymagenta': # red + blue
        return np.logical_and(np.logical_and(img[...,0] > 200, img[...,1] < 100), img[...,2] > 200)
    elif color == 'myyellow': # red + green
        return np.logical_and(np.logical_and(img[...,0] > 200, img[...,1] > 200), img[...,2] < 100)



def make_equation_bbox(pages, eq_aabb):
    with open(eq_aabb) as f:
        fields = f.read().split('\t')
        pageno = int(fields[2])
        xmin = float(fields[3])
        ymin = float(fields[4])
        xmax = float(fields[5])
        ymax = float(fields[6])
    page = pages[pageno]
    h, w = page.shape[:2]
    return page, AABB(int(xmin * w), int(ymin * h), int(xmax * w), int(ymax * h))



def make_macro_lut(filename):
    with open(filename) as f:
        return build_macro_lut(LatexTokenizer(f.read()))



def main(args):
    src = args.src
    main_file = find_main_tex_file(src)
    macro_lut = make_macro_lut(main_file)
    annotations = read_equation_annotations(args.annotations)
    (filename, line) = get_equation_approx_location(annotations)
    src_filename = os.path.join(src, filename)
    raw_equation = find_equation(src_filename, line, macro_lut)
    tokens = expand_tokens(LatexTokenizer(raw_equation), macro_lut)
    for i, (fragment, color_equation) in enumerate(all_colorizations(tokens)):
        print('colorization', i)
        dst = os.path.join(args.dst, os.path.basename(src) + f'_{i}')
        copytree(src, dst)
        with open(os.path.join(dst, 'fragment.txt'), 'w') as f:
            f.write(fragment)
        main_file = find_main_tex_file(dst)
        inject_macro(main_file)
        dst_filename = os.path.join(dst, filename)
        replace_in_file(dst_filename, raw_equation, color_equation)
        pdf_name = render_tex(main_file)
        if pdf_name is None:
            rmtree(dst)
            continue
        # read pages as images and convert to numpy arrays
        pages = convert_from_path(pdf_name, dpi=DPI)
        pages = [np.array(p) for p in pages]
        # find page and bbox for equation
        page, eq_aabb = make_equation_bbox(pages, args.eq_aabb)
        with open(os.path.join(dst, 'scores.tsv'), 'w') as f:
            for ann_id, ann in enumerate(annotations):
                for comp_id, comp in enumerate(ann):
                    comp_aabbs = list(get_bboxes_from_component(comp, eq_aabb, dpi=DPI))
                    for color in DEFAULT_COLORS:
                        p, r, f1 = match_component(page, eq_aabb, comp_aabbs, color)
                        print(f'{ann_id}\t{comp_id}\t{color}\t{p}\t{r}\t{f1}', file=f)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('src')
    parser.add_argument('dst')
    parser.add_argument('annotations')
    parser.add_argument('eq_aabb')
    args = parser.parse_args()
    main(args)
